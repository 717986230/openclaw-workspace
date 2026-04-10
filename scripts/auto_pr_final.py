#!/usr/bin/env python3
"""
Auto PR System - 最终版本
"""

import subprocess
import json
import time
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# 配置
WORK_DIR = Path(r"D:\CODE\auto-pr-work")
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
PROGRESS_FILE = LOG_DIR / "auto_pr_progress.json"

SIMPLE_DOC_KEYWORDS = ["SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]

TARGET_REPOS = [
    {"repo": "python/cpython", "label": "easy"},
    {"repo": "pallets/click", "label": "good first issue"},
    {"repo": "psf/requests", "label": "good first issue"},
]

def run_cmd(cmd: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """执行命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, encoding='utf-8', errors='replace', timeout=timeout
        )
        return result
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
    return {}

def search_issues(limit: int = 5) -> List[Dict]:
    """搜索 issue"""
    print("\n[Search] 搜索 issue...")
    issues = []
    
    for config in TARGET_REPOS:
        repo = config['repo']
        label = config['label']
        
        print(f"  检查 {repo}...")
        result = run_cmd(
            f'gh issue list --repo {repo} --label "{label}" --state open --limit {limit} --json number,title,body',
            timeout=30
        )
        
        if result.returncode != 0:
            continue
        
        for item in json.loads(result.stdout):
            title = item.get('title', '')
            body = item.get('body', '')[:1000]
            
            if any(kw.lower() in title.lower() for kw in SIMPLE_DOC_KEYWORDS):
                print(f"    [Skip] #{item['number']}: 简单文档")
                continue
            
            # 检查是否已有 PR
            issue_detail = run_cmd(
                f'gh issue view {item["number"]} --repo {repo} --json closedAt,state --jq "{{closed: .closedAt, state: .state}}"',
                timeout=10
            )
            if issue_detail.returncode == 0:
                detail = json.loads(issue_detail.stdout)
                if detail.get('closed'):
                    print(f"    [Skip] #{item['number']}: 已关闭")
                    continue
            
            print(f"    [Found] #{item['number']}: {title[:40]}")
            issues.append({
                "repo": repo,
                "issue_num": item["number"],
                "title": title,
                "body": body,
                "url": f"https://github.com/{repo}/issues/{item['number']}"
            })
    
    return issues

def analyze_issue(issue: Dict) -> Dict:
    """分析 issue"""
    print(f"\n[Analyze] #{issue['issue_num']}: {issue['title'][:50]}")
    
    analysis = {
        "issue": issue,
        "problem_type": None,
        "can_auto_fix": False,
        "fix_plan": []
    }
    
    title_lower = issue['title'].lower()
    
    if 'dead' in title_lower or 'url' in title_lower or 'link' in title_lower:
        analysis['problem_type'] = 'dead_url'
        analysis['can_auto_fix'] = True
        urls = re.findall(r'https?://[^\s\'"<>]+', issue.get('body', ''))
        analysis['fix_plan'].append({"action": "replace_url", "urls": urls[:5]})
    
    elif 'typo' in title_lower or 'spelling' in title_lower:
        analysis['problem_type'] = 'typo'
        analysis['can_auto_fix'] = True
    
    elif 'error' in title_lower or 'wrong' in title_lower:
        analysis['problem_type'] = 'bug'
        analysis['can_auto_fix'] = False
    
    return analysis

def process_issue(issue: Dict, dry_run: bool = True) -> Dict:
    """处理单个 issue"""
    print(f"\n{'='*60}")
    print(f"[Process] {issue['repo']} #{issue['issue_num']}")
    print(f"{'='*60}")
    
    analysis = analyze_issue(issue)
    
    result = {
        "issue": issue,
        "status": "analyzed",
        "analysis": analysis,
        "pr_url": None
    }
    
    if not analysis['can_auto_fix']:
        print("  [Skip] 无法自动修复")
        result['status'] = 'needs_manual'
        return result
    
    print(f"  类型: {analysis['problem_type']}")
    print(f"  可自动修复: {analysis['can_auto_fix']}")
    
    if dry_run:
        print("  [Dry Run] 跳过实际修复")
        result['status'] = 'dry_run_complete'
    else:
        # 实际修复逻辑（这里只是占位）
        print("  [TODO] 实现实际修复逻辑")
        result['status'] = 'pending_implementation'
    
    return result

def main():
    parser = argparse.ArgumentParser(description='Auto PR System')
    parser.add_argument('--dry-run', action='store_true', help='模拟运行')
    parser.add_argument('--limit', type=int, default=3, help='处理数量')
    args = parser.parse_args()
    
    print("=" * 60)
    print("Auto PR System")
    print(f"模式: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print("=" * 60)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    progress = load_json(PROGRESS_FILE)
    processed = {p.get('issue', {}).get('issue_num') for p in progress.get('results', [])}
    
    issues = search_issues(limit=args.limit)
    issues = [i for i in issues if i['issue_num'] not in processed]
    
    print(f"\n待处理: {len(issues)} 个新 issue")
    
    for issue in issues[:args.limit]:
        result = process_issue(issue, dry_run=args.dry_run)
        progress.setdefault('results', []).append(result)
        save_json(progress, PROGRESS_FILE)
    
    print(f"\n{'='*60}")
    print("总结:")
    for r in progress.get('results', [])[-args.limit:]:
        status = r.get('status', 'unknown')
        issue = r.get('issue', {})
        print(f"  [{status}] {issue.get('repo')} #{issue.get('issue_num')}: {issue.get('title', '')[:30]}")
    
    print(f"\n详细结果: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
