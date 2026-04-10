import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db')
c = conn.cursor()
c.execute("SELECT title, substr(content, 1, 100) FROM memories WHERE type='event' ORDER BY created_at DESC LIMIT 10")
for row in c.fetchall():
    print(f'{row[0]}: {row[1]}')
conn.close()
