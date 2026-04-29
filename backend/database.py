import sqlite3
import json
from datetime import datetime


DB_PATH = "assignmentforge.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    # First, ensure the table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            assignment_type TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Check for missing columns and add them if they don't exist
    cursor = conn.execute("PRAGMA table_info(assignments);")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    required_columns = [
        ("business_name", "TEXT"),
        ("business_website", "TEXT"),
        ("additional_requirements", "TEXT")
    ]
    
    for col_name, col_type in required_columns:
        if col_name not in existing_columns:
            conn.execute(f"ALTER TABLE assignments ADD COLUMN {col_name} {col_type}")
            print(f"Added missing column: {col_name}")
            
    conn.commit()
    conn.close()


def save_assignment(assignment_id: str, student_name: str, course_code: str, assignment_type: str, content: dict, business_name: str = "", business_website: str = "", additional_requirements: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO assignments (id, student_name, course_code, assignment_type, business_name, business_website, additional_requirements, content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (assignment_id, student_name, course_code, assignment_type, business_name, business_website, additional_requirements, json.dumps(content), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, student_name, course_code, assignment_type, created_at FROM assignments ORDER BY created_at DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_assignment_by_id(assignment_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["content"] = json.loads(d["content"])
        return d
    return None
