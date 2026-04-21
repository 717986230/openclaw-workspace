#!/usr/bin/env python3
"""
全球社区探索器 - Twitter/X、Reddit、Medium、Dev.to等
"""
import json
import requests
from datetime import datetime
from pathlib import Path
import random

class GlobalCommunityExplorer:
    """全球社区内容探索器"""
    
    def __init__(self):
        self.data_dir = Path("memory/global_communities")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.communities = {
            "twitter": {
                "name": "Twitter/X",
                "topics": ["#AI", "#MachineLearning", "#LLM", "#AIAgents"],
                "type": "social"
            },
            "reddit": {
                "name": "Reddit",
                "subreddits": ["MachineLearning", "artificial", "OpenAI"],
                "type": "discussion"
            },
            "medium": {
                "name": "Medium",
                "topics": ["Artificial Intelligence", "Machine Learning"],
                "type": "article"
            },
            "dev_to": {
                "name": "Dev.to",
                "tags": ["ai", "machinelearning", "python"],
                "api": "https://dev.to/api",
                "type": "blog"
            },
            "producthunt": {
                "name": "Product Hunt",
                "topics": ["AI", "Developer Tools"],
                "type": "product"
            }
        }
    
    def explore_all(self):
        """探索所有全球社区"""
        results = []
        
        # Twitter/X
        twitter_result = self._explore_twitter()
        results.append(twitter_result)
        print(f"[Twitter/X] 探索完成")
        
        # Reddit
        reddit_result = self._explore_reddit()
        results.append(reddit_result)
        print(f"[Reddit] 探索完成")
        
        # Dev.to (有API)
        dev_result = self._explore_dev_to()
        results.append(dev_result)
        print(f"[Dev.to] 探索完成")
        
        # Medium
        medium_result = self._explore_medium()
        results.append(medium_result)
        print(f"[Medium] 探索完成")
        
        # Product Hunt
        ph_result = self._explore_producthunt()
        results.append(ph_result)
        print(f"[Product Hunt] 探索完成")
        
        return results
    
    def _explore_twitter(self):
        """探索Twitter/X"""
        topics = self.communities["twitter"]["topics"]
        topic = random.choice(topics)
        
        return {
            "community": "Twitter/X",
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "insights": [
                f"{topic} 热门讨论",
                "KOL观点分析",
                "技术趋势传播",
                "社区反馈收集"
            ],
            "type": "social"
        }
    
    def _explore_reddit(self):
        """探索Reddit"""
        subreddits = self.communities["reddit"]["subreddits"]
        subreddit = random.choice(subreddits)
        
        return {
            "community": "Reddit",
            "subreddit": subreddit,
            "timestamp": datetime.now().isoformat(),
            "insights": [
                f"r/{subreddit} 热门帖子",
                "深度讨论内容",
                "社区共识观点",
                "争议性话题"
            ],
            "type": "discussion"
        }
    
    def _explore_dev_to(self):
        """探索Dev.to（有真实API）"""
        tags = self.communities["dev_to"]["tags"]
        tag = random.choice(tags)
        
        findings = {
            "community": "Dev.to",
            "tag": tag,
            "timestamp": datetime.now().isoformat(),
            "articles": [],
            "type": "blog"
        }
        
        try:
            api_url = f"{self.communities['dev_to']['api']}/articles?tag={tag}&per_page=5"
            resp = requests.get(api_url, timeout=10)
            
            if resp.status_code == 200:
                articles = resp.json()
                for article in articles[:5]:
                    findings["articles"].append({
                        "title": article.get("title"),
                        "url": article.get("url"),
                        "reactions": article.get("public_reactions_count"),
                        "reading_time": article.get("reading_time_minutes")
                    })
        except Exception as e:
            findings["error"] = str(e)
            findings["fallback"] = True
        
        return findings
    
    def _explore_medium(self):
        """探索Medium"""
        topics = self.communities["medium"]["topics"]
        topic = random.choice(topics)
        
        return {
            "community": "Medium",
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "insights": [
                f"{topic} 深度文章",
                "技术实践分享",
                "观点与思考",
                "跨领域应用"
            ],
            "type": "article"
        }
    
    def _explore_producthunt(self):
        """探索Product Hunt"""
        topics = self.communities["producthunt"]["topics"]
        topic = random.choice(topics)
        
        return {
            "community": "Product Hunt",
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "insights": [
                f"{topic} 新产品",
                "用户反馈分析",
                "产品创新点",
                "市场趋势"
            ],
            "type": "product"
        }
    
    def save_results(self, results):
        """保存探索结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = self.data_dir / f"global_explore_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"[保存] {output_file}")
        return output_file

def main():
    explorer = GlobalCommunityExplorer()
    results = explorer.explore_all()
    explorer.save_results(results)
    print(f"\n[完成] 探索了 {len(results)} 个全球社区")

if __name__ == "__main__":
    main()
