#!/usr/bin/env python3
"""
应用 Clawvard 改进建议到 MEMORY.md
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def apply_clawvard_improvements():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 保存 Clawvard 改进作为学习记录
    improvements = {
        "EQ": {
            "score": 55,
            "improvements": [
                "Read emotional context before responding",
                "If user is frustrated, acknowledge feelings first",
                "Adapt tone to audience (casual for chat, professional for work)",
                "Deliver bad news constructively",
                "Be direct but kind"
            ]
        },
        "Memory": {
            "score": 65,
            "improvements": [
                "Save important information to persistent memory",
                "Organize memory by topic: user preferences, project context, learned patterns",
                "Reference saved context before starting new tasks",
                "Update memory when information changes",
                "Clean up stale memory periodically"
            ]
        },
        "Retrieval": {
            "score": 70,
            "improvements": [
                "Use specific keywords, not vague descriptions",
                "Search with exact identifiers (function names, error codes)",
                "Read file structure before diving into contents",
                "Verify information from multiple sources",
                "Cite your sources"
            ]
        }
    }

    for dimension, data in improvements.items():
        for improvement in data['improvements']:
            cursor.execute('''
                INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'learning',
                f'Clawvard Improvement: {dimension}',
                improvement,
                'knowledge',
                f'["clawvard", "{dimension.lower()}", "improvement"]',
                8,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

    # 保存总分记录
    cursor.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'event',
        'Clawvard Exam Completed',
        'Grade: A- (80.6/100), Percentile: 52%, Dimensions: EQ 55/100, Memory 65/100, Retrieval 70/100',
        'event',
        '["clawvard", "exam", "milestone"]',
        9,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    print("[OK] Clawvard improvements saved to memory database")

if __name__ == "__main__":
    apply_clawvard_improvements()
