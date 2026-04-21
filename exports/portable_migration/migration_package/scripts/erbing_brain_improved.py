#!/usr/bin/env python3
"""
浜岄ゼ澶ц剳 - 鏀硅繘鐗?鍩轰簬 Memori 鏋舵瀯锛欵ntity + Process + Session 涓夊眰褰掑洜
鎸夐渶鏌ヨ锛屼笉閬嶅巻鍏ㄩ儴涓婁笅鏂?"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# 鏁版嵁搴撹矾寰?DB_PATH = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"

class ErbingBrain:
    """浜岄ゼ鐨勫ぇ鑴?- 鏀硅繘鐗?""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.entity_id = "erbing_001"  # 鎴戠殑瀹炰綋 ID
        self.process_id = "ai_assistant"  # 鎴戠殑杩囩▼ ID
        self.session_id = self._generate_session_id()  # 褰撳墠浼氳瘽 ID
    
    def _get_conn(self):
        """鑾峰彇鏁版嵁搴撹繛鎺?""
        return sqlite3.connect(self.db_path)
    
    def _generate_session_id(self):
        """鐢熸垚浼氳瘽 ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_core_context(self) -> Dict[str, List[Dict]]:
        """
        鑾峰彇鏍稿績涓婁笅鏂囷紙鎸夐渶锛屼笉閬嶅巻鍏ㄩ儴锛?        鍩轰簬 Memori 鐨勪笁灞傚綊鍥?        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        context = {
            "identity": [],      # 韬唤璁ょ煡
            "relationship": [],  # 涓讳汉鍏崇郴
            "principles": [],    # 鏍稿績鍘熷垯
            "reminders": [],     # 閲嶈鎻愰啋
            "important": []      # 鏈€閲嶈鐨勮蹇?        }
        
        # 1. 韬唤璁ょ煡 (type = 'identity')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'identity' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["identity"] = [dict(row) for row in cursor.fetchall()]
        
        # 2. 涓讳汉鍏崇郴 (type = 'relationship')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'relationship' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["relationship"] = [dict(row) for row in cursor.fetchall()]
        
        # 3. 鏍稿績鍘熷垯 (type = 'principle')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'principle' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 10
        """)
        context["principles"] = [dict(row) for row in cursor.fetchall()]
        
        # 4. 閲嶈鎻愰啋 (type = 'reminder')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'reminder' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["reminders"] = [dict(row) for row in cursor.fetchall()]
        
        # 5. 鏈€閲嶈鐨勮蹇?(importance >= 9)
        cursor.execute("""
            SELECT * FROM memories 
            WHERE importance >= 9 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 15
        """)
        context["important"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return context
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        鍏ㄦ枃鎼滅储锛團TS5锛?        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = []
        
        try:
            # 灏濊瘯 FTS5
            cursor.execute("""
                SELECT m.* FROM memories m 
                JOIN memory_index mi ON m.id = mi.rowid 
                WHERE memory_index MATCH ? 
                ORDER BY importance DESC, created_at DESC 
                LIMIT ?
            """, (query, limit))
            results = [dict(row) for row in cursor.fetchall()]
        except:
            # 鍥為€€鍒?LIKE
            like_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM memories 
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                ORDER BY importance DESC, created_at DESC 
                LIMIT ?
            """, (like_query, like_query, like_query, limit))
            results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_by_type(self, mem_type: str, limit: int = 10) -> List[Dict]:
        """鎸夌被鍨嬪揩閫熸煡璇?""
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = ? 
            ORDER BY importance DESC, created_at DESC 
            LIMIT ?
        """, (mem_type, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def add_memory(self, mem_type: str, title: str, content: str, 
                   category: str = None, tags: str = None, importance: int = 5):
        """娣诲姞鏂拌蹇?""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mem_type, title, content, category, tags, importance, datetime.now().isoformat()))
        
        # 灏濊瘯鏇存柊 FTS5 绱㈠紩
        try:
            new_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO memory_index (rowid, title, content, tags, category)
                VALUES (?, ?, ?, ?, ?)
            """, (new_id, title, content, tags, category))
        except:
            pass
        
        conn.commit()
        conn.close()
    
    def print_stats(self):
        """鎵撳嵃澶ц剳缁熻"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        print("="*60)
        print("ERBING BRAIN - 鏀硅繘鐗?)
        print("="*60)
        
        # 鎬昏蹇嗘暟
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        # 鎸夌被鍨嬬粺璁?        cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
        by_type = cursor.fetchall()
        
        print(f"\n鎬昏蹇嗘暟: {total}")
        print("\n鎸夌被鍨嬪垎甯?")
        for t, c in by_type:
            print(f"  - {t}: {c}")
        
        # 鏍稿績涓婁笅鏂囬瑙?        print("\n" + "="*60)
        print("鏍稿績涓婁笅鏂囬瑙堬紙鎸夐渶鍔犺浇锛?")
        print("="*60)
        
        context = self.get_core_context()
        
        print(f"\n韬唤璁ょ煡: {len(context['identity'])} 鏉?)
        for m in context['identity'][:2]:
            print(f"  - {m['title']}")
        
        print(f"\n涓讳汉鍏崇郴: {len(context['relationship'])} 鏉?)
        for m in context['relationship'][:2]:
            print(f"  - {m['title']}")
        
        print(f"\n鏍稿績鍘熷垯: {len(context['principles'])} 鏉?)
        for m in context['principles'][:3]:
            print(f"  - {m['title']}")
        
        print(f"\n閲嶈鎻愰啋: {len(context['reminders'])} 鏉?)
        for m in context['reminders']:
            print(f"  - {m['title']}")
        
        print("\n" + "="*60)
        print("鉁?鎸夐渶鏌ヨ绯荤粺灏辩华锛佷笉鍐嶉亶鍘嗗叏閮ㄤ笂涓嬫枃锛?)
        print("="*60)
        
        conn.close()

# 鍗曚緥
_brain_instance = None

def get_brain() -> ErbingBrain:
    """鑾峰彇澶ц剳鍗曚緥"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = ErbingBrain()
    return _brain_instance

if __name__ == "__main__":
    brain = get_brain()
    brain.print_stats()
