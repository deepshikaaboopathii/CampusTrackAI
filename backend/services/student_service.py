import sqlite3
from backend.database.db import get_db
from ml.predict import analyze_student_profile

def get_students(search=None, department=None, batch=None, placement_status=None,
                 placement_eligible=None, min_cgpa=None, max_cgpa=None,
                 sort_by="cgpa", sort_order="desc", page=1, limit=15):
    page = max(1, int(page))
    limit = max(1, min(100, int(limit)))
    offset = (page - 1) * limit

    conditions = []
    params = []

    if search:
        search_term = f"%{search.strip()}%"
        conditions.append("(student_id LIKE ? OR name LIKE ? OR email LIKE ? OR company_name LIKE ?)")
        params.extend([search_term, search_term, search_term, search_term])

    if department and department != "All":
        conditions.append("department = ?")
        params.append(department)

    if batch and batch != "All":
        conditions.append("batch = ?")
        params.append(batch)

    if placement_status and placement_status != "All":
        conditions.append("placement_status = ?")
        params.append(placement_status)

    if placement_eligible is not None and placement_eligible != "All":
        conditions.append("placement_eligible = ?")
        params.append(1 if str(placement_eligible) in ["1", "true", "True"] else 0)

    if min_cgpa:
        conditions.append("cgpa >= ?")
        params.append(float(min_cgpa))

    if max_cgpa:
        conditions.append("cgpa <= ?")
        params.append(float(max_cgpa))

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    allowed_sort_fields = {
        "cgpa": "cgpa",
        "student_id": "student_id",
        "name": "name",
        "attendance": "attendance",
        "aptitude_score": "aptitude_score",
        "technical_score": "technical_score",
        "salary_package": "salary_package",
        "backlog_count": "backlog_count"
    }
    sort_field = allowed_sort_fields.get(sort_by, "cgpa")
    sort_direction = "ASC" if str(sort_order).lower() == "asc" else "DESC"

    with get_db() as conn:
        cursor = conn.cursor()

        # Count total matches
        count_query = f"SELECT COUNT(*) FROM students {where_clause}"
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()[0]

        # Fetch paginated items
        data_query = f"""
            SELECT * FROM students
            {where_clause}
            ORDER BY {sort_field} {sort_direction}
            LIMIT ? OFFSET ?
        """
        cursor.execute(data_query, params + [limit, offset])
        rows = [dict(r) for r in cursor.fetchall()]

    total_pages = (total_records + limit - 1) // limit if total_records > 0 else 1

    return {
        "students": rows,
        "pagination": {
            "current_page": page,
            "limit": limit,
            "total_records": total_records,
            "total_pages": total_pages
        }
    }

def get_student_by_id(identifier):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM students
            WHERE id = ? OR student_id = ?
        """, (identifier, identifier))
        row = cursor.fetchone()
        if not row:
            return None

        student = dict(row)

        # Fetch semester records
        cursor.execute("""
            SELECT semester, sgpa, attendance_pct, backlogs
            FROM semester_records
            WHERE student_id = ?
            ORDER BY semester ASC
        """, (student["student_id"],))
        student["semester_records"] = [dict(r) for r in cursor.fetchall()]

    # Run ML readiness diagnostic
    readiness = analyze_student_profile(student)
    student["readiness_analysis"] = readiness

    # Prepare radar chart metrics
    student["radar_metrics"] = [
        {"skill": "Aptitude", "score": student["aptitude_score"], "fullMark": 100},
        {"skill": "Technical", "score": student["technical_score"], "fullMark": 100},
        {"skill": "Communication", "score": student["communication_score"], "fullMark": 100},
        {"skill": "Coding Ability", "score": round(student["programming_rating"] * 20, 1), "fullMark": 100},
        {"skill": "Soft Skills", "score": student["soft_skills_score"], "fullMark": 100},
        {"skill": "Academic (CGPA)", "score": round(student["cgpa"] * 10, 1), "fullMark": 100}
    ]

    return student

def create_student(data: dict):
    # Field validation
    required = ["name", "email", "department", "batch", "graduation_year", "cgpa", "attendance"]
    for field in required:
        if field not in data or data[field] is None:
            return None, f"Field '{field}' is required"

    with get_db() as conn:
        cursor = conn.cursor()

        # Generate student_id if not supplied
        student_id = data.get("student_id")
        if not student_id:
            dept_code = "".join([w[0] for w in data["department"].split() if w[0].isalpha()]).upper()[:2]
            cursor.execute("SELECT COUNT(*) FROM students WHERE department = ?", (data["department"],))
            cnt = cursor.fetchone()[0] + 1
            student_id = f"CT{data['graduation_year']}{dept_code}{cnt:03d}"

        # Uniqueness check
        cursor.execute("SELECT id FROM students WHERE student_id = ? OR email = ?", (student_id, data["email"]))
        if cursor.fetchone():
            return None, "Student ID or Email already exists."

        # Compute placement eligibility
        cgpa = float(data["cgpa"])
        attendance = float(data["attendance"])
        backlogs = int(data.get("backlog_count", 0))
        eligible = 1 if (cgpa >= 6.0 and backlogs <= 1 and attendance >= 70.0) else 0

        cursor.execute("""
            INSERT INTO students (
                student_id, name, email, gender, department, batch, graduation_year,
                cgpa, attendance, backlog_count, aptitude_score, technical_score,
                communication_score, programming_rating, projects_count, certifications_count,
                internships_count, soft_skills_score, placement_eligible, placement_status,
                company_name, job_role, salary_package
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, data["name"], data["email"], data.get("gender", "Other"),
            data["department"], data["batch"], int(data["graduation_year"]),
            cgpa, attendance, backlogs,
            float(data.get("aptitude_score", 65.0)),
            float(data.get("technical_score", 65.0)),
            float(data.get("communication_score", 65.0)),
            float(data.get("programming_rating", 3.0)),
            int(data.get("projects_count", 0)),
            int(data.get("certifications_count", 0)),
            int(data.get("internships_count", 0)),
            float(data.get("soft_skills_score", 70.0)),
            eligible,
            data.get("placement_status", "Not Placed"),
            data.get("company_name"),
            data.get("job_role"),
            float(data["salary_package"]) if data.get("salary_package") else None
        ))
        new_id = cursor.lastrowid

        # Insert default semester records if provided
        if "semester_records" in data and isinstance(data["semester_records"], list):
            for sem_rec in data["semester_records"]:
                cursor.execute("""
                    INSERT INTO semester_records (student_id, semester, sgpa, attendance_pct, backlogs)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, sem_rec["semester"], sem_rec["sgpa"], sem_rec.get("attendance_pct", attendance), sem_rec.get("backlogs", 0)))
        else:
            # Generate default 6 semesters around CGPA
            for s in range(1, 7):
                cursor.execute("""
                    INSERT INTO semester_records (student_id, semester, sgpa, attendance_pct, backlogs)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, s, round(cgpa + (s % 2 - 0.5) * 0.2, 2), attendance, 0))

    return get_student_by_id(new_id), None

