#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
List all memory-related files in workspace
"""

import os

workspace = "C:\\Users\\Administrator\\.openclaw\\workspace"

print("=" * 60)
print("MEMORY SYSTEM FILES")
print("=" * 60)
print("")

# Check memory directory
memory_dir = os.path.join(workspace, "memory")
if os.path.exists(memory_dir):
    print("[MEMORY DIRECTORY]")
    for root, dirs, files in os.walk(memory_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, workspace)
            print(f"  {rel_path}")
    print("")

# Check scripts directory
scripts_dir = os.path.join(workspace, "scripts")
if os.path.exists(scripts_dir):
    print("[SCRIPTS DIRECTORY]")
    for file in os.listdir(scripts_dir):
        if "memory" in file.lower() or "palace" in file.lower() or "brain" in file.lower():
            print(f"  scripts/{file}")
    print("")

# Check GBrain files
gbrain_files = [
    "GBRAIN_IMPLEMENTATION_GUIDE.md",
    "GBRAIN_INTEGRATION_REPORT.md"
]
print("[GBRAIN FILES]")
for file in gbrain_files:
    file_path = os.path.join(workspace, file)
    if os.path.exists(file_path):
        print(f"  {file}")
print("")

print("=" * 60)
