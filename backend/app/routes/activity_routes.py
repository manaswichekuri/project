import uuid
from flask import Blueprint, request, jsonify
from app.services.activity_service import get_activities, add_activity_log, get_activity_stats
from app.ml.synthetic_generator import generate_synthetic_dataset
from app.utils.json_encoder import jsonify_doc
from app.utils.request_utils import parse_int
from app.utils.auth import require_auth

activity_bp = Blueprint('activities', __name__, url_prefix='/api/v1/activities')
activity_bp.before_request(require_auth)

VALID_EVENT_TYPES = {'LOGIN', 'LOGOUT', 'FILE_ACCESS', 'FILE_DOWNLOAD', 'FILE_UPLOAD', 'APP_USAGE'}

@activity_bp.route('', methods=['GET'])
def list_activities():
    user_id = request.args.get('user_id')
    event_type = request.args.get('event_type')
    after_hours = request.args.get('after_hours', '').lower() in ('true', '1')
    page = parse_int(request.args.get('page'), 'page', 1, minimum=1)
    limit = parse_int(request.args.get('limit'), 'limit', 50, minimum=1, maximum=500)

    result = get_activities(
        user_id=user_id,
        event_type=event_type,
        after_hours_only=after_hours,
        page=page,
        limit=limit
    )
    return jsonify_doc(result)

@activity_bp.route('/stats', methods=['GET'])
def activity_stats():
    return jsonify_doc(get_activity_stats())

@activity_bp.route('', methods=['POST'])
def create_activity():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object'}), 400

    missing = [f for f in ('user_id', 'event_type', 'timestamp') if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing required field(s): {', '.join(missing)}"}), 400
    if data['event_type'] not in VALID_EVENT_TYPES:
        return jsonify({'error': f"event_type must be one of: {', '.join(sorted(VALID_EVENT_TYPES))}"}), 400

    file_details = data.get('file_details') or {}
    if not isinstance(file_details, dict):
        return jsonify({'error': 'file_details must be an object'}), 400

    try:
        activity = {
            'activity_id': data.get('activity_id') or f"ACT-{uuid.uuid4().hex[:10].upper()}",
            'user_id': str(data['user_id']),
            'timestamp': str(data['timestamp']),
            'event_type': data['event_type'],
            'location_ip': str(data.get('location_ip', '')),
            'location_name': str(data.get('location_name', '')),
            'device_id': str(data.get('device_id', '')),
            'app_used': str(data.get('app_used', '')),
            'file_details': {
                'filename': str(file_details.get('filename', '')),
                'files_accessed_count': int(file_details.get('files_accessed_count', 0)),
                'download_size_mb': float(file_details.get('download_size_mb', 0.0)),
                'upload_size_mb': float(file_details.get('upload_size_mb', 0.0)),
            },
            'after_hours': bool(data.get('after_hours', False)),
            'failed_logins': int(data.get('failed_logins', 0)),
            'is_demo_synthetic': False,
        }
    except (TypeError, ValueError):
        return jsonify({'error': 'Numeric fields (failed_logins, file_details counts/sizes) must be numbers'}), 400

    new_log = add_activity_log(activity)
    return jsonify_doc({'message': 'Activity recorded', 'activity': new_log}, 201)

@activity_bp.route('/synthetic/generate', methods=['POST'])
def trigger_synthetic_generation():
    data = request.get_json(silent=True) or {}
    days = parse_int(data.get('days'), 'days', 7, minimum=1, maximum=60)
    reset = bool(data.get('reset', True))

    res = generate_synthetic_dataset(num_days=days, reset_db=reset)
    return jsonify_doc(res, 201)
