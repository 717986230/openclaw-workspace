import sqlite3
conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# Search for brain and git related memories
cursor.execute("SELECT title, content, category FROM memories WHERE title LIKE '%brain%' OR title LIKE '%git%' OR content LIKE '%brain%' OR content LIKE '%git%' LIMIT 50")
rows = cursor.fetchall()
print(f"Found {len(rows)} rows")
for r in rows:
    print(f"\nTitle: {r[0]}\nCategory: {r[2]}\nContent: {r[1][:200]}")
conn.close()