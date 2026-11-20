import os
from flask import Blueprint, request, jsonify, Response, send_file
from backend.services.dataset_service import (
    parse_and_validate_file, commit_import, export_students_csv
)
from backend.services.auth_service import token_required

dataset_bp = Blueprint("dataset", __name__, url_prefix="/api/dataset")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAMPLE_TEMPLATE_PATH = os.path.join(BASE_DIR, "datasets", "sample_template.csv")

@dataset_bp.route("/upload", methods=["POST"])
@token_required
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    summary, err = parse_and_validate_file(file)
    if err:
        return jsonify({"error": err}), 400

    return jsonify({"message": "File parsed and validated successfully", "summary": summary}), 200

@dataset_bp.route("/commit", methods=["POST"])
@token_required
def commit_dataset():
    data = request.get_json() or {}
    filename = data.get("filename")
    mode = data.get("mode", "upsert")

    if not filename:
        return jsonify({"error": "Filename is required"}), 400

    result, err = commit_import(filename, mode=mode)
    if err:
        return jsonify({"error": err}), 400

    return jsonify(result), 200

@dataset_bp.route("/template", methods=["GET"])
def download_template():
    if os.path.exists(SAMPLE_TEMPLATE_PATH):
        return send_file(
            SAMPLE_TEMPLATE_PATH,
            mimetype="text/csv",
            as_attachment=True,
            download_name="campustrack_student_template.csv"
        )
    return jsonify({"error": "Sample template file not found"}), 404

@dataset_bp.route("/export", methods=["GET"])
def export_csv():
    dept = request.args.get("department")
    status = request.args.get("status")
    training_only = request.args.get("training_needed") in ["1", "true", "True"]

    csv_data = export_students_csv(department=dept, status=status, training_needed_only=training_only)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=campustrack_students_export.csv"}
    )

