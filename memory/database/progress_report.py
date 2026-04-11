#!/usr/bin/env python3
"""Progress report generator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from hybrid_memory import get_memory

def main():
    mem = get_memory()
    conn = mem.sqlite_conn
    cursor = conn.cursor()

    # Stats
    cursor.execute("SELECT COUNT(*) FROM memories")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT type, COUNT(*) as cnt FROM memories GROUP BY type ORDER BY cnt DESC")
    by_type = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM memories WHERE importance >= 8")
    high_importance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM memories WHERE category LIKE '%erbing%'")
    erbing_projects = cursor.fetchone()[0]

    print("="*60)
    print("ERBING PROJECT - PROGRESS REPORT")
    print("="*60)
    print(f"\n[DATABASE] Total memories: {total}")
    print(f"[DATABASE] High importance: {high_importance}")
    print(f"[DATABASE] Erbing projects: {erbing_projects}")
    print(f"\n[BY TYPE]:")
    for t, c in by_type[:10]:
        print(f"  {t}: {c}")

if __name__ == "__main__":
    main()
