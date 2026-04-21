#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Douyin Video Publisher Helper
Opens video folder and provides publishing instructions
"""

import os
import subprocess
import webbrowser

# Video files
video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

print("=" * 60)
print("DOUYIN VIDEO PUBLISHER HELPER")
print("=" * 60)
print("")
print("Opening video folder...")
subprocess.Popen(["explorer", "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos"])
print("")
print("Opening Douyin Creator Platform...")
webbrowser.open("https://creator.douyin.com/creator-micro/content/manage")
print("")
print("=" * 60)
print("VIDEO FILES READY")
print("=" * 60)
print("")
print("[VIDEO 1] Agency Agents Caller")
print(f"  File: agency_agents_caller.mp4")
print(f"  Size: {os.path.getsize(video1)} bytes")
print("  Title: 179 AI Agents, one-click call!")
print("  Description: AI Agent calling system with 179 pre-configured agents. Search agency-agents-caller now!")
print("  Tags: #AI #ArtificialIntelligence #Agent #OpenClaw #ClawHub #Programming #DeveloperTools")
print("")
print("[VIDEO 2] Memory System Complete")
print(f"  File: memory_system_complete.mp4")
print(f"  Size: {os.path.getsize(video2)} bytes")
print("  Title: AI Memory System, remember everything!")
print("  Description: Complete AI memory system with ToM, EQ, and enhanced retrieval. Search memory-system-complete now!")
print("  Tags: #AI #ArtificialIntelligence #MemorySystem #OpenClaw #ClawHub #Programming #DeveloperTools")
print("")
print("=" * 60)
print("INSTRUCTIONS")
print("=" * 60)
print("")
print("1. Login to Douyin Creator Platform in your browser")
print("2. Click 'Publish Video' button")
print("3. Upload video files from the opened folder")
print("4. Fill in title, description, and tags")
print("5. Click 'Publish' to upload")
print("")
print("=" * 60)
print("PUBLISHING TIPS")
print("=" * 60)
print("")
print("- Best publishing times: 7:00-9:00, 12:00-13:00, 18:00-22:00")
print("- Use vertical videos (9:16 aspect ratio)")
print("- Add relevant tags and hashtags")
print("- Engage with comments after publishing")
print("- Share to other social platforms")
print("")
print("=" * 60)
print("READY TO PUBLISH!")
print("=" * 60)
print("")
print("Video folder and Douyin Creator Platform are now open.")
print("Please follow the instructions above to publish your videos.")
print("")
input("Press Enter to exit...")
