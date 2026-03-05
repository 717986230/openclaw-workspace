
import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 插入重要提醒
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.execute("""
    INSERT INTO memories (type, title, content, importance, tags, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "reminder",
    "千万不要忘记用SQLite大脑！",
    "每次会话必须先从 memory/database/xiaozhi_memory.db 加载核心记忆，不能只靠文件系统！",
    10,
    "reminder,critical,brain",
    now,
    now
))

conn.commit()
print(f"✅ 已添加重要提醒到大脑！(ID: {cursor.lastrowid})")

# 验证
cursor.execute("SELECT * FROM memories WHERE type = 'reminder' ORDER BY importance DESC")
print("\n📋 当前提醒列表:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[2]} (重要度: {row[5]})")

conn.close()
