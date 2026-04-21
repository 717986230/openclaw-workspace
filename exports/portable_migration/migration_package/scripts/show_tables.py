import sqlite3
conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print("Tables:", tables)
conn.close()