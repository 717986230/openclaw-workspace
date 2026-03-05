#!/usr/bin/env python3
\"\"\"
二饼大脑快速访问 API
按需查询，避免遍历全部上下文
\"\"\"

import sqlite3
from typing import List, Dict, Optional

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

class ErbingBrain:
    \"\"\"二饼大脑 - 快速记忆访问\"\"\"
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def _get_conn(self):
        \"\"\"获取数据库连接\"\"\"
        return sqlite3.connect(self.db_path)
    
    def get_by_type(self, mem_type: str, limit: int = 10) -> List[Dict]:
        \"\"\"按类型快速查询\"\"\"
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE type = ? ORDER BY importance DESC, created_at DESC LIMIT ?",
            (mem_type, limit)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_important(self, min_importance: int = 8, limit: int = 20) -> List[Dict]:
        \"\"\"获取重要记忆\"\"\"
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM memories WHERE importance >= ? ORDER BY importance DESC, created_at DESC LIMIT ?",
            (min_importance, limit)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        \"\"\"全文搜索（FTS5）\"\"\"
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # 尝试 FTS5
            cursor.execute(
                \"\"\"SELECT m.* FROM memories m 
                   JOIN memory_index mi ON m.id = mi.rowid 
                   WHERE memory_index MATCH ? 
                   ORDER BY importance DESC, created_at DESC LIMIT ?\"\"\",
                (query, limit)
            )
            results = [dict(row) for row in cursor.fetchall()]
        except:
            # 回退到 LIKE
            cursor.execute(
                \"\"\"SELECT * FROM memories 
                   WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                   ORDER BY importance DESC, created_at DESC LIMIT ?\"\"\",
                (f\"%{query}%\", f\"%{query}%\", f\"%{query}%\", limit)
            )
            results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    
    def get_identity(self) -> List[Dict]:
        \"\"\"获取身份认知\"\"\"
        return self.get_by_type("identity")
    
    def get_relationship(self) -> List[Dict]:
        \"\"\"获取主人关系\"\"\"
        return self.get_by_type("relationship")
    
    def get_principles(self) -> List[Dict]:
        \"\"\"获取核心原则\"\"\"
        return self.get_by_type("principle")
    
    def get_reminders(self) -> List[Dict]:
        \"\"\"获取重要提醒\"\"\"
        return self.get_by_type("reminder")
    
    def get_core_context(self) -> Dict[str, List[Dict]]:
        \"\"\"获取核心上下文（按需加载，不遍历全部）\"\"\"
        return {
            "identity": self.get_identity(),
            "relationship": self.get_relationship(),
            "principles": self.get_principles(),
            "reminders": self.get_reminders(),
            "important": self.get_important(min_importance=9, limit=10)
        }

# 单例
_brain = None

def get_brain() -> ErbingBrain:
    \"\"\"获取大脑单例\"\"\"
    global _brain
    if _brain is None:
        _brain = ErbingBrain()
    return _brain

if __name__ == "__main__":
    print("="*60)
    print("Erbing Brain Quick Access API")
    print("="*60)
    
    brain = get_brain()
    
    print("\n[TEST] Testing core context loading...")
    core = brain.get_core_context()
    
    print(f"\n✅ Quick access API ready!")
    print(f"   - Identity: {len(core['identity'])}")
    print(f"   - Relationship: {len(core['relationship'])}")
    print(f"   - Principles: {len(core['principles'])}")
    print(f"   - Reminders: {len(core['reminders'])}")
    print(f"   - Important: {len(core['important'])}")
    print("\n✅ No more full-context traversal! On-demand fast queries!")
