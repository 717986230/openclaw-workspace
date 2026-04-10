#!/usr/bin/env python3
"""Force clean all memory markdown files except database/."""

import os
from pathlib import Path

BASE = Path(r"C:\Users\Administrator\.openclaw\workspace\memory")
WORKSPACE = Path(r"C:\Users\Administrator\.openclaw\workspace")

# Protected files (never delete)
PROTECTED = [
    WORKSPACE / "MEMORY.md",
    WORKSPACE / "SOUL.md",
    WORKSPACE / "TOOLS.md",
    WORKSPACE / "AGENTS.md",
    WORKSPACE / "BOOTSTRAP.md",
    WORKSPACE / "USER.md",
    WORKSPACE / "HEARTBEAT.md",
]

deleted = 0
errors = []

# Walk through memory directory
for root, dirs, files in os.walk(BASE):
    # Skip database directory
    if "database" in root:
        continue

    for f in files:
        if f.endswith((".md", ".json")):
            filepath = Path(root) / f
            if filepath not in PROTECTED:
                try:
                    filepath.unlink()
                    deleted += 1
                except Exception as e:
                    errors.append(f"{f}: {e}")

print(f"Deleted {deleted} files")
if errors:
    print(f"Errors: {len(errors)}")
    for e in errors[:5]:
        print(f"  {e}")
