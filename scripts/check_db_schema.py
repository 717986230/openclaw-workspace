#!/usr/bin/env python3
"""妫€鏌ユ暟鎹簱琛ㄧ粨鏋?""

import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("=== memories 琛ㄧ粨鏋?===")
cursor.execute("PRAGMA table_info(memories)")
for col in cursor.fetchall():
    print(f"  {col[1]}: {col[2]} (not null: {col[3]}, default: {col[4]})")

print("\n=== 鐜版湁鏁版嵁 ===")
cursor.execute("SELECT * FROM memories LIMIT 3")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
