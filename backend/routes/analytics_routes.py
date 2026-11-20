from flask import Blueprint, request, jsonify
from backend.services.analytics_service import get_academic_analytics, get_placement_analytics

analytics_bp = Blueprint("analytics", __name__, url_prefix="/api/analytics")

@analytics_bp.route("/academic", methods=["GET"])
def academic_analytics():
    dept = request.args.get("department")
    data = get_academic_analytics(department=dept)
    return jsonify(data), 200

@analytics_bp.route("/placement", methods=["GET"])
def placement_analytics():
    dept = request.args.get("department")
    batch = request.args.get("batch")
    year = request.args.get("year")
    data = get_placement_analytics(department=dept, batch=batch, year=year)
    return jsonify(data), 200

