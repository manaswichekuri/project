from flask import Blueprint, jsonify
from app.utils.db import get_db, is_mock_db
from app.utils.json_encoder import jsonify_doc
from app.utils.auth import require_auth

system_bp = Blueprint('system', __name__, url_prefix='/api/v1/system')
system_bp.before_request(require_auth)

@system_bp.route('/status', methods=['GET'])
def get_system_status():
    db = get_db()
    
    users_count = db.users.count_documents({})
    activities_count = db.activities.count_documents({})
    alerts_count = db.alerts.count_documents({})
    open_alerts_count = db.alerts.count_documents({'status': 'Open'})
    
    return jsonify_doc({
        'status': 'HEALTHY',
        'system_name': 'AI-Powered Insider Threat Detection System',
        'version': '1.0.0-capstone',
        'database': {
            'is_mock': is_mock_db(),
            'collections': {
                'users': users_count,
                'activities': activities_count,
                'alerts': alerts_count,
                'open_alerts': open_alerts_count
            }
        },
        'ml_engine': {
            'algorithm': 'Isolation Forest (scikit-learn)',
            'status': 'READY'
        }
    })
