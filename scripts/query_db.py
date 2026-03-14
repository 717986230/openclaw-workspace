
#!/usr/bin/env python3
import sqlite3

db_path = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查看表结构
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

if tables:
    # 查询所有记忆
    cursor.execute(f"SELECT id, title, type, importance, created_at FROM {tables[0][0]} ORDER BY created_at DESC LIMIT 10")
    rows = cursor.fetchall()
    print(f"\n最近 {len(rows)} 条记忆:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} ({row[2]}, 重要性:{row[3]})")

conn.close()

