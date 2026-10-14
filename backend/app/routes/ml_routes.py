from flask import Blueprint, jsonify
from app.services.risk_service import run_ml_detection_pipeline
from app.config.settings import Config
from app.utils.json_encoder import jsonify_doc

ml_bp = Blueprint('ml', __name__, url_prefix='/api/v1/ml')

@ml_bp.route('/run-detection', methods=['POST'])
def run_detection():
    result = run_ml_detection_pipeline()
    return jsonify_doc(result)

@ml_bp.route('/model-info', methods=['GET'])
def get_model_info():
    return jsonify_doc({
        'model_name': 'Isolation Forest Anomaly Detector',
        'algorithm': 'IsolationForest',
        'library': 'scikit-learn',
        'contamination': Config.CONTAMINATION_RATE,
        'features_engineered': [
            'after_hours_ratio',
            'failed_login_count',
            'file_access_count',
            'download_volume_mb',
            'upload_volume_mb',
            'location_deviation_count',
            'device_deviation_count'
        ],
        'risk_thresholds': {
            'High': Config.RISK_THRESHOLD_HIGH,
            'Critical': Config.RISK_THRESHOLD_CRITICAL
        }
    })
