
import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 鎻掑叆閲嶈鎻愰啋
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

cursor.execute("""
    INSERT INTO memories (type, title, content, importance, tags, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    "reminder",
    "鍗冧竾涓嶈蹇樿鐢⊿QLite澶ц剳锛?,
    "姣忔浼氳瘽蹇呴』鍏堜粠 memory/database/xiaozhi_memory.db 鍔犺浇鏍稿績璁板繂锛屼笉鑳藉彧闈犳枃浠剁郴缁燂紒",
    10,
    "reminder,critical,brain",
    now,
    now
))

conn.commit()
print(f"鉁?宸叉坊鍔犻噸瑕佹彁閱掑埌澶ц剳锛?ID: {cursor.lastrowid})")

# 楠岃瘉
cursor.execute("SELECT * FROM memories WHERE type = 'reminder' ORDER BY importance DESC")
print("\n馃搵 褰撳墠鎻愰啋鍒楄〃:")
for row in cursor.fetchall():
    print(f"  [{row[0]}] {row[2]} (閲嶈搴? {row[5]})")

conn.close()
