#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export agents from database to JSON
"""

import sqlite3
import json
import os

def export_agents(db_path: str, output_path: str):
    """导出所有Agent到JSON文件"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询所有Agent
    cursor.execute('SELECT * FROM agent_prompts')
    columns = [description[0] for description in cursor.description]

    agents = []
    for row in cursor.fetchall():
        agent = dict(zip(columns, row))
        # 解析JSON字段
        if agent.get('metadata'):
            agent['metadata'] = json.loads(agent['metadata'])
        agents.append(agent)

    # 保存到JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"Exported {len(agents)} agents to {output_path}")
    return agents

if __name__ == "__main__":
    db_path = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'
    output_path = 'C:/Users/Administrator/.openclaw/workspace/skills/agency-agents-caller/data/agents.json'

    # 创建data目录
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 导出
    agents = export_agents(db_path, output_path)

    # 统计
    categories = {}
    for agent in agents:
        cat = agent.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\nTotal agents: {len(agents)}")
    print(f"\nBy category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
