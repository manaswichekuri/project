import os
from app.ml.synthetic_generator import generate_synthetic_dataset
from app.ml.preprocessor import FeaturePreprocessor
from app.ml.model import IsolationForestModel


def _features(db):
    activities = list(db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in db.users.find({}, {'_id': 0})}
    return FeaturePreprocessor().extract_features_from_activities(activities, users)


def test_synthetic_generator_and_preprocessor(db):
    res = generate_synthetic_dataset(num_days=2, reset_db=True)
    assert res['users_created'] == 14
    assert res['activities_created'] > 0

    preprocessor = FeaturePreprocessor()
    activities = list(db.activities.find({}, {'_id': 0}))
    users = {u['user_id']: u for u in db.users.find({}, {'_id': 0})}
    feat_df = preprocessor.extract_features_from_activities(activities, users)
    assert len(feat_df) == 14

    X_scaled = preprocessor.fit_transform(feat_df)
    assert X_scaled.shape == (14, 7)


def test_activity_ids_unique_across_runs(db):
    generate_synthetic_dataset(num_days=1, reset_db=True)
    generate_synthetic_dataset(num_days=1, reset_db=False)
    ids = [a['activity_id'] for a in db.activities.find({}, {'activity_id': 1})]
    assert len(ids) == len(set(ids))


def test_isolation_forest_model(db, tmp_path):
    generate_synthetic_dataset(num_days=2, reset_db=True)
    X_scaled = FeaturePreprocessor().fit_transform(_features(db))

    model = IsolationForestModel(contamination=0.1)
    model.train(X_scaled)
    scores = model.predict_anomaly_scores(X_scaled)
    assert len(scores) == 14

    path = os.path.join(tmp_path, 'model.joblib')
    model.save_model(path)
    reloaded = IsolationForestModel()
    assert reloaded.load_model(path)
    assert len(reloaded.predict_anomaly_scores(X_scaled)) == 14
