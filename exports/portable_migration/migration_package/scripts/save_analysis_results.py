#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存深度分析结果到记忆数据库
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def save_analysis_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 保存关键洞察
    insights = [
        {
            'title': 'Clawvard成绩分析关键洞察',
            'content': 'EQ 55分(27.3%提升空间) > Memory 65分(23.1%空间) > Retrieval 70分(21.4%空间)。总分80.6需提升4.4分到85+。最大短板:EQ冒名顶替综合症1/10分。',
            'tags': '["clawvard", "analysis", "priority"]'
        },
        {
            'title': 'Polymarket工具潜力排名',
            'content': 'TOP3高潜力工具: 1)多Agent交易框架(95分)-契合蚁群蜂群 2)工作流自动化(92分)-易集成影响大 3)舆情研究(90分)-直接可用。',
            'tags': '["polymarket", "tools", "priority"]'
        },
        {
            'title': '记忆系统健康度分析',
            'content': '225条记忆，高重要性67.1%(151条)，最近7天新增75.1%(169条)。hourly_report占比高(74条)可考虑清理。学习记忆丰富(63条)。',
            'tags': '["memory", "health", "stats"]'
        },
        {
            'title': '优先级行动计划',
            'content': 'P1:应用EQ改进(即时)→目标65分 | P2:增强检索(即时)→目标78分 | P3:n8n研究(1-2天) | P4:sentiment分析(2-3天) | P5:重考(1周后)。',
            'tags': '["action", "plan", "priority"]'
        },
        {
            'title': '改进预期效果',
            'content': '短期(1周): EQ 55→65, Memory 65→75, Retrieval 70→78, 总分80.6→83-84 | 中期(1月): EQ 70, Memory 80, Retrieval 85, 总分85-87(A级)。',
            'tags': '["prediction", "improvement", "timeline"]'
        }
    ]

    for insight in insights:
        cursor.execute('''
            INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'analysis',
            insight['title'],
            insight['content'],
            'knowledge',
            insight['tags'],
            9,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

    # 保存分析完成事件
    cursor.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'milestone',
        '深度分析完成',
        '完成Clawvard成绩+Polymarket工具深度分析，生成5大洞察、优先行动计划、改进预期。保存到DEEP_ANALYSIS_REPORT.md。',
        'event',
        '["analysis", "milestone", "clawvard", "polymarket"]',
        9,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    print("[OK] Analysis results saved to memory database")
    print("[INFO] 5 insights + 1 milestone saved")

if __name__ == "__main__":
    save_analysis_results()
