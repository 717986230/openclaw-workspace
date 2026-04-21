
import sqlite3
import os

db_path = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

if not os.path.exists(db_path):
    print("Database not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 50)
print("Database Status")
print("=" * 50)

# Get stats
cursor.execute("SELECT COUNT(*) FROM memories")
total = cursor.fetchone()[0]
print("Total memories:", total)

cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
by_type = cursor.fetchall()
print("\nBy type:")
for t, cnt in by_type:
    print(f"  {t}: {cnt}")

# Get recent memories
print("\n" + "=" * 50)
print("Recent 5 memories:")
print("=" * 50)
cursor.execute("SELECT id, type, title, importance FROM memories ORDER BY created_at DESC LIMIT 5")
for row in cursor.fetchall():
    print(f"[{row[0]}] {row[1]} - {row[2]} (importance: {row[3]})")

conn.close()
print("\n[OK] Done")

