
import sqlite3
import os

db_path = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

if not os.path.exists(db_path):
    print("ERROR: DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 50)
print("DATABASE WORKING!")
print("=" * 50)

cursor.execute("SELECT COUNT(*) FROM memories")
total = cursor.fetchone()[0]
print("Total memories:", total)

cursor.execute("SELECT id, type, title, importance FROM memories ORDER BY created_at DESC LIMIT 5")
print("\nLatest 5:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[1]} - {row[2]} (imp:{row[3]})")

conn.close()
print("\n[OK] Database is working perfectly!")

