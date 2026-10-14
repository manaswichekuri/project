import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_admin_login_success(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'Admin@12345'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data
    assert data['user']['username'] == 'admin'

def test_admin_login_invalid_password(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin',
        'password': 'WrongPassword123'
    })
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_admin_login_missing_fields(client):
    response = client.post('/api/v1/auth/login', json={
        'username': 'admin'
    })
    assert response.status_code == 400
