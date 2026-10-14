import pytest
from app.ml.explainer import RiskExplainer
from app.services.risk_service import run_ml_detection_pipeline, get_risk_summary
from app import create_app

@pytest.fixture
def app_client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

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

def test_full_risk_detection_run(app_client):
    res_gen = app_client.post('/api/v1/activities/synthetic/generate', json={'days': 3, 'reset': True})
    assert res_gen.status_code == 201

    res_ml = app_client.post('/api/v1/ml/run-detection')
    assert res_ml.status_code == 200
    data = res_ml.get_json()
    assert data['users_evaluated'] == 14
    assert data['alerts_generated'] >= 1

    res_sum = app_client.get('/api/v1/risk/summary')
    assert res_sum.status_code == 200
    sum_data = res_sum.get_json()
    assert sum_data['total_users'] == 14
    assert sum_data['high_risk_users_count'] >= 1
