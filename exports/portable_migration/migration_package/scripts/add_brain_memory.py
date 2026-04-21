#!/usr/bin/env python3
import sqlite3
from datetime import datetime

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'
now = datetime.now().isoformat()

conn = sqlite3.connect(DB)
cursor = conn.cursor()
cursor.execute('''
INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'learning',
    'brain.js 1.6.1 整合完成',
    '完成 brain.js 与 workspace 的整合。版本选择 1.6.1（纯 JS，无原生依赖）。'
    'v2 beta 因依赖 gl 原生模块（需 Visual Studio）被放弃，synaptic 作为备选。'
    '新建 lib/ 目录：brain_integration.js（统一入口）、train.js（训练脚手架）、demo.js（5个demo）。'
    '更新 scripts/brain_lib.js 桥接旧 API。已提交 git commit 7dbbd9dd。',
    'knowledge',
    '["brain.js","neural-network","integration","npm","synaptic"]',
    8,
    now,
    now
))
conn.commit()
print(f'saved, id={cursor.lastrowid}')
conn.close()