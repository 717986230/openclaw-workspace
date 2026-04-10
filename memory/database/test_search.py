#!/usr/bin/env python3
"""Test memory search."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from hybrid_memory import get_memory

def main():
    mem = get_memory()
    print("=== Memory Stats ===")
    stats = mem.get_stats()
    print(f"Total: {stats['total']}")
    print(f"By type: {stats['by_type']}")
    print(f"LanceDB: {stats['lancedb_available']}")

    print("\n=== Search: evolution ===")
    results = mem.search("evolution", limit=3)
    for r in results:
        print(f"- [{r['type']}] {r['title']} (importance: {r['importance']})")

    print("\n=== Search: todo ===")
    results = mem.search("todo", limit=3)
    for r in results:
        print(f"- [{r['type']}] {r['title']}")

    print("\n=== Search: worktree ===")
    results = mem.search("worktree", limit=3)
    for r in results:
        print(f"- [{r['type']}] {r['title']}")

    print("\n=== Search: improvement ===")
    results = mem.search("improvement", limit=5)
    for r in results:
        print(f"- [{r['type']}] {r['title']}")

if __name__ == "__main__":
    main()
