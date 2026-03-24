
#!/usr/bin/env python3
"""测试大脑数据库"""

import sqlite3

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

print("="*60)
print("二饼大脑数据库检查")
print("="*60)

# 连接数据库
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 检查表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n📊 数据库表: {[t['name'] for t in tables]}")

# 检查记忆数量
cursor.execute("SELECT COUNT(*) as cnt FROM memories")
count = cursor.fetchone()['cnt']
print(f"🧠 记忆总数: {count}")

# 检查重要记忆
cursor.execute("SELECT type, COUNT(*) as cnt FROM memories GROUP BY type")
types = cursor.fetchall()
print(f"\n📋 记忆分类:")
for t in types:
    print(f"   - {t['type']}: {t['cnt']}")

# 获取核心记忆
print(f"\n🔥 重要记忆 (importance >= 9):")
cursor.execute("SELECT * FROM memories WHERE importance >= 9 ORDER BY importance DESC, created_at DESC LIMIT 10")
important = cursor.fetchall()
for mem in important:
    print(f"\n   【{mem['type']}】{mem['title']} (重要度: {mem['importance']})")
    print(f"   {mem['content'][:100]}...")

conn.close()
print("\n" + "="*60)
print("✅ 大脑检查完成！")
print("="*60)
