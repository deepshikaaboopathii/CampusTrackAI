import os
import io
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from backend.config import Config
from backend.database.db import get_db

EXPECTED_COLUMNS = [
    "student_id", "name", "email", "gender", "department", "batch",
    "graduation_year", "cgpa", "attendance", "backlog_count",
    "aptitude_score", "technical_score", "communication_score",
    "programming_rating", "projects_count", "certifications_count",
    "internships_count", "soft_skills_score"
]

OPTIONAL_COLUMNS = [
    "placement_eligible", "placement_status", "company_name", "job_role", "salary_package"
]

def parse_and_validate_file(file_storage):
    """
    Parses CSV or Excel file, validates schema, detects missing values and duplicate IDs,
    and returns comprehensive validation summary with preview rows.
    """
    filename = secure_filename(file_storage.filename)
    if not filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        return None, "Only .csv, .xlsx, or .xls file formats are supported."

    # Save to uploads folder
    save_path = os.path.join(Config.UPLOAD_FOLDER, filename)
    file_storage.save(save_path)

    try:
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(save_path)
        else:
            df = pd.read_excel(save_path)
    except Exception as e:
        return None, f"Failed to parse tabular file: {str(e)}"

    total_rows = len(df)
    if total_rows == 0:
        return None, "Uploaded file contains no data rows."

    # Check missing required columns
    cols = [c.strip().lower() for c in df.columns]
    df.columns = cols
    missing_cols = [col for col in EXPECTED_COLUMNS if col not in cols]

    # Detect duplicates within the file
    duplicate_ids_count = 0
    if "student_id" in df.columns:
        duplicate_ids_count = int(df["student_id"].duplicated().sum())

    # Detect existing duplicates in the database
    db_existing_count = 0
    if "student_id" in df.columns:
        with get_db() as conn:
            cursor = conn.cursor()
            existing_ids = set(r[0] for r in cursor.execute("SELECT student_id FROM students").fetchall())
            file_ids = set(df["student_id"].dropna().astype(str))
            db_existing_count = len(file_ids.intersection(existing_ids))

    # Detect missing values per column
    missing_counts = df.isnull().sum().to_dict()
    total_missing_cells = int(df.isnull().sum().sum())

    # Preview top 10 rows (convert NaN to None for JSON)
    preview_df = df.head(10).replace({np.nan: None})
    preview_records = preview_df.to_dict(orient="records")

    summary = {
        "filename": filename,
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "columns_detected": list(df.columns),
        "missing_required_columns": missing_cols,
        "is_valid_schema": len(missing_cols) == 0,
        "duplicate_ids_in_file": duplicate_ids_count,
        "already_in_database": db_existing_count,
        "missing_cells_count": total_missing_cells,
        "missing_per_column": missing_counts,
        "preview": preview_records,
        "file_token": filename  # Used to commit import
    }

    return summary, None

