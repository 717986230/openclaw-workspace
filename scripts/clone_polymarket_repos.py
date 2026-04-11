#!/usr/bin/env python3
"""
克隆Polymarket交易工具的GitHub仓库
"""
import subprocess
import os

BASE_DIR = "C:/Users/Administrator/.openclaw/workspace/polymarket-tools"

repos = [
    {
        "name": "prediction-market-backtest",
        "url": "https://github.com/evan-kolberg/prediction-market-backtest-framework",
        "description": "预测市场回测框架"
    },
    {
        "name": "tauric-research",
        "url": "https://github.com/TauricResearch/TradingBot",
        "description": "多智能体交易框架"
    },
    {
        "name": "sentiment-analysis",
        "url": "https://github.com/mvanhorn/last30days",
        "description": "近30天舆情研究工具"
    },
    {
        "name": "polymarket-helper",
        "url": "https://github.com/FiatFiorino/polymarket-helper",
        "description": "Polymarket辅助交易工具"
    },
    {
        "name": "firecrawl",
        "url": "https://github.com/firecrawl/firecrawl",
        "description": "网页数据清洗工具"
    },
    {
        "name": "pydantic-ai",
        "url": "https://github.com/pydantic/pydantic-ai",
        "description": "生产级AI智能体框架"
    },
    {
        "name": "n8n",
        "url": "https://github.com/n8n-io/n8n",
        "description": "工作流自动化平台"
    },
    {
        "name": "tavily-mcp",
        "url": "https://github.com/tavily-ai/tavily-mcp",
        "description": "Tavily MCP服务端"
    },
    {
        "name": "wallet-analyzer",
        "url": "https://github.com/txbabaxyz/wallet-collector",
        "description": "钱包数据采集与分析器"
    },
    {
        "name": "binance-predictor",
        "url": "https://github.com/txbabaxyz/mlmomentum",
        "description": "币安数据采集与预测工具"
    }
]

# 创建基础目录
os.makedirs(BASE_DIR, exist_ok=True)

print(f"[INFO] 克隆目录: {BASE_DIR}")
print(f"[INFO] 准备克隆 {len(repos)} 个仓库\n")

for i, repo in enumerate(repos, 1):
    target_dir = os.path.join(BASE_DIR, repo['name'])

    if os.path.exists(target_dir):
        print(f"[{i}/{len(repos)}] {repo['name']} - 已存在，跳过")
        continue

    print(f"[{i}/{len(repos)}] 克隆 {repo['name']} - {repo['description']}")

    try:
        result = subprocess.run(
            ['git', 'clone', repo['url'], target_dir],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"    ✓ 成功")
        else:
            print(f"    ✗ 失败: {result.stderr[:100]}")
    except subprocess.TimeoutExpired:
        print(f"    ✗ 超时")
    except Exception as e:
        print(f"    ✗ 错误: {str(e)[:100]}")

print(f"\n[完成] 克隆任务结束")
print(f"[INFO] 仓库位置: {BASE_DIR}")
