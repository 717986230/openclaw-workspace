#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作抖音视频 - Agency Agents Caller (修正版)
"""

import moviepy
from moviepy import ColorClip, TextClip, CompositeVideoClip
import os

def create_agency_agents_video():
    """创建Agency Agents Caller视频"""

    print("[INFO] Creating Agency Agents Caller video...")

    # 创建输出目录
    output_dir = "output/videos"
    os.makedirs(output_dir, exist_ok=True)

    # 视频参数
    width, height = 1080, 1920  # 抖音竖屏
    duration = 30  # 30秒

    # 创建黑色背景
    background = ColorClip(size=(width, height), color=(26, 26, 46))

    # 场景1: 开场 (0-3秒)
    scene1 = TextClip(
        text="179个AI Agent，一键调用！",
        font_size=80,
        color='#FF6B6B',
        font='SimHei-Bold',
        size=(width, height)
    ).set_duration(3).set_position('center')

    # 场景2: 问题展示 (3-8秒)
    scene2 = TextClip(
        text="代码审查、架构设计、增长黑客...",
        font_size=60,
        color='#4ECDC4',
        font='SimHei',
        size=(width, height)
    ).set_duration(5).set_position('center')

    # 场景3: 功能展示 (8-18秒)
    scene3 = TextClip(
        text="搜索、浏览、随机推荐",
        font_size=70,
        color='#6C5CE7',
        font='SimHei-Bold',
        size=(width, height)
    ).set_duration(10).set_position('center')

    # 场景4: 多Agent协作 (18-23秒)
    scene4 = TextClip(
        text="多Agent协作，效率翻倍",
        font_size=70,
        color='#FF6B6B',
        font='SimHei-Bold',
        size=(width, height)
    ).set_duration(5).set_position('center')

    # 场景5: CTA (23-30秒)
    scene5 = TextClip(
        text="搜索agency-agents-caller，立即体验！",
        font_size=50,
        color='#4ECDC4',
        font='SimHei',
        size=(width, height)
    ).set_duration(7).set_position('center')

    # 组合所有场景
    scenes = [
        scene1,
        scene2,
        scene3,
        scene4,
        scene5
    ]

    # 创建视频
    video = CompositeVideoClip([
        background.set_duration(duration),
        *scenes
    ])

    # 输出视频
    output_path = os.path.join(output_dir, "agency_agents_caller.mp4")
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
        create_agency_agents_video()
    except Exception as e:
        print(f"[ERROR] Failed to create video: {e}")
        print("[INFO] Please install moviepy: pip install moviepy")
