#!/usr/bin/env python3
"""
二饼大脑 - 改进版
基于 Memori 架构：Entity + Process + Session 三层归因
按需查询，不遍历全部上下文
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

# 数据库路径
DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

class ErbingBrain:
    """二饼的大脑 - 改进版"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self.entity_id = "erbing_001"  # 我的实体 ID
        self.process_id = "ai_assistant"  # 我的过程 ID
        self.session_id = self._generate_session_id()  # 当前会话 ID
    
    def _get_conn(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def _generate_session_id(self):
        """生成会话 ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def get_core_context(self) -> Dict[str, List[Dict]]:
        """
        获取核心上下文（按需，不遍历全部）
        基于 Memori 的三层归因
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        context = {
            "identity": [],      # 身份认知
            "relationship": [],  # 主人关系
            "principles": [],    # 核心原则
            "reminders": [],     # 重要提醒
            "important": []      # 最重要的记忆
        }
        
        # 1. 身份认知 (type = 'identity')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'identity' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["identity"] = [dict(row) for row in cursor.fetchall()]
        
        # 2. 主人关系 (type = 'relationship')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'relationship' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["relationship"] = [dict(row) for row in cursor.fetchall()]
        
        # 3. 核心原则 (type = 'principle')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'principle' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 10
        """)
        context["principles"] = [dict(row) for row in cursor.fetchall()]
        
        # 4. 重要提醒 (type = 'reminder')
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type = 'reminder' 
            ORDER BY importance DESC, created_at DESC 
            LIMIT 5
        """)
        context["reminders"] = [dict(row) for row in cursor.fetchall()]
        
        # 5. 最重要的记忆 (importance >= 9)
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
        全文搜索（FTS5）
        """
        conn = self._get_conn()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        results = []
        
        try:
            # 尝试 FTS5
            cursor.execute("""
                SELECT m.* FROM memories m 
                JOIN memory_index mi ON m.id = mi.rowid 
                WHERE memory_index MATCH ? 
                ORDER BY importance DESC, created_at DESC 
                LIMIT ?
            """, (query, limit))
            results = [dict(row) for row in cursor.fetchall()]
        except:
            # 回退到 LIKE
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
        """按类型快速查询"""
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
        """添加新记忆"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mem_type, title, content, category, tags, importance, datetime.now().isoformat()))
        
        # 尝试更新 FTS5 索引
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
        """打印大脑统计"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        print("="*60)
        print("ERBING BRAIN - 改进版")
        print("="*60)
        
        # 总记忆数
        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]
        
        # 按类型统计
        cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
        by_type = cursor.fetchall()
        
        print(f"\n总记忆数: {total}")
        print("\n按类型分布:")
        for t, c in by_type:
            print(f"  - {t}: {c}")
        
        # 核心上下文预览
        print("\n" + "="*60)
        print("核心上下文预览（按需加载）:")
        print("="*60)
        
        context = self.get_core_context()
        
        print(f"\n身份认知: {len(context['identity'])} 条")
        for m in context['identity'][:2]:
            print(f"  - {m['title']}")
        
        print(f"\n主人关系: {len(context['relationship'])} 条")
        for m in context['relationship'][:2]:
            print(f"  - {m['title']}")
        
        print(f"\n核心原则: {len(context['principles'])} 条")
        for m in context['principles'][:3]:
            print(f"  - {m['title']}")
        
        print(f"\n重要提醒: {len(context['reminders'])} 条")
        for m in context['reminders']:
            print(f"  - {m['title']}")
        
        print("\n" + "="*60)
        print("✅ 按需查询系统就绪！不再遍历全部上下文！")
        print("="*60)
        
        conn.close()

# 单例
_brain_instance = None

def get_brain() -> ErbingBrain:
    """获取大脑单例"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = ErbingBrain()
    return _brain_instance

if __name__ == "__main__":
    brain = get_brain()
    brain.print_stats()
