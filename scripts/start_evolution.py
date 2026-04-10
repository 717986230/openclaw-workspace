#!/usr/bin/env python3
"""
进化配置启动脚本
自动加载今天的进化配置并启动定时任务
"""

import sqlite3
import json
import schedule
import time
from datetime import datetime

DB_PATH = 'memory/database/xiaozhi_memory.db'

def load_today_evolution_config():
    """从数据库加载今天的进化配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT title, content, importance
        FROM memories
        WHERE type = 'evolution_config'
        AND created_at LIKE ?
        ORDER BY importance DESC
        LIMIT 1
    ''', (f'{today}%',))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'title': result[0],
            'content': result[1],
            'importance': result[2]
        }
    return None

def daily_evolution_check():
    """每日进化检查"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily Evolution Check")

    # 1. 检查数据库记忆系统状态
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM memories')
    total = cursor.fetchone()[0]
    conn.close()

    print(f"  - Memory system: {total} records")

    # 2. 检查进化配置
    config = load_today_evolution_config()
    if config:
        print(f"  - Evolution config: {config['title']}")

    # 3. TODO: 检查友好项目的 GFI

def weekly_review():
    """每周复盘"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Weekly Evolution Review")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 统计本周学习内容
    cursor.execute('''
        SELECT type, COUNT(*) as count
        FROM memories
        WHERE created_at >= datetime('now', '-7 days')
        GROUP BY type
    ''')

    results = cursor.fetchall()
    print("  - This week's learning:")
    for row in results:
        print(f"    {row[0]}: {row[1]} items")

    conn.close()

def main():
    print("=" * 60)
    print("Evolution System Starting...")
    print("=" * 60)

    # 加载今天的进化配置
    config = load_today_evolution_config()
    if config:
        print(f"\nLoaded config: {config['title']}")
        print(f"Importance: {config['importance']}/10")
    else:
        print("\nNo evolution config found for today")

    # 设置定时任务
    schedule.every().day.at("08:00").do(daily_evolution_check)
    schedule.every().sunday.at("20:00").do(weekly_review)

    print("\nScheduled tasks:")
    print("  - Daily check: 08:00")
    print("  - Weekly review: Sunday 20:00")

    print("\nEvolution system running... (Ctrl+C to stop)")

    # 启动调度器
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n\nEvolution system stopped.")

if __name__ == '__main__':
    main()
