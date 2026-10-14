from flask import Blueprint, request, jsonify
from app.services.activity_service import get_activities, add_activity_log
from app.ml.synthetic_generator import generate_synthetic_dataset
from app.utils.json_encoder import jsonify_doc

activity_bp = Blueprint('activities', __name__, url_prefix='/api/v1/activities')

@activity_bp.route('', methods=['GET'])
def list_activities():
    user_id = request.args.get('user_id')
    event_type = request.args.get('event_type')
    after_hours = request.args.get('after_hours', '').lower() in ('true', '1')
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))

    result = get_activities(
        user_id=user_id,
        event_type=event_type,
        after_hours_only=after_hours,
        page=page,
        limit=limit
    )
    return jsonify_doc(result)

@activity_bp.route('', methods=['POST'])
def create_activity():
    data = request.get_json()
    if not data or not data.get('user_id'):
        return jsonify({'error': 'Invalid activity payload, user_id required'}), 400

    new_log = add_activity_log(data)
    return jsonify_doc({'message': 'Activity recorded', 'activity': new_log}, 201)

@activity_bp.route('/synthetic/generate', methods=['POST'])
def trigger_synthetic_generation():
    data = request.get_json() or {}
    days = int(data.get('days', 7))
    reset = data.get('reset', True)

    res = generate_synthetic_dataset(num_days=days, reset_db=reset)
    return jsonify_doc(res, 201)
