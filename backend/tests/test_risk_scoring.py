import bson
from app.ml.explainer import RiskExplainer

def test_risk_explainer_reasons():
    normal_row = {
        'after_hours_ratio': 0.0,
        'failed_login_count': 0,
        'file_access_count': 3,
        'download_volume_mb': 12.0,
        'upload_volume_mb': 1.0,
        'location_deviation_count': 0,
        'device_deviation_count': 0
    }
    reasons_normal = RiskExplainer.generate_reasons_for_user(normal_row)
    assert 'Behavior consistent with standard employee baseline profile' in reasons_normal[0]

    anomalous_row = {
        'after_hours_ratio': 0.75,
        'failed_login_count': 5,
        'file_access_count': 85,
        'download_volume_mb': 1250.0,
        'upload_volume_mb': 350.0,
        'location_deviation_count': 2,
        'device_deviation_count': 1
    }
    reasons_anom = RiskExplainer.generate_reasons_for_user(anomalous_row)
    assert len(reasons_anom) >= 5
    assert any('Unusual after-hours activity' in r for r in reasons_anom)
    assert any('Multiple failed login attempts' in r for r in reasons_anom)
    assert any('Download volume significantly above baseline' in r for r in reasons_anom)
    assert any('Abnormally high data egress' in r for r in reasons_anom)
    # Counts are totals across the analysis window, not single-session or consecutive figures
    assert not any('consecutive' in r or 'in session' in r for r in reasons_anom)

    reasons_one = RiskExplainer.generate_reasons_for_user({**normal_row, 'failed_login_count': 1})
    assert any('(1 failed attempt over the analysis period)' in r for r in reasons_one)

def test_full_risk_detection_run(auth_client, db):
    res_gen = auth_client.post('/api/v1/activities/synthetic/generate', json={'days': 3, 'reset': True})
    assert res_gen.status_code == 201

    res_ml = auth_client.post('/api/v1/ml/run-detection')
    assert res_ml.status_code == 200
    data = res_ml.get_json()
    assert data['users_evaluated'] == 14
    assert data['alerts_generated'] >= 1

    res_sum = auth_client.get('/api/v1/risk/summary')
    assert res_sum.status_code == 200
    sum_data = res_sum.get_json()
    assert sum_data['total_users'] == 14
    assert sum_data['high_risk_users_count'] >= 1

    # Persisted documents must be BSON-encodable for a real MongoDB server
    for doc in db.risk_scores.find({}, {'_id': 0}):
        bson.encode(doc)


def test_detection_auto_seeds_empty_db(auth_client):
    res = auth_client.post('/api/v1/ml/run-detection')
    assert res.status_code == 200
    assert res.get_json()['users_evaluated'] == 14


def test_detection_does_not_duplicate_open_alerts(auth_client):
    auth_client.post('/api/v1/activities/synthetic/generate', json={'days': 3, 'reset': True})
    first = auth_client.post('/api/v1/ml/run-detection').get_json()
    second = auth_client.post('/api/v1/ml/run-detection').get_json()
    assert first['alerts_generated'] >= 1
    assert second['alerts_generated'] == 0


def test_risk_categories_separate_normal_from_anomalous(auth_client):
    auth_client.post('/api/v1/activities/synthetic/generate', json={'days': 7, 'reset': True})
    auth_client.post('/api/v1/ml/run-detection')
    users = {u['user_id']: u for u in auth_client.get('/api/v1/users').get_json()['users']}
    normal = [users[f'EMP-10{i:02d}'] for i in range(1, 11)]
    assert all(u['risk_category'] == 'Low' for u in normal), [(u['user_id'], u['current_risk_score']) for u in normal]
    assert users['EMP-1013']['risk_category'] == 'Critical'
    assert users['EMP-1014']['risk_category'] == 'Critical'
    for uid in ('EMP-1011', 'EMP-1012'):
        assert users[uid]['current_risk_score'] > max(u['current_risk_score'] for u in normal)
