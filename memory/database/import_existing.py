#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导入现有的文件记忆到数据库
"""

import sqlite3
import json
from pathlib import Path
import sys

# 添加 init_db 的路径
sys.path.insert(0, str(Path(__file__).parent))
from init_db import add_memory, DB_PATH

# 工作区根路径
WORKSPACE = Path(__file__).parent.parent.parent


def import_memory_md():
    """导入 MEMORY.md"""
    memory_md = WORKSPACE / "MEMORY.md"
    if memory_md.exists():
        content = memory_md.read_text(encoding="utf-8")
        add_memory(
            type_="memory",
            title="长期记忆 - MEMORY.md",
            content=content,
            category="core",
            tags=["memory", "core", "long-term"],
            importance=10
        )


def import_events():
    """导入事件日志"""
    events_dir = WORKSPACE / "memory" / "events"
    if events_dir.exists():
        for event_file in events_dir.glob("*.md"):
            content = event_file.read_text(encoding="utf-8")
            add_memory(
                type_="event",
                title=f"事件 - {event_file.stem}",
                content=content,
                category="events",
                tags=["event", event_file.stem],
                importance=8
            )


def import_learnings():
    """导入学习笔记"""
    learnings_dir = WORKSPACE / "memory" / "learnings"
    if learnings_dir.exists():
        for learning_file in learnings_dir.glob("*.md"):
            content = learning_file.read_text(encoding="utf-8")
            add_memory(
                type_="learning",
                title=f"学习 - {learning_file.stem}",
                content=content,
                category="learnings",
                tags=["learning", learning_file.stem],
                importance=7
            )


def import_preferences():
    """导入偏好设置"""
    preferences_dir = WORKSPACE / "memory" / "preferences"
    if preferences_dir.exists():
        for pref_file in preferences_dir.glob("*.md"):
            content = pref_file.read_text(encoding="utf-8")
            add_memory(
                type_="preference",
                title=f"偏好 - {pref_file.stem}",
                content=content,
                category="preferences",
                tags=["preference", pref_file.stem],
                importance=9
            )


def import_improvements():
    """导入改进记录"""
    improvements_md = WORKSPACE / "memory" / "improvements.md"
    if improvements_md.exists():
        content = improvements_md.read_text(encoding="utf-8")
        add_memory(
            type_="improvement",
            title="改进记录 - improvements.md",
            content=content,
            category="improvements",
            tags=["improvement", "history"],
            importance=8
        )


if __name__ == "__main__":
    print(f"[IMPORT] Starting import from files to {DB_PATH}")
    print()

    import_memory_md()
    import_events()
    import_learnings()
    import_preferences()
    import_improvements()

    print()
    print("[DONE] Import complete!")
