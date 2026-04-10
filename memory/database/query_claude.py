import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('xiaozhi_memory.db')
cursor = conn.cursor()
# 查找蜂群和Claude Code相关记忆
cursor.execute("""SELECT title, content, created_at FROM memories 
WHERE content LIKE '%Claude Code%' OR content LIKE '%插件系统%' OR content LIKE '%架构%' OR title LIKE '%蜂群%' OR title LIKE '%采集%'
ORDER BY created_at DESC LIMIT 30""")
rows = cursor.fetchall()
for row in rows:
    print(f'=== {row[0]} ({row[2]}) ===')
    print(row[1][:1000] if row[1] else '(empty)')
    print()
