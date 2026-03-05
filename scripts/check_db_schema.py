#!/usr/bin/env python3
"""检查数据库表结构"""

import sqlite3

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== memories 表结构 ===")
cursor.execute("PRAGMA table_info(memories)")
for col in cursor.fetchall():
    print(f"  {col[1]}: {col[2]} (not null: {col[3]}, default: {col[4]})")

print("\n=== 现有数据 ===")
cursor.execute("SELECT * FROM memories LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
