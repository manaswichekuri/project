import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Pre-populate synthetic data for API route testing
        client.post('/api/v1/activities/synthetic/generate', json={'days': 2, 'reset': True})
        client.post('/api/v1/ml/run-detection')
        yield client

def test_system_status_route(client):
    res = client.get('/api/v1/system/status')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'HEALTHY'

def test_list_users_route(client):
    res = client.get('/api/v1/users')
    assert res.status_code == 200
    data = res.get_json()
    assert 'users' in data
    assert len(data['users']) == 14

def test_user_detail_route(client):
    res = client.get('/api/v1/users/EMP-1013')
    assert res.status_code == 200
    assert res.get_json()['user']['user_id'] == 'EMP-1013'

def test_user_risk_profile_route(client):
    res = client.get('/api/v1/users/EMP-1013/risk-profile')
    assert res.status_code == 200
    data = res.get_json()
    assert 'risk_history' in data
    assert 'recent_activities' in data

def test_list_activities_route(client):
    res = client.get('/api/v1/activities')
    assert res.status_code == 200
    assert 'activities' in res.get_json()

def test_list_alerts_route(client):
    res = client.get('/api/v1/alerts')
    assert res.status_code == 200
    alerts = res.get_json()['alerts']
    assert len(alerts) >= 1

def test_update_alert_status_route(client):
    res = client.get('/api/v1/alerts')
    alerts = res.get_json()['alerts']
    assert len(alerts) > 0
    alert_id = alerts[0]['alert_id']

    patch_res = client.patch(f'/api/v1/alerts/{alert_id}', json={'status': 'Investigating'})
    assert patch_res.status_code == 200
    assert patch_res.get_json()['alert']['status'] == 'Investigating'
