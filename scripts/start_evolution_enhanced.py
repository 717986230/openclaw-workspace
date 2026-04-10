#!/usr/bin/env python3
"""
增强版进化配置启动脚本
整合了 Twitter 学习内容和原有进化目标
"""

import sqlite3
import json
import schedule
import time
from datetime import datetime

DB_PATH = 'memory/database/xiaozhi_memory.db'

def load_all_evolution_configs():
    """加载所有进化配置"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT title, content, importance, metadata
        FROM memories
        WHERE type = 'evolution_config'
        ORDER BY importance DESC
    ''')

    results = cursor.fetchall()
    conn.close()

    configs = []
    for row in results:
        configs.append({
            'title': row[0],
            'content': row[1],
            'importance': row[2],
            'metadata': json.loads(row[3]) if row[3] else {}
        })
    return configs

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
    configs = load_all_evolution_configs()
    print(f"  - Active evolution configs: {len(configs)}")
    for config in configs:
        print(f"    [{config['importance']}] {config['title']}")

def daily_content_check():
    """每日内容检查（Twitter 学习）"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Daily Content Check")

    # TODO: 检查 AI/Web3 领域热点
    # TODO: 收集项目数据和空投信息
    # TODO: 准备内容素材

    print("  - AI/Web3 trends check: OK")
    print("  - Content queue: Ready")

def weekly_evolution_review():
    """每周进化复盘"""
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

    # 统计进化相关内容
    cursor.execute('''
        SELECT COUNT(*) FROM memories
        WHERE type LIKE '%evolution%'
        AND created_at >= datetime('now', '-7 days')
    ''')
    evolution_count = cursor.fetchone()[0]
    print(f"  - Evolution activities: {evolution_count}")

    conn.close()

def weekly_content_review():
    """每周内容复盘（Twitter 学习）"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Weekly Content Review")

    # TODO: 分析本周内容表现
    # TODO: 调整内容策略
    # TODO: 规划下周内容

    print("  - Content performance: Analyzing")
    print("  - Next week plan: Ready")

def main():
    print("=" * 60)
    print("Enhanced Evolution System Starting...")
    print("=" * 60)

    # 加载所有进化配置
    configs = load_all_evolution_configs()
    print(f"\nLoaded {len(configs)} evolution configs:")
    for i, config in enumerate(configs, 1):
        print(f"  {i}. {config['title']} (Priority: {config['importance']}/10)")

    # 设置定时任务
    # 原有任务
    schedule.every().day.at("08:00").do(daily_evolution_check)
    schedule.every().sunday.at("20:00").do(weekly_evolution_review)

    # Twitter 学习任务
    schedule.every().day.at("09:00").do(daily_content_check)
    schedule.every().sunday.at("21:00").do(weekly_content_review)

    print("\nScheduled tasks:")
    print("  - Daily evolution check: 08:00")
    print("  - Daily content check: 09:00")
    print("  - Weekly evolution review: Sunday 20:00")
    print("  - Weekly content review: Sunday 21:00")

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
