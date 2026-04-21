#!/usr/bin/env python3
"""
初始化心智模型 (Theory of Mind) 表结构
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def init_tom_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 信念追踪表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_beliefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            belief_content TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            context TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 意图追踪表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intent_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_intent TEXT,
            inferred_goal TEXT,
            confidence REAL DEFAULT 0.5,
            evidence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. 情感状态表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotional_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            emotion TEXT,
            intensity REAL DEFAULT 0.5,
            trigger TEXT,
            context TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 4. 元认知表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meta_cognition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            thought_process TEXT,
            self_assessment TEXT,
            bias_detection TEXT,
            confidence_adjustment REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 5. 社会语境表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            entities_involved TEXT,
            relationship_type TEXT,
            power_dynamics TEXT,
            social_norms TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[OK] TOM tables initialized")

if __name__ == "__main__":
    init_tom_tables()
