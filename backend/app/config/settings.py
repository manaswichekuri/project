import os
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

DEFAULT_SECRET_KEY = 'default-capstone-secret-key-2026'


def _env_bool(name, default):
    return os.getenv(name, str(default)).lower() in ('true', '1', 't', 'yes')


class Config:
    APP_ENV = os.getenv('APP_ENV', 'development').lower()
    SECRET_KEY = os.getenv('SECRET_KEY', DEFAULT_SECRET_KEY)
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/insider_threat_db')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'insider_threat_db')
    USE_MOCK_DB = _env_bool('USE_MOCK_DB', False)
    # Fall back to in-memory mongomock when MongoDB is unreachable (dev convenience only)
    ALLOW_MOCK_FALLBACK = _env_bool('ALLOW_MOCK_FALLBACK', APP_ENV != 'production')

    # Authentication
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin').strip().lower()
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin@12345')
    JWT_EXPIRES_HOURS = float(os.getenv('JWT_EXPIRES_HOURS', 8))

    # Comma-separated list of allowed origins for CORS ("*" allows all)
    CORS_ORIGINS = [o.strip() for o in os.getenv('CORS_ORIGINS', 'http://localhost:4200').split(',') if o.strip()]

    # ML & Risk Thresholds
    CONTAMINATION_RATE = float(os.getenv('CONTAMINATION_RATE', 0.1))
    RISK_THRESHOLD_HIGH = float(os.getenv('RISK_THRESHOLD_HIGH', 60.0))
    RISK_THRESHOLD_CRITICAL = float(os.getenv('RISK_THRESHOLD_CRITICAL', 85.0))

    # Directory where the trained model artifact is persisted
    MODEL_DIR = os.getenv('MODEL_DIR', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets'))
