import sqlite3
import sys
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT title, content, created_at 
    FROM memories 
    WHERE type = 'milestone' 
    ORDER BY created_at DESC 
    LIMIT 10
''')
rows = cursor.fetchall()

for row in rows:
    print(f'【{row[0]}】')
    print(f'时间: {row[2]}')
    print(row[1])
    print('='*60)
    
conn.close()
