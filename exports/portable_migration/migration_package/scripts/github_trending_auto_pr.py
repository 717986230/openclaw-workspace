#!/usr/bin/env python3
"""
GitHub Trending Auto PR System - Complete Version
每小时扫描前20热门项目，自动发现问题并提交PR
"""

import os
import sys
import json
import sqlite3
import subprocess
import time
import re
import base64
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import argparse

# Configuration
DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")
WORK_DIR = Path(r"D:\CODE\auto-pr-workspace")
MAX_PROJECTS = 20
MAX_PRS_PER_RUN = 3
LANGUAGES = ["python", "javascript", "typescript", "go", "rust"]
EXCLUDE_REPOS = ["public-apis/public-apis"]

@dataclass
class Issue:
    repo: str
    type: str
    file: str
    line: int
    description: str
    fix_description: str
    priority: int
    code_snippet: str = ""
    fix_code: str = ""
    issue_number: int = 0

@dataclass
class PRResult:
    repo: str
    issue_type: str
    pr_url: str
    status: str
    timestamp: str
    details: str

def run_cmd(cmd, check=True, encoding='utf-8'):
    """Run command with proper encoding"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding=encoding, errors='replace')
    if check and result.returncode != 0:
        print(f"Error: {result.stderr[:200]}")
    return result

def get_github_token() -> str:
    """Get GitHub token"""
    result = run_gh(["auth", "status", "--show-token"])
    if result.returncode == 0:
        for line in result.stdout.split('\n'):
            if "Token:" in line:
                return line.split("Token:")[-1].strip()
    return ""

def discover_trending(language: str, limit: int = 20) -> List[Dict]:
    """Discover trending repositories"""
    print(f"=== Discovering trending {language} repos ===")
    
    repos = []
    
    result = run_gh([
        "search", "repos",
        "--language", language,
        "--sort", "stars",
        "--order", "desc",
        "--limit", str(limit),
        "--json", "fullName,description,forksCount",
        "stars:>1000"
    ])
    
    if result is None:
        print("Error: gh command failed")
        return repos
    
    if result.returncode == 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            for item in data:
                name = item.get("fullName", "")
                if name and name not in EXCLUDE_REPOS:
                    repos.append({
                        "full_name": name,
                        "stars": item.get("forksCount", 0) * 10,
                        "language": language,
                        "open_issues": 0,
                        "url": f"https://github.com/{name}"
                    })
        except json.JSONDecodeError as e:
            print(f"JSON error: {e}")
    
    print(f"Found {len(repos)} repos")
    return repos

def find_good_first_issues(repo: str) -> List[Issue]:
    """Find good first issues"""
    issues = []
    
    result = run_gh([
        "issue", "list",
        "--repo", repo,
        "--label", "good first issue,help wanted,bug",
        "--limit", "5",
        "--state", "open",
        "--json", "number,title,labels"
    ])
    
    if result.returncode == 0:
        try:
            for item in json.loads(result.stdout):
                labels = [l["name"] for l in item.get("labels", [])]
                itype = "bug" if "bug" in labels else "docs"
                issues.append(Issue(
                    repo=repo, type=ityp, file="", line=0,
                    description=item.get("title", ""),
                    fix_description=f"Fix #{item['number']}",
                    priority=8,
                    issue_number=item.get("number", 0)
                ))
        except:
            pass
    
    return issues

def find_typos(repo: str) -> List[Issue]:
    """Find typos in README"""
    issues = []
    
    result = run_gh(["api", f"repos/{repo}/readme"])
    if result.returncode != 0:
        return issues
    
    try:
        data = json.loads(result.stdout)
        content = base64.b64decode(data["content"]).decode('utf-8', errors='ignore')
        
        typos = [
            ("teh", "the"), ("hte", "the"), ("wiht", "with"),
            ("recieve", "receive"), ("occured", "occurred"),
            ("untill", "until"), ("accomodate", "accommodate"),
        ]
        
        for wrong, right in typos:
            if re.search(rf'\b{wrong}\b', content, re.I):
                line = content[:content.lower().find(wrong)].count('\n') + 1
                issues.append(Issue(
                    repo=repo, type="typo", file="README.md", line=line,
                    description=f"Typo: {wrong} -> {right}",
                    fix_description=f"Fix typo: {wrong} -> {right}",
                    priority=7, fix_code=right
                ))
    except:
        pass
    
    return issues

def find_missing_files(repo: str, stars: int) -> List[Issue]:
    """Check for missing important files"""
    issues = []
    
    result = run_gh(["api", f"repos/{repo}/contents"])
    if result.returncode != 0:
        return issues
    
    try:
        files = [f["name"] for f in json.loads(result.stdout)]
        
        if stars > 1000 and "CONTRIBUTING.md" not in files:
            issues.append(Issue(
                repo=repo, type="docs", file="CONTRIBUTING.md", line=0,
                description="Missing CONTRIBUTING.md",
                fix_description="Add CONTRIBUTING.md",
                priority=6
            ))
        
        if stars > 500 and "SECURITY.md" not in files:
            issues.append(Issue(
                repo=repo, type="security", file="SECURITY.md", line=0,
                description="Missing SECURITY.md",
                fix_description="Add SECURITY.md",
                priority=8
            ))
    except:
        pass
    
    return issues

def analyze_repo(repo: Dict) -> List[Issue]:
    """Analyze repository for issues"""
    print(f"\n=== Analyzing {repo['full_name']} ===")
    print(f"Stars: {repo['stars']:,} | Issues: {repo['open_issues']}")
    
    all_issues = []
    all_issues.extend(find_good_first_issues(repo["full_name"]))
    all_issues.extend(find_typos(repo["full_name"]))
    all_issues.extend(find_missing_files(repo["full_name"], repo["stars"]))
    
    print(f"Found {len(all_issues)} potential issues")
    return all_issues

def fork_and_clone(repo: str) -> Optional[Path]:
    """Fork and clone repository"""
    safe_name = repo.replace("/", "-")
    work_path = WORK_DIR / safe_name
    
    if work_path.exists():
        shutil.rmtree(work_path)
    work_path.mkdir(parents=True, exist_ok=True)
    
    # Get username
    user_result = run_gh(["api", "user", "--jq", ".login"])
    if user_result.returncode != 0:
        return None
    username = user_result.stdout.strip()
    
    fork_repo = f"{username}/{repo.split('/')[-1]}"
    
    # Create fork if needed
    check = run_gh(["repo", "view", fork_repo])
    if check.returncode != 0:
        print(f"Forking {repo}...")
        run_gh(["repo", "fork", repo, "--clone=false"])
        time.sleep(2)
    
    # Clone
    print(f"Cloning {fork_repo}...")
    subprocess.run(
        ["git", "clone", f"https://github.com/{fork_repo}.git", str(work_path)],
        capture_output=True
    )
    
    if not (work_path / ".git").exists():
        return None
    
    subprocess.run(
        ["git", "-C", str(work_path), "remote", "add", "upstream", f"https://github.com/{repo}.git"],
        capture_output=True
    )
    
    return work_path

def apply_fix(work_path: Path, issue: Issue) -> bool:
    """Apply fix based on issue type"""
    
    if issue.type == "typo":
        readme = work_path / "README.md"
        if readme.exists():
            content = readme.read_text(encoding='utf-8', errors='ignore')
            # Find and replace the typo
            for wrong in ["teh", "hte", "wiht", "recieve", "occured", "untill", "accomodate"]:
                if wrong in content.lower():
                    pattern = re.compile(re.escape(wrong), re.I)
                    content = pattern.sub(issue.fix_code if issue.fix_code else wrong, content)
            readme.write_text(content, encoding='utf-8')
            return True
    
    elif issue.type == "docs" and "CONTRIBUTING.md" in issue.file:
        content = """# Contributing

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Code of Conduct

