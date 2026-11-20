import datetime
import jwt
from functools import wraps
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config import Config
from backend.database.db import get_db

def create_token(user: dict) -> str:
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "full_name": user["full_name"],
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def authenticate(email_or_user, password):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ? OR username = ?",
            (email_or_user, email_or_user)
        )
        row = cursor.fetchone()
        if not row:
            return None, "Invalid credentials."

        user = dict(row)
        if not check_password_hash(user["password_hash"], password):
            return None, "Invalid credentials."

        # Do not leak hash
        user.pop("password_hash", None)
        token = create_token(user)
        return {"user": user, "token": token}, None

def register_user(username, email, password, full_name, role="faculty"):
    if role not in ["admin", "faculty"]:
        role = "faculty"

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
        if cursor.fetchone():
            return None, "A user with this email or username already exists."

        pwd_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, pwd_hash, role, full_name))
        new_id = cursor.lastrowid

    return {"id": new_id, "username": username, "email": email, "role": role, "full_name": full_name}, None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]

        if not token:
            return jsonify({"error": "Authorization token required"}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Token is invalid or expired"}), 401

        request.current_user = payload
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token_req = token_required(f)
        return token_req(*args, **kwargs)
    return decorated

