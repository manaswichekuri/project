def test_system_status_route(seeded_client):
    res = seeded_client.get('/api/v1/system/status')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'HEALTHY'
    assert data['database']['collections']['users'] == 14

def test_model_info_route(seeded_client):
    res = seeded_client.get('/api/v1/ml/model-info')
    assert res.status_code == 200
    assert len(res.get_json()['features_engineered']) == 7

def test_list_users_route(seeded_client):
    res = seeded_client.get('/api/v1/users')
    assert res.status_code == 200
    assert len(res.get_json()['users']) == 14

def test_user_search_and_filters(seeded_client):
    res = seeded_client.get('/api/v1/users?search=Dmitri')
    assert [u['user_id'] for u in res.get_json()['users']] == ['EMP-1013']
    # Regex metacharacters are treated literally rather than crashing or matching everything
    res = seeded_client.get('/api/v1/users?search=(')
    assert res.status_code == 200
    assert res.get_json()['users'] == []
    res = seeded_client.get('/api/v1/users?department=Finance')
    assert all(u['department'] == 'Finance' for u in res.get_json()['users'])

def test_user_detail_route(seeded_client):
    res = seeded_client.get('/api/v1/users/EMP-1013')
    assert res.status_code == 200
    assert res.get_json()['user']['user_id'] == 'EMP-1013'

def test_user_not_found(seeded_client):
    assert seeded_client.get('/api/v1/users/NOPE').status_code == 404
    assert seeded_client.get('/api/v1/users/NOPE/risk-profile').status_code == 404

def test_user_risk_profile_route(seeded_client):
    res = seeded_client.get('/api/v1/users/EMP-1013/risk-profile')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['risk_history']) >= 1
    assert len(data['recent_activities']) >= 1

def test_list_activities_route(seeded_client):
    res = seeded_client.get('/api/v1/activities?limit=10&page=2&event_type=All')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data['activities']) == 10
    assert data['page'] == 2

def test_activities_bad_pagination(seeded_client):
    assert seeded_client.get('/api/v1/activities?page=abc').status_code == 400
    res = seeded_client.get('/api/v1/activities?page=-5&limit=100000')
    assert res.status_code == 200
    data = res.get_json()
    assert data['page'] == 1 and data['limit'] == 500

def test_create_activity_validation(auth_client):
    assert auth_client.post('/api/v1/activities', json={}).status_code == 400
    assert auth_client.post('/api/v1/activities', json={'user_id': 'EMP-1', 'event_type': 'HACK', 'timestamp': 'x'}).status_code == 400
    assert auth_client.post('/api/v1/activities', json={
        'user_id': 'EMP-1', 'event_type': 'LOGIN', 'timestamp': '2026-01-01T10:00:00Z', 'failed_logins': 'many'
    }).status_code == 400

def test_create_activity(auth_client):
    res = auth_client.post('/api/v1/activities', json={
        'user_id': 'EMP-1001',
        'event_type': 'FILE_DOWNLOAD',
        'timestamp': '2026-01-01T10:00:00Z',
        'file_details': {'filename': 'a.txt', 'download_size_mb': 12.5},
    })
    assert res.status_code == 201
    activity = res.get_json()['activity']
    assert activity['activity_id'].startswith('ACT-')
    assert '_id' not in activity
    listed = auth_client.get('/api/v1/activities?user_id=EMP-1001').get_json()
    assert listed['total'] == 1

def test_synthetic_generate_bad_days(auth_client):
    assert auth_client.post('/api/v1/activities/synthetic/generate', json={'days': 'x'}).status_code == 400

def test_list_alerts_route(seeded_client):
    res = seeded_client.get('/api/v1/alerts')
    assert res.status_code == 200
    assert len(res.get_json()['alerts']) >= 1

def test_alert_stats_route(seeded_client):
    res = seeded_client.get('/api/v1/alerts/stats')
    assert res.status_code == 200
    assert res.get_json()['total'] >= 1

def test_risk_summary_route(seeded_client):
    data = seeded_client.get('/api/v1/risk/summary').get_json()
    assert data['total_users'] == 14
    assert sum(data['risk_distribution'].values()) == 14

def test_update_alert_status_route(seeded_client):
    alerts = seeded_client.get('/api/v1/alerts').get_json()['alerts']
    assert len(alerts) > 0
    alert_id = alerts[0]['alert_id']

    patch_res = seeded_client.patch(f'/api/v1/alerts/{alert_id}', json={'status': 'Investigating', 'notes': 'Looking'})
    assert patch_res.status_code == 200
    alert = patch_res.get_json()['alert']
    assert alert['status'] == 'Investigating'
    assert alert['admin_notes'] == 'Looking'

def test_update_alert_invalid(seeded_client):
    assert seeded_client.patch('/api/v1/alerts/ALT-NOPE', json={'status': 'Resolved'}).status_code == 404
    assert seeded_client.patch('/api/v1/alerts/ALT-NOPE', json={}).status_code == 400

def test_unknown_route_and_method(client):
    assert client.get('/api/v1/does-not-exist').get_json()['code'] == 404
    assert client.delete('/api/v1/auth/login').status_code == 405

def test_activity_stats_route(seeded_client):
    data = seeded_client.get('/api/v1/activities/stats').get_json()
    assert data['total'] > 0
    assert sum(data['event_type_breakdown'].values()) == data['total']
