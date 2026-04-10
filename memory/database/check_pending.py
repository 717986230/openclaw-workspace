#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect(r'C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db')
c = conn.cursor()
c.execute("SELECT title, content FROM memories WHERE type='improvement'")
for row in c.fetchall():
    print(f"=== {row[0]} ===")
    print(row[1][:500])
    print()
conn.close()
