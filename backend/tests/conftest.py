import os
import tempfile

# Must be set before the app (and its Config) is imported
os.environ['USE_MOCK_DB'] = 'true'
os.environ['APP_ENV'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key-for-pytest-only-0123456789'
os.environ['ADMIN_USERNAME'] = 'admin'
os.environ['ADMIN_PASSWORD'] = 'Admin@12345'
os.environ['MODEL_DIR'] = tempfile.mkdtemp(prefix='itd-models-')

import pytest
from app import create_app
from app.utils.db import get_db, reset_db_connection


@pytest.fixture
def app():
    # Fresh in-memory database per test so tests are independent
    reset_db_connection()
    application = create_app()
    application.config['TESTING'] = True
    with application.app_context():
        yield application
    reset_db_connection()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return get_db()


@pytest.fixture
def auth_headers(client):
    res = client.post('/api/v1/auth/login', json={'username': 'admin', 'password': 'Admin@12345'})
    assert res.status_code == 200
    return {'Authorization': f"Bearer {res.get_json()['token']}"}


class AuthClient:
    """Thin wrapper around the Flask test client that sends the Bearer token on every call."""

    def __init__(self, client, headers):
        self._client = client
        self._headers = headers

    def __getattr__(self, method):
        fn = getattr(self._client, method)

        def call(*args, **kwargs):
            kwargs['headers'] = {**self._headers, **kwargs.get('headers', {})}
            return fn(*args, **kwargs)
        return call


@pytest.fixture
def auth_client(client, auth_headers):
    return AuthClient(client, auth_headers)


@pytest.fixture
def seeded_client(auth_client):
    res = auth_client.post('/api/v1/activities/synthetic/generate', json={'days': 2, 'reset': True})
    assert res.status_code == 201
    res = auth_client.post('/api/v1/ml/run-detection')
    assert res.status_code == 200
    return auth_client
