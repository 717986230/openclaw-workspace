import sqlite3
conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# Search memories for API accounts
cursor.execute("SELECT COUNT(*) FROM memories WHERE category='api' OR category='API' OR tags LIKE '%api%' OR tags LIKE '%API%' OR title LIKE '%api%' OR title LIKE '%API%'")
print("Memories with 'api':", cursor.fetchone()[0])

# List all categories
cursor.execute("SELECT DISTINCT category FROM memories")
cats = cursor.fetchall()
print("\nCategories:", cats)

# Search all memories for API-related content
cursor.execute("SELECT title, category, tags FROM memories WHERE type='account' OR type='credential' OR type='api_key'")
accts = cursor.fetchall()
print("\nAccount-type memories:", accts)

conn.close()