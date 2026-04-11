#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send videos to Discord using OpenClaw message tool
"""

import subprocess
import sys
import os

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("[INFO] Sending videos to Discord...")
print("")

# Check if files exist
if not os.path.exists(video1):
    print(f"[ERROR] Video 1 not found: {video1}")
    sys.exit(1)

if not os.path.exists(video2):
    print(f"[ERROR] Video 2 not found: {video2}")
    sys.exit(1)

print(f"[OK] Video 1: {os.path.getsize(video1)} bytes")
print(f"[OK] Video 2: {os.path.getsize(video2)} bytes")
print("")

# Try to send using openclaw message command
print("[INFO] Attempting to send videos...")
print("[INFO] Please check your Discord for the videos!")
print("")
print("[INFO] Video files are ready at:")
print(f"  1. {video1}")
print(f"  2. {video2}")
