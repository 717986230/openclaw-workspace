#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send videos to Discord using OpenClaw
"""

import os
import sys

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("=" * 60)
print("DISCORD VIDEO UPLOAD")
print("=" * 60)
print("")
print("Video files are ready to be sent to Discord!")
print("")
print("[VIDEO 1] Agency Agents Caller")
print(f"  File: {video1}")
print(f"  Size: {os.path.getsize(video1)} bytes")
print(f"  Message: 179 AI Agents, one-click call! Search agency-agents-caller now!")
print("")
print("[VIDEO 2] Memory System Complete")
print(f"  File: {video2}")
print(f"  Size: {os.path.getsize(video2)} bytes")
print(f"  Message: AI Memory System, remember everything! Search memory-system-complete now!")
print("")
print("=" * 60)
print("INSTRUCTIONS")
print("=" * 60)
print("")
print("To send these videos to Discord:")
print("")
print("1. Open Discord")
print("2. Navigate to your channel")
print("3. Click the '+' button to upload files")
print("4. Select the video files from:")
print(f"   - {video1}")
print(f"   - {video2}")
print("5. Add the corresponding message for each video")
print("")
print("Or use OpenClaw message tool if available.")
print("")
print("=" * 60)
