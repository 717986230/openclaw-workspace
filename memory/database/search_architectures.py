#!/usr/bin/env python3
"""Search for agent architectures and extensions."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_memory import get_memory

def main():
    mem = get_memory()

    print("=== Search: agent architecture cognitive ===")
    results = mem.search('agent architecture cognitive', limit=10)
    for r in results[:5]:
        print(f"- [{r['type']}] {r['title']}")

    print("\n=== Search: framework extension system ===")
    results2 = mem.search('framework extension', limit=10)
    for r in results2[:5]:
        print(f"- [{r['type']}] {r['title']}")

if __name__ == "__main__":
    main()
