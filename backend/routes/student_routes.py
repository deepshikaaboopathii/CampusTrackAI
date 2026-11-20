from flask import Blueprint, request, jsonify
from backend.services.student_service import (
    get_students, get_student_by_id, create_student,
    update_student, delete_student, get_filter_options
)
from backend.services.auth_service import token_required

student_bp = Blueprint("students", __name__, url_prefix="/api/students")

@student_bp.route("", methods=["GET"])
def list_students():
    search = request.args.get("search")
    dept = request.args.get("department")
    batch = request.args.get("batch")
    status = request.args.get("placement_status")
    eligible = request.args.get("placement_eligible")
    min_cgpa = request.args.get("min_cgpa")
    max_cgpa = request.args.get("max_cgpa")
    sort_by = request.args.get("sort_by", "cgpa")
    sort_order = request.args.get("sort_order", "desc")
    page = request.args.get("page", 1)
    limit = request.args.get("limit", 15)

    data = get_students(
        search=search, department=dept, batch=batch,
        placement_status=status, placement_eligible=eligible,
        min_cgpa=min_cgpa, max_cgpa=max_cgpa,
        sort_by=sort_by, sort_order=sort_order,
        page=page, limit=limit
    )
    return jsonify(data), 200

@student_bp.route("/filters", methods=["GET"])
def filter_options():
    options = get_filter_options()
    return jsonify(options), 200

@student_bp.route("/<identifier>", methods=["GET"])
def student_detail(identifier):
    student = get_student_by_id(identifier)
    if not student:
        return jsonify({"error": "Student record not found"}), 404
    return jsonify(student), 200

@student_bp.route("", methods=["POST"])
@token_required
def add_student():
    data = request.get_json() or {}
    new_student, err = create_student(data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Student created successfully", "student": new_student}), 201

@student_bp.route("/<identifier>", methods=["PUT"])
@token_required
def edit_student(identifier):
    data = request.get_json() or {}
    updated, err = update_student(identifier, data)
    if err:
        return jsonify({"error": err}), 400
    return jsonify({"message": "Student updated successfully", "student": updated}), 200

@student_bp.route("/<identifier>", methods=["DELETE"])
@token_required
def remove_student(identifier):
    success, err = delete_student(identifier)
    if not success:
        return jsonify({"error": err}), 404
    return jsonify({"message": "Student record deleted successfully"}), 200

