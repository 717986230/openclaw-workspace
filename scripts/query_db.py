
#!/usr/bin/env python3
import sqlite3

db_path = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 鏌ョ湅琛ㄧ粨鏋?cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

if tables:
    # 鏌ヨ鎵€鏈夎蹇?    cursor.execute(f"SELECT id, title, type, importance, created_at FROM {tables[0][0]} ORDER BY created_at DESC LIMIT 10")
    rows = cursor.fetchall()
    print(f"\n鏈€杩?{len(rows)} 鏉¤蹇?")
    for row in rows:
        print(f"  {row[0]}: {row[1]} ({row[2]}, 閲嶈鎬?{row[3]})")

conn.close()

