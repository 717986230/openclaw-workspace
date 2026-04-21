#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send videos to Discord using OpenClaw message tool
"""

import subprocess
import sys

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("[INFO] Sending videos to Discord...")
print("")

# Send video 1
print("[INFO] Sending video 1: Agency Agents Caller")
try:
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "discord", "--file", video1,
         "--message", "179 AI Agents, one-click call! Search agency-agents-caller now!"],
        capture_output=True,
        text=True
    )
    print(f"[OK] Video 1 sent: {result.stdout}")
except Exception as e:
    print(f"[ERROR] Failed to send video 1: {e}")

print("")

# Send video 2
print("[INFO] Sending video 2: Memory System Complete")
try:
    result = subprocess.run(
        ["openclaw", "message", "send", "--channel", "discord", "--file", video2,
         "--message", "AI Memory System, remember everything! Search memory-system-complete now!"],
        capture_output=True,
        text=True
    )
    print(f"[OK] Video 2 sent: {result.stdout}")
except Exception as e:
    print(f"[ERROR] Failed to send video 2: {e}")

print("")
print("[OK] All videos sent to Discord!")
