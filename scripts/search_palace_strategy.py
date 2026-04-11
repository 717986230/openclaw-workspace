#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Search for palace and strategy related files in workspace
"""

import os
import re

workspace = "C:\\Users\\Administrator\\.openclaw\\workspace"

print("=" * 60)
print("SEARCHING FOR PALACE AND STRATEGY FILES")
print("=" * 60)
print("")

# Search terms
search_terms = [
    "palace",
    "strategy",
    "strategies",
    "四条",
    "宫殿",
    "memory palace",
    "four strategies",
    "4 strategies"
]

found_files = []

# Walk through all files
for root, dirs, files in os.walk(workspace):
    for file in files:
        if file.endswith(('.md', '.txt', '.py', '.json')):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for term in search_terms:
                        if term.lower() in content.lower():
                            found_files.append((file_path, term))
                            break
            except Exception as e:
                pass

if found_files:
    print(f"Found {len(found_files)} files containing search terms:")
    print("")
    for file_path, term in found_files:
        print(f"[{term.upper()}]")
        print(f"  File: {file_path}")
        print("")
else:
    print("No files found containing search terms")

print("=" * 60)
print("SEARCH COMPLETE")
print("=" * 60)
