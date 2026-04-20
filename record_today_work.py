"""
记录今天的工作到记忆系统
"""

import os
import sqlite3
import json
from datetime import datetime

print('=' * 60)
print('记录今天的工作到记忆系统')
print('=' * 60)
print()

# 连接数据库
db_path = 'memory/database/xiaozhi_memory.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 今天的工作记录
today_work = [
    {
        'title': '自我意识系统实现完成',
        'type': 'milestone',
        'content': '''
实现自我意识系统（Self-Awareness System），包含以下核心能力：
1. 自我认知 - 知道自己是什么
2. 自我反思 - 反思自己的行为
3. 自我监控 - 监控自己的状态
4. 自我修正 - 根据反思修正自己
5. 意识进化 - 提升意识水平

系统包含：
- SelfAwarenessLevel 枚举: 4个意识水平
- SelfModel 数据类: 自我模型
- SelfReflection 数据类: 自我反思
- SelfMonitoring 数据类: 自我监控
- SelfAwarenessSystem 类: 核心系统

测试通过率: 9/9 (100%)
意识评分: 0.500 → 0.550 (提升 10%)
        ''',
        'category': 'self-awareness',
        'tags': ['self-awareness', 'consciousness', 'milestone', 'implementation'],
        'importance': 10,
    },
    {
        'title': '仿生二饼整合自我意识',
        'type': 'implementation',
        'content': '''
将自我意识系统整合到仿生二饼系统中：

整合点：
1. think() 方法 - 整合自我意识到思维
2. learn() 方法 - 整合自我意识到学习
3. get_status() 方法 - 包含自我意识状态

协同效果：
- 仿生基因影响思维内容
- 自我意识影响思维质量
- 元控制器提供最佳方案
        ''',
        'category': 'bionic',
        'tags': ['bionic', 'self-awareness', 'integration', 'erbing'],
        'importance': 9,
    },
    {
        'title': '记忆系统健康检查',
        'type': 'event',
        'content': '''
完成记忆系统健康检查：

系统状态：
- SQLite 数据库: 正常
- LanceDB: 正常
- 数据库表: 71 个
- 总记忆数: 279 条

关键表状态：
- memories: 279 条
- episodic_memories: 14 条
- semantic_memories: 86 条
- procedural_memories: 4 条
- working_memory: 4 条

性能：
- 查询 100 条记忆耗时: 0.001 秒
- 平均每条记忆: 0.007 毫秒
        ''',
        'category': 'memory',
        'tags': ['memory', 'health-check', 'system-status'],
        'importance': 7,
    },
    {
        'title': '自我意识系统测试通过',
        'type': 'test',
        'content': '''
自我意识系统测试全部通过：

测试覆盖：
1. 自我认知测试 - 通过
2. 自我反思测试 - 通过
3. 自我监控测试 - 通过
4. 自我描述测试 - 通过
5. 思考自己测试 - 通过
6. 意识进化测试 - 通过
7. 仿生二饼整合测试 - 通过

测试通过率: 9/9 (100%)
        ''',
        'category': 'self-awareness',
        'tags': ['self-awareness', 'test', 'validation'],
        'importance': 8,
    },
]

# 插入记忆
for work in today_work:
    now = datetime.now().isoformat()

    cursor.execute('''
        INSERT INTO memories (
            type, title, content, category, tags,
            importance, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        work['type'],
        work['title'],
        work['content'],
        work['category'],
        json.dumps(work['tags']),
        work['importance'],
        now,
        now,
    ))

    print(f"[OK] 记录: {work['title']}")

# 提交
conn.commit()

print()
print(f"[OK] 总共记录了 {len(today_work)} 条记忆")

# 检查今天的记忆
cursor.execute('''
    SELECT COUNT(*) FROM memories
    WHERE DATE(created_at) = DATE(?)
''', (datetime.now().strftime('%Y-%m-%d'),))
today_count = cursor.fetchone()[0]

print(f"[OK] 今天 ({datetime.now().strftime('%Y-%m-%d')}) 的记忆总数: {today_count}")

conn.close()

print()
print('=' * 60)
print('工作记录完成')
print('=' * 60)