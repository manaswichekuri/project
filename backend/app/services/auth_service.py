import werkzeug.security as security
from pymongo.errors import DuplicateKeyError
from app.config.settings import Config
from app.utils.db import get_db


def seed_default_admin():
    """Ensures the configured admin account exists and its password matches ADMIN_PASSWORD."""
    db = get_db()
    # Atomic upsert: several gunicorn workers may run this concurrently at boot
    try:
        db.admins.update_one(
            {"username": Config.ADMIN_USERNAME},
            {"$setOnInsert": {
                "username": Config.ADMIN_USERNAME,
                "password_hash": security.generate_password_hash(Config.ADMIN_PASSWORD),
                "role": "Security Administrator",
                "name": "SOC Lead Admin",
                "email": "admin@cyber.soc"
            }},
            upsert=True
        )
    except DuplicateKeyError:
        pass  # another worker inserted it first

    existing = db.admins.find_one({"username": Config.ADMIN_USERNAME})
    if not security.check_password_hash(existing["password_hash"], Config.ADMIN_PASSWORD):
        # ADMIN_PASSWORD was rotated via environment: re-hash the stored credential
        db.admins.update_one(
            {"_id": existing["_id"]},
            {"$set": {"password_hash": security.generate_password_hash(Config.ADMIN_PASSWORD)}}
        )


def _public_admin(admin):
    return {
        "username": admin["username"],
        "name": admin.get("name", "SOC Lead Admin"),
        "role": admin.get("role", "Security Administrator"),
        "email": admin.get("email", "admin@cyber.soc")
    }


def authenticate_admin(username, password):
    clean_username = (username or "").strip().lower()
    if not clean_username or not password:
        return None

    db = get_db()
    admin = db.admins.find_one({"username": clean_username})
    if not admin or not security.check_password_hash(admin["password_hash"], password):
        return None

    return _public_admin(admin)


def get_admin(username):
    admin = get_db().admins.find_one({"username": (username or "").strip().lower()})
    return _public_admin(admin) if admin else None
