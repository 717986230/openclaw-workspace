
import sqlite3
import sys

db_path = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    for row in cursor.fetchall():
        print(f"  - {row[0]}")
    
    print("\nMemories count:")
    cursor.execute("SELECT COUNT(*) FROM memories")
    print(f"  {cursor.fetchone()[0]}")
    
    print("\nImportant memories:")
    cursor.execute("SELECT id, type, title, importance FROM memories WHERE importance >= 9 ORDER BY importance DESC")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]}: {row[2]} (importance: {row[3]})")
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
