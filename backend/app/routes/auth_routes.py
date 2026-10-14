import logging
from flask import Blueprint, request, jsonify, g
from app.services.auth_service import authenticate_admin, get_admin
from app.utils.auth import create_token, require_auth
from app.utils.json_encoder import jsonify_doc

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = authenticate_admin(username, password)
    if not admin:
        logger.warning("Failed login attempt for username: %r", username[:64])
        return jsonify({'error': 'Invalid administrator credentials'}), 401

    logger.info("Successful login for admin: %r", admin['username'])
    return jsonify_doc({
        'message': 'Authentication successful',
        'token': create_token(admin),
        'user': admin
    })

@auth_bp.route('/me', methods=['GET'])
def me():
    denied = require_auth()
    if denied:
        return denied
    admin = get_admin(g.current_admin.get('sub'))
    if not admin:
        return jsonify({'error': 'Account no longer exists', 'code': 401}), 401
    return jsonify_doc({'user': admin})
