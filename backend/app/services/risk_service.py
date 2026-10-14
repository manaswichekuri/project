import os
import uuid
from app.utils.db import get_db
from app.ml.preprocessor import FeaturePreprocessor
from app.ml.model import IsolationForestModel
from app.ml.explainer import RiskExplainer
from app.ml.synthetic_generator import generate_synthetic_dataset
from app.config.settings import Config
from app.utils.time_utils import utc_now_iso

def run_ml_detection_pipeline():
    db = get_db()
    
    # 1. Fetch activities and users
    activities = list(db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in db.users.find({}, {'_id': 0})}

    # Auto-seed synthetic dataset if database is currently empty
    if not activities or not users:
        generate_synthetic_dataset(num_days=7, reset_db=False)
        activities = list(db.activities.find({}, {'_id': 0}))
        users = {u['user_id']: u for u in db.users.find({}, {'_id': 0})}

    if not activities or not users:
        return {'message': 'No activity logs or user accounts found to analyze.', 'evaluations': 0}

    # 2. Extract features
    preprocessor = FeaturePreprocessor()
    feat_df = preprocessor.extract_features_from_activities(activities, users)

    if feat_df.empty:
        return {'message': 'No features extracted from activities.', 'evaluations': 0}

    X_scaled = preprocessor.fit_transform(feat_df)

    # 3. Fit & Predict Isolation Forest model
    model = IsolationForestModel(contamination=Config.CONTAMINATION_RATE)
    model.train(X_scaled)
    raw_scores = model.predict_anomaly_scores(X_scaled)
    model.save_model(os.path.join(Config.MODEL_DIR, 'pretrained_model.joblib'))

    # 4. Compute risk scores and explainable reasons for each user
    evaluated_at = utc_now_iso()
    risk_score_docs = []
    alert_docs = []

    for idx, row in feat_df.iterrows():
        u_id = row['user_id']
        raw_score = float(raw_scores[idx])

        # score_samples returns -s, where s in (0, 1] is the Isolation Forest anomaly score:
        # s <= 0.5 means no distinct anomaly, s -> 1 means clearly anomalous. Map s in [0.5, 1] to 0-50 points.
        anomaly_score = -raw_score
        ml_anomaly_weight = max(0.0, min(50.0, (anomaly_score - 0.5) * 100.0))

        # Heuristic Risk Rule Additions
        rule_points = 0.0
        if row['after_hours_ratio'] > 0.20:
            rule_points += 25.0 * (row['after_hours_ratio'] * 1.5)
        if row['failed_login_count'] >= 3:
            rule_points += min(30.0, row['failed_login_count'] * 7.5)
        if row['download_volume_mb'] > 300.0:
            rule_points += min(35.0, (row['download_volume_mb'] / 500.0) * 20.0)
        if row['upload_volume_mb'] > 100.0:
            rule_points += min(30.0, (row['upload_volume_mb'] / 200.0) * 20.0)
        if row['location_deviation_count'] >= 1:
            rule_points += 25.0 * row['location_deviation_count']
        if row['device_deviation_count'] >= 1:
            rule_points += 20.0 * row['device_deviation_count']

        total_risk_score = round(max(0.0, min(100.0, ml_anomaly_weight + rule_points)), 1)

        # Categorize Risk
        if total_risk_score >= Config.RISK_THRESHOLD_CRITICAL:
            category = 'Critical'
        elif total_risk_score >= Config.RISK_THRESHOLD_HIGH:
            category = 'High'
        elif total_risk_score >= 30.0:
            category = 'Medium'
        else:
            category = 'Low'

        # Generate Explainable Reasons
        reasons = RiskExplainer.generate_reasons_for_user(row.to_dict())

        risk_doc = {
            'user_id': u_id,
            'evaluated_at': evaluated_at,
            'raw_anomaly_score': round(raw_score, 4),
            'normalized_risk_score': total_risk_score,
            'risk_category': category,
            'contributing_reasons': reasons,
            'feature_metrics': row.to_dict()
        }
        risk_score_docs.append(risk_doc)

        # Generate Alert if risk >= High threshold
        if total_risk_score >= Config.RISK_THRESHOLD_HIGH:
            # Check if open alert already exists for user to avoid spamming duplicates
            existing_open = db.alerts.find_one({'user_id': u_id, 'status': 'Open'})
            if not existing_open:
                alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
                alert_doc = {
                    'alert_id': alert_id,
                    'user_id': u_id,
                    'timestamp': evaluated_at,
                    'event_type': 'ANOMALOUS_BEHAVIOR_DETECTED',
                    'risk_score': total_risk_score,
                    'severity': category,
                    'status': 'Open',
                    'reasons': reasons,
                    'assigned_to': None,
                    'updated_at': evaluated_at
                }
                alert_docs.append(alert_doc)

    # 5. Persist to MongoDB
    if risk_score_docs:
        db.risk_scores.insert_many(risk_score_docs)
    if alert_docs:
        db.alerts.insert_many(alert_docs)

    return {
        'message': f"ML Anomaly Detection completed. Evaluated {len(risk_score_docs)} users.",
        'users_evaluated': len(risk_score_docs),
        'alerts_generated': len(alert_docs),
        'high_critical_users': sum(1 for r in risk_score_docs if r['risk_category'] in ['High', 'Critical'])
    }

def get_risk_summary():
    db = get_db()
    users = list(db.users.find({}, {'_id': 0}))
    total_users = len(users)
    total_activities = db.activities.count_documents({})

    low_cnt = 0
    medium_cnt = 0
    high_cnt = 0
    critical_cnt = 0

    for user in users:
        latest_risk = db.risk_scores.find_one(
            {'user_id': user['user_id']},
            sort=[('evaluated_at', -1)]
        )
        cat = latest_risk.get('risk_category', 'Low') if latest_risk else 'Low'
        if cat == 'Critical':
            critical_cnt += 1
        elif cat == 'High':
            high_cnt += 1
        elif cat == 'Medium':
            medium_cnt += 1
        else:
            low_cnt += 1

    return {
        'total_users': total_users,
        'total_activities': total_activities,
        'risk_distribution': {
            'Low': low_cnt,
            'Medium': medium_cnt,
            'High': high_cnt,
            'Critical': critical_cnt
        },
        'high_risk_users_count': high_cnt + critical_cnt,
        'active_alerts_count': db.alerts.count_documents({'status': 'Open'})
    }
