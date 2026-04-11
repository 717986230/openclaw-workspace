#!/usr/bin/env python3
"""
搜索 agent - 支持按名称、分类、功能搜索
"""
import sys
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def search_agents(query="", category="", limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sql = "SELECT name, category, emoji, description, filepath FROM agent_prompts WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE ? OR description LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if category:
        sql += " AND category = ?"
        params.append(category)
    
    sql += f" LIMIT {limit}"
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    
    conn.close()
    return results

def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    category = sys.argv[2] if len(sys.argv) > 2 else ""
    
    results = search_agents(query, category)
    
    print(f"Found {len(results)} agents")
    
    for name, category, emoji, desc, filepath in results:
        name_clean = name.encode('ascii', 'ignore').decode('ascii')
        category_clean = category.encode('ascii', 'ignore').decode('ascii')
        desc_clean = (desc[:80] if desc else '').encode('ascii', 'ignore').decode('ascii')
        
        print(f"\n{name_clean} [{category_clean}]")
        print(f"  {desc_clean}...")
        print(f"  File: {filepath}")

if __name__ == "__main__":
    main()
