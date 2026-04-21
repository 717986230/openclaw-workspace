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
    'brain.js 神经网络记忆系统整合完成',
    'brain.js 1.6.1 已整合进记忆系统，日常稳定调用。'
    'nn_bridge.py（纯numpy，无需外部ML依赖）：ImportancePredictor预测重要性、MemoryTagger自动打标签。'
    'nn_eval_quick.js（Node.js brain.js）：意图分类+重要性评估，Python通过subprocess调用。'
    'nn_memory_bridge.py：Python端桥接层。'
    '意图分类测试准确，重要性预测效果良好。git commit 771da7f2。',
    'knowledge',
    '["brain.js","neural-network","memory","integration","importance","intent-classification"]',
    9,
    now,
    now
))
conn.commit()
print(f'saved, id={cursor.lastrowid}')
conn.close()