
import sqlite3

db_path = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get schema
    cursor.execute("PRAGMA table_info(memories)")
    print("memories table schema:")
    for col in cursor.fetchall():
        print(f"  {col}")
    
    # Try to read some data
    cursor.execute("SELECT id, type, title, importance FROM memories LIMIT 5")
    print("\nSample memories:")
    for row in cursor.fetchall():
        print(f"  {row}")
    
    conn.close()
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
