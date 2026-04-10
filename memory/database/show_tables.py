import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('xiaozhi_memory.db')
cursor = conn.cursor()
# 显示所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in database:")
for t in tables:
    print(f"  - {t[0]}")
