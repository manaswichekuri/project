import os
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-capstone-secret-key-2026')
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/insider_threat_db')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'insider_threat_db')
    USE_MOCK_DB = os.getenv('USE_MOCK_DB', 'false').lower() in ('true', '1', 't')
    
    # ML & Risk Thresholds
    CONTAMINATION_RATE = float(os.getenv('CONTAMINATION_RATE', 0.1))
    RISK_THRESHOLD_HIGH = float(os.getenv('RISK_THRESHOLD_HIGH', 60.0))
    RISK_THRESHOLD_CRITICAL = float(os.getenv('RISK_THRESHOLD_CRITICAL', 85.0))
