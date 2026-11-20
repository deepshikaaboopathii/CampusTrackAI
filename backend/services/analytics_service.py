import sqlite3
import numpy as np
import pandas as pd
from backend.database.db import get_db

def get_dashboard_stats(department=None, batch=None, year=None):
    conditions = []
    params = []

    if department and department != "All":
        conditions.append("department = ?")
        params.append(department)
    if batch and batch != "All":
        conditions.append("batch = ?")
        params.append(batch)
    if year and year != "All":
        conditions.append("graduation_year = ?")
        params.append(int(year))

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    with get_db() as conn:
        cursor = conn.cursor()

        # Aggregate metrics
        query = f"""
            SELECT
                COUNT(*) as total_students,
                SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) as placed_count,
                SUM(CASE WHEN placement_status = 'In Process' THEN 1 ELSE 0 END) as in_process_count,
                SUM(CASE WHEN placement_eligible = 1 THEN 1 ELSE 0 END) as eligible_count,
                SUM(CASE WHEN (backlog_count > 0 OR technical_score < 60 OR aptitude_score < 60 OR cgpa < 6.5) THEN 1 ELSE 0 END) as training_needed_count,
                AVG(cgpa) as avg_cgpa,
                AVG(attendance) as avg_attendance,
                AVG(aptitude_score) as avg_aptitude,
                AVG(technical_score) as avg_technical,
                AVG(communication_score) as avg_communication,
                AVG(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END) as avg_salary,
                MAX(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END) as max_salary,
                MIN(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END) as min_salary
            FROM students
            {where}
        """
        cursor.execute(query, params)
        agg = dict(cursor.fetchone())

        total = agg["total_students"] or 0
        placed = agg["placed_count"] or 0
        placement_pct = round((placed / total * 100), 1) if total > 0 else 0.0

        # Placement Rate & Stats by Department
        dept_query = f"""
            SELECT
                department,
                COUNT(*) as total,
                SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) as placed,
                ROUND(AVG(cgpa), 2) as avg_cgpa,
                ROUND(AVG(aptitude_score), 1) as avg_aptitude,
                ROUND(AVG(technical_score), 1) as avg_technical,
                ROUND(AVG(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END), 2) as avg_package
            FROM students
            {where}
            GROUP BY department
        """
        cursor.execute(dept_query, params)
        dept_rows = []
        for r in cursor.fetchall():
            d = dict(r)
            d["placement_rate"] = round((d["placed"] / d["total"] * 100), 1) if d["total"] > 0 else 0
            dept_rows.append(d)

        # Placed vs Unplaced vs In Process breakdown
        status_query = f"""
            SELECT placement_status, COUNT(*) as count
            FROM students
            {where}
            GROUP BY placement_status
        """
        cursor.execute(status_query, params)
        status_breakdown = [{"name": r["placement_status"], "value": r["count"]} for r in cursor.fetchall()]

        # Salary distribution buckets (<5, 5-8, 8-12, 12-18, 18+)
        salary_query = f"""
            SELECT
                CASE
                    WHEN salary_package < 5 THEN '< 5 LPA'
                    WHEN salary_package >= 5 AND salary_package < 8 THEN '5 - 8 LPA'
                    WHEN salary_package >= 8 AND salary_package < 12 THEN '8 - 12 LPA'
                    WHEN salary_package >= 12 AND salary_package < 18 THEN '12 - 18 LPA'
                    ELSE '18+ LPA'
                END as bucket,
                COUNT(*) as count
            FROM students
            WHERE placement_status = 'Placed' AND salary_package IS NOT NULL
            {"AND " + " AND ".join(conditions) if conditions else ""}
            GROUP BY bucket
            ORDER BY MIN(salary_package)
        """
        cursor.execute(salary_query, params)
        salary_dist = [{"range": r["bucket"], "count": r["count"]} for r in cursor.fetchall()]

        # Average Semester SGPA progression
        sem_query = """
            SELECT semester, ROUND(AVG(sgpa), 2) as avg_sgpa, ROUND(AVG(attendance_pct), 1) as avg_attendance
            FROM semester_records
            GROUP BY semester
            ORDER BY semester ASC
        """
        cursor.execute(sem_query)
        sem_progression = [{"semester": f"Sem {r['semester']}", "sgpa": r["avg_sgpa"], "attendance": r["avg_attendance"]} for r in cursor.fetchall()]

    return {
        "kpis": {
            "total_students": total,
            "placed_students": placed,
            "placement_percentage": placement_pct,
            "eligible_students": agg["eligible_count"] or 0,
            "training_needed": agg["training_needed_count"] or 0,
            "avg_cgpa": round(agg["avg_cgpa"] or 0.0, 2),
            "avg_attendance": round(agg["avg_attendance"] or 0.0, 1),
            "avg_aptitude": round(agg["avg_aptitude"] or 0.0, 1),
            "avg_technical": round(agg["avg_technical"] or 0.0, 1),
            "avg_communication": round(agg["avg_communication"] or 0.0, 1),
            "avg_salary": round(agg["avg_salary"] or 0.0, 2),
            "max_salary": round(agg["max_salary"] or 0.0, 2),
            "min_salary": round(agg["min_salary"] or 0.0, 2)
        },
        "department_stats": dept_rows,
        "placement_status_breakdown": status_breakdown,
        "salary_distribution": salary_dist,
        "semester_trends": sem_progression
    }

