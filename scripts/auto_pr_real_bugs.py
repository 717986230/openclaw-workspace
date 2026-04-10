#!/usr/bin/env python3
"""
Real Bug Fix PR - 修复真正的 bug，不是简单的文档
"""

import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(r"D:\CODE\auto-pr-work")

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

def find_real_bugs():
    """找真正的 bug，不是简单的文档问题"""
    bugs = []
    
    # Vue - 类型定义问题
    result = run_cmd('gh issue view 10252 --repo vuejs/vue --json title,body,labels')
    if result.returncode == 0:
        bugs.append({
            "repo": "vuejs/vue",
            "issue_num": 10252,
            "title": "Fix: Wrong definition of AsyncComponentFactory",
            "type": "bug"
        })
    
    # React - Firefox breakpoint 问题
    result = run_cmd('gh issue view 17355 --repo facebook/react --json title,body')
    if result.returncode == 0:
        bugs.append({
            "repo": "facebook/react", 
            "issue_num": 17355,
            "title": "Fix: Firefox breakpoint issue",
            "type": "bug"
        })
    
    # freeCodeCamp - typo
    result = run_cmd('gh issue list --repo freeCodeCamp/freeCodeCamp --search "typo" --limit 5 --state open --json number,title')
    if result.returncode == 0:
        for item in json.loads(result.stdout)[:2]:
            bugs.append({
                "repo": "freeCodeCamp/freeCodeCamp",
                "issue_num": item["number"],
                "title": item["title"],
                "type": "typo"
            })
    
    return bugs

def create_real_bug_pr(bug):
    """创建真正的 bug 修复 PR"""
    print(f"\n{'='*60}")
    print(f"Creating PR for REAL BUG: {bug['repo']} #{bug['issue_num']}")
    print(f"Title: {bug['title']}")
    print(f"{'='*60}")
    
    repo = bug["repo"]
    issue_num = bug["issue_num"]
    
    # 获取 issue 详情
    issue_result = run_cmd(f'gh issue view {issue_num} --repo {repo} --json title,body,comments')
    if issue_result.returncode != 0:
        print("Failed to get issue details")
        return None
    
    issue_data = json.loads(issue_result.stdout)
    print(f"\nIssue Description:\n{issue_data.get('body', '')[:500]}")
    
    # Fork
    user_result = run_cmd("gh api user --jq .login")
    username = user_result.stdout.strip()
    fork_repo = f"{username}/{repo.split('/')[-1]}"
    
    print(f"\n1. Checking fork...")
    check = run_cmd(f"gh repo view {fork_repo}")
    if check.returncode != 0:
        print(f"Forking {repo}...")
        run_cmd(f"gh repo fork {repo} --clone=false")
        time.sleep(5)
    
    # Clone
    work_path = WORK_DIR / repo.replace("/", "-")
    if work_path.exists():
        import shutil
        try:
            shutil.rmtree(work_path)
        except:
            pass
    work_path.mkdir(parents=True, exist_ok=True)
    
    print(f"2. Cloning...")
    run_cmd(f"git clone --depth 100 https://github.com/{fork_repo}.git {work_path}")
    
    if not (work_path / ".git").exists():
        print("Clone failed")
        return None
    
    # 分析问题并尝试修复
    print(f"3. Analyzing issue #{issue_num}...")
    
    # 根据不同类型的 bug 应用不同修复策略
    if bug["type"] == "typo":
        # 对于 typo，直接修复
        print("Looking for typo in code...")
        # 这里需要实际分析代码找 typo
        
    # Commit
    print("4. Creating fix branch...")
    run_cmd(f'git -C {work_path} config user.email "erbing@openclaw.ai"')
    run_cmd(f'git -C {work_path} config user.name "Erbing"')
    
    branch = f"fix-issue-{issue_num}"
    run_cmd(f'git -C {work_path} checkout -b {branch}')
    
    # 这里应该有实际的代码修复
    # 暂时标记为需要进一步分析
    print(f"\nNOTE: This issue requires manual code analysis to fix.")
    print(f"Issue link: https://github.com/{repo}/issues/{issue_num}")
    
    # 保存 issue 信息
    issue_info = {
        "repo": repo,
        "issue_num": issue_num,
        "title": bug["title"],
        "url": f"https://github.com/{repo}/issues/{issue_num}",
        "body": issue_data.get("body", "")[:1000]
    }
    
    return issue_info

def main():
    print("=" * 60)
    print("Real Bug Fix PR System")
    print("Finding and fixing REAL bugs, not simple docs")
    print("=" * 60)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    bugs = find_real_bugs()
    print(f"\nFound {len(bugs)} real bugs to fix")
    
    results = []
    for bug in bugs[:3]:
        result = create_real_bug_pr(bug)
        if result:
            results.append(result)
    
    print(f"\n{'='*60}")
    print("Summary:")
    for r in results:
        print(f"\n{r['repo']} #{r['issue_num']}:")
        print(f"  Title: {r['title']}")
        print(f"  Link: {r['url']}")
        print(f"  Description: {r['body'][:200]}...")
    
    # 保存结果
    import json
    result_path = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\real_bugs_found.json")
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {result_path}")

if __name__ == "__main__":
    main()