Please be respectful and constructive.
"""
        (work_path / "CONTRIBUTING.md").write_text(content, encoding='utf-8')
        return True
    
    elif issue.type == "security" and "SECURITY.md" in issue.file:
        content = """# Security Policy

## Reporting a Vulnerability

Please email the maintainers for security issues.

Do not create public issues for security vulnerabilities.

## Supported Versions

Only the latest version is supported.
"""
        (work_path / "SECURITY.md").write_text(content, encoding='utf-8')
        return True
    
    return False

def create_pr(repo: str, issue: Issue) -> Optional[PRResult]:
    """Create PR for an issue"""
    print(f"\n--- Creating PR: {issue.type} for {repo} ---")
    
    work_path = fork_and_clone(repo)
    if not work_path:
        return None
    
    if not apply_fix(work_path, issue):
        print("Could not apply fix")
        return None
    
    # Configure git
    subprocess.run(["git", "-C", str(work_path), "config", "user.email", "erbing@openclaw.ai"], capture_output=True)
    subprocess.run(["git", "-C", str(work_path), "config", "user.name", "Erbing (OpenClaw AI)"], capture_output=True)
    
    # Create branch
    branch = f"fix-{issue.type}-{hashlib.md5(issue.description.encode()).hexdigest()[:8]}"
    subprocess.run(["git", "-C", str(work_path), "checkout", "-b", branch], capture_output=True)
    
    # Commit
    subprocess.run(["git", "-C", str(work_path), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(work_path), "commit", "-m", f"Fix: {issue.fix_description}"], capture_output=True)
    
    # Push
    token = get_github_token()
    user_result = run_gh(["api", "user", "--jq", ".login"])
    username = user_result.stdout.strip() if user_result.returncode == 0 else "unknown"
    
    push_url = f"https://{token}@github.com/{username}/{repo.split('/')[-1]}.git"
    subprocess.run(["git", "-C", str(work_path), "push", push_url, branch], capture_output=True)
    
    # Create PR
    pr_body = f"""## Summary
{issue.fix_description}