def get_academic_analytics(department=None):
    dept_filter = "WHERE s.department = ?" if department and department != "All" else ""
    params = [department] if department and department != "All" else []

    with get_db() as conn:
        cursor = conn.cursor()

        # CGPA distribution bins
        cursor.execute(f"""
            SELECT
                CASE
                    WHEN cgpa < 6.0 THEN '< 6.0'
                    WHEN cgpa >= 6.0 AND cgpa < 7.0 THEN '6.0 - 6.9'
                    WHEN cgpa >= 7.0 AND cgpa < 8.0 THEN '7.0 - 7.9'
                    WHEN cgpa >= 8.0 AND cgpa < 9.0 THEN '8.0 - 8.9'
                    ELSE '9.0 - 10.0'
                END as bin,
                COUNT(*) as count
            FROM students s
            {dept_filter}
            GROUP BY bin
        """, params)
        cgpa_dist = [{"bin": r["bin"], "students": r["count"]} for r in cursor.fetchall()]

        # Attendance vs CGPA scatter sample (up to 120 points for fast rendering)
        cursor.execute(f"""
            SELECT student_id, name, department, attendance, cgpa, placement_status
            FROM students s
            {dept_filter}
            ORDER BY RANDOM()
            LIMIT 120
        """, params)
        attendance_cgpa = [
            {
                "student_id": r["student_id"],
                "name": r["name"],
                "department": r["department"],
                "attendance": r["attendance"],
                "cgpa": r["cgpa"],
                "status": r["placement_status"]
            }
            for r in cursor.fetchall()
        ]

        # Aptitude vs Technical score comparison sample
        cursor.execute(f"""
            SELECT student_id, name, aptitude_score, technical_score, programming_rating, placement_status
            FROM students s
            {dept_filter}
            ORDER BY RANDOM()
            LIMIT 120
        """, params)
        aptitude_vs_tech = [
            {
                "student_id": r["student_id"],
                "name": r["name"],
                "aptitude": r["aptitude_score"],
                "technical": r["technical_score"],
                "coding": r["programming_rating"],
                "status": r["placement_status"]
            }
            for r in cursor.fetchall()
        ]

        # Students with declining academic performance (drop of >= 0.6 SGPA in recent semesters)
        cursor.execute("""
            SELECT s.student_id, s.name, s.department, s.cgpa, s.attendance,
                   MIN(sr.sgpa) as lowest_sem, MAX(sr.sgpa) as highest_sem,
                   COUNT(sr.semester) as sem_count
            FROM students s
            JOIN semester_records sr ON s.student_id = sr.student_id
            GROUP BY s.student_id
            HAVING (MAX(sr.sgpa) - MIN(sr.sgpa)) >= 0.8 AND s.cgpa < 7.8
            ORDER BY (MAX(sr.sgpa) - MIN(sr.sgpa)) DESC
            LIMIT 15
        """)
        declining_students = [
            {
                "student_id": r["student_id"],
                "name": r["name"],
                "department": r["department"],
                "cgpa": r["cgpa"],
                "attendance": r["attendance"],
                "drop_margin": round(r["highest_sem"] - r["lowest_sem"], 2),
                "alert": "Performance drop observed between semesters"
            }
            for r in cursor.fetchall()
        ]

        # High Placement Potential Talent (CGPA >= 8.0, Tech >= 75, Apt >= 75, 0 backlogs)
        cursor.execute(f"""
            SELECT student_id, name, department, cgpa, technical_score, aptitude_score,
                   internships_count, programming_rating, placement_status, company_name
            FROM students s
            WHERE cgpa >= 8.0 AND technical_score >= 75 AND aptitude_score >= 75 AND backlog_count = 0
            {('AND s.department = ?' if department and department != 'All' else '')}
            ORDER BY (cgpa * 10 + technical_score + aptitude_score) DESC
            LIMIT 15
        """, params)
        high_potential = [
            {
                "student_id": r["student_id"],
                "name": r["name"],
                "department": r["department"],
                "cgpa": r["cgpa"],
                "technical_score": r["technical_score"],
                "aptitude_score": r["aptitude_score"],
                "internships": r["internships_count"],
                "programming_rating": r["programming_rating"],
                "placement_status": r["placement_status"],
                "company_name": r["company_name"]
            }
            for r in cursor.fetchall()
        ]

        # Skill gap breakdown by department
        cursor.execute("""
            SELECT
                department,
                ROUND(AVG(aptitude_score), 1) as avg_aptitude,
                ROUND(AVG(technical_score), 1) as avg_tech,
                ROUND(AVG(communication_score), 1) as avg_comm,
                ROUND(AVG(programming_rating * 20), 1) as avg_prog,
                ROUND(AVG(soft_skills_score), 1) as avg_soft
            FROM students
            GROUP BY department
        """)
        skill_matrix = [dict(r) for r in cursor.fetchall()]

    return {
        "cgpa_distribution": cgpa_dist,
        "attendance_vs_cgpa": attendance_cgpa,
        "aptitude_vs_tech": aptitude_vs_tech,
        "declining_students": declining_students,
        "high_potential_students": high_potential,
        "skill_matrix": skill_matrix
    }

