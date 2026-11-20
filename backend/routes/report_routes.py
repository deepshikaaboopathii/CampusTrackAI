from flask import Blueprint, request, jsonify
from backend.services.analytics_service import get_dashboard_stats, get_placement_analytics
from backend.services.student_service import get_students
from backend.database.db import get_db

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@report_bp.route("/summary", methods=["GET"])
def college_summary_report():
    year = request.args.get("year")
    batch = request.args.get("batch")

    stats = get_dashboard_stats(batch=batch, year=year)
    placement_info = get_placement_analytics(batch=batch, year=year)

    return jsonify({
        "college_name": "CampusTrack Institute of Technology",
        "academic_year": year or "Current",
        "kpis": stats["kpis"],
        "departments": stats["department_stats"],
        "top_recruiters": placement_info["company_stats"][:8]
    }), 200

@report_bp.route("/training-needed", methods=["GET"])
def training_needed_report():
    dept = request.args.get("department")

    where_clauses = ["(backlog_count > 0 OR technical_score < 60 OR aptitude_score < 60 OR cgpa < 6.5)"]
    params = []

    if dept and dept != "All":
        where_clauses.append("department = ?")
        params.append(dept)

    where_sql = " WHERE " + " AND ".join(where_clauses)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT student_id, name, department, batch, cgpa, attendance,
                   backlog_count, aptitude_score, technical_score, communication_score,
                   programming_rating
            FROM students
            {where_sql}
            ORDER BY backlog_count DESC, technical_score ASC, aptitude_score ASC
        """, params)
        students = [dict(r) for r in cursor.fetchall()]

    for s in students:
        reasons = []
        if s["backlog_count"] > 0:
            reasons.append(f"{s['backlog_count']} active backlogs")
        if s["cgpa"] < 6.5:
            reasons.append(f"Low CGPA ({s['cgpa']})")
        if s["technical_score"] < 60:
            reasons.append(f"Tech score {s['technical_score']}/100")
        if s["aptitude_score"] < 60:
            reasons.append(f"Aptitude {s['aptitude_score']}/100")
        s["intervention_reasons"] = reasons

    return jsonify({
        "total_requiring_training": len(students),
        "department": dept or "All Departments",
        "students": students
    }), 200

