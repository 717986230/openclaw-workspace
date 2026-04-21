#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化因果关系图谱和知识点关系图谱表
Initialize Causal Graph and Knowledge Graph Tables
"""

import sqlite3
from datetime import datetime

def create_causal_relations_table(db_path):
    """创建因果关系表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS causal_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cause_memory_id INTEGER NOT NULL,
            effect_memory_id INTEGER NOT NULL,
            causal_type TEXT NOT NULL,
            strength REAL DEFAULT 0.0,
            confidence REAL DEFAULT 0.0,
            evidence TEXT,
            conditions TEXT,
            time_delay INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cause_memory_id) REFERENCES memories(id),
            FOREIGN KEY (effect_memory_id) REFERENCES memories(id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_causal_cause ON causal_relations(cause_memory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_causal_effect ON causal_relations(effect_memory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_causal_type ON causal_relations(causal_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_causal_strength ON causal_relations(strength)")

    conn.commit()
    conn.close()

    print("[OK] causal_relations table created")

def create_knowledge_relations_table(db_path):
    """创建知识点关系表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_memory_id INTEGER NOT NULL,
            target_memory_id INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            relation_strength REAL DEFAULT 0.0,
            relation_direction TEXT,
            attributes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_memory_id) REFERENCES memories(id),
            FOREIGN KEY (target_memory_id) REFERENCES memories(id)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_source ON knowledge_relations(source_memory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_target ON knowledge_relations(target_memory_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_type ON knowledge_relations(relation_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_strength ON knowledge_relations(relation_strength)")

    conn.commit()
    conn.close()

    print("[OK] knowledge_relations table created")

def verify_tables(db_path):
    """验证表创建"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    print("\n[Verification]")
    if 'causal_relations' in tables:
        cursor.execute("SELECT COUNT(*) FROM causal_relations")
        count = cursor.fetchone()[0]
        print(f"  [OK] causal_relations ({count} records)")
    else:
        print(f"  [X] causal_relations (not found)")

    if 'knowledge_relations' in tables:
        cursor.execute("SELECT COUNT(*) FROM knowledge_relations")
        count = cursor.fetchone()[0]
        print(f"  [OK] knowledge_relations ({count} records)")
    else:
        print(f"  [X] knowledge_relations (not found)")

    conn.close()

def main():
    """主函数"""
    print("="*60)
    print("Initialize Causal Graph and Knowledge Graph Tables")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("")

    db_path = "C:\\Users\\Administrator\\.openclaw\\workspace\\memory\\database\\xiaozhi_memory.db"

    # 1. 创建因果关系表
    print("[1/3] Creating causal_relations table...")
    create_causal_relations_table(db_path)

    # 2. 创建知识点关系表
    print("\n[2/3] Creating knowledge_relations table...")
    create_knowledge_relations_table(db_path)

    # 3. 验证表
    print("\n[3/3] Verifying tables...")
    verify_tables(db_path)

    print("\n" + "="*60)
    print("Initialization Complete!")
    print("="*60)
    print("\nNext Steps:")
    print("1. Use CausalGraph class to manage causal relations")
    print("2. Use KnowledgeGraph class to manage knowledge relations")
    print("3. Integrate with memory system for automatic detection")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
