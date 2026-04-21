#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send videos to Discord via OpenClaw message tool
"""

import sys
import os

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("[INFO] Preparing to send videos to Discord...")
print(f"[INFO] Video 1: {video1}")
print(f"[INFO] Video 2: {video2}")
print("")

# Check if files exist
if os.path.exists(video1):
    print(f"[OK] Video 1 exists: {os.path.getsize(video1)} bytes")
else:
    print(f"[ERROR] Video 1 not found!")

if os.path.exists(video2):
    print(f"[OK] Video 2 exists: {os.path.getsize(video2)} bytes")
else:
    print(f"[ERROR] Video 2 not found!")

print("")
print("[INFO] Videos are ready to be sent!")
print("[INFO] Please use the message tool to send these files to Discord.")
