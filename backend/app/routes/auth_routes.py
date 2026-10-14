import logging
from flask import Blueprint, request, jsonify
from app.services.auth_service import authenticate_admin
from app.utils.json_encoder import jsonify_doc

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    admin = authenticate_admin(username, password)
    if not admin:
        logger.warning(f"Failed login attempt for username: '{username}'")
        return jsonify({'error': 'Invalid administrator credentials'}), 401

    logger.info(f"Successful login for admin: '{admin['username']}'")
    return jsonify_doc({
        'message': 'Authentication successful',
        'token': f'demo-jwt-token-for-{admin["username"]}',
        'user': admin
    })
