
#!/usr/bin/env python3
"""娴嬭瘯澶ц剳鏁版嵁搴?""

import sqlite3

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

print("="*60)
print("浜岄ゼ澶ц剳鏁版嵁搴撴鏌?)
print("="*60)

# 杩炴帴鏁版嵁搴?conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 妫€鏌ヨ〃
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"\n馃搳 鏁版嵁搴撹〃: {[t['name'] for t in tables]}")

# 妫€鏌ヨ蹇嗘暟閲?cursor.execute("SELECT COUNT(*) as cnt FROM memories")
count = cursor.fetchone()['cnt']
print(f"馃 璁板繂鎬绘暟: {count}")

# 妫€鏌ラ噸瑕佽蹇?cursor.execute("SELECT type, COUNT(*) as cnt FROM memories GROUP BY type")
types = cursor.fetchall()
print(f"\n馃搵 璁板繂鍒嗙被:")
for t in types:
    print(f"   - {t['type']}: {t['cnt']}")

# 鑾峰彇鏍稿績璁板繂
print(f"\n馃敟 閲嶈璁板繂 (importance >= 9):")
cursor.execute("SELECT * FROM memories WHERE importance >= 9 ORDER BY importance DESC, created_at DESC LIMIT 10")
important = cursor.fetchall()
for mem in important:
    print(f"\n   銆恵mem['type']}銆憑mem['title']} (閲嶈搴? {mem['importance']})")
    print(f"   {mem['content'][:100]}...")

conn.close()
print("\n" + "="*60)
print("鉁?澶ц剳妫€鏌ュ畬鎴愶紒")
print("="*60)
