#!/usr/bin/env python3
"""
蚁群新闻采集器 - 快速采集AI/LLM/Multi-Agent领域新闻
用法: python swarm_news_collector.py [--topic ai|reasoning|agent] [--limit 10]
"""
import requests
import json
import sys
from datetime import datetime
from pathlib import Path

class SwarmNewsCollector:
    """蚁群采集器 - 快速采集并标记信息素"""
    
    def __init__(self):
        self.base_url = "https://hn.algolia.com/api/v1/search"
        self.topics = {
            "ai": "ai+agent",
            "reasoning": "llm+reasoning",
            "agent": "multi+agent"
        }
    
    def collect(self, topic="ai", limit=10):
        """采集指定主题的新闻"""
        if topic not in self.topics:
            topic = "ai"
        
        url = f"{self.base_url}?query={self.topics[topic]}&tags=story&hitsPerPage={limit}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            return self._mark_pheromones(data.get("hits", []))
        except Exception as e:
            return {"error": str(e)}
    
    def _mark_pheromones(self, hits):
        """标记信息素：quality(>500点), trail(200-500), standard(<200)"""
        marked = {"quality": [], "trail": [], "standard": []}
        
        for item in hits:
            points = item.get("points", 0)
            entry = {
                "title": item.get("title", ""),
                "points": points,
                "comments": item.get("num_comments", 0),
                "url": item.get("url", ""),
                "date": item.get("created_at", "")
            }
            
            if points > 500:
                marked["quality"].append(entry)
            elif points > 200:
                marked["trail"].append(entry)
            else:
                marked["standard"].append(entry)
        
        return marked
    
    def format_output(self, marked):
        """格式化输出"""
        output = []
        
        if marked.get("quality"):
            output.append("[Q] 质量信息素 (高价值):")
            for i, item in enumerate(marked["quality"][:5], 1):
                output.append(f"  {i}. {item['title']} ({item['points']}点)")
        
        if marked.get("trail"):
            output.append("\n[T] 路径信息素 (技术探索):")
            for i, item in enumerate(marked["trail"][:3], 1):
                output.append(f"  {i}. {item['title']} ({item['points']}点)")
        
        return "\n".join(output) if output else "无内容"

def main():
    topic = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--topic" else "ai"
    limit = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--limit" else 10
    
    collector = SwarmNewsCollector()
    results = collector.collect(topic, limit)
    
    if "error" in results:
        print(f"错误: {results['error']}")
        return
    
    print(collector.format_output(results))
    
    # 保存JSON结果
    output_file = Path("memory/learnings") / f"news_{topic}_{datetime.now().strftime('%Y%m%d')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 详细结果已保存: {output_file}")

if __name__ == "__main__":
    main()
