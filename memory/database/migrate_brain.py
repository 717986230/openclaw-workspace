#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移 erbing_brain.json 到 SQLite 数据库
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"
BRAIN_PATH = Path(__file__).parent.parent / "erbing_brain.json"

def migrate():
    with open(BRAIN_PATH, "r", encoding="utf-8") as f:
        brain = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    migrated = 0

    # 1. 迁移 core_memories
    for mem in brain.get("core_memories", []):
        cursor.execute("""
            INSERT OR IGNORE INTO memories (type, title, content, category, importance, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "core_memory",
            mem["title"],
            mem.get("content", ""),
            mem.get("category", "general"),
            mem.get("importance", 5),
            mem.get("created_at", datetime.now().isoformat()),
            json.dumps({"source": "erbing_brain.json", "original_id": mem.get("id")})
        ))
        if cursor.rowcount > 0:
            migrated += 1

    # 2. 迁移 learnings
    for learn in brain.get("learnings", []):
        cursor.execute("""
            INSERT OR IGNORE INTO memories (type, title, content, category, importance, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "learning",
            f"{learn.get('topic', 'Unknown')} / {learn.get('subtopic', '')}",
            learn.get("content", ""),
            "learning",
            int(learn.get("difficulty", 5)),
            learn.get("created_at", datetime.now().isoformat()),
            json.dumps({
                "source": "erbing_brain.json",
                "original_id": learn.get("id"),
                "summary": learn.get("summary", ""),
                "tags": learn.get("tags", ""),
                "mastery_level": learn.get("mastery_level", 0)
            })
        ))
        if cursor.rowcount > 0:
            migrated += 1

    # 3. 迁移 skills
    for skill in brain.get("skills", []):
        cursor.execute("""
            INSERT OR IGNORE INTO memories (type, title, content, category, importance, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "skill",
            f"技能: {skill.get('name', 'unknown')}",
            skill.get("description", ""),
            skill.get("category", "tool"),
            5 + skill.get("proficiency_level", 0),
            datetime.now().isoformat(),
            json.dumps({"source": "erbing_brain.json", "proficiency_level": skill.get("proficiency_level", 0)})
        ))
        if cursor.rowcount > 0:
            migrated += 1

    conn.commit()

    # 验证
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]

    conn.close()

    print(f"[OK] 迁移完成: {migrated} 条新记录入库, 总记录数: {total}")
    return migrated

if __name__ == "__main__":
    migrate()