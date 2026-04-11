import sqlite3

conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Database tables:")
for t in tables:
    print(f"  - {t[0]}")
conn.close()
