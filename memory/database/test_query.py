#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据库查询
"""

import sqlite3
import sys
sys.path.insert(0, str(sys.path[0]))
from init_db import DB_PATH, search_memories, get_memories_by_type


def test_basic_query():
    """测试基本查询"""
    print(f"[TEST] Testing database queries at {DB_PATH}")
    print()

    # 查询所有记忆
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    count = cursor.fetchone()[0]
    print(f"[TOTAL] Total memories in database: {count}")
    print()

    # 按类型分组统计
    print("[BY TYPE] Memories by type:")
    cursor.execute("""
        SELECT type, COUNT(*) as cnt
        FROM memories
        GROUP BY type
        ORDER BY cnt DESC
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]}")
    print()

    # 列出最近的5条记忆
    print("[LATEST] Latest 5 memories:")
    cursor.execute("""
        SELECT id, type, title, created_at
        FROM memories
        ORDER BY created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} - {row[2]} ({row[3]})")
    print()

    conn.close()


def test_search():
    """测试全文搜索"""
    print("[SEARCH] Testing full-text search:")

    # 搜索 "安全"
    results = search_memories("安全 OR security")
    print(f"  搜索 '安全 OR security': {len(results)} 条结果")
    for r in results[:3]:
        print(f"    - [{r[0]}] {r[2]}")
    print()

    # 搜索 "主人"
    results = search_memories("主人 OR owner")
    print(f"  搜索 '主人 OR owner': {len(results)} 条结果")
    for r in results[:3]:
        print(f"    - [{r[0]}] {r[2]}")
    print()


if __name__ == "__main__":
    test_basic_query()
    test_search()
    print("[DONE] All tests passed!")
