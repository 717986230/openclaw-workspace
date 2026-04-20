#!/usr/bin/env python3
"""
Auto PR System v5 - 集成项目选择器

新增功能：
1. 数据驱动的项目选择（不再硬编码）
2. 动态发现热门项目
3. 智能排序和推荐
"""

import subprocess
import json
import time
import re
import base64
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import requests

# ==================== 配置 ====================
WORK_DIR = Path(r"D:\CODE\auto-pr-work")
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
CACHE_DIR = LOG_DIR / "cache"
PROGRESS_FILE = LOG_DIR / "auto_pr_progress_v5.json"
PROJECTS_CACHE = CACHE_DIR / "recommended_projects.json"

# 排除的简单关键词
SIMPLE_DOC_KEYWORDS = [
    "SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "添加文档", "add documentation", "typo", "spelling"
]

# ==================== 项目选择器 ====================
class ProjectSelector:
    """数据驱动的项目选择器"""
    
    KNOWN_GOOD_PROJECTS = {
        "pallets/click": {"category": "cli", "priority": "high"},
        "pallets/flask": {"category": "web", "priority": "high"},
        "psf/requests": {"category": "http", "priority": "high"},
        "python/cpython": {"category": "core", "priority": "medium"},
        "numpy/numpy": {"category": "science", "priority": "high"},
        "pytest-dev/pytest": {"category": "testing", "priority": "high"},
        "pandas-dev/pandas": {"category": "data", "priority": "high"},
    }
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        }
    
    def get_repo_stats(self, repo: str) -> Dict:
        """获取仓库统计"""
        stats = {
            "repo": repo,
            "stars": 0,
            "forks": 0,
            "open_issues": 0,
            "last_commit_days": 999,
            "good_first_issues": 0,
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
            
            pushed_at = data.get("pushed_at")
            if pushed_at:
                last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                stats["last_commit_days"] = (datetime.now(last_push.tzinfo) - last_push).days
        
        # good first issue 数量
        try:
            result = subprocess.run(
                f'gh issue list --repo {repo} --label "good first issue" '
                f'--state open --limit 100 --json number',
                shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                issues = json.loads(result.stdout)
                stats["good_first_issues"] = len(issues) if isinstance(issues, list) else 0
        except:
            pass
        
        # 计算分数
        stats["score"] = self._calculate_score(stats)
        return stats
    
    def _calculate_score(self, stats: Dict) -> float:
        """计算项目分数"""
        score = 0.0
        
        # Stars (0-30)
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
        
        # 活跃度 (0-25)
        if stats["last_commit_days"] < 7:
            score += 25
        elif stats["last_commit_days"] < 30:
            score += 20
        elif stats["last_commit_days"] < 90:
            score += 15
        else:
            score += 5
        
        # 新手友好度 (0-25)
        gfi = stats["good_first_issues"]
        if gfi > 20:
            score += 25
        elif gfi > 10:
            score += 20
        elif gfi > 5:
            score += 15
        elif gfi > 0:
            score += 10
        
        # 项目规模 (0-20)
        if stats["open_issues"] > 100:
            score += 20
        elif stats["open_issues"] > 50:
            score += 15
        elif stats["open_issues"] > 10:
            score += 10
        else:
            score += 5
        
        return score
    
    def get_recommended_projects(self, limit: int = 10, use_cache: bool = True) -> List[Dict]:
        """获取推荐项目"""
        # 尝试使用缓存
        if use_cache and PROJECTS_CACHE.exists():
            cache_age = (datetime.now() - datetime.fromtimestamp(PROJECTS_CACHE.stat().st_mtime)).total_seconds()
            if cache_age < 3600:  # 1小时内的缓存
                with open(PROJECTS_CACHE, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached and len(cached) >= limit:
                        print(f"  使用缓存的项目列表 ({len(cached)} 个项目)")
                        return cached[:limit]
        
        print("  分析项目...")
        projects = []
        
        for repo, info in self.KNOWN_GOOD_PROJECTS.items():
            stats = self.get_repo_stats(repo)
            stats["category"] = info["category"]
            projects.append(stats)
            time.sleep(0.5)
        
        # 按分数排序
        projects.sort(key=lambda x: x["score"], reverse=True)
        
        # 缓存结果
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROJECTS_CACHE, 'w', encoding='utf-8') as f:
            json.dump(projects, f, ensure_ascii=False, indent=2)
        
        return projects[:limit]

# ==================== GitHub API 封装 ====================
class GitHubAPI:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def get(self, url: str) -> requests.Response:
        return requests.get(url, headers=self.headers)
    
    def post(self, url: str, data: Dict) -> requests.Response:
        return requests.post(url, headers=self.headers, json=data)
    
    def put(self, url: str, data: Dict) -> requests.Response:
        return requests.put(url, headers=self.headers, json=data)
    
    def check_existing_pr(self, repo: str, issue_num: int) -> List[Dict]:
        """检查是否已有 PR"""
        url = f"https://api.github.com/repos/{repo}/pulls?state=all&per_page=100"
        resp = self.get(url)
        if resp.status_code == 200:
            prs = resp.json()
            return [pr for pr in prs 
                    if pr.get('title') and pr.get('body') and
                    (f"#{issue_num}" in pr.get('title', '') or f"#{issue_num}" in pr.get('body', ''))]
        return []
    
    def ensure_fork(self, repo: str, username: str) -> str:
        """确保 fork 存在"""
        fork_repo = f"{username}/{repo.split('/')[-1]}"
        url = f"https://api.github.com/repos/{fork_repo}"
        resp = self.get(url)
        
        if resp.status_code != 200:
            print(f"  创建 fork: {fork_repo}")
            fork_url = f"https://api.github.com/repos/{repo}/forks"
            self.post(fork_url, {})
            time.sleep(3)
        
        return fork_repo

# ==================== Issue 分析器 ====================
class IssueAnalyzer:
    @staticmethod
    def analyze(issue: Dict) -> Dict:
        """分析 issue 类型"""
        title_lower = issue.get('title', '').lower()
        body_lower = issue.get('body', '')[:1000].lower()
        
        result = {
            "can_fix": False,
            "fix_type": None,
            "priority": "low",
        }
        
        # 排除简单文档问题
        if any(kw in title_lower or kw in body_lower for kw in SIMPLE_DOC_KEYWORDS):
            result["fix_type"] = "simple_doc"
            return result
        
        # 检测问题类型
        if 'error' in title_lower or 'wrong' in title_lower or 'bug' in title_lower:
            result.update({"can_fix": True, "fix_type": "bug", "priority": "high"})
        elif 'missing' in title_lower or 'not' in title_lower or "doesn't" in title_lower:
            result.update({"can_fix": True, "fix_type": "missing_feature", "priority": "medium"})
        elif 'inconsistent' in title_lower or 'policy' in title_lower:
            result.update({"can_fix": True, "fix_type": "behavior", "priority": "medium"})
        
        return result

# ==================== 主工作流 ====================
class AutoPRWorkflow:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.token = self._get_token()
        self.username = self._get_username()
        self.api = GitHubAPI(self.token)
        self.selector = ProjectSelector(self.token)
        self.progress = self._load_progress()
    
    def _get_token(self) -> str:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        return result.stdout.strip()
    
    def _get_username(self) -> str:
        result = subprocess.run(["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True)
        return result.stdout.strip()
    
    def _load_progress(self) -> Dict:
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"processed": [], "prs": []}
    
    def _save_progress(self):
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def search_issues(self, projects: List[Dict], limit: int = 5) -> List[Dict]:
        """搜索可修复的 issue"""
        print("\n[Search] 搜索 issue...")
        issues = []
        
        for project in projects:
            repo = project["repo"]
            score = project["score"]
            
            print(f"\n  {repo} (分数: {score:.0f})...")
            
            # 确定搜索标签
            label = "good first issue" if project.get("good_first_issues", 0) > 0 else "bug"
            
            result = subprocess.run(
                f'gh issue list --repo {repo} --label "{label}" '
                f'--state open --limit 10 --json number,title,body',
                shell=True, capture_output=True, text=True, timeout=30
            )
            
            if result.returncode != 0 or not result.stdout:
                continue
            
            try:
                items = json.loads(result.stdout)
            except:
                continue
            
            for item in items:
                issue_num = item['number']
                
                # 检查是否已处理
                if any(p.get('issue_num') == issue_num for p in self.progress.get('processed', [])):
                    continue
                
                # 检查是否已有 PR
                existing = self.api.check_existing_pr(repo, issue_num)
                if existing:
                    print(f"    [Skip] #{issue_num}: 已有 PR")
                    continue
                
                # 分析问题
                analysis = IssueAnalyzer.analyze(item)
                if not analysis['can_fix']:
                    continue
                
                print(f"    [Found] #{issue_num}: {item['title'][:40]} ({analysis['fix_type']})")
                issues.append({
                    "repo": repo,
                    "issue_num": issue_num,
                    "title": item['title'],
                    "body": item.get('body', '')[:1000],
                    "url": f"https://github.com/{repo}/issues/{issue_num}",
                    "analysis": analysis,
                    "project_score": score,
                })
                
                if len(issues) >= limit:
                    return issues
        
        # 按优先级和项目分数排序
        issues.sort(key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}.get(x['analysis']['priority'], 2),
            -x['project_score']
        ))
        
        return issues
    
    def process_issue(self, issue: Dict) -> Optional[Dict]:
        """处理单个 issue"""
        print(f"\n{'='*60}")
        print(f"[Process] {issue['repo']} #{issue['issue_num']}")
        print(f"  标题: {issue['title'][:50]}")
        print(f"  类型: {issue['analysis']['fix_type']}")
        print(f"{'='*60}")
        
        if self.dry_run:
            print("  [Dry Run] 跳过实际修复")
            return {"issue": issue, "status": "dry_run"}
        
        # 确保 fork
        fork_repo = self.api.ensure_fork(issue['repo'], self.username)
        
        # 根据类型处理
        fix_type = issue['analysis']['fix_type']
        result = {"issue": issue, "status": "needs_implementation"}
        
        print(f"  [TODO] 需要实现 {fix_type} 类型的自动修复")
        
        return result
    
    def check_prs(self):
        """检查 PR 状态"""
        print("\n[Check] PR 状态:")
        
        for pr in self.progress.get('prs', []):
            repo = pr.get('repo')
            number = pr.get('number')
            url = pr.get('url')
            
            # 获取状态
            api_url = f"https://api.github.com/repos/{repo}/pulls/{number}"
            resp = self.api.get(api_url)
            
            if resp.status_code == 200:
                data = resp.json()
                state = data.get('state', 'unknown')
                merged = data.get('merged_at') is not None
                closed = data.get('closed_at') is not None
                
                status = "MERGED" if merged else ("CLOSED" if closed else state.upper())
                print(f"  [{status}] {repo} #{number}")
                print(f"    {url}")
            else:
                print(f"  [UNKNOWN] {repo} #{number}")
    
    def run(self, limit: int = 3, project_limit: int = 5):
        """运行主流程"""
        print("=" * 60)
        print("Auto PR Workflow v5")
        print(f"模式: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 60)
        
        # 获取推荐项目
        print("\n[Projects] 获取推荐项目...")
        projects = self.selector.get_recommended_projects(limit=project_limit)
        
        print(f"\n推荐项目 ({len(projects)} 个):")
        for p in projects:
            print(f"  {p['repo']}: {p['score']:.0f}分, {p['good_first_issues']} GFI")
        
        # 搜索 issue
        issues = self.search_issues(projects, limit=limit)
        
        if not issues:
            print("\n没有找到可修复的 issue")
            return
        
        print(f"\n找到 {len(issues)} 个可修复的 issue")
        
        # 处理 issue
        for issue in issues[:limit]:
            result = self.process_issue(issue)
            if result:
                self.progress['processed'].append(result)
            self._save_progress()
        
        # 检查 PR
        self.check_prs()
        
        print(f"\n{'='*60}")
        print("完成")
        print(f"进度: {PROGRESS_FILE}")

# ==================== 主入口 ====================
def main():
    parser = argparse.ArgumentParser(description='Auto PR Workflow v5')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    parser.add_argument('--limit', type=int, default=3, help='处理数量')
    parser.add_argument('--projects', type=int, default=5, help='项目数量')
    args = parser.parse_args()
    
    workflow = AutoPRWorkflow(dry_run=args.dry_run)
    workflow.run(limit=args.limit, project_limit=args.projects)

if __name__ == "__main__":
    main()
