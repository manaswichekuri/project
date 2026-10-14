from flask import Blueprint, jsonify
from app.services.risk_service import get_risk_summary
from app.utils.json_encoder import jsonify_doc
from app.utils.auth import require_auth

risk_bp = Blueprint('risk', __name__, url_prefix='/api/v1/risk')
risk_bp.before_request(require_auth)

@risk_bp.route('/summary', methods=['GET'])
def risk_summary():
    summary = get_risk_summary()
    return jsonify_doc(summary)
