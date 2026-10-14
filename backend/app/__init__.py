import logging
from flask import Flask, jsonify
from flask_cors import CORS
from app.config.settings import Config
from app.utils.db import init_db_indexes
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
    
    # Enable CORS for Angular frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize DB indexes
    with app.app_context():
        init_db_indexes()
        
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
            'frontend_dashboard_url': 'http://localhost:4200',
            'endpoints': {
                'auth': '/api/v1/auth/login',
                'system_status': '/api/v1/system/status',
                'users': '/api/v1/users',
                'activities': '/api/v1/activities',
                'alerts': '/api/v1/alerts',
                'risk_summary': '/api/v1/risk/summary',
                'ml_detection': '/api/v1/ml/run-detection'
            }
        })

    # Global error handlers
    @app.errorhandler(404)
    def handle_404(e):
        return jsonify({'error': 'Resource not found', 'code': 404}), 404

    @app.errorhandler(500)
    def handle_500(e):
        app.logger.error(f"Internal server error: {e}")
        return jsonify({'error': 'Internal server error', 'code': 500}), 500

    return app
