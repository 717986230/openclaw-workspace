#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化设计模式数据库
"""

import sqlite3
import json
from pathlib import Path

# 数据库路径
DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
SCHEMA_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/design_patterns_schema.sql"

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 读取并执行 SQL
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        sql = f.read()
        cursor.executescript(sql)

    conn.commit()
    conn.close()
    print("Database tables created successfully")

def insert_sample_data():
    """插入示例数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 示例设计系统
    design_systems = [
        ("claude", "ai", "https://claude.ai", "Anthropic's AI assistant. Warm terracotta accent, clean editorial layout"),
        ("vercel", "devtools", "https://vercel.com", "Frontend deployment platform. Black and white precision, Geist font"),
        ("linear", "productivity", "https://linear.app", "Project management for engineers. Ultra-minimal, precise, purple accent"),
        ("stripe", "fintech", "https://stripe.com", "Payment infrastructure. Signature purple gradients, weight-300 elegance"),
        ("apple", "media", "https://apple.com", "Consumer electronics. Premium white space, SF Pro, cinematic imagery"),
    ]

    for name, category, url, description in design_systems:
        cursor.execute("""
            INSERT OR IGNORE INTO design_systems (name, category, url, description)
            VALUES (?, ?, ?, ?)
        """, (name, category, url, description))

    # 示例色彩系统
    color_palettes = [
        ("claude", "primary", "primary", "#D97757", "Warm terracotta for brand and CTAs"),
        ("claude", "neutral", "neutral-50", "#FAFAFA", "Light background"),
        ("vercel", "primary", "primary", "#000000", "Black for primary actions"),
        ("vercel", "neutral", "neutral-50", "#FAFAFA", "Light background"),
        ("linear", "primary", "primary", "#5E6AD2", "Purple accent for brand"),
        ("linear", "neutral", "neutral-50", "#FAFAFA", "Light background"),
        ("stripe", "primary", "primary", "#635BFF", "Purple gradient for brand"),
        ("stripe", "neutral", "neutral-50", "#FAFAFA", "Light background"),
    ]

    for name, role, color_name, hex_value, usage in color_palettes:
        cursor.execute("""
            INSERT OR IGNORE INTO color_palettes (design_system_id, role, name, hex, usage)
            SELECT id, ?, ?, ?, ?
            FROM design_systems WHERE name = ?
        """, (role, color_name, hex_value, usage, name))

    # 示例排版系统
    typography_systems = [
        ("claude", "sans-serif", "Inter", "16px", "400", "1.5", "0", "Body text"),
        ("vercel", "sans-serif", "Geist", "16px", "400", "1.5", "0", "Body text"),
        ("linear", "sans-serif", "Inter", "16px", "400", "1.5", "0", "Body text"),
        ("apple", "sans-serif", "SF Pro Display", "17px", "400", "1.47", "0", "Body text"),
    ]

    for name, font_type, font_family, font_size, font_weight, line_height, letter_spacing, usage in typography_systems:
        cursor.execute("""
            INSERT OR IGNORE INTO typography_systems (design_system_id, font_family, font_type, font_size, font_weight, line_height, letter_spacing, usage)
            SELECT id, ?, ?, ?, ?, ?, ?, ?
            FROM design_systems WHERE name = ?
        """, (font_family, font_type, font_size, font_weight, line_height, letter_spacing, usage, name))

    # 示例设计标签
    design_tags = [
        ("claude", "warm"),
        ("claude", "editorial"),
        ("claude", "clean"),
        ("vercel", "minimal"),
        ("vercel", "monochrome"),
        ("vercel", "precise"),
        ("linear", "ultra-minimal"),
        ("linear", "purple"),
        ("linear", "precise"),
        ("stripe", "gradient"),
        ("stripe", "purple"),
        ("stripe", "elegant"),
        ("apple", "premium"),
        ("apple", "white-space"),
        ("apple", "cinematic"),
    ]

    for name, tag in design_tags:
        cursor.execute("""
            INSERT OR IGNORE INTO design_tags (design_system_id, tag)
            SELECT id, ?
            FROM design_systems WHERE name = ?
        """, (tag, name))

    conn.commit()
    conn.close()
    print("Sample data inserted successfully")

if __name__ == "__main__":
    init_database()
    insert_sample_data()
    print("\nDatabase initialization complete!")
    print(f"Database location: {DB_PATH}")
