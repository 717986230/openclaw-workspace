#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
import sys

BASE_DIR = "C:/Users/Administrator/.openclaw/workspace/polymarket-tools"

repos = [
    ("prediction-market-backtest", "https://github.com/evan-kolberg/prediction-market-backtest-framework", "Backtest framework"),
    ("tauric-research", "https://github.com/TauricResearch/TradingBot", "Multi-agent trading"),
    ("sentiment-analysis", "https://github.com/mvanhorn/last30days", "Sentiment analysis"),
    ("polymarket-helper", "https://github.com/FiatFiorino/polymarket-helper", "Polymarket helper"),
    ("firecrawl", "https://github.com/firecrawl/firecrawl", "Web scraping"),
    ("pydantic-ai", "https://github.com/pydantic/pydantic-ai", "AI agent framework"),
    ("n8n", "https://github.com/n8n-io/n8n", "Workflow automation"),
    ("tavily-mcp", "https://github.com/tavily-ai/tavily-mcp", "MCP server"),
    ("wallet-analyzer", "https://github.com/txbabaxyz/wallet-collector", "Wallet analysis"),
    ("binance-predictor", "https://github.com/txbababyz/mlmomentum", "Price prediction")
]

os.makedirs(BASE_DIR, exist_ok=True)

results = []
for i, (name, url, desc) in enumerate(repos, 1):
    target_dir = os.path.join(BASE_DIR, name)
    
    if os.path.exists(target_dir):
        results.append((i, name, "EXISTS", "Already cloned"))
        continue
    
    try:
        result = subprocess.run(
            ['git', 'clone', url, target_dir],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            results.append((i, name, "SUCCESS", "Cloned successfully"))
        else:
            error = result.stderr.replace('\n', ' ')[:80]
            results.append((i, name, "FAILED", error))
    except Exception as e:
        results.append((i, name, "ERROR", str(e)[:80]))

# Save results to file
output_file = "C:/Users/Administrator/.openclaw/workspace/scripts/clone_results.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Clone Results - {len(results)} repos\n")
    f.write("=" * 60 + "\n")
    for i, name, status, msg in results:
        f.write(f"[{i}/{len(results)}] {name}: {status} - {msg}\n")

print(f"Results saved to: {output_file}")
print(f"Processed: {len(results)} repos")
