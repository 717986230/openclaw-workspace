#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作抖音视频 - Memory System Complete (正确版)
"""

import moviepy
from moviepy import ColorClip, TextClip, CompositeVideoClip
import os

def create_memory_system_video():
    """创建Memory System Complete视频"""

    print("[INFO] Creating Memory System Complete video...")

    # 创建输出目录
    output_dir = "output/videos"
    os.makedirs(output_dir, exist_ok=True)

    # 视频参数
    width, height = 1080, 1920  # 抖音竖屏
    duration = 35  # 35秒

    # 创建背景
    background = ColorClip(size=(width, height), color=(45, 52, 54)).with_duration(duration)

    # 场景1: 开场 (0-4秒)
    scene1 = TextClip(
        text="AI记忆系统，让AI记住一切！",
        font_size=80,
        color='#6C5CE7',
        size=(width, height)
    ).with_duration(4).with_position('center')

    # 场景2: 问题展示 (4-10秒)
    scene2 = TextClip(
        text="AI总是忘记上下文？",
        font_size=70,
        color='#FF6B6B',
        size=(width, height)
    ).with_duration(6).with_position('center').with_start(4)

    # 场景3: 解决方案 (10-20秒)
    scene3 = TextClip(
        text="双脑架构：结构化 + 语义搜索",
        font_size=60,
        color='#4ECDC4',
        size=(width, height)
    ).with_duration(10).with_position('center').with_start(10)

    # 场景4: 功能展示 (20-28秒)
    scene4 = TextClip(
        text="ToM心智模型、情感分析、增强检索",
        font_size=50,
        color='#6C5CE7',
        size=(width, height)
    ).with_duration(8).with_position('center').with_start(20)

    # 场景5: Ollama集成 (28-32秒)
    scene5 = TextClip(
        text="支持Ollama本地模型",
        font_size=70,
        color='#FF6B6B',
        size=(width, height)
    ).with_duration(4).with_position('center').with_start(28)

    # 场景6: CTA (32-35秒)
    scene6 = TextClip(
        text="搜索memory-system-complete，立即体验！",
        font_size=45,
        color='#4ECDC4',
        size=(width, height)
    ).with_duration(3).with_position('center').with_start(32)

    # 组合所有场景
    video = CompositeVideoClip([
        background,
        scene1,
        scene2,
        scene3,
        scene4,
        scene5,
        scene6
    ])

    # 输出视频
    output_path = os.path.join(output_dir, "memory_system_complete.mp4")
    video.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        preset='medium'
    )

    print(f"[OK] Video created: {output_path}")
    return output_path

if __name__ == "__main__":
    try:
        create_memory_system_video()
    except Exception as e:
        print(f"[ERROR] Failed to create video: {e}")
        print("[INFO] Please install moviepy: pip install moviepy")
