
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from datetime import datetime

def search_hn(query, limit=10):
    """搜索 Hacker News"""
    url = "https://hn.algolia.com/api/v1/search"
    params = {
        "query": query,
        "tags": "story",
        "hitsPerPage": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get('hits', [])
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        return []

def print_news(news, title):
    """打印新闻结果"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")
    
    if not news:
        print("❌ 没有找到相关新闻\n")
        return
    
    for i, item in enumerate(news, 1):
        print(f"{i}. {item.get('title', '无标题')}")
        
        author = item.get('author')
        points = item.get('points')
        comments = item.get('num_comments')
        
        if author or points or comments:
            parts = []
            if author:
                parts.append(f"作者: {author}")
            if points is not None:
                parts.append(f"热度: {points} 点")
            if comments is not None:
                parts.append(f"评论: {comments}")
            if parts:
                print(f"   {' · '.join(parts)}")
        
        url = item.get('url')
        if url:
            print(f"   链接: {url}")
        
        created_at = item.get('created_at')
        if created_at:
            print(f"   时间: {created_at}")
        
        print()
    
    print(f"{'='*60}\n")

def main():
    print("🔍 正在搜索战火消息...")
    war_news = search_hn("war conflict military attack tension", limit=15)
    print_news(war_news, "🔥 战火消息")
    
    print("🔍 正在搜索原油市场动态...")
    oil_news = search_hn("oil crude prices market OPEC energy", limit=15)
    print_news(oil_news, "🛢️ 原油市场动态")
    
    print("✅ 搜索完成！")

if __name__ == "__main__":
    main()
