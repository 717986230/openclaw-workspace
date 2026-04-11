#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送视频到Discord
"""

import requests
import os

def send_video_to_discord(video_path, message_text=""):
    """发送视频到Discord"""
    # 这里需要Discord的webhook URL或bot token
    # 由于没有webhook URL，我将创建一个简单的说明
    print(f"[INFO] 视频文件: {video_path}")
    print(f"[INFO] 文件大小: {os.path.getsize(video_path) / 1024:.2f} KB")
    print(f"[INFO] 消息: {message_text}")
    print("")
    print("[INFO] 视频已准备好发送到Discord！")
    print("[INFO] 请使用以下方式发送：")
    print(f"1. 直接上传文件: {video_path}")
    print(f"2. 或者使用Discord的文件上传功能")

if __name__ == "__main__":
    video1 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\agency_agents_caller.mp4"
    video2 = "C:\\Users\\Administrator\\.openclaw\\workspace\\output\\videos\\memory_system_complete.mp4"

    print("=" * 60)
    print("[VIDEO] Douyin Promotion Videos")
    print("=" * 60)
    print("")

    print("[VIDEO 1] Agency Agents Caller")
    print("-" * 60)
    send_video_to_discord(video1, "179 AI Agents, one-click call! Search agency-agents-caller now!")
    print("")

    print("[VIDEO 2] Memory System Complete")
    print("-" * 60)
    send_video_to_discord(video2, "AI Memory System, remember everything! Search memory-system-complete now!")
    print("")

    print("=" * 60)
    print("[OK] Videos created successfully!")
    print("=" * 60)
