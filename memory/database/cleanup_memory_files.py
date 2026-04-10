#!/usr/bin/env python3
"""List and clean up memory markdown files."""

import os
from pathlib import Path

BASE = Path(r"C:\Users\Administrator\.openclaw\workspace\memory")

# Files to DELETE (not in database/)
to_delete = []

# Walk through memory directory
for root, dirs, files in os.walk(BASE):
    # Skip database directory
    if "database" in root:
        continue

    for f in files:
        if f.endswith((".md", ".json")):
            filepath = Path(root) / f
            to_delete.append(filepath)

print("=== Files to DELETE ===")
for f in to_delete:
    print(f"  {f.relative_to(BASE)}")

print(f"\nTotal: {len(to_delete)} files")

# Ask for confirmation
confirm = input("\nDelete these files? (y/n): ")
if confirm.lower() == "y":
    for f in to_delete:
        f.unlink()
        print(f"Deleted: {f.name}")
    print("\nAll files deleted!")
else:
    print("Cancelled")
