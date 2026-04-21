#!/usr/bin/env python3
"""
Auto PR v6 - 友好项目优先
"""

import subprocess
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import requests

LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
PROGRESS_FILE = LOG_DIR / "auto_pr_v6.json"

FRIENDLY_PROJECTS = [
    "pandas-dev/pandas",
    "numpy/numpy",
    "pytest-dev/pytest",
]

class AutoPRv6:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.token = self._get_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }
    
    def _get_token(self) -> str:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
        return result.stdout.strip()
    
    def get_issues(self, repo: str, limit: int = 5) -> List[Dict]:
        """获取 good first issues"""
        cmd = 'gh issue list --repo {} --label "good first issue" --state open --limit {} --json number,title'.format(repo, limit)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            try:
                return json.loads(result.stdout)
            except:
                pass
        return []
    
    def check_has_pr(self, repo: str, issue_num: int) -> bool:
        """检查是否已有 PR"""
        cmd = 'gh pr list --repo {} --search "fixes #{}" --state open --json number'.format(repo, issue_num)
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and result.stdout:
            try:
                prs = json.loads(result.stdout)
                return len(prs) > 0
            except:
                pass
        return False
    
    def post_comment(self, repo: str, issue_num: int, body: str) -> bool:
        """发表评论"""
        url = "https://api.github.com/repos/{}/issues/{}/comments".format(repo, issue_num)
        data = {"body": body}
        resp = requests.post(url, headers=self.headers, json=data)
        return resp.status_code == 201
    
    def run(self, limit: int = 3):
        print("=" * 60)
        print("Auto PR v6 - 友好项目优先")
        print("模式:", "DRY RUN" if self.dry_run else "LIVE")
        print("=" * 60)
        
        all_issues = []
        
        for repo in FRIENDLY_PROJECTS:
            print("\n检查:", repo)
            issues = self.get_issues(repo, limit=5)
            
            for issue in issues:
                num = issue["number"]
                has_pr = self.check_has_pr(repo, num)
                
                if has_pr:
                    print("  [Skip] #{} - 已有 PR".format(num))
                else:
                    print("  [Found] #{} - {}".format(num, issue["title"][:40]))
                    all_issues.append({
                        "repo": repo,
                        "issue_num": num,
                        "title": issue["title"]
                    })
        
        print("\n找到 {} 个待处理 issue".format(len(all_issues)))
        
        # 提出解决方案
        for issue in all_issues[:limit]:
            self.propose_solution(issue)
        
        print("\n完成")
    
    def propose_solution(self, issue: Dict):
        """提出解决方案"""
        repo = issue["repo"]
        num = issue["issue_num"]
        
        print("\n[Propose] {} #{}".format(repo, num))
        
        comment = """Hi, I'd like to help with this issue.

I'm interested in contributing a fix. Could the maintainers provide some guidance on the preferred approach?

I'm happy to discuss the implementation before submitting a PR.

Thanks!
"""
        
        if self.dry_run:
            print("  [Dry Run] 跳过评论")
            print("  预览:", comment[:100])
        else:
            success = self.post_comment(repo, num, comment)
            if success:
                print("  成功发表评论")
            else:
                print("  发表评论失败")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    
    workflow = AutoPRv6(dry_run=args.dry_run)
    workflow.run(limit=args.limit)


if __name__ == "__main__":
    main()
