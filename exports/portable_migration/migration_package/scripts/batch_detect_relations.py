#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量自动检测关系
Batch Auto Detection of Relations
"""

import sys
sys.path.append("C:\\Users\\Administrator\\.openclaw\\workspace\\scripts")

from auto_relation_detector import AutoRelationManager
import sqlite3
from datetime import datetime

def batch_detect_all():
    """批量检测所有记忆的关系"""
    print("="*60)
    print("Batch Auto Detection of Relations")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"
    manager = AutoRelationManager(db_path)

    # 获取所有记忆ID
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM memories")
    total_memories = cursor.fetchone()[0]

    cursor.execute("SELECT id FROM memories ORDER BY created_at DESC")
    memory_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    print(f"Total memories: {total_memories}")
    print(f"Processing {len(memory_ids)} memories...")
    print("")

    # 批量检测
    total_causal = 0
    total_knowledge = 0

    for i, memory_id in enumerate(memory_ids):
        print(f"[{i+1}/{len(memory_ids)}] Processing memory {memory_id}...")

        result = manager.auto_detect_and_add_relations(memory_id)

        causal_count = len(result['causal_relations'])
        knowledge_count = len(result['knowledge_relations'])

        total_causal += causal_count
        total_knowledge += knowledge_count

        if causal_count > 0 or knowledge_count > 0:
            print(f"  - Found {causal_count} causal relations")
            print(f"  - Found {knowledge_count} knowledge relations")

    print("")
    print("="*60)
    print("Batch Detection Complete!")
    print("="*60)
    print(f"Total causal relations detected: {total_causal}")
    print(f"Total knowledge relations detected: {total_knowledge}")
    print(f"Total relations detected: {total_causal + total_knowledge}")
    print("="*60)

def verify_relations():
    """验证关系检测结果"""
    print("\n" + "="*60)
    print("Verifying Relations")
    print("="*60)
    print("")

    db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查因果关系
    cursor.execute("SELECT COUNT(*) FROM causal_relations")
    causal_count = cursor.fetchone()[0]

    cursor.execute("SELECT causal_type, COUNT(*) FROM causal_relations GROUP BY causal_type")
    causal_by_type = cursor.fetchall()

    print(f"Causal Relations: {causal_count}")
    for causal_type, count in causal_by_type:
        print(f"  - {causal_type}: {count}")

    # 检查知识点关系
    cursor.execute("SELECT COUNT(*) FROM knowledge_relations")
    knowledge_count = cursor.fetchone()[0]

    cursor.execute("SELECT relation_type, COUNT(*) FROM knowledge_relations GROUP BY relation_type")
    knowledge_by_type = cursor.fetchall()

    print(f"\nKnowledge Relations: {knowledge_count}")
    for relation_type, count in knowledge_by_type:
        print(f"  - {relation_type}: {count}")

    conn.close()

    print("\n" + "="*60)

def main():
    """主函数"""
    # 批量检测
    batch_detect_all()

    # 验证结果
    verify_relations()

if __name__ == "__main__":
    main()