## Changes
- {issue.description}

## Type
{issue.type}

{'Fixes #' + str(issue.issue_number) if issue.issue_number else ''}
"""
    
    pr_result = run_gh([
        "pr", "create",
        "--repo", repo,
        "--title", f"Fix: {issue.fix_description}",
        "--body", pr_body,
        "--base", "main",
        "--head", f"{username}:{branch}"
    ])
    
    if pr_result.returncode == 0:
        pr_url = pr_result.stdout.strip()
        print(f"PR created: {pr_url}")
        return PRResult(
            repo=repo,
            issue_type=issue.type,
            pr_url=pr_url,
            status="created",
            timestamp=datetime.now().isoformat(),
            details=issue.description
        )
    
    return None

def save_to_db(result: PRResult):
    """Save PR result to database"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('event', f'PR Created: {result.repo}', 
          f"Type: {result.issue_type}\nURL: {result.pr_url}\nDetails: {result.details}",
          'github', '["pr", "auto"]', 8, result.timestamp))
    
    conn.commit()
    conn.close()

def sync_db():
    """Sync database to LanceDB"""
    sync_script = DB_PATH.parent / "sync_to_lancedb.py"
    if sync_script.exists():
        subprocess.run(["python", str(sync_script)], capture_output=True)

def run_hourly():
    """Run hourly scan"""
    print("=" * 60)
    print(f"GitHub Trending Auto PR - {datetime.now().isoformat()}")
    print("=" * 60)
    
    all_issues = []
    
    # Discover trending repos
    for lang in LANGUAGES:
        repos = discover_trending(lang, MAX_PROJECTS // len(LANGUAGES))
        
        for repo in repos[:MAX_PROJECTS // len(LANGUAGES)]:
            issues = analyze_repo(repo)
            all_issues.extend(issues)
    
    print(f"\n=== Total issues found: {len(all_issues)} ===")
    
    # Sort by priority
    all_issues.sort(key=lambda x: x.priority, reverse=True)
    
    # Create PRs for top issues
    prs_created = 0
    for issue in all_issues[:MAX_PRS_PER_RUN]:
        result = create_pr(issue.repo, issue)
        if result:
            save_to_db(result)
            prs_created += 1
    
    sync_db()
    
    print(f"\n=== Completed: {prs_created} PRs created ===")
    return prs_created

def main():
    parser = argparse.ArgumentParser(description="GitHub Trending Auto PR System")
    parser.add_argument("--run", action="store_true", help="Run once")
    parser.add_argument("--schedule", action="store_true", help="Run hourly")
    parser.add_argument("--language", type=str, default="python", help="Language to scan")
    parser.add_argument("--limit", type=int, default=20, help="Max repos to scan")
    args = parser.parse_args()
    
    if args.schedule:
        while True:
            run_hourly()
            print(f"\nSleeping for 1 hour...")
            time.sleep(3600)
    else:
        run_hourly()

if __name__ == "__main__":
    main()
