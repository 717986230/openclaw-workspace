#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent调用系统 - 从agent_prompts表加载179个Agent
"""
import sqlite3
import json
from typing import List, Dict, Optional

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

class AgentCaller:
    """Agent调用器"""
    
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
    
    def list_all_agents(self, limit: int = 20) -> List[Dict]:
        """列出所有可用的Agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, category, description, emoji, color, tools, vibe
            FROM agent_prompts
            ORDER BY id
            LIMIT ?
        ''', (limit,))
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'id': row['id'],
                'name': row['name'],
                'category': row['category'],
                'description': row['description'],
                'emoji': row['emoji'],
                'color': row['color'],
                'tools': row['tools'],
                'vibe': row['vibe']
            })
        
        return agents
    
    def search_agents(self, keyword: str) -> List[Dict]:
        """搜索Agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, category, description, emoji, tools
            FROM agent_prompts
            WHERE name LIKE ? OR description LIKE ? OR category LIKE ?
            ORDER BY name
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'id': row['id'],
                'name': row['name'],
                'category': row['category'],
                'description': row['description'],
                'emoji': row['emoji'],
                'tools': row['tools']
            })
        
        return agents
    
    def get_agent_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取Agent完整信息"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM agent_prompts
            WHERE name LIKE ?
            LIMIT 1
        ''', (f'%{name}%',))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_agents_by_category(self, category: str) -> List[Dict]:
        """根据分类获取Agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, name, category, description, emoji
            FROM agent_prompts
            WHERE category = ?
            ORDER BY name
        ''', (category,))
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                'id': row['id'],
                'name': row['name'],
                'category': row['category'],
                'description': row['description'],
                'emoji': row['emoji']
            })
        
        return agents
    
    def get_random_agent(self) -> Optional[Dict]:
        """随机获取一个Agent"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM agent_prompts
            ORDER BY RANDOM()
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def count_agents(self) -> int:
        """统计Agent数量"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM agent_prompts")
        return cursor.fetchone()[0]
    
    def get_categories(self) -> List[str]:
        """获取所有Agent分类"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT category
            FROM agent_prompts
            WHERE category IS NOT NULL
            ORDER BY category
        ''')
        
        return [row[0] for row in cursor.fetchall()]
    
    def get_agent_full_prompt(self, agent_id: int) -> Optional[str]:
        """获取Agent的完整prompt"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT full_content FROM agent_prompts
            WHERE id = ?
        ''', (agent_id,))
        
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    
    def close(self):
        self.conn.close()

# CLI接口
if __name__ == "__main__":
    import sys
    
    caller = AgentCaller()
    
    print("="*70)
    print("Agent Caller System - 179 Agents Available")
    print("="*70)
    
    # 统计信息
    total = caller.count_agents()
    print(f"\nTotal Agents: {total}")
    
    # 获取分类
    categories = caller.get_categories()
    print(f"\nCategories ({len(categories)}): {', '.join(categories[:10])}")
    
    # 根据参数执行不同操作
    if len(sys.argv) > 1:
        keyword = sys.argv[1]
        
        if keyword == '--random':
            # 随机获取一个Agent
            agent = caller.get_random_agent()
            if agent:
                print(f"\nRandom Agent:")
                print(f"  Name: {agent['name']}")
                print(f"  Category: {agent['category']}")
                print(f"  Description: {agent['description']}")
                print(f"  Tools: {agent['tools']}")
                print(f"\nFull Prompt (first 500 chars):")
                print(agent['full_content'][:500] if agent.get('full_content') else 'N/A')
        
        elif keyword == '--categories':
            # 显示所有分类及其Agent数量
            print("\nAgents by Category:")
            for category in categories:
                agents = caller.get_agents_by_category(category)
                print(f"  {category}: {len(agents)} agents")
        
        else:
            # 搜索Agent
            print(f"\nSearching for: {keyword}")
            agents = caller.search_agents(keyword)
            print(f"Found: {len(agents)} agents")
            
            for agent in agents[:10]:
                print(f"\n- {agent['name']} ({agent['category']})")
                print(f"  {agent['description']}")
    
    else:
        # 显示前20个Agent
        print("\nFirst 20 Agents:")
        agents = caller.list_all_agents(20)
        
        for i, agent in enumerate(agents, 1):
            emoji = agent['emoji'] if agent['emoji'] else ''
            print(f"\n{i}. {agent['name']} ({agent['category']})")
            print(f"   {agent['description'][:80]}...")
    
    caller.close()
