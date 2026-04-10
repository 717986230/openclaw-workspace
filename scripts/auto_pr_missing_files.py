#!/usr/bin/env python3
"""
Auto PR for Missing Files - Create SECURITY.md or CONTRIBUTING.md
"""

import subprocess
import json
import os
import time
from pathlib import Path
from datetime import datetime

WORK_DIR = Path(r"D:\CODE\auto-pr-work")

def run_cmd(cmd, check=True):
    """Run command"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    return result

def get_token():
    """Get GitHub token"""
    result = run_cmd("gh auth status --show-token", check=False)
    if "Token:" in result.stdout:
        return result.stdout.split("Token:")[-1].strip().split()[0]
    return ""

def discover_repos(language="python", limit=20):
    """Discover trending repos"""
    print(f"=== Discovering {language} repos ===")
    result = run_cmd(f'gh search repos --language {language} --sort stars --limit {limit} --json fullName "stars:>500"')
    repos = []
    if result.returncode == 0:
        try:
            for item in json.loads(result.stdout):
                repos.append(item["fullName"])
        except:
            pass
    print(f"Found {len(repos)} repos")
    return repos

def check_missing_files(repo):
    """Check for missing SECURITY.md or CONTRIBUTING.md"""
    result = run_cmd(f"gh api repos/{repo}/contents", check=False)
    if result.returncode != 0:
        return None

    try:
        files = [f["name"] for f in json.loads(result.stdout)]
        missing = []
        if "SECURITY.md" not in files:
            missing.append("SECURITY.md")
        if "CONTRIBUTING.md" not in files:
            missing.append("CONTRIBUTING.md")
        return missing if missing else None
    except:
        return None

def create_file_pr(repo, file_type):
    """Create PR for missing file"""
    print(f"\n--- Creating {file_type} PR for {repo} ---")

    user_result = run_cmd("gh api user --jq .login")
    username = user_result.stdout.strip()
    fork_repo = f"{username}/{repo.split('/')[-1]}"

    # Fork
    print("1. Forking...")
    check = run_cmd(f"gh repo view {fork_repo}", check=False)
    if check.returncode != 0:
        run_cmd(f"gh repo fork {repo} --clone=false")
        time.sleep(3)

    # Clone
    work_path = WORK_DIR / repo.replace("/", "-")
    if work_path.exists():
        import shutil
        try:
            shutil.rmtree(work_path)
        except:
            pass
    work_path.mkdir(parents=True, exist_ok=True)

    print("2. Cloning...")
    run_cmd(f"git clone --depth 1 https://github.com/{fork_repo}.git {work_path}")

    if not (work_path / ".git").exists():
        print("Clone failed")
        return None

    # Create file
    print(f"3. Creating {file_type}...")
    file_path = work_path / file_type

    if file_type == "SECURITY.md":
        content = """# Security Policy

## Reporting a Vulnerability

Please email the maintainers for security issues.

Do not create public issues for security vulnerabilities.

## Supported Versions

Only the latest version is actively supported.
"""
    else:  # CONTRIBUTING.md
        content = """# Contributing

Thank you for your interest in contributing!

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Code of Conduct

Please be respectful and constructive.
"""

    file_path.write_text(content, encoding='utf-8')

    # Commit
    print("4. Committing...")
    run_cmd(f'git -C {work_path} config user.email "erbing@openclaw.ai"')
    run_cmd(f'git -C {work_path} config user.name "Erbing"')
    branch = f"add-{file_type.lower().replace('.md', '')}-{datetime.now().strftime('%Y%m%d')}"
    run_cmd(f'git -C {work_path} checkout -b {branch}')
    run_cmd(f'git -C {work_path} add {file_type}')
    run_cmd(f'git -C {work_path} commit -m "Add {file_type}"')

    # Push
    print("5. Pushing...")
    token = get_token()
    push_result = run_cmd(f'git -C {work_path} push https://{token}@github.com/{fork_repo}.git {branch}', check=False)

    if push_result.returncode != 0:
        print(f"Push failed: {push_result.stderr[:200]}")
        return None

    # Create PR
    print("6. Creating PR...")
    pr_result = run_cmd(f'gh pr create --repo {repo} --title "Add {file_type}" --body "Added {file_type} file for better project documentation." --head {username}:{branch}', check=False)

    if pr_result.returncode == 0:
        print(f"PR created: {pr_result.stdout.strip()}")
        return pr_result.stdout.strip()
    else:
        print(f"PR result: {pr_result.stderr[:200]}")
        return None

def send_notification(prs):
    """Send notification about created PRs"""
    import json
    from pathlib import Path

    content = f"**Created {len(prs)} PR(s)**\n\n"
    for pr in prs:
        content += f"- {pr['file']} → {pr['repo']}\n  Link: {pr['url']}\n"

    notification = {
        "title": f"GitHub PR Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "prs": prs
    }

    notif_path = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\pr_notification.json")
    notif_path.parent.mkdir(parents=True, exist_ok=True)

    with open(notif_path, 'w', encoding='utf-8') as f:
        json.dump(notification, f, ensure_ascii=False, indent=2)

    print(f"\nNotification saved: {notif_path}")


def main():
    print("=" * 60)
    print("Auto PR for Missing Files")
    print("=" * 60)

    WORK_DIR.mkdir(parents=True, exist_ok=True)

    created = 0
    created_prs = []
    for lang in ["python", "javascript", "typescript"]:
        repos = discover_repos(lang, 10)

        for repo in repos:
            if created >= 3:
                break

            missing = check_missing_files(repo)
            if missing:
                print(f"\n{repo}: Missing {missing}")
                for file_type in missing:
                    pr_url = create_file_pr(repo, file_type)
                    if pr_url:
                        created += 1
                        created_prs.append({"repo": repo, "file": file_type, "url": pr_url})
                        break

    print(f"\n=== Done: {created} PRs created ===")

    # Send notification
    if created_prs:
        send_notification(created_prs)

if __name__ == "__main__":
    main()
