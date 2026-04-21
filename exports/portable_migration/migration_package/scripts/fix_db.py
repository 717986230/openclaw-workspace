
# -*- coding: utf-8 -*-
import sys
import os

# 添加数据库路径
db_path = os.path.join(os.path.dirname(__file__), '..', 'memory', 'database')
sys.path.insert(0, db_path)

try:
    from hybrid_memory import get_memory
    mem = get_memory()
    
    print("=" * 50)
    print("数据库状态")
    print("=" * 50)
    
    stats = mem.get_stats()
    print(f"总记忆数: {stats['total']}")
    print(f"按类型分布: {stats['by_type']}")
    print(f"LanceDB可用: {stats['lancedb_available']}")
    print()
    
    print("最近5条记忆:")
    recent = mem.search("", limit=5)
    for r in recent:
        print(f"  [{r['id']}] {r['type']} - {r['title']} (重要性:{r['importance']})")
    
    print()
    print("[OK] 数据库工作正常！")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

