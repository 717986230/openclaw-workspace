#!/usr/bin/env python3
"""
多平台热搜聚合器
用法: python hot_trending.py [--platform PLATFORM] [--limit N]
示例:
  python hot_trending.py                  # 获取所有平台热搜
  python hot_trending.py --platform 微博  # 只看微博
  python hot_trending.py --limit 5         # 每平台只显示5条
"""
import argparse
import json
from datetime import datetime
from ddgs import DDGS

# 平台配置
PLATFORMS = {
    "微博": {"query": "微博热搜", "site": "weibo.com"},
    "知乎": {"query": "知乎热榜", "site": "zhihu.com"},
    "百度": {"query": "百度热搜榜", "site": "baidu.com"},
    "抖音": {"query": "抖音热榜", "site": "douyin.com"},
    "小红书": {"query": "小红书热门", "site": "xiaohongshu.com"},
    "B站": {"query": "B站热门", "site": "bilibili.com"},
    "推特": {"query": "Twitter trending", "site": "twitter.com"},
    "Reddit": {"query": "Reddit trending", "site": "reddit.com"},
}


def get_trending(platform: str, limit: int = 10) -> list:
    """获取单个平台热搜"""
    try:
        ddgs = DDGS()
        config = PLATFORMS.get(platform, {"query": platform, "site": ""})
        
        # 搜索当前平台热搜
        results = list(ddgs.news(f"{config['query']} 今日", max_results=limit))
        
        return [
            {
                "title": r.get("title", ""),
                "source": platform,
                "date": r.get("date", "")[:10] if r.get("date") else "",
                "url": r.get("url", "")
            }
            for r in results
        ]
    except Exception as e:
        print(f"  ⚠️ {platform} 获取失败: {e}")
        return []


def get_all_trending(limit: int = 10) -> dict:
    """获取所有平台热搜"""
    all_results = {}
    
    for platform in PLATFORMS.keys():
        print(f"  📡 正在获取 {platform}...")
        all_results[platform] = get_trending(platform, limit)
    
    return all_results


def format_output(results: dict):
    """格式化输出"""
    print("\n" + "=" * 60)
    print("📈 多平台热搜聚合")
    print("=" * 60)
    print(f"🕐 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    for platform, items in results.items():
        print(f"\n🔥 {platform}")
        print("-" * 40)
        
        if not items:
            print("  暂无数据")
            continue
            
        for i, item in enumerate(items[:10], 1):
            title = item.get("title", "")
            date = item.get("date", "")
            print(f"  {i}. {title}")
            if date:
                print(f"     🕐 {date}")


def main():
    parser = argparse.ArgumentParser(
        description="多平台热搜聚合器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--platform", "-p", 
                        help="指定平台 (微博/知乎/百度/抖音/小红书/B站/推特/Reddit)")
    parser.add_argument("--limit", "-l", type=int, default=10, 
                        help="每平台条数 (默认: 10)")
    
    args = parser.parse_args()
    
    print(f"\n🕐 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.platform:
        # 获取指定平台
        print(f"📌 查询平台: {args.platform}")
        results = {args.platform: get_trending(args.platform, args.limit)}
    else:
        # 获取所有平台
        print("📌 查询所有平台...")
        results = get_all_trending(args.limit)
    
    format_output(results)
    print("\n✅ 查询完成")


if __name__ == "__main__":
    main()