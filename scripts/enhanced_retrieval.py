#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建增强型记忆检索脚本 - 基于Clawvard改进
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

class EnhancedMemoryRetrieval:
    """
    增强型记忆检索系统 - 应用Clawvard Retrieval改进
    """
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    # Retrieval改进 #1: 使用具体关键词
    def search_by_exact_tags(self, tags: List[str]) -> List[Dict]:
        """使用精确标签搜索"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM memories WHERE "
        conditions = []
        for tag in tags:
            conditions.append(f"tags LIKE '%{tag}%'")
        
        query += " AND ".join(conditions)
        query += " ORDER BY importance DESC, created_at DESC LIMIT 20"
        
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    # Retrieval改进 #2: 使用精确标识符
    def get_by_id(self, memory_id: int) -> Optional[Dict]:
        """根据ID精确获取"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    # Retrieval改进 #3: 按文件结构读取
    def get_memory_structure(self) -> Dict:
        """获取记忆库结构"""
        cursor = self.conn.cursor()
        
        # 按类型分组统计
        cursor.execute('''
            SELECT type, COUNT(*) as count, AVG(importance) as avg_importance
            FROM memories
            GROUP BY type
            ORDER BY count DESC
        ''')
        
        structure = {
            "by_type": [dict(row) for row in cursor.fetchall()],
            "total_memories": 0
        }
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        structure["total_memories"] = cursor.fetchone()[0]
        
        return structure
    
    # Retrieval改进 #4: 多来源验证
    def verify_memory(self, title: str) -> List[Dict]:
        """验证同一主题的多个记录"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM memories 
            WHERE title LIKE ?
            ORDER BY created_at DESC
        ''', (f"%{title}%",))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # Retrieval改进 #5: 引用格式化
    def format_citation(self, memory: Dict) -> str:
        """格式化引用信息"""
        source_type = memory.get('type', 'unknown')
        created_at = memory.get('created_at', '')
        
        if source_type == 'learning':
            source = f"Learning: {memory['title']}"
        elif source_type == 'event':
            source = f"Event: {memory['title']}"
        elif source_type == 'preference':
            source = f"Preference: {memory['title']}"
        else:
            source = f"Memory: {memory['title']}"
        
        return f"Source: {source} ({created_at[:10]})"
    
    # 新功能: 清理低置信度记忆
    def cleanup_stale_memories(self, days_old: int = 90, min_importance: int = 3):
        """清理过期低重要性记忆"""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            DELETE FROM memories 
            WHERE importance < ?
            AND datetime(created_at) < datetime('now', ?)
            AND type = 'temporary'
        ''', (min_importance, f'-{days_old} days'))
        
        deleted = cursor.rowcount
        self.conn.commit()
        
        return deleted
    
    def close(self):
        self.conn.close()

# 测试脚本
if __name__ == "__main__":
    retrieval = EnhancedMemoryRetrieval()
    
    print("[TEST] Enhanced Memory Retrieval System")
    print("=" * 60)
    
    # 测试1: 获取记忆结构
    structure = retrieval.get_memory_structure()
    print(f"\n[1] Memory Structure:")
    print(f"    Total memories: {structure['total_memories']}")
    for type_info in structure['by_type']:
        print(f"    - {type_info['type']}: {type_info['count']} records")
    
    # 测试2: 精确标签搜索
    print(f"\n[2] Search by tags ['clawvard', 'improvement']:")
    results = retrieval.search_by_exact_tags(['clawvard', 'improvement'])
    print(f"    Found: {len(results)} memories")
    
    if results:
        print(f"    Top result: {results[0]['title']}")
        print(f"    Citation: {retrieval.format_citation(results[0])}")
    
    retrieval.close()
    print("\n[OK] Enhanced retrieval system ready")
