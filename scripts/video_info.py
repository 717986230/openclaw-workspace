#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send videos to Discord
"""

import os
import sys

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("[INFO] Video files are ready!")
print("")
print("[VIDEO 1] Agency Agents Caller")
print(f"  Path: {video1}")
print(f"  Size: {os.path.getsize(video1)} bytes")
print(f"  Message: 179 AI Agents, one-click call! Search agency-agents-caller now!")
print("")
print("[VIDEO 2] Memory System Complete")
print(f"  Path: {video2}")
print(f"  Size: {os.path.getsize(video2)} bytes")
print(f"  Message: AI Memory System, remember everything! Search memory-system-complete now!")
print("")
print("[INFO] Please upload these videos to Discord manually or use the OpenClaw message tool.")
print("[INFO] Videos are located in: C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\")
