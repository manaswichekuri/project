from flask import Blueprint, request, jsonify
from app.services.alert_service import get_alerts, update_alert_status, get_alert_stats
from app.utils.json_encoder import jsonify_doc
from app.utils.auth import require_auth

alert_bp = Blueprint('alerts', __name__, url_prefix='/api/v1/alerts')
alert_bp.before_request(require_auth)

@alert_bp.route('', methods=['GET'])
def list_alerts():
    status = request.args.get('status')
    severity = request.args.get('severity')
    user_id = request.args.get('user_id')

    alerts = get_alerts(status=status, severity=severity, user_id=user_id)
    return jsonify_doc({'alerts': alerts, 'total': len(alerts)})

@alert_bp.route('/<alert_id>', methods=['PATCH'])
def update_alert(alert_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    notes = data.get('notes')

    if not new_status:
        return jsonify({'error': 'Status field is required'}), 400

    updated = update_alert_status(alert_id, new_status, notes)
    if not updated:
        return jsonify({'error': f'Alert {alert_id} not found or invalid status'}), 404

    return jsonify_doc({'message': 'Alert status updated successfully', 'alert': updated})

@alert_bp.route('/stats', methods=['GET'])
def alert_stats():
    stats = get_alert_stats()
    return jsonify_doc(stats)
