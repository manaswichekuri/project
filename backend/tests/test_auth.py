def test_admin_login_success(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'Admin@12345'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['token'].count('.') == 2  # a real JWT
    assert data['user']['username'] == 'admin'

def test_admin_login_username_case_insensitive(client):
    response = client.post('/api/v1/auth/login', json={'username': ' ADMIN ', 'password': 'Admin@12345'})
    assert response.status_code == 200

def test_admin_login_invalid_password(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'WrongPassword123'
    })
    assert response.status_code == 401
    assert 'error' in response.get_json()

def test_former_backdoor_passwords_rejected(client):
    for pwd in ('admin', 'admin123', 'admin@12345'):
        res = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': pwd})
        assert res.status_code == 401, pwd

def test_regex_username_does_not_match(client):
    res = client.post('/api/v1/auth/login', json={'username': '.*', 'password': 'Admin@12345'})
    assert res.status_code == 401

def test_admin_login_missing_fields(client):
    response = client.post('/api/v1/auth/login', json={'username': 'admin'})
    assert response.status_code == 400

def test_login_non_json_body(client):
    response = client.post('/api/v1/auth/login', data='not json', content_type='text/plain')
    assert response.status_code == 400

def test_me_endpoint(auth_client, client):
    assert client.get('/api/v1/auth/me').status_code == 401
    res = auth_client.get('/api/v1/auth/me')
    assert res.status_code == 200
    assert res.get_json()['user']['username'] == 'admin'

def test_protected_routes_require_token(client):
    for method, url in [
        ('get', '/api/v1/users'),
        ('get', '/api/v1/activities'),
        ('get', '/api/v1/alerts'),
        ('get', '/api/v1/alerts/stats'),
        ('get', '/api/v1/risk/summary'),
        ('get', '/api/v1/system/status'),
        ('get', '/api/v1/ml/model-info'),
        ('post', '/api/v1/ml/run-detection'),
        ('post', '/api/v1/activities/synthetic/generate'),
    ]:
        res = getattr(client, method)(url)
        assert res.status_code == 401, url

def test_invalid_token_rejected(client):
    res = client.get('/api/v1/users', headers={'Authorization': 'Bearer demo-jwt-token-for-admin'})
    assert res.status_code == 401

def test_expired_token_rejected(client, monkeypatch):
    from app.config.settings import Config
    from app.utils.auth import create_token
    monkeypatch.setattr(Config, 'JWT_EXPIRES_HOURS', -1)
    token = create_token({'username': 'admin'})
    res = client.get('/api/v1/users', headers={'Authorization': f'Bearer {token}'})
    assert res.status_code == 401

def test_health_is_public(client):
    res = client.get('/api/v1/health')
    assert res.status_code == 200
    assert res.get_json()['status'] == 'ok'

def test_seed_is_idempotent_and_rotates_password(client, db, monkeypatch):
    from app.config.settings import Config
    from app.services.auth_service import seed_default_admin
    seed_default_admin()
    seed_default_admin()
    assert db.admins.count_documents({'username': 'admin'}) == 1

    monkeypatch.setattr(Config, 'ADMIN_PASSWORD', 'N3w-Strong-Pass!')
    seed_default_admin()
    assert client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'Admin@12345'}).status_code == 401
    assert client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'N3w-Strong-Pass!'}).status_code == 200
