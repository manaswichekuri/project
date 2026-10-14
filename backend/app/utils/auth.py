from datetime import timedelta

import jwt
from flask import request, jsonify, g

from app.config.settings import Config
from app.utils.time_utils import utc_now

JWT_ALGORITHM = 'HS256'


def create_token(admin):
    now = utc_now()
    payload = {
        'sub': admin['username'],
        'name': admin.get('name'),
        'role': admin.get('role'),
        'iat': now,
        'exp': now + timedelta(hours=Config.JWT_EXPIRES_HOURS),
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(token):
    """Returns the decoded payload, or None if the token is invalid or expired."""
    try:
        return jwt.decode(token, Config.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None


def require_auth():
    """before_request hook: rejects requests without a valid Bearer token."""
    if request.method == 'OPTIONS':
        return None

    header = request.headers.get('Authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return jsonify({'error': 'Authentication required', 'code': 401}), 401

    payload = verify_token(token.strip())
    if not payload:
        return jsonify({'error': 'Invalid or expired token', 'code': 401}), 401

    g.current_admin = payload
    return None