def commit_import(filename: str, mode: str = "upsert"):
    """
    Imports the validated file into the database.
    Mode: 'skip_duplicates' or 'upsert'.
    """
    file_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(file_path):
        return None, "File not found or expired. Please upload again."

    if filename.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    df.columns = [c.strip().lower() for c in df.columns]
    df = df.where(pd.notnull(df), None)

    imported_count = 0
    skipped_count = 0

    with get_db() as conn:
        cursor = conn.cursor()

        for _, row in df.iterrows():
            st_id = str(row.get("student_id", "")).strip()
            if not st_id:
                skipped_count += 1
                continue

            # Check if exists
            cursor.execute("SELECT id FROM students WHERE student_id = ?", (st_id,))
            existing = cursor.fetchone()

            if existing:
                if mode == "skip_duplicates":
                    skipped_count += 1
                    continue
                else:
                    # Update existing record
                    cursor.execute("""
                        UPDATE students SET
                            name = ?, email = ?, gender = ?, department = ?, batch = ?,
                            graduation_year = ?, cgpa = ?, attendance = ?, backlog_count = ?,
                            aptitude_score = ?, technical_score = ?, communication_score = ?,
                            programming_rating = ?, projects_count = ?, certifications_count = ?,
                            internships_count = ?, soft_skills_score = ?,
                            placement_eligible = ?, placement_status = ?,
                            company_name = ?, job_role = ?, salary_package = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE student_id = ?
                    """, (
                        row.get("name", "Student"), row.get("email", f"{st_id.lower()}@campus.edu"),
                        row.get("gender", "Other"), row.get("department", "Computer Science"),
                        row.get("batch", "2021-2025"), int(row.get("graduation_year", 2025)),
                        float(row.get("cgpa", 7.0)), float(row.get("attendance", 75.0)),
                        int(row.get("backlog_count", 0)), float(row.get("aptitude_score", 65.0)),
                        float(row.get("technical_score", 65.0)), float(row.get("communication_score", 65.0)),
                        float(row.get("programming_rating", 3.0)), int(row.get("projects_count", 0)),
                        int(row.get("certifications_count", 0)), int(row.get("internships_count", 0)),
                        float(row.get("soft_skills_score", 70.0)),
                        int(row.get("placement_eligible", 1)),
                        row.get("placement_status", "Not Placed"),
                        row.get("company_name"), row.get("job_role"),
                        float(row["salary_package"]) if row.get("salary_package") is not None else None,
                        st_id
                    ))
                    imported_count += 1
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO students (
                        student_id, name, email, gender, department, batch,
                        graduation_year, cgpa, attendance, backlog_count,
                        aptitude_score, technical_score, communication_score,
                        programming_rating, projects_count, certifications_count,
                        internships_count, soft_skills_score, placement_eligible,
                        placement_status, company_name, job_role, salary_package
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    st_id, row.get("name", "Student"), row.get("email", f"{st_id.lower()}@campus.edu"),
                    row.get("gender", "Other"), row.get("department", "Computer Science"),
                    row.get("batch", "2021-2025"), int(row.get("graduation_year", 2025)),
                    float(row.get("cgpa", 7.0)), float(row.get("attendance", 75.0)),
                    int(row.get("backlog_count", 0)), float(row.get("aptitude_score", 65.0)),
                    float(row.get("technical_score", 65.0)), float(row.get("communication_score", 65.0)),
                    float(row.get("programming_rating", 3.0)), int(row.get("projects_count", 0)),
                    int(row.get("certifications_count", 0)), int(row.get("internships_count", 0)),
                    float(row.get("soft_skills_score", 70.0)),
                    int(row.get("placement_eligible", 1)),
                    row.get("placement_status", "Not Placed"),
                    row.get("company_name"), row.get("job_role"),
                    float(row["salary_package"]) if row.get("salary_package") is not None else None
                ))
                imported_count += 1

        # Record dataset log
        cursor.execute("""
            INSERT INTO dataset_logs (filename, uploaded_by, total_records, valid_records, status)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, "User Upload", len(df), imported_count, "Import Completed"))

    return {
        "filename": filename,
        "imported_records": imported_count,
        "skipped_records": skipped_count,
        "message": f"Successfully processed {imported_count} records into the database ({skipped_count} skipped)."
    }, None

def export_students_csv(department=None, status=None, training_needed_only=False):
    """Generates CSV text for student records based on filters."""
    conditions = []
    params = []

    if department and department != "All":
        conditions.append("department = ?")
        params.append(department)
    if status and status != "All":
        conditions.append("placement_status = ?")
        params.append(status)
    if training_needed_only:
        conditions.append("(backlog_count > 0 OR technical_score < 60 OR aptitude_score < 60 OR cgpa < 6.5)")

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    with get_db() as conn:
        query = f"SELECT * FROM students {where} ORDER BY cgpa DESC"
        df = pd.read_sql_query(query, conn, params=params)

    # Clean CSV buffer
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()

