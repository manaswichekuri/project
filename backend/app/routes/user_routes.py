from flask import Blueprint, request, jsonify
from app.services.user_service import get_all_users, get_user_by_id, get_user_risk_profile
from app.utils.json_encoder import jsonify_doc
from app.utils.auth import require_auth

user_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')
user_bp.before_request(require_auth)

@user_bp.route('', methods=['GET'])
def list_users():
    search = request.args.get('search')
    department = request.args.get('department')
    risk_category = request.args.get('risk_category')

    users = get_all_users(search_query=search, department=department, risk_category=risk_category)
    return jsonify_doc({'users': users, 'total': len(users)})

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': f'User {user_id} not found'}), 404
    return jsonify_doc({'user': user})

@user_bp.route('/<user_id>/risk-profile', methods=['GET'])
def get_user_profile(user_id):
    profile = get_user_risk_profile(user_id)
    if not profile:
        return jsonify({'error': f'User {user_id} not found'}), 404
    return jsonify_doc(profile)
