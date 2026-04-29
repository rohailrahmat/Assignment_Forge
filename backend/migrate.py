import sqlite3

DB_PATH = "assignmentforge.db"

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get existing columns
    cursor.execute("PRAGMA table_info(assignments);")
    existing_columns = [col[1] for col in cursor.fetchall()]
    
    new_columns = [
        ("business_name", "TEXT"),
        ("business_website", "TEXT"),
        ("additional_requirements", "TEXT")
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in existing_columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE assignments ADD COLUMN {col_name} {col_type}")
    
    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
