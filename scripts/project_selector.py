#!/usr/bin/env python3
"""
项目选择器 - 数据驱动的热门项目判断

判断依据：
1. GitHub Stars 数量（流行度）
2. 最近活跃度（commit 频率）
3. Issue 响应速度（维护积极性）
4. PR 合并速度（开放程度）
5. "good first issue" 标签数量（新手友好度）
"""

import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import requests

class ProjectSelector:
    """热门项目选择器"""
    
    # 已知的高质量项目白名单
    KNOWN_GOOD_PROJECTS = {
        "pallets/click": {"category": "cli", "priority": "high"},
        "pallets/flask": {"category": "web", "priority": "high"},
        "psf/requests": {"category": "http", "priority": "high"},
        "python/cpython": {"category": "core", "priority": "medium"},
        "numpy/numpy": {"category": "science", "priority": "high"},
        "pytest-dev/pytest": {"category": "testing", "priority": "high"},
        "pandas-dev/pandas": {"category": "data", "priority": "high"},
        "django/django": {"category": "web", "priority": "medium"},
        "fastapi/fastapi": {"category": "api", "priority": "high"},
    }
    
    def __init__(self):
        self.token = self._get_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }
    
    def _get_token(self) -> str:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    
    def _run_gh(self, cmd: str) -> Dict:
        """执行 gh 命令"""
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, encoding='utf-8', errors='replace'
        )
        if result.returncode == 0 and result.stdout:
            try:
                return json.loads(result.stdout)
            except:
                return {}
        return {}
    
    def get_repo_stats(self, repo: str) -> Dict:
        """获取仓库统计数据"""
        print(f"  分析 {repo}...")
        
        stats = {
            "repo": repo,
            "stars": 0,
            "forks": 0,
            "open_issues": 0,
            "last_commit_days": 999,
            "good_first_issues": 0,
            "avg_pr_merge_days": 0,
            "score": 0,
        }
        
        # 基本信息
        url = f"https://api.github.com/repos/{repo}"
        resp = requests.get(url, headers=self.headers)
        
        if resp.status_code == 200:
            data = resp.json()
            stats["stars"] = data.get("stargazers_count", 0)
            stats["forks"] = data.get("forks_count", 0)
            stats["open_issues"] = data.get("open_issues_count", 0)
            
            # 最后提交时间
            pushed_at = data.get("pushed_at")
            if pushed_at:
                last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                stats["last_commit_days"] = (datetime.now(last_push.tzinfo) - last_push).days
        
        # 获取 good first issue 数量
        result = self._run_gh(
            f'gh issue list --repo {repo} --label "good first issue" '
            f'--state open --limit 100 --json number'
        )
        if isinstance(result, list):
            stats["good_first_issues"] = len(result)
        
        # 计算分数
        stats["score"] = self._calculate_score(stats)
        
        return stats
    
    def _calculate_score(self, stats: Dict) -> float:
        """计算项目分数"""
        score = 0.0
        
        # Stars 分数（0-30分）
        if stats["stars"] > 50000:
            score += 30
        elif stats["stars"] > 10000:
            score += 25
        elif stats["stars"] > 5000:
            score += 20
        elif stats["stars"] > 1000:
            score += 15
        else:
            score += 10
        
        # 活跃度分数（0-25分）
        if stats["last_commit_days"] < 7:
            score += 25
        elif stats["last_commit_days"] < 30:
            score += 20
        elif stats["last_commit_days"] < 90:
            score += 15
        else:
            score += 5
        
        # 新手友好度（0-25分）
        gfi = stats["good_first_issues"]
        if gfi > 20:
            score += 25
        elif gfi > 10:
            score += 20
        elif gfi > 5:
            score += 15
        elif gfi > 0:
            score += 10
        else:
            score += 0
        
        # 项目规模（0-20分）
        if stats["open_issues"] > 100:
            score += 20
        elif stats["open_issues"] > 50:
            score += 15
        elif stats["open_issues"] > 10:
            score += 10
        else:
            score += 5
        
        return score
    
    def discover_projects(self, limit: int = 20) -> List[Dict]:
        """发现热门项目"""
        print("\n[Discover] 发现热门项目...")
        
        projects = []
        
        # 1. 首先检查白名单项目
        print("\n  检查已知优质项目:")
        for repo, info in self.KNOWN_GOOD_PROJECTS.items():
            stats = self.get_repo_stats(repo)
            stats["category"] = info["category"]
            stats["source"] = "whitelist"
            projects.append(stats)
            time.sleep(1)  # 避免 API 限制
        
        # 2. 搜索热门 Python 项目
        print("\n  搜索热门 Python 项目:")
        result = subprocess.run(
            'gh search repos --language python --limit 20 --json full_name,stargazers_count '
            '-- "--stars:>5000 archived:false"',
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode == 0:
            for item in json.loads(result.stdout):
                repo = item.get("full_name")
                if repo and not any(p["repo"] == repo for p in projects):
                    stats = self.get_repo_stats(repo)
                    stats["source"] = "search"
                    projects.append(stats)
                    time.sleep(1)
        
        # 按分数排序
        projects.sort(key=lambda x: x["score"], reverse=True)
        
        return projects[:limit]
    
    def get_recommended_projects(self, limit: int = 10) -> List[Dict]:
        """获取推荐项目列表"""
        projects = self.discover_projects(limit=limit)
        
        print(f"\n{'='*60}")
        print("推荐项目列表（按分数排序）:")
        print(f"{'='*60}")
        print(f"{'项目':<30} {'Stars':>8} {'GFI':>5} {'活跃度':>6} {'分数':>6}")
        print("-" * 60)
        
        for p in projects[:limit]:
            stars = f"{p['stars']:,}"
            gfi = str(p['good_first_issues'])
            active = f"{p['last_commit_days']}d"
            score = f"{p['score']:.1f}"
            print(f"{p['repo']:<30} {stars:>8} {gfi:>5} {active:>6} {score:>6}")
        
        return projects[:limit]


def main():
    selector = ProjectSelector()
    projects = selector.get_recommended_projects(limit=15)
    
    # 保存结果
    import json
    from pathlib import Path
    
    output_path = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\recommended_projects.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存: {output_path}")


if __name__ == "__main__":
    main()
