#!/usr/bin/env python3
"""Record Phase 1 milestones to database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_memory import get_memory
from datetime import datetime

def main():
    mem = get_memory()
    conn = mem.sqlite_conn
    cursor = conn.cursor()
    
    # Record three important milestones
    milestones = [
        ('milestone', 'Phase 1: 四策略检索系统实现', '实现了四种检索策略：按需归因、时间衰减、重要性优先、向量语义。支持智能组合检索模式。', 'erbing-1b', 'retrieval, phase1, strategy, milestone', 9),
        ('milestone', 'Phase 1: 数据库迁移方案设计', '完成了从文件记忆到数据库优先架构的迁移方案。包括源文件分析、自动类型推断、重要性评估、迁移验证等功能。', 'erbing-1b', 'migration, database, phase1, milestone', 9),
        ('milestone', 'Phase 1: Erbing-1B架构完善', '完善了左右脑架构设计，集成四策略检索系统，设计了数据库优先训练策略，建立了完整的评估指标体系。', 'erbing-1b', 'architecture, dual-brain, phase1, milestone', 9),
    ]
    
    for m in milestones:
        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, m)
    
    conn.commit()
    print('[SUCCESS] Three milestones recorded to database')

if __name__ == "__main__":
    main()
