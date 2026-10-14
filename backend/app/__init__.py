import logging
from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from app.config.settings import Config, DEFAULT_SECRET_KEY
from app.utils.db import init_db_indexes
from app.utils.request_utils import BadRequest
from app.services.auth_service import seed_default_admin
from app.routes.system_routes import system_bp
from app.routes.auth_routes import auth_bp
from app.routes.user_routes import user_bp
from app.routes.activity_routes import activity_bp
from app.routes.alert_routes import alert_bp
from app.routes.ml_routes import ml_bp
from app.routes.risk_routes import risk_bp

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if config_class.APP_ENV == 'production' and config_class.SECRET_KEY == DEFAULT_SECRET_KEY:
        app.logger.warning("SECRET_KEY is set to the insecure default. Set a strong SECRET_KEY in production!")

    origins = config_class.CORS_ORIGINS
    CORS(app, resources={r"/api/*": {"origins": '*' if '*' in origins else origins}})

    # Initialize DB indexes and the admin account
    with app.app_context():
        init_db_indexes()
        seed_default_admin()

    # Register blueprints
    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(ml_bp)
    app.register_blueprint(risk_bp)

    # Root & API info routes
    @app.route('/')
    @app.route('/api')
    @app.route('/api/v1')
    def index():
        return jsonify({
            'status': 'HEALTHY',
            'service': 'AI-Powered Insider Threat Detection REST API',
            'endpoints': {
                'health': '/api/v1/health',
                'auth': '/api/v1/auth/login',
                'system_status': '/api/v1/system/status',
                'users': '/api/v1/users',
                'activities': '/api/v1/activities',
                'alerts': '/api/v1/alerts',
                'risk_summary': '/api/v1/risk/summary',
                'ml_detection': '/api/v1/ml/run-detection'
            }
        })

    # Lightweight liveness probe (no auth, no heavy queries)
    @app.route('/api/v1/health')
    def health():
        return jsonify({'status': 'ok'})

    # Global error handlers
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        return jsonify({'error': str(e), 'code': 400}), 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        message = 'Resource not found' if e.code == 404 else e.description
        return jsonify({'error': message, 'code': e.code}), e.code

    @app.errorhandler(Exception)
    def handle_500(e):
        app.logger.exception(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error', 'code': 500}), 500

    return app
