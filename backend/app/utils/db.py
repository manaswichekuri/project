import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock
from app.config.settings import Config

logger = logging.getLogger(__name__)

_db_instance = None
_is_mock = False

def get_db():
    global _db_instance, _is_mock
    if _db_instance is not None:
        return _db_instance

    if Config.USE_MOCK_DB:
        logger.info("Configured to use mongomock in-memory database.")
        client = mongomock.MongoClient()
        _db_instance = client[Config.MONGODB_DB_NAME]
        _is_mock = True
        return _db_instance

    try:
        client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        _db_instance = client[Config.MONGODB_DB_NAME]
        _is_mock = False
        logger.info("Connected to MongoDB.")
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        if not Config.ALLOW_MOCK_FALLBACK:
            logger.error(f"Could not connect to MongoDB server ({e}) and mock fallback is disabled.")
            raise RuntimeError("MongoDB is unavailable. Check MONGODB_URI or set ALLOW_MOCK_FALLBACK=true for local development.") from e
        logger.warning(f"Could not connect to MongoDB server ({e}). Falling back to in-memory mongomock database.")
        client = mongomock.MongoClient()
        _db_instance = client[Config.MONGODB_DB_NAME]
        _is_mock = True

    return _db_instance

def reset_db_connection():
    """Drops the cached connection so the next get_db() call reconnects (used by tests)."""
    global _db_instance, _is_mock
    _db_instance = None
    _is_mock = False

def is_mock_db():
    return _is_mock

def init_db_indexes():
    db = get_db()
    try:
        db.users.create_index("user_id", unique=True)
        db.admins.create_index("username", unique=True)
        db.activities.create_index([("user_id", 1), ("timestamp", -1)])
        db.risk_scores.create_index([("user_id", 1), ("evaluated_at", -1)])
        db.alerts.create_index("alert_id", unique=True)
        db.alerts.create_index([("status", 1), ("timestamp", -1)])
        logger.info("Database indexes successfully initialized.")
    except Exception as e:
        logger.warning(f"Index initialization note: {e}")
