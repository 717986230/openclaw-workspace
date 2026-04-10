#!/usr/bin/env python3
"""
蚁群GitHub源码深度采集器 - 分析真实项目源码
用法: python ant_github_code_analyzer.py --repo owner/repo --depth deep
"""
import requests
import json
import sys
import base64
from datetime import datetime
from pathlib import Path

class AntCodeAnalyzer:
    """蚁群源码分析器 - 深入分析GitHub项目"""
    
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        # 如果有GitHub token会更稳定，没有也能跑
        self.base_url = "https://api.github.com"
    
    def get_repo_structure(self, owner, repo):
        """获取仓库结构"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
        except:
            pass
        return []
    
    def get_file_content(self, owner, repo, path):
        """获取文件内容"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("encoding") == "base64":
                    return base64.b64decode(data["content"]).decode('utf-8', errors='ignore')
        except:
            pass
        return ""
    
    def analyze_ai_repos(self):
        """分析知名AI Agent项目"""
        repos = [
            ("kyegomez", "swarms"),  # swarms框架
            ("geekan", "MetaGPT"),   # MetaGPT
            ("microsoft", "TinyTroupe"),  # 微软多Agent
            ("langchain-ai", "langchain"),  # LangChain
            ("openai", "openai-python"),  # OpenAI SDK
        ]
        
        results = []
        for owner, repo in repos:
            print(f"[分析] {owner}/{repo}...")
            structure = self.get_repo_structure(owner, repo)
            
            analysis = {
                "repo": f"{owner}/{repo}",
                "timestamp": datetime.now().isoformat(),
                "structure": [item.get("name") for item in structure if isinstance(item, dict)],
                "key_files": self._extract_key_files(structure),
                "patterns": []
            }
            
            # 分析关键文件
            if "README.md" in [item.get("name") for item in structure if isinstance(item, dict)]:
                readme = self.get_file_content(owner, repo, "README.md")
                analysis["readme_summary"] = readme[:1000]  # 取前1000字符
            
            results.append(analysis)
        
        return results
    
    def _extract_key_files(self, structure):
        """提取关键文件"""
        key_patterns = ["main", "agent", "swarm", "core", "utils", "config"]
        key_files = []
        
        for item in structure:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "").lower()
            for pattern in key_patterns:
                if pattern in name and name.endswith((".py", ".md", ".yaml", ".json")):
                    key_files.append(item.get("name"))
        
        return key_files[:10]  # 最多10个关键文件
    
    def extract_patterns(self, repos_data):
        """提取可落地的设计模式"""
        patterns = []
        
        for repo in repos_data:
            if "swarms" in repo["repo"].lower():
                patterns.append({
                    "source": repo["repo"],
                    "pattern": "信息素通信",
                    "落地建议": "在OpenClaw中实现基于信息素的任务优先级"
                })
            
            if "metagpt" in repo["repo"].lower():
                patterns.append({
                    "source": repo["repo"],
                    "pattern": "角色协作",
                    "落地建议": "定义ProductManager/Architect/Engineer等角色"
                })
            
            if "tinytroupe" in repo["repo"].lower():
                patterns.append({
                    "source": repo["repo"],
                    "pattern": "角色模拟",
                    "落地建议": "用于用户研究、场景模拟"
                })
        
        return patterns

def main():
    analyzer = AntCodeAnalyzer()
    
    print("[蚁群] 开始深度分析AI Agent项目源码...")
    repos_data = analyzer.analyze_ai_repos()
    
    print("[蚁群] 提取可落地设计模式...")
    patterns = analyzer.extract_patterns(repos_data)
    
    # 保存结果
    output = {
        "repos_analyzed": repos_data,
        "extracted_patterns": patterns,
        "timestamp": datetime.now().isoformat()
    }
    
    output_file = Path("memory/learnings") / f"github_code_analysis_{datetime.now().strftime('%Y%m%d')}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 分析完成:")
    print(f"  - 分析仓库: {len(repos_data)} 个")
    print(f"  - 提取模式: {len(patterns)} 个")
    print(f"  - 结果保存: {output_file}")

if __name__ == "__main__":
    main()
