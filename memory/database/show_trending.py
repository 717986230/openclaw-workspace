#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db')
c = conn.cursor()
c.execute("SELECT title, content FROM memories WHERE title LIKE '%Trending%' AND type='event' ORDER BY created_at DESC LIMIT 3")
for row in c.fetchall():
    print('=== ' + row[0] + ' ===')
    print(row[1][:800])
    print()
conn.close()
