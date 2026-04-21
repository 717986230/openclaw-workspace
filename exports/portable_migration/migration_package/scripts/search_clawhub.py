#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search for clawhub related files"""

import os

def find_files(root_dir, pattern):
    """Find files matching pattern"""
    matches = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if pattern.lower() in file.lower():
                matches.append(os.path.join(root, file))
    return matches

# Search for clawhub files
workspace = 'C:/Users/Administrator/.openclaw/workspace'
clawhub_files = find_files(workspace, 'clawhub')

print(f"Found {len(clawhub_files)} clawhub files:")
for f in clawhub_files[:20]:
    print(f"  {f}")
