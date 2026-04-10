#!/usr/bin/env python3
"""
记忆迁移脚本 - 将所有本地记忆文件导入数据库
执行时间: 2026-04-05
"""

import sqlite3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 数据库路径
DB_PATH = 'memory/database/xiaozhi_memory.db'

# 记忆目录映射
MEMORY_DIRS = {
    'hourly_reports': {'type': 'hourly_report', 'category': 'report', 'importance': 5},
    'learnings': {'type': 'learning', 'category': 'knowledge', 'importance': 7},
    'preferences': {'type': 'preference', 'category': 'config', 'importance': 6},
    'events': {'type': 'event', 'category': 'log', 'importance': 4},
    'skills': {'type': 'skill_note', 'category': 'skill', 'importance': 8},
    'improvements': {'type': 'improvement', 'category': 'todo', 'importance': 7},
}

def import_file(cursor, filepath, mem_type, category, importance):
    """导入单个文件到数据库"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 限制内容长度
        if len(content) > 10000:
            content = content[:10000] + "\n... [truncated]"
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            mem_type,
            Path(filepath).stem,
            content,
            category,
            json.dumps([mem_type, category]),
            importance,
            now,
            now,
            json.dumps({'source_file': str(filepath), 'migrated': True})
        ))
        return True
    except Exception as e:
        print(f"  [FAIL] Failed to import {filepath}: {e}")
        return False

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_imported = 0
    
    for dirname, config in MEMORY_DIRS.items():
        dirpath = Path('memory') / dirname
        if not dirpath.exists():
            print(f"[SKIP] Directory {dirname} not found, skipping")
            continue
        
        files = list(dirpath.glob('*'))
        if not files:
            continue
        
        print(f"\n[DIR] Processing {dirname}: {len(files)} files")
        
        imported = 0
        for fpath in files:
            if fpath.is_file() and fpath.suffix in ['.txt', '.md', '.json']:
                if import_file(cursor, fpath, config['type'], config['category'], config['importance']):
                    imported += 1
        
        conn.commit()
        print(f"  [OK] Imported {imported} files")
        total_imported += imported
    
    conn.close()
    print(f"\n[DONE] Total imported: {total_imported} files to database")

if __name__ == '__main__':
    main()
