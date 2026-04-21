#!/usr/bin/env python3
"""
Auto PR System v4 - 完整工作流版本

功能：
1. 自动搜索有价值的 issue（排除简单文档）
2. 检查是否已有 PR
3. 分析问题并生成修复方案
4. 通过 GitHub API 提交修复（无需 git clone）
5. 自动创建 PR
6. 跟踪 PR 状态

使用方法：
    python auto_pr_workflow.py [--dry-run] [--limit N] [--check-pr]
"""

import subprocess
import json
import time
import re
import base64
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import requests

# ==================== 配置 ====================
WORK_DIR = Path(r"D:\CODE\auto-pr-work")
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
CACHE_DIR = LOG_DIR / "cache"
PROGRESS_FILE = LOG_DIR / "auto_pr_progress_v4.json"

# 排除的简单关键词
SIMPLE_DOC_KEYWORDS = [
    "SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
    "添加文档", "add documentation", "typo", "spelling"
]

# 目标仓库配置
TARGET_REPOS = [
    {"repo": "pallets/click", "label": "good first issue"},
    {"repo": "psf/requests", "label": "bug"},
    {"repo": "python/cpython", "label": "easy"},
    {"repo": "pallets/flask", "label": "good first issue"},
]

# ==================== 工具函数 ====================
def run_cmd(cmd: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """执行命令"""
    try:
        return subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, encoding='utf-8', errors='replace', timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(cmd, 1, '', 'timeout')

def save_json(data: Dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path: Path) -> Dict:
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "prs": []}

def get_github_token() -> str:
    """获取 GitHub token"""
    result = run_cmd("gh auth token", timeout=10)
    return result.stdout.strip()

def get_github_username() -> str:
    """获取用户名"""
    result = run_cmd("gh api user --jq .login", timeout=10)
    return result.stdout.strip()

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
    
    def get_file_content(self, repo: str, path: str, ref: str = "main") -> Tuple[str, str]:
        """获取文件内容和 SHA"""
        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
        resp = self.get(url)
        if resp.status_code == 200:
            data = resp.json()
            content = base64.b64decode(data['content']).decode('utf-8')
            return content, data['sha']
        return "", ""
    
    def update_file(self, repo: str, path: str, content: str, sha: str, message: str, branch: str = "main") -> bool:
        """更新文件"""
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
        data = {
            "message": message,
            "content": content_b64,
            "sha": sha,
            "branch": branch
        }
        resp = self.put(url, data)
        return resp.status_code == 200
    
    def create_pr(self, repo: str, title: str, body: str, head: str, base: str = "main") -> Optional[str]:
        """创建 PR"""
        url = f"https://api.github.com/repos/{repo}/pulls"
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        resp = self.post(url, data)
        if resp.status_code == 201:
            return resp.json()['html_url']
        return None
    
    def get_issue(self, repo: str, number: int) -> Dict:
        """获取 issue 详情"""
        url = f"https://api.github.com/repos/{repo}/issues/{number}"
        resp = self.get(url)
        return resp.json() if resp.status_code == 200 else {}
    
    def get_pr_status(self, repo: str, number: int) -> Dict:
        """获取 PR 状态"""
        url = f"https://api.github.com/repos/{repo}/pulls/{number}"
        resp = self.get(url)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "state": data['state'],
                "merged": data.get('merged_at') is not None,
                "closed": data.get('closed_at') is not None,
                "mergeable": data.get('mergeable'),
                "reviews": len(data.get('reviews', []))
            }
        return {}
    
    def check_existing_pr(self, repo: str, issue_num: int) -> List[Dict]:
        """检查是否已有相关 PR"""
        url = f"https://api.github.com/repos/{repo}/pulls"
        params = {"state": "all", "per_page": 100}
        resp = self.get(url + "?" + "&".join(f"{k}={v}" for k, v in params.items()))
        if resp.status_code == 200:
            prs = resp.json()
            # 查找包含 issue 编号的 PR
            return [pr for pr in prs 
                    if pr.get('title') and pr.get('body') and 
                    (f"#{issue_num}" in pr.get('title', '') or f"#{issue_num}" in pr.get('body', ''))]
        return []
    
    def ensure_fork(self, repo: str) -> str:
        """确保 fork 存在"""
        username = get_github_username()
        fork_repo = f"{username}/{repo.split('/')[-1]}"
        
        # 检查 fork 是否存在
        url = f"https://api.github.com/repos/{fork_repo}"
        resp = self.get(url)
        
        if resp.status_code != 200:
            # 创建 fork
            print(f"  Creating fork: {fork_repo}")
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
            "needs_clarification": False
        }
        
        # 排除简单文档问题
        if any(kw in title_lower or kw in body_lower for kw in SIMPLE_DOC_KEYWORDS):
            result["fix_type"] = "simple_doc"
            return result
        
        # 检测问题类型
        if 'error' in title_lower or 'wrong' in title_lower or 'bug' in title_lower:
            result["can_fix"] = True
            result["fix_type"] = "bug"
            result["priority"] = "high"
        
        elif 'missing' in title_lower or 'not' in title_lower or "doesn't" in title_lower:
            result["can_fix"] = True
            result["fix_type"] = "missing_feature"
            result["priority"] = "medium"
        
        elif 'inconsistent' in title_lower:
            result["can_fix"] = True
            result["fix_type"] = "consistency"
            result["priority"] = "medium"
        
        elif 'policy' in title_lower or 'preserve' in title_lower:
            result["can_fix"] = True
            result["fix_type"] = "behavior"
            result["priority"] = "medium"
        
        return result

