
#!/usr/bin/env python3
"""
娣诲姞璁板繂鍒版暟鎹簱
"""

import sqlite3
from datetime import datetime

DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def add_memory(title, content, mem_type="learning", importance=8, tags=""):
    """娣诲姞涓€鏉¤蹇?""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO memories (title, content, type, importance, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (title, content, mem_type, importance, tags, now, now))
    
    memory_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f"鉁?璁板繂宸叉坊鍔?(ID: {memory_id})")
    return memory_id

if __name__ == "__main__":
    # Pinchtab 瀛︿範绗旇
    title = "Pinchtab - AI Agent娴忚鍣ㄦ帶鍒跺伐鍏?
    content = """
Pinchtab 鏄竴涓粎 12MB 鐨勪簩杩涘埗鏂囦欢锛屽彲浠ヨ浠讳綍 AI Agent 瀹屽叏鑷姩鍖栨帶鍒舵祻瑙堝櫒銆?
鏍稿績浼樺娍锛?1. 闆堕厤缃細涓㈣繘鍘诲氨鑳借窇锛岀洿鎺ユ帴绠℃湰鍦?Chrome
2. 鐪侀挶绁炲櫒锛氫紶缁熸埅鍥炬柟妗?椤甸潰1涓嘥okens锛孭inchtab鍙800锛屾垚鏈爫鎺?3鍊?3. 闅愯韩娼滆锛氳嚜甯?stealth mode锛屼富娴佺綉绔欏弽鐖瓥鐣ュ熀鏈槸鎽嗚
4. 鏅鸿兘 Diff锛氭瘡娆″彧杩斿洖鍙樺寲鐨勫唴瀹癸紝Agent涓嶇敤鍙嶅璇诲簾璇?
鎶€鏈壒鐐癸細
- 涓嶉檺寮€鍙戣瑷€銆佷笉缁戝畾浠讳綍 SDK
- 鐢氳嚦閫氳繃 curl 閮借兘鐩存帴璋冪敤
- GitHub: https://github.com/pinchtab/pinchtab
    """.strip()
    
    tags = "宸ュ叿,娴忚鍣?AI Agent,Pinchtab,鎴愭湰浼樺寲"
    
    add_memory(title, content, mem_type="learning", importance=9, tags=tags)

