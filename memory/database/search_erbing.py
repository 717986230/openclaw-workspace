#!/usr/bin/env python3
"""Search Erbing-1B related memories."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_memory import get_memory

def main():
    mem = get_memory()
    
    print("=== Search: Erbing-1B ===")
    results = mem.search("Erbing-1B 架构", limit=10)
    for r in results:
        print(f"\n- [{r['type']}] {r['title']} (importance: {r['importance']})")
        print(f"  {r['content'][:200]}...")
    
    print("\n\n=== Search: 四策略检索 ===")
    results = mem.search("四策略检索 Phase", limit=5)
    for r in results:
        print(f"\n- [{r['type']}] {r['title']} (importance: {r['importance']})")
        print(f"  {r['content'][:200]}...")
    
    print("\n\n=== Search: 数据库迁移 ===")
    results = mem.search("数据库迁移 方案", limit=5)
    for r in results:
        print(f"\n- [{r['type']}] {r['title']} (importance: {r['importance']})")
        print(f"  {r['content'][:200]}...")

if __name__ == "__main__":
    main()
