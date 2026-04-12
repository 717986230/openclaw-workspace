#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设计模式匹配工具
用于查找相似风格的设计系统
"""

import sqlite3
from typing import List, Dict, Tuple

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def find_similar_designs(query_tags: List[str], limit: int = 5) -> List[Dict]:
    """
    根据标签查找相似的设计系统

    Args:
        query_tags: 查询标签列表
        limit: 返回结果数量

    Returns:
        相似设计系统列表
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 构建查询
    placeholders = ','.join(['?' for _ in query_tags])
    query = f"""
        SELECT
            ds.id,
            ds.name,
            ds.category,
            ds.description,
            COUNT(dt.tag) as match_count
        FROM design_systems ds
        LEFT JOIN design_tags dt ON ds.id = dt.design_system_id
        WHERE dt.tag IN ({placeholders})
        GROUP BY ds.id
        ORDER BY match_count DESC
        LIMIT ?
    """

    cursor.execute(query, query_tags + [limit])
    results = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "description": row[3],
            "match_count": row[4]
        }
        for row in results
    ]

def get_design_system_details(name: str) -> Dict:
    """
    获取设计系统的详细信息

    Args:
        name: 设计系统名称

    Returns:
        设计系统详细信息
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 获取基本信息
    cursor.execute("""
        SELECT id, name, category, url, description
        FROM design_systems
        WHERE name = ?
    """, (name,))
    basic_info = cursor.fetchone()

    if not basic_info:
        conn.close()
        return None

    design_id = basic_info[0]

    # 获取色彩系统
    cursor.execute("""
        SELECT role, name, hex, usage
        FROM color_palettes
        WHERE design_system_id = ?
    """, (design_id,))
    colors = cursor.fetchall()

    # 获取排版系统
    cursor.execute("""
        SELECT font_family, font_type, font_size, font_weight, line_height, letter_spacing, usage
        FROM typography_systems
        WHERE design_system_id = ?
    """, (design_id,))
    typography = cursor.fetchall()

    # 获取标签
    cursor.execute("""
        SELECT tag
        FROM design_tags
        WHERE design_system_id = ?
    """, (design_id,))
    tags = [row[0] for row in cursor.fetchall()]

    conn.close()

    return {
        "id": basic_info[0],
        "name": basic_info[1],
        "category": basic_info[2],
        "url": basic_info[3],
        "description": basic_info[4],
        "colors": [
            {
                "role": row[0],
                "name": row[1],
                "hex": row[2],
                "usage": row[3]
            }
            for row in colors
        ],
        "typography": [
            {
                "font_family": row[0],
                "font_type": row[1],
                "font_size": row[2],
                "font_weight": row[3],
                "line_height": row[4],
                "letter_spacing": row[5],
                "usage": row[6]
            }
            for row in typography
        ],
        "tags": tags
    }

def get_all_design_systems() -> List[Dict]:
    """获取所有设计系统"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, category, url, description
        FROM design_systems
        ORDER BY name
    """)

    results = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "url": row[3],
            "description": row[4]
        }
        for row in results
    ]

if __name__ == "__main__":
    # 示例：查找相似的设计系统
    print("=== Finding similar designs ===")
    similar = find_similar_designs(["minimal", "purple"], limit=3)
    for design in similar:
        print(f"{design['name']} ({design['category']}) - {design['match_count']} matches")

    print("\n=== Design system details ===")
    details = get_design_system_details("linear")
    if details:
        print(f"Name: {details['name']}")
        print(f"Category: {details['category']}")
        print(f"Tags: {', '.join(details['tags'])}")
        print(f"Colors: {len(details['colors'])} colors")
        print(f"Typography: {len(details['typography'])} fonts")

    print("\n=== All design systems ===")
    all_designs = get_all_design_systems()
    for design in all_designs:
        print(f"- {design['name']} ({design['category']})")
