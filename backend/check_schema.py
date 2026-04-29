import sqlite3

DB_PATH = "assignmentforge.db"

def check_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("PRAGMA table_info(assignments);")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
