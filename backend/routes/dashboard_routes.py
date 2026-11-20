from flask import Blueprint, request, jsonify
from backend.services.analytics_service import get_dashboard_stats

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("/stats", methods=["GET"])
def dashboard_stats():
    dept = request.args.get("department")
    batch = request.args.get("batch")
    year = request.args.get("year")

    stats = get_dashboard_stats(department=dept, batch=batch, year=year)
    return jsonify(stats), 200