def update_student(identifier, data: dict):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ? OR student_id = ?", (identifier, identifier))
        existing = cursor.fetchone()
        if not existing:
            return None, "Student record not found"

        student = dict(existing)
        s_id = student["id"]

        # Recalculate eligibility if parameters changed
        cgpa = float(data.get("cgpa", student["cgpa"]))
        attendance = float(data.get("attendance", student["attendance"]))
        backlogs = int(data.get("backlog_count", student["backlog_count"]))
        eligible = 1 if (cgpa >= 6.0 and backlogs <= 1 and attendance >= 70.0) else 0

        cursor.execute("""
            UPDATE students SET
                name = ?, email = ?, gender = ?, department = ?, batch = ?, graduation_year = ?,
                cgpa = ?, attendance = ?, backlog_count = ?, aptitude_score = ?, technical_score = ?,
                communication_score = ?, programming_rating = ?, projects_count = ?,
                certifications_count = ?, internships_count = ?, soft_skills_score = ?,
                placement_eligible = ?, placement_status = ?, company_name = ?,
                job_role = ?, salary_package = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get("name", student["name"]),
            data.get("email", student["email"]),
            data.get("gender", student["gender"]),
            data.get("department", student["department"]),
            data.get("batch", student["batch"]),
            int(data.get("graduation_year", student["graduation_year"])),
            cgpa, attendance, backlogs,
            float(data.get("aptitude_score", student["aptitude_score"])),
            float(data.get("technical_score", student["technical_score"])),
            float(data.get("communication_score", student["communication_score"])),
            float(data.get("programming_rating", student["programming_rating"])),
            int(data.get("projects_count", student["projects_count"])),
            int(data.get("certifications_count", student["certifications_count"])),
            int(data.get("internships_count", student["internships_count"])),
            float(data.get("soft_skills_score", student["soft_skills_score"])),
            eligible,
            data.get("placement_status", student["placement_status"]),
            data.get("company_name", student["company_name"]),
            data.get("job_role", student["job_role"]),
            float(data["salary_package"]) if data.get("salary_package") is not None else None,
            s_id
        ))

    return get_student_by_id(s_id), None

def delete_student(identifier):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT student_id FROM students WHERE id = ? OR student_id = ?", (identifier, identifier))
        row = cursor.fetchone()
        if not row:
            return False, "Student not found"
        st_id = row[0]
        cursor.execute("DELETE FROM semester_records WHERE student_id = ?", (st_id,))
        cursor.execute("DELETE FROM students WHERE student_id = ?", (st_id,))
    return True, None

def get_filter_options():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT department FROM students ORDER BY department")
        departments = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT batch FROM students ORDER BY batch DESC")
        batches = [r[0] for r in cursor.fetchall()]

        cursor.execute("SELECT DISTINCT graduation_year FROM students ORDER BY graduation_year DESC")
        grad_years = [r[0] for r in cursor.fetchall()]

    return {
        "departments": departments,
        "batches": batches,
        "graduation_years": grad_years,
        "placement_statuses": ["Placed", "Not Placed", "In Process"]
    }

