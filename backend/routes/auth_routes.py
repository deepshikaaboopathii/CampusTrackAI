from flask import Blueprint, request, jsonify
from backend.services.auth_service import authenticate, register_user, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email_or_user = data.get("email") or data.get("username")
    password = data.get("password")

    if not email_or_user or not password:
        return jsonify({"error": "Email/Username and password are required"}), 400

    result, err = authenticate(email_or_user, password)
    if err:
        return jsonify({"error": err}), 401

    return jsonify({
        "message": "Login successful",
        "user": result["user"],
        "token": result["token"]
    }), 200

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    role = data.get("role", "faculty")

    if not all([username, email, password, full_name]):
        return jsonify({"error": "All fields (username, email, password, full_name) are required"}), 400

    user, err = register_user(username, email, password, full_name, role)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({"message": "Registration successful", "user": user}), 201

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    return jsonify({"user": request.current_user}), 200

