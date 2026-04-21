#!/usr/bin/env python3
"""
搜索 GitHub 和 Twitter 上的最新 AI Agent 内容
"""
import sys
import os
import io
import json
import requests
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GITHUB_API = "https://api.github.com"
TWITTER_SEARCH = "https://api.twitter.com/2/tweets/search/recent"

# GitHub 搜索关键词
GITHUB_QUERIES = [
    "AI agent framework",
    "autonomous agent",
    "multi-agent system",
    "LLM agent",
    "agent orchestration",
    "self-evolving agent",
    "memory system agent",
    "theory of mind agent"
]

# Twitter 搜索关键词
TWITTER_QUERIES = [
    "AI agent",
    "autonomous agent",
    "multi-agent",
    "LLM agent",
    "agent framework"
]


def search_github(query: str, days: int = 7) -> list:
    """搜索 GitHub"""
    results = []
    try:
        date_str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        url = f"{GITHUB_API}/search/repositories"
        params = {
            "q": f"{query} created:>{date_str}",
            "sort": "stars",
            "order": "desc",
            "per_page": 10
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for repo in data.get("items", []):
                results.append({
                    "name": repo["full_name"],
                    "stars": repo["stargazers_count"],
                    "description": repo.get("description", "")[:100],
                    "language": repo.get("language"),
                    "created": repo["created_at"],
                    "url": repo["html_url"]
                })
    except Exception as e:
        results.append({"error": str(e)})
    return results


def search_twitter(query: str, days: int = 7) -> list:
    """搜索 Twitter (需要 API key，这里模拟)"""
    # 实际需要 Twitter API v2 Bearer Token
    # 这里返回模拟数据
    return [
        {
            "query": query,
            "note": "Twitter API requires authentication",
            "mock": True
        }
    ]


def main():
    """主函数"""
    result = {
        "timestamp": datetime.now().isoformat(),
        "github": {},
        "twitter": {},
        "summary": {}
    }

    # GitHub 搜索
    print("Searching GitHub...")
    for query in GITHUB_QUERIES[:5]:  # 限制前5个
        print(f"  - {query}")
        repos = search_github(query, days=30)
        result["github"][query] = repos

    # Twitter 搜索（模拟）
    print("Searching Twitter...")
    for query in TWITTER_QUERIES[:3]:
        print(f"  - {query}")
        tweets = search_twitter(query, days=7)
        result["twitter"][query] = tweets

    # 统计
    total_repos = sum(len(v) for v in result["github"].values())
    result["summary"] = {
        "github_queries": len(result["github"]),
        "total_repos": total_repos,
        "twitter_queries": len(result["twitter"])
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()