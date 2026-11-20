-- CampusTrack AI Database Schema
PRAGMA foreign_keys = ON;

-- Users table for Authentication (Admin and Faculty roles)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'faculty')) NOT NULL DEFAULT 'faculty',
    full_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students master table
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    gender TEXT DEFAULT 'Other',
    department TEXT NOT NULL,
    batch TEXT NOT NULL,
    graduation_year INTEGER NOT NULL,
    cgpa REAL NOT NULL,
    attendance REAL NOT NULL,
    backlog_count INTEGER NOT NULL DEFAULT 0,
    aptitude_score REAL NOT NULL,
    technical_score REAL NOT NULL,
    communication_score REAL NOT NULL,
    programming_rating REAL NOT NULL DEFAULT 3.0,
    projects_count INTEGER NOT NULL DEFAULT 0,
    certifications_count INTEGER NOT NULL DEFAULT 0,
    internships_count INTEGER NOT NULL DEFAULT 0,
    soft_skills_score REAL NOT NULL DEFAULT 70.0,
    placement_eligible INTEGER NOT NULL DEFAULT 1,
    placement_status TEXT CHECK(placement_status IN ('Placed', 'Not Placed', 'In Process')) NOT NULL DEFAULT 'Not Placed',
    company_name TEXT,
    job_role TEXT,
    salary_package REAL, -- in LPA (Lakhs Per Annum)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Semester-wise academic performance table
CREATE TABLE IF NOT EXISTS semester_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    semester INTEGER NOT NULL,
    sgpa REAL NOT NULL,
    attendance_pct REAL NOT NULL,
    backlogs INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    UNIQUE(student_id, semester)
);

-- Uploaded dataset logs table
CREATE TABLE IF NOT EXISTS dataset_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    uploaded_by TEXT DEFAULT 'Admin',
    total_records INTEGER NOT NULL,
    valid_records INTEGER NOT NULL,
    status TEXT DEFAULT 'Success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high-performance querying and filtering
CREATE INDEX IF NOT EXISTS idx_students_dept ON students(department);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(placement_status);
CREATE INDEX IF NOT EXISTS idx_students_batch ON students(batch);
CREATE INDEX IF NOT EXISTS idx_students_cgpa ON students(cgpa);
CREATE INDEX IF NOT EXISTS idx_semester_student ON semester_records(student_id);

