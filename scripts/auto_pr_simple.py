#!/usr/bin/env python3
"""
Simple GitHub PR Creator - Fixed Version
自动发现热门项目问题并创建 PR
"""

import subprocess
import json
import os
import time
import base64
import re
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(r"D:\CODE\auto-pr-work")
GITHUB_TOKEN = None

def run_cmd(cmd, check=True):
    """Run command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result

def get_token():
    """Get GitHub token"""
    result = run_cmd("gh auth status --show-token", check=False)
    if "Token:" in result.stdout:
        return result.stdout.split("Token:")[-1].strip().split()[0]
    return ""

def discover_repos(language="python", limit=10):
    """Discover trending repos"""
    print(f"=== Discovering {language} repos ===")
    result = run_cmd(f'gh search repos --language {language} --sort stars --limit {limit} --json fullName "stars:>1000"')
    repos = []
    if result.returncode == 0:
        try:
            for item in json.loads(result.stdout):
                repos.append(item["fullName"])
        except:
            pass
    print(f"Found {len(repos)} repos")
    return repos

def find_typos(repo):
    """Find typos in README"""
    issues = []
    result = run_cmd(f'gh api repos/{repo}/readme', check=False)
    if result.returncode != 0:
        return issues

    try:
        data = json.loads(result.stdout)
        content = base64.b64decode(data["content"]).decode('utf-8', errors='ignore')

        typos = [
            ("teh", "the"),
            ("hte", "the"),
            ("wiht", "with"),
            ("recieve", "receive"),
            ("occured", "occurred"),
            ("accomodate", "accommodate"),
        ]

        for wrong, right in typos:
            matches = list(re.finditer(rf'\b{wrong}\b', content, re.I))
            if matches:
                issues.append({
                    "type": "typo",
                    "wrong": wrong,
                    "right": right,
                    "count": len(matches)
                })
    except:
        pass

    return issues

def create_typo_fix_pr(repo, issues):
    """Create PR for typo fix"""
    print(f"\n--- Creating typo PR for {repo} ---")

    # Fork repo
    print("1. Forking...")
    user_result = run_cmd("gh api user --jq .login")
    username = user_result.stdout.strip()

    fork_repo = f"{username}/{repo.split('/')[-1]}"

    # Check if fork exists
    check = run_cmd(f"gh repo view {fork_repo}", check=False)
    if check.returncode != 0:
        run_cmd(f"gh repo fork {repo} --clone=false")
        time.sleep(3)

    # Clone
    work_path = WORK_DIR / repo.replace("/", "-")
    if work_path.exists():
        import shutil
        shutil.rmtree(work_path)
    work_path.mkdir(parents=True, exist_ok=True)

    print("2. Cloning...")
    run_cmd(f"git clone https://github.com/{fork_repo}.git {work_path}")

    if not (work_path / ".git").exists():
        print("Clone failed")
        return None

    # Fix typos
    print("3. Fixing typos...")
    readme = work_path / "README.md"
    if readme.exists():
        content = readme.read_text(encoding='utf-8', errors='ignore')
        for issue in issues:
            content = re.sub(rf'\b{issue["wrong"]}\b', issue["right"], content, flags=re.I)
        readme.write_text(content, encoding='utf-8')

    # Commit
    print("4. Committing...")
    run_cmd(f'git -C {work_path} config user.email "erbing@openclaw.ai"')
    run_cmd(f'git -C {work_path} config user.name "Erbing"')
    run_cmd(f'git -C {work_path} checkout -b fix-typo-{datetime.now().strftime("%Y%m%d")}')
    run_cmd(f'git -C {work_path} add README.md')
    run_cmd(f'git -C {work_path} commit -m "Fix typo in README"')

    # Push with token
    print("5. Pushing...")
    token = get_token()
    push_result = run_cmd(f'git -C {work_path} push https://{token}@github.com/{fork_repo}.git HEAD:fix-typo-{datetime.now().strftime("%Y%m%d")}', check=False)

    if push_result.returncode != 0:
        print(f"Push failed: {push_result.stderr}")
        return None

    # Create PR
    print("6. Creating PR...")
    pr_result = run_cmd(f'''gh pr create --repo {repo} --title "Fix typo in README" --body "Fixed typo: {', '.join([i['wrong'] + ' -> ' + i['right'] for i in issues])}" --head {username}:fix-typo-{datetime.now().strftime("%Y%m%d")}''', check=False)

    if pr_result.returncode == 0:
        print(f"✓ PR created: {pr_result.stdout.strip()}")
        return pr_result.stdout.strip()
    else:
        print(f"PR failed: {pr_result.stderr}")
        return None

def main():
    print("=" * 60)
    print("GitHub Auto PR - Simple Version")
    print("=" * 60)

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    repos = discover_repos("python", 5)

    for repo in repos[:3]:
        issues = find_typos(repo)
        if issues:
            print(f"\n{repo}: Found {len(issues)} typo types")
            pr_url = create_typo_fix_pr(repo, issues)
            if pr_url:
                print(f"SUCCESS: {pr_url}")
                break
        else:
            print(f"\n{repo}: No typos found")

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
