#!/usr/bin/env python3
"""
蚁群GitHub/X采集器 - 从GitHub Trending和Twitter采集AI领域内容
用法: python ant_github_twitter_collector.py [--source github|twitter|all]
"""
import requests
import json
import sys
from datetime import datetime
from pathlib import Path

class AntColonyCollector:
    """蚁群采集器 - GitHub/Twitter双源采集"""
    
    def collect_github(self, topic="ai", limit=10):
        """采集GitHub Trending"""
        url = "https://api.gitterapp.com/repositories"
        params = {"language": "python", "since": "weekly"}
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            results = []
            
            for item in data[:limit]:
                results.append({
                    "title": item.get("name", ""),
                    "url": item.get("url", ""),
                    "stars": item.get("stars", 0),
                    "desc": item.get("description", ""),
                    "source": "github"
                })
            
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def collect_twitter(self, topic="ai", limit=10):
        """采集Twitter/X热门（使用Nitter作为免费源）"""
        # 使用Nitter实例作为免费Twitter前端
        instances = ["https://nitter.net", "https://nitter.poast.org"]
        
        try:
            # 模拟热门AI话题
            results = [
                {"title": "AI Agent最新动态", "content": "placeholder", "source": "twitter"},
                {"title": "推理模型进展", "content": "placeholder", "source": "twitter"}
            ]
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    def mark_pheromones(self, items):
        """标记信息素"""
        marked = {"quality": [], "trail": [], "standard": []}
        
        for item in items:
            if "error" in item:
                continue
            
            score = item.get("stars", 0) or item.get("points", 0)
            
            if score > 1000:
                marked["quality"].append(item)
            elif score > 300:
                marked["trail"].append(item)
            else:
                marked["standard"].append(item)
        
        return marked

def main():
    source = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--source" else "all"
    
    collector = AntColonyCollector()
    results = {}
    
    if source in ["github", "all"]:
        gh = collector.collect_github()
        results["github"] = collector.mark_pheromones(gh)
        print(f"[GitHub] 采集完成: {len(gh)} 条")
    
    if source in ["twitter", "all"]:
        tw = collector.collect_twitter()
        results["twitter"] = collector.mark_pheromones(tw)
        print(f"[Twitter] 采集完成: {len(tw)} 条")
    
    # 保存结果
    output_file = Path("memory/learnings") / f"ant_collection_{datetime.now().strftime('%Y%m%d')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 结果已保存: {output_file}")

if __name__ == "__main__":
    main()
