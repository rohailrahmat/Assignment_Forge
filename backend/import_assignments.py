import os
import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime
from docx import Document
from pypdf import PdfReader

DB_PATH = "assignmentforge.db"
SAMPLES_DIR = Path("samples")

def extract_text(file_path):
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".txt":
            return file_path.read_text(encoding="utf-8")
        elif suffix == ".docx":
            doc = Document(file_path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif suffix == ".pdf":
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")
        return ""

def parse_metadata(filename, content):
    # Try to extract from filename first
    # Example: Nour Kharbouti – Assignment - 4 P1.pdf
    name_match = re.match(r"^(.+?)\s*[-–]\s*Assignment\s*[-–]\s*(\d+)\s*(P\d+)?", filename, re.I)
    
    student_name = "Unknown"
    assignment_num = "1"
    part = ""
    
    if name_match:
        student_name = name_match.group(1).strip()
        assignment_num = name_match.group(2)
        part = name_match.group(3) or ""
    
    # Try to extract from content if possible
    course_code = "AUTO"
    if "CA-CNTOR" in content or "Content Outreach" in content:
        course_code = "CA-CNTOR"
    elif "SMALT" in content:
        course_code = "SMALT"
    elif "CA-SEMKT" in content:
        course_code = "CA-SEMKT"

    return {
        "student_name": student_name,
        "course_code": course_code,
        "assignment_type": "imported_reference",
        "assignment_number": assignment_num,
        "part": part,
        "title": f"Assignment {assignment_num} {part}".strip()
    }

def import_all():
    conn = sqlite3.connect(DB_PATH)
    count = 0
    
    print(f"Scanning {SAMPLES_DIR}...")
    for file in SAMPLES_DIR.rglob("*"):
        if file.suffix.lower() not in [".docx", ".pdf", ".txt"]:
            continue
            
        print(f"Importing {file.name}...")
        text = extract_text(file)
        if not text.strip():
            continue
            
        meta = parse_metadata(file.name, text)
        
        # Create a basic content structure for the UI to display
        content_json = {
            "title": meta["title"],
            "student_name": meta["student_name"],
            "course": meta["course_code"],
            "sections": [
                {
                    "heading": "Imported Content",
                    "content": [{"type": "paragraph", "text": text}]
                }
            ]
        }
        
        assignment_id = f"imp-{hash(file.name) % 1000000}-{datetime.now().strftime('%M%S')}"
        
        try:
            conn.execute(
                "INSERT OR REPLACE INTO assignments (id, student_name, course_code, assignment_type, business_name, business_website, additional_requirements, content, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    assignment_id,
                    meta["student_name"],
                    meta["course_code"],
                    meta["assignment_type"],
                    "Unknown (Imported)",
                    "N/A",
                    f"Imported from {file.name}",
                    json.dumps(content_json),
                    datetime.utcnow().isoformat()
                )
            )
            count += 1
        except Exception as e:
            print(f"Failed to insert {file.name}: {e}")

    conn.commit()
    conn.close()
    print(f"Successfully imported {count} assignments into the database.")

if __name__ == "__main__":
    import_all()
