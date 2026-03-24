
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用数据库大脑搜索
"""

import sys
from pathlib import Path

# 添加 database 目录到路径
db_path = Path(__file__).parent.parent / "memory" / "database"
sys.path.insert(0, str(db_path))

from hybrid_memory import get_memory

def search_memory(query, limit=5):
    """搜索记忆"""
    mem = get_memory()
    
    print(f"📊 当前记忆统计: {mem.get_stats()}")
    print(f"\n🔍 搜索: '{query}'")
    
    results = mem.search(query, limit=limit)
    
    if results:
        print(f"\n✅ 找到 {len(results)} 条结果:")
        for i, r in enumerate(results, 1):
            print(f"\n{i}. {r['title']}")
            print(f"   类型: {r['type']} | 重要性: {r['importance']}")
            print(f"   标签: {r.get('tags', [])}")
            if r.get('content'):
                preview = r['content'][:100] + "..." if len(r['content']) > 100 else r['content']
                print(f"   摘要: {preview}")
    else:
        print("\n❌ 没有找到结果")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Pinchtab"
    search_memory(query)

