import os
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash
from backend.database.db import get_db, init_db, DB_PATH

def seed_database():
    print("Initializing database schema...")
    init_db()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    datasets_dir = os.path.join(base_dir, "datasets")
    students_csv = os.path.join(datasets_dir, "sample_students.csv")
    semesters_csv = os.path.join(datasets_dir, "sample_semesters.csv")

    with get_db() as conn:
        cursor = conn.cursor()

        # Seed Default Users (Admin and Faculty)
        cursor.execute("DELETE FROM users")
        admin_pass = generate_password_hash("Admin@123")
        faculty_pass = generate_password_hash("Faculty@123")

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", "admin@campustrack.ai", admin_pass, "admin", "System Administrator"))

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, ("faculty", "faculty@campustrack.ai", faculty_pass, "faculty", "Prof. Robert Davis"))

        print("Default users seeded: admin@campustrack.ai and faculty@campustrack.ai")

        # Seed Students from CSV
        if os.path.exists(students_csv):
            cursor.execute("DELETE FROM students")
            df_students = pd.read_csv(students_csv)
            # Replace NaN with None for SQLite NULLs
            df_students = df_students.where(pd.notnull(df_students), None)

            students_data = [
                (
                    row["student_id"], row["name"], row["email"], row.get("gender", "Other"),
                    row["department"], row["batch"], int(row["graduation_year"]),
                    float(row["cgpa"]), float(row["attendance"]), int(row["backlog_count"]),
                    float(row["aptitude_score"]), float(row["technical_score"]),
                    float(row["communication_score"]), float(row["programming_rating"]),
                    int(row["projects_count"]), int(row["certifications_count"]),
                    int(row["internships_count"]), float(row["soft_skills_score"]),
                    int(row["placement_eligible"]), row["placement_status"],
                    row["company_name"], row["job_role"],
                    float(row["salary_package"]) if row["salary_package"] is not None else None
                )
                for _, row in df_students.iterrows()
            ]

            cursor.executemany("""
                INSERT INTO students (
                    student_id, name, email, gender, department, batch, graduation_year,
                    cgpa, attendance, backlog_count, aptitude_score, technical_score,
                    communication_score, programming_rating, projects_count, certifications_count,
                    internships_count, soft_skills_score, placement_eligible, placement_status,
                    company_name, job_role, salary_package
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, students_data)
            print(f"Seeded {len(students_data)} student records.")

        # Seed Semester Records
        if os.path.exists(semesters_csv):
            cursor.execute("DELETE FROM semester_records")
            df_sem = pd.read_csv(semesters_csv)
            sem_data = [
                (
                    row["student_id"], int(row["semester"]),
                    float(row["sgpa"]), float(row["attendance_pct"]),
                    int(row["backlogs"])
                )
                for _, row in df_sem.iterrows()
            ]
            cursor.executemany("""
                INSERT INTO semester_records (
                    student_id, semester, sgpa, attendance_pct, backlogs
                ) VALUES (?, ?, ?, ?, ?)
            """, sem_data)
            print(f"Seeded {len(sem_data)} semester performance records.")

        # Seed initial dataset log
        cursor.execute("DELETE FROM dataset_logs")
        cursor.execute("""
            INSERT INTO dataset_logs (filename, uploaded_by, total_records, valid_records, status)
            VALUES (?, ?, ?, ?, ?)
        """, ("sample_students.csv", "System Seeder", 450, 450, "Completed"))

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_database()