def get_placement_analytics(department=None, batch=None, year=None):
    conditions = []
    params = []

    if department and department != "All":
        conditions.append("department = ?")
        params.append(department)
    if batch and batch != "All":
        conditions.append("batch = ?")
        params.append(batch)
    if year and year != "All":
        conditions.append("graduation_year = ?")
        params.append(int(year))

    where = " WHERE " + " AND ".join(conditions) if conditions else ""

    with get_db() as conn:
        cursor = conn.cursor()

        # Company-wise recruitment statistics
        comp_where = " WHERE placement_status = 'Placed' AND company_name IS NOT NULL"
        if conditions:
            comp_where += " AND " + " AND ".join(conditions)

        cursor.execute(f"""
            SELECT
                company_name,
                COUNT(*) as student_count,
                ROUND(AVG(salary_package), 2) as avg_package,
                MAX(salary_package) as highest_package,
                MIN(salary_package) as lowest_package
            FROM students
            {comp_where}
            GROUP BY company_name
            ORDER BY student_count DESC, avg_package DESC
            LIMIT 15
        """, params)
        company_stats = [dict(r) for r in cursor.fetchall()]

        # Department placement summary
        cursor.execute(f"""
            SELECT
                department,
                COUNT(*) as total_students,
                SUM(CASE WHEN placement_eligible = 1 THEN 1 ELSE 0 END) as eligible,
                SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) as placed,
                ROUND(AVG(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END), 2) as avg_ctc,
                MAX(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END) as max_ctc
            FROM students
            {where}
            GROUP BY department
        """, params)
        dept_placement = []
        for r in cursor.fetchall():
            d = dict(r)
            d["placement_pct"] = round((d["placed"] / d["eligible"] * 100), 1) if d["eligible"] > 0 else 0
            dept_placement.append(d)

        # Batch comparison trends
        cursor.execute("""
            SELECT
                batch,
                COUNT(*) as total,
                SUM(CASE WHEN placement_status = 'Placed' THEN 1 ELSE 0 END) as placed,
                ROUND(AVG(CASE WHEN placement_status = 'Placed' THEN salary_package ELSE NULL END), 2) as avg_ctc
            FROM students
            GROUP BY batch
            ORDER BY batch ASC
        """)
        batch_trends = [dict(r) for r in cursor.fetchall()]

    return {
        "company_stats": company_stats,
        "department_placement": dept_placement,
        "batch_trends": batch_trends
    }