# ==================== 主工作流 ====================
class AutoPRWorkflow:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.token = get_github_token()
        self.api = GitHubAPI(self.token)
        self.username = get_github_username()
        self.progress = load_json(PROGRESS_FILE)
    
    def search_issues(self, limit: int = 10) -> List[Dict]:
        """搜索可修复的 issue"""
        print("\n[Search] 搜索 issue...")
        issues = []
        
        for config in TARGET_REPOS:
            repo = config['repo']
            label = config['label']
            
            print(f"\n  检查 {repo}...")
            result = run_cmd(
                f'gh issue list --repo {repo} --label "{label}" '
                f'--state open --limit {limit} --json number,title,body',
                timeout=30
            )
            
            if result.returncode != 0:
                continue
            
            for item in json.loads(result.stdout):
                # 检查是否已处理
                processed_nums = [p.get('issue_num') for p in self.progress.get('processed', [])]
                if item['number'] in processed_nums:
                    continue
                
                # 检查是否已有 PR
                existing_prs = self.api.check_existing_pr(repo, item['number'])
                if existing_prs:
                    print(f"    [Skip] #{item['number']}: 已有 PR")
                    continue
                
                # 分析问题
                analysis = IssueAnalyzer.analyze(item)
                if not analysis['can_fix']:
                    continue
                
                print(f"    [Found] #{item['number']}: {item['title'][:40]} ({analysis['fix_type']})")
                issues.append({
                    "repo": repo,
                    "issue_num": item['number'],
                    "title": item['title'],
                    "body": item.get('body', '')[:1000],
                    "url": f"https://github.com/{repo}/issues/{item['number']}",
                    "analysis": analysis
                })
        
        # 按优先级排序
        issues.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x['analysis']['priority'], 2))
        
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
        
        # 确保 fork 存在
        fork_repo = self.api.ensure_fork(issue['repo'])
        
        # 根据问题类型应用修复
        fix_type = issue['analysis']['fix_type']
        
        if fix_type == "bug":
            result = self.fix_bug(issue, fork_repo)
        elif fix_type == "behavior":
            result = self.fix_behavior(issue, fork_repo)
        else:
            result = self.fix_generic(issue, fork_repo)
        
        return result
    
    def fix_bug(self, issue: Dict, fork_repo: str) -> Dict:
        """修复 bug 类型问题"""
        # 这里需要根据具体问题实现
        # 目前只是占位
        print("  [TODO] Bug 修复逻辑需要具体实现")
        return {"issue": issue, "status": "needs_implementation"}
    
    def fix_behavior(self, issue: Dict, fork_repo: str) -> Dict:
        """修复行为问题（如 cookie policy）"""
        print("  [Fix] 检查行为问题...")
        
        # 根据 issue 内容决定修复策略
        # 这里可以添加更多自动化逻辑
        
        return {"issue": issue, "status": "needs_implementation"}
    
    def fix_generic(self, issue: Dict, fork_repo: str) -> Dict:
        """通用修复"""
        print("  [Fix] 需要人工分析具体问题")
        return {"issue": issue, "status": "needs_manual_fix"}
    
    def check_prs(self):
        """检查已创建的 PR 状态"""
        print("\n[Check] 检查 PR 状态...")
        
        for pr in self.progress.get('prs', []):
            repo = pr.get('repo')
            number = pr.get('number')
            url = pr.get('url')
            
            status = self.api.get_pr_status(repo, number)
            
            state_icon = "OPEN" if status.get('state') == 'open' else "CLOSED"
            merged_icon = "MERGED" if status.get('merged') else ""
            
            print(f"  [{state_icon}] {merged_icon} {repo} #{number}: {url}")
    
    def save_progress(self):
        """保存进度"""
        save_json(self.progress, PROGRESS_FILE)
    
    def run(self, limit: int = 3):
        """运行主流程"""
        print("=" * 60)
        print("Auto PR Workflow v4")
        print(f"模式: {'DRY RUN' if self.dry_run else 'LIVE'}")
        print("=" * 60)
        
        # 搜索 issue
        issues = self.search_issues()
        
        if not issues:
            print("\n没有找到可修复的 issue")
            return
        
        print(f"\n找到 {len(issues)} 个可修复的 issue")
        
        # 处理 issue
        for issue in issues[:limit]:
            result = self.process_issue(issue)
            if result:
                self.progress['processed'].append(result)
                if result.get('pr_url'):
                    self.progress['prs'].append({
                        "repo": issue['repo'],
                        "number": result['pr_number'],
                        "url": result['pr_url']
                    })
            self.save_progress()
        
        # 检查 PR 状态
        self.check_prs()
        
        print(f"\n{'='*60}")
        print("完成")
        print(f"进度文件: {PROGRESS_FILE}")

# ==================== 主入口 ====================
def main():
    parser = argparse.ArgumentParser(description='Auto PR Workflow')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    parser.add_argument('--limit', type=int, default=3, help='处理数量')
    parser.add_argument('--check-pr', action='store_true', help='只检查 PR 状态')
    args = parser.parse_args()
    
    workflow = AutoPRWorkflow(dry_run=args.dry_run)
    
    if args.check_pr:
        workflow.check_prs()
    else:
        workflow.run(limit=args.limit)

if __name__ == "__main__":
    main()
