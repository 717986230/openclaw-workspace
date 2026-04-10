#!/usr/bin/env python3
"""Insert new memories into the database."""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "xiaozhi_memory.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert evolution system memories
    memories = [
        ("learning", "Evolution System Configuration", """
## AI Agent Evolution Configuration

### Core Principles
1. Self-Iteration - Auto-review after each task
2. Memory-Driven - All history from database queries
3. Tool-First - Reuse existing tools before creating new ones
4. Progressive Enhancement - Small iterations, verify and rollback

### Evolution Phases
- Phase 1 (DONE): TodoWrite, Ask, Worktree, Memory, Sessions
- Phase 2 (IN_PROGRESS): Skill discovery, Error learning, Token optimization
- Phase 3 (PLANNED): Predict needs, Auto workflow, Knowledge graph
- Phase 4 (LONG_TERM): Self-modification, Skill creation, Meta-learning

### Triggers
- Periodic: Daily 8:00 self-improving
- Threshold: 50+ sessions cleanup
- Keywords: evolution, optimize, improve
""", "evolution", json.dumps(["evolution", "config", "phases"]), 9),

        ("skill", "TodoWrite Task Tracking", """
## TodoWrite - Task Tracking System

Script: scripts/todo-track.ps1

### Commands
- ./todo-track.ps1 -Action init
- ./todo-track.ps1 -Action add -Task "task"
- ./todo-track.ps1 -Action complete -Index 1
- ./todo-track.ps1 -Action list
- ./todo-track.ps1 -Action archive

### Config
File: memory/preferences/todo-config.json
- autoTrack: true
- showProgress: true
- archiveOnComplete: true
""", "tool", json.dumps(["todo", "tracking", "task"]), 8),

        ("skill", "Ask User Interaction", """
## Ask - User Interaction System

Script: skills/claude-code-features/scripts/ask.ps1

### Modes
- confirm: Yes/No confirmation
- select: Single choice
- multiselect: Multiple choice
- input: Free text

### Usage
./ask.ps1 -Question "Confirm?" -Type confirm
./ask.ps1 -Question "Choose?" -Type select -Options @("A","B")
""", "tool", json.dumps(["ask", "interaction", "user"]), 7),

        ("skill", "Git Worktree Isolation", """
## Worktree Isolation Mode

Script: skills/claude-code-features/scripts/worktree-manage.ps1

### Commands
- ./worktree-manage.ps1 -Action create -Branch "feature"
- ./worktree-manage.ps1 -Action list
- ./worktree-manage.ps1 -Action remove -Path ".worktrees/feature"

### Config
- enabled: true
- branchPrefix: task/
- cleanupOnMerge: true
""", "tool", json.dumps(["worktree", "git", "isolation"]), 7),

        ("learning", "Evolution Cycle Script", """
## Evolution Cycle Script

Script: scripts/evolution-cycle.ps1

### Actions
- full: Complete cycle (analyze, suggest, improve, report)
- analyze: Check current state
- report: Generate report
- improve: Execute improvements

### Output
- Analyzes pending/completed items
- Suggests improvements by priority
- Generates daily report to memory/learnings/
""", "evolution", json.dumps(["evolution", "cycle", "script"]), 8),

        ("improvement", "Claude Code Features Integration", """
## Completed Improvements - 2026-04-02

### 1. TodoWrite Integration
- Problem: Lack of task tracking
- Solution: Created todo-track.ps1
- Result: Can track complex tasks

### 2. Ask User Interaction
- Problem: Limited user interaction
- Solution: Created ask.ps1
- Result: Support confirm/select/multiselect/input

### 3. Worktree Isolation
- Problem: Workspace conflicts
- Solution: Created worktree-manage.ps1
- Result: Parallel development support

### 4. Evolution System
- Problem: No evolution framework
- Solution: Created evolution-config + cycle script
- Result: Clear evolution path
""", "improvement", json.dumps(["completed", "claude-code", "integration"]), 9),

        ("improvement", "Pending Improvements", """
## Pending Improvements - 2026-04-02

### High Priority
- [ ] Auto skill discovery
- [ ] Learn from errors
- [ ] Token optimization

### Medium Priority
- [ ] Multi-agent collaboration
- [ ] Knowledge graph construction
- [ ] Predict user needs

### Low Priority
- [ ] Self-modification
- [ ] Skill creation
- [ ] Cross-domain transfer
""", "improvement", json.dumps(["pending", "priority", "todo"]), 8)
    ]

    for mem in memories:
        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mem[0], mem[1], mem[2], mem[3], mem[4], mem[5], datetime.now().isoformat()))

    conn.commit()
    print(f"Inserted {len(memories)} memories")

    # Query verification
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]
    print(f"Total memories: {total}")

    # Show by type
    cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    main()
