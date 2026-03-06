
#!/usr/bin/env python3
"""
检查数据库结构
"""

import sqlite3

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", tables)

# 查看memories表结构
if tables:
    cursor.execute(f"PRAGMA table_info({tables[0][0]})")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col}")

conn.close()

