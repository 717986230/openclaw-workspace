#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent调用示例 - 演示如何使用179个Agent
"""
import sqlite3
import json

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def demo_agent_usage():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("="*70)
    print("Agent调用示例")
    print("="*70)
    
    # 示例1: 按分类浏览
    print("\n[示例1] 按分类浏览Agent:")
    print("-" * 70)
    
    categories = ['engineering', 'marketing', 'specialized', 'strategy']
    for category in categories:
        cursor.execute('''
            SELECT name, description FROM agent_prompts
            WHERE category = ?
            LIMIT 3
        ''', (category,))
        
        agents = cursor.fetchall()
        if agents:
            print(f"\n{category.upper()} ({len(agents)} examples):")
            for agent in agents:
                print(f"  - {agent['name']}: {agent['description'][:60]}...")
    
    # 示例2: 搜索特定功能的Agent
    print("\n\n[示例2] 搜索'数据'相关Agent:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT name, category, description
        FROM agent_prompts
        WHERE description LIKE '%data%' OR name LIKE '%Data%'
        LIMIT 10
    ''')
    
    for agent in cursor.fetchall():
        print(f"  {agent['name']} ({agent['category']})")
        print(f"    {agent['description'][:80]}...")
    
    # 示例3: 获取特定Agent的详细信息
    print("\n\n[示例3] 获取'Backend Architect'详细信息:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT * FROM agent_prompts
        WHERE name = 'Backend Architect'
        LIMIT 1
    ''')
    
    agent = cursor.fetchone()
    if agent:
        print(f"Name: {agent['name']}")
        print(f"Category: {agent['category']}")
        print(f"Description: {agent['description']}")
        print(f"Tools: {agent['tools']}")
        print(f"Vibe: {agent['vibe']}")
        
        # 保存完整prompt到文件
        if agent['full_content']:
            with open('C:/Users/Administrator/.openclaw/workspace/scripts/backend_architect_prompt.md', 'w', encoding='utf-8') as f:
                f.write(agent['full_content'])
            print("\nFull prompt saved to: backend_architect_prompt.md")
    
    # 示例4: 统计信息
    print("\n\n[示例4] Agent统计:")
    print("-" * 70)
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM agent_prompts
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    print("\nAgents by Category:")
    for row in cursor.fetchall():
        print(f"  {row['category']}: {row['count']} agents")
    
    conn.close()
    
    print("\n" + "="*70)
    print("调用方式:")
    print("="*70)
    print("""
# 在代码中使用:
from scripts.agent_caller import AgentCaller

caller = AgentCaller()

# 1. 搜索Agent
agents = caller.search_agents('data')

# 2. 获取特定Agent
agent = caller.get_agent_by_name('Backend Architect')

# 3. 按分类获取
engineering_agents = caller.get_agents_by_category('engineering')

# 4. 随机获取
random_agent = caller.get_random_agent()

# 5. 获取完整prompt
prompt = caller.get_agent_full_prompt(agent_id)

# 使用Agent的prompt
if agent:
    print(f"Using {agent['name']}...")
    # 将agent['full_content']传递给LLM
""")

if __name__ == "__main__":
    demo_agent_usage()
