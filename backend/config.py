import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "campustrack_ai_secret_super_key_2026")
    JWT_SECRET = os.environ.get("JWT_SECRET", "campustrack_jwt_secret_token_secure_key")
    JWT_EXPIRATION_HOURS = 24
    DB_NAME = "campustrack.db"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datasets", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload

os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

