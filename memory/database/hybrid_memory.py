#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小智的混合记忆系统
向量数据库 (LanceDB) + 结构化数据库 (SQLite)
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 尝试导入 LanceDB
try:
    import lancedb
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

# 数据库路径
BASE_PATH = Path(__file__).parent
SQLITE_DB = BASE_PATH / "xiaozhi_memory.db"
LANCEDB_PATH = BASE_PATH / "lancedb"


class HybridMemory:
    """混合记忆系统"""

    def __init__(self):
        self.sqlite_conn = sqlite3.connect(SQLITE_DB)
        self.sqlite_conn.row_factory = sqlite3.Row

        if LANCEDB_AVAILABLE:
            LANCEDB_PATH.mkdir(parents=True, exist_ok=True)
            self.lancedb_conn = lancedb.connect(LANCEDB_PATH)
            self._init_lancedb()
        else:
            self.lancedb_conn = None

    def _init_lancedb(self):
        """初始化 LanceDB 表"""
        if "memories" not in self.lancedb_conn.table_names():
            # 创建空表（实际使用时需要嵌入模型）
            pass

    def add_memory(
        self,
        type_: str,
        title: str,
        content: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: int = 5,
        metadata: Optional[Dict] = None
    ) -> int:
        """添加一条记忆"""
        cursor = self.sqlite_conn.cursor()

        tags_json = json.dumps(tags) if tags else None
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (type_, title, content, category, tags_json, importance, metadata_json))

        memory_id = cursor.lastrowid
        self.sqlite_conn.commit()

        # TODO: 同时添加到 LanceDB（需要嵌入模型）

        return memory_id

    def search(
        self,
        query: str,
        type_: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """搜索记忆（混合搜索）"""
        cursor = self.sqlite_conn.cursor()

        where_clauses = []
        params = []

        if type_:
            where_clauses.append("type = ?")
            params.append(type_)
        if category:
            where_clauses.append("category = ?")
            params.append(category)

        # 基础 SQL 查询
        sql = """
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories
        """
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)
        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]

        # 解析 JSON 字段
        for r in results:
            if r["tags"]:
                r["tags"] = json.loads(r["tags"])

        # TODO: 如果 LanceDB 可用，加入向量搜索结果

        return results

    def get_by_type(self, type_: str, limit: int = 50) -> List[Dict]:
        """按类型获取记忆"""
        return self.search(query="", type_=type_, limit=limit)

    def get_by_id(self, memory_id: int) -> Optional[Dict]:
        """按 ID 获取记忆"""
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories WHERE id = ?
        """, (memory_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result["tags"]:
                result["tags"] = json.loads(result["tags"])
            return result
        return None

    def get_stats(self) -> Dict:
        """获取记忆统计"""
        cursor = self.sqlite_conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM memories")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT type, COUNT(*) as cnt
            FROM memories
            GROUP BY type
            ORDER BY cnt DESC
        """)
        by_type = {row[0]: row[1] for row in cursor.fetchall()}

        return {
            "total": total,
            "by_type": by_type,
            "lancedb_available": LANCEDB_AVAILABLE
        }


# 全局实例
_hybrid_memory = None


def get_memory() -> HybridMemory:
    """获取混合记忆系统实例"""
    global _hybrid_memory
    if _hybrid_memory is None:
        _hybrid_memory = HybridMemory()
    return _hybrid_memory


if __name__ == "__main__":
    mem = get_memory()

    print("=" * 50)
    print("小智的混合记忆系统")
    print("=" * 50)
    print()

    stats = mem.get_stats()
    print(f"总记忆数: {stats['total']}")
    print(f"按类型分布: {stats['by_type']}")
    print(f"LanceDB 可用: {stats['lancedb_available']}")
    print()

    # 测试搜索
    print("最近的 5 条记忆:")
    recent = mem.search("", limit=5)
    for r in recent:
        print(f"  [{r['id']}] {r['type']} - {r['title']}")

    print()
    print("[OK] 混合记忆系统就绪！")
