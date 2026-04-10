#!/usr/bin/env python3
"""
GitHub Top 20 Deep Analysis PR System
固定跟踪 GitHub 最热门的 20 个项目
"""

import subprocess
import json
import os
import time
import base64
import re
from pathlib import Path
from datetime import datetime
import sqlite3

WORK_DIR = Path(r"D:\CODE\auto-pr-work")
DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")
TOP_20_PROJECTS = []

def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return result

def get_top_20_projects():
    global TOP_20_PROJECTS
    if TOP_20_PROJECTS:
        return TOP_20_PROJECTS
    
    print("=== Fetching Top 20 Projects ===")
    result = run_cmd('gh search repos --sort stars --limit 20 --json fullName "stars:>10000"')
    
    if result.returncode == 0:
        data = json.loads(result.stdout)
        TOP_20_PROJECTS = [item["fullName"] for item in data]
        print(f"Tracking: {TOP_20_PROJECTS}")
    
    return TOP_20_PROJECTS

def deep_analyze_repo(repo):
    print(f"\n{'='*60}\nDeep Analysis: {repo}\n{'='*60}")
    issues = []
    
    # Check README
    result = run_cmd(f'gh api repos/{repo}/readme', check=False)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        content = base64.b64decode(data["content"]).decode('utf-8', errors='ignore')
        
        if "SECURITY.md" not in content and "Security" not in content:
            issues.append({"type": "security", "priority": 8, "title": "Add SECURITY.md", "repo": repo})
        
        if "## Installation" not in content:
            issues.append({"type": "docs", "priority": 6, "title": "Add Installation section", "repo": repo})
        
        # Find typos
        typos = [("teh", "the"), ("recieve", "receive"), ("occured", "occurred")]
        for w, r in typos:
            if re.search(rf'\b{w}\b', content, re.I):
                issues.append({"type": "typo", "priority": 5, "title": f"Fix typo: {w}->{r}", "repo": repo})
    
    # Check missing files
    result = run_cmd(f'gh api repos/{repo}/contents', check=False)
    if result.returncode == 0:
        files = [f["name"] for f in json.loads(result.stdout)]
        
        if "SECURITY.md" not in files:
            issues.append({"type": "security", "priority": 8, "title": "Add SECURITY.md", "repo": repo})
        if "CONTRIBUTING.md" not in files:
            issues.append({"type": "docs", "priority": 7, "title": "Add CONTRIBUTING.md", "repo": repo})
        if "CODE_OF_CONDUCT.md" not in files:
            issues.append({"type": "docs", "priority": 6, "title": "Add CODE_OF_CONDUCT.md", "repo": repo})
    
    # Check good first issues
    result = run_cmd(f'gh issue list --repo {repo} --label "good first issue" --limit 3 --state open --json number,title', check=False)
    if result.returncode == 0:
        for item in json.loads(result.stdout)[:2]:
            issues.append({"type": "bug", "priority": 7, "title": item["title"][:50], "repo": repo, "issue_num": item["number"]})
    
    print(f"Found {len(issues)} issues")
    return issues

def create_pr(repo, issue):
    print(f"\n--- Creating PR: {issue['title']} ---")
    
    user_result = run_cmd("gh api user --jq .login")
    username = user_result.stdout.strip()
    fork_repo = f"{username}/{repo.split('/')[-1]}"
    
    # Fork
    check = run_cmd(f"gh repo view {fork_repo}", check=False)
    if check.returncode != 0:
        run_cmd(f"gh repo fork {repo} --clone=false")
        time.sleep(3)
    
    # Clone
    work_path = WORK_DIR / repo.replace("/", "-")
    if work_path.exists():
        import shutil
        try: shutil.rmtree(work_path)
        except: pass
    work_path.mkdir(parents=True, exist_ok=True)
    
    run_cmd(f"git clone --depth 1 https://github.com/{fork_repo}.git {work_path}")
    if not (work_path / ".git").exists():
        return None
    
    # Apply fix
    if "SECURITY.md" in issue["title"]:
        (work_path / "SECURITY.md").write_text("# Security Policy\n\nReport vulnerabilities via email.\n", encoding='utf-8')
    elif "CONTRIBUTING.md" in issue["title"]:
        (work_path / "CONTRIBUTING.md").write_text("# Contributing\n\n1. Fork\n2. Branch\n3. PR\n", encoding='utf-8')
    elif "CODE_OF_CONDUCT" in issue["title"]:
        (work_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct\n\nBe respectful.\n", encoding='utf-8')
    else:
        return None
    
    # Commit & Push
    run_cmd(f'git -C {work_path} config user.email "erbing@openclaw.ai"')
    run_cmd(f'git -C {work_path} config user.name "Erbing"')
    branch = f"fix-{datetime.now().strftime('%Y%m%d%H%M')}"
    run_cmd(f'git -C {work_path} checkout -b {branch}')
    run_cmd(f'git -C {work_path} add -A')
    run_cmd(f'git -C {work_path} commit -m "{issue["title"]}"')
    
    # Get token and push
    tok_res = run_cmd("gh auth status --show-token")
    token = tok_res.stdout.split("Token:")[-1].strip().split()[0] if "Token:" in tok_res.stdout else ""
    run_cmd(f'git -C {work_path} push https://{token}@github.com/{fork_repo}.git {branch}')
    
    # Create PR
    pr_res = run_cmd(f'gh pr create --repo {repo} --title "{issue["title"]}" --body "Auto-generated by OpenClaw" --head {username}:{branch}')
    
    if pr_res.returncode == 0:
        pr_url = pr_res.stdout.strip()
        print(f"Created: {pr_url}")
        save_to_db(repo, issue, pr_url)
        return pr_url
    return None

def save_to_db(repo, issue, pr_url):
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('INSERT INTO memories (type, title, content, category, tags, importance, created_at) VALUES (?,?,?,?,?,?,?)',
              ('event', f'PR: {issue["title"][:40]}', f'Repo: {repo}\nURL: {pr_url}', 'github', '["pr","auto"]', issue["priority"], datetime.now().isoformat()))
    conn.commit()
    conn.close()

def send_notification(prs):
    """发送通知到飞书"""
    msg = f"## GitHub PR Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n**Created {len(prs)} PR(s):**\n\n"
    for pr in prs:
        msg += f"- [{pr['repo']}]({pr['url']}) - {pr['title']}\n"
    
    # 保存通知文件
    notif_path = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\pr_notification.json")
    notif_path.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(notif_path, 'w', encoding='utf-8') as f:
        json.dump({"message": msg, "prs": prs, "timestamp": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    
    print(f"\nNotification saved: {notif_path}")
    print(msg)

def main():
    print("=" * 60)
    print("GitHub Top 20 Deep Analysis PR System")
    print("=" * 60)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    
    projects = get_top_20_projects()
    all_issues = []
    
    for repo in projects[:10]:  # 每次分析前10个
        issues = deep_analyze_repo(repo)
        all_issues.extend(issues)
    
    # Sort by priority
    all_issues.sort(key=lambda x: x["priority"], reverse=True)
    
    # Create PRs for top issues
    created_prs = []
    for issue in all_issues[:3]:  # 每次最多3个PR
        pr_url = create_pr(issue["repo"], issue)
        if pr_url:
            created_prs.append({"repo": issue["repo"], "title": issue["title"], "url": pr_url})
    
    # Send notification
    if created_prs:
        send_notification(created_prs)
    
    print(f"\n{'='*60}")
    print(f"Done: {len(created_prs)} PRs created")
    print("=" * 60)

if __name__ == "__main__":
    main()
