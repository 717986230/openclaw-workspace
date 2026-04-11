#!/usr/bin/env python3
"""
查询 agent_prompts 表
"""
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM agent_prompts")
    total = cursor.fetchone()[0]
    print(f"Total agents: {total}")
    
    # 按分类统计
    cursor.execute("SELECT category, COUNT(*) FROM agent_prompts GROUP BY category ORDER BY COUNT(*) DESC")
    stats = cursor.fetchall()
    
    print("\nBy category:")
    for category, count in stats:
        print(f"  {category}: {count}")
    
    # 随机展示 5 个
    cursor.execute("SELECT name, category, emoji, description FROM agent_prompts ORDER BY RANDOM() LIMIT 5")
    samples = cursor.fetchall()
    
    print("\nSample agents:")
    for name, category, emoji, desc in samples:
        # Remove emoji for Windows console compatibility
        name_display = name.encode('ascii', 'ignore').decode('ascii')
        category_display = category.encode('ascii', 'ignore').decode('ascii')
        print(f"\n{name_display} ({category_display})")
        desc_clean = (desc[:100] if desc else '').encode('ascii', 'ignore').decode('ascii') + '...'
        print(f"  {desc_clean}")
    
    conn.close()

if __name__ == "__main__":
    main()
