#!/usr/bin/env python3
"""
保存Polymarket交易工具学习内容到记忆数据库
"""
import sqlite3
from datetime import datetime

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def save_polymarket_learning():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 保存10个GitHub项目
    projects = [
        {
            "name": "预测市场回测框架",
            "url": "github.com/evan-kolberg/p",
            "function": "基于Polymarket与Kalshi真实历史数据，回测交易策略"
        },
        {
            "name": "多智能体交易框架",
            "url": "github.com/TauricResearch",
            "function": "快速搭建完整的AI交易系统"
        },
        {
            "name": "近30天舆情研究工具",
            "url": "github.com/mvanhorn/last3",
            "function": "自动分析过去30天新闻、社交动态与预测市场数据"
        },
        {
            "name": "Polymarket辅助交易工具",
            "url": "github.com/FiatFiorino/po",
            "function": "提供市场趋势指标，辅助判断行情方向"
        },
        {
            "name": "网页数据清洗工具",
            "url": "github.com/firecrawl/fire",
            "function": "将任意网页转换为干净可用的结构化数据"
        },
        {
            "name": "生产级AI智能体框架",
            "url": "github.com/pydantic/pydan",
            "function": "用于搭建可上线运行的交易机器人"
        },
        {
            "name": "工作流自动化平台",
            "url": "github.com/n8n-io/n8n",
            "function": "用于新闻分析、信息筛选与自动化流程搭建"
        },
        {
            "name": "Tavily MCP服务端",
            "url": "github.com/tavily-ai/tavi",
            "function": "内置专业检索能力的AI搜索服务"
        },
        {
            "name": "钱包数据采集与分析器",
            "url": "github.com/txbabaxyz/coll",
            "function": "抓取任意钱包的完整交易历史并进行分析"
        },
        {
            "name": "币安数据采集与预测工具",
            "url": "github.com/txbabaxyz/mlmo",
            "function": "预测市场走势，计算资产合理估值"
        }
    ]

    for project in projects:
        cursor.execute('''
            INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'learning',
            f'Polymarket工具: {project["name"]}',
            f'{project["function"]}\nGitHub: {project["url"]}',
            'knowledge',
            '["polymarket", "trading", "github", "tool"]',
            7,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

    # 保存来源信息
    cursor.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'event',
        '学习Polymarket交易工具',
        '从Twitter @DtDt666 学习了10个Polymarket交易相关的GitHub开源项目，包括回测框架、多Agent系统、舆情分析等工具',
        'event',
        '["polymarket", "twitter", "learning", "github"]',
        8,
        datetime.now().isoformat(),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    print("[OK] Polymarket learning saved to memory database")
    print(f"[INFO] 10 projects + 1 event saved")

if __name__ == "__main__":
    save_polymarket_learning()
