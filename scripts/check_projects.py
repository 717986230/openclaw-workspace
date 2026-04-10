#!/usr/bin/env python3
"""
检查项目的友好度
"""

import subprocess
import json
import requests
from datetime import datetime

def get_token():
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return result.stdout.strip()

def check_repo(token, repo):
    """检查仓库"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    
    # 基本信息
    url = f"https://api.github.com/repos/{repo}"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        return None
    
    data = resp.json()
    
    # 活跃度
    pushed_at = data.get("pushed_at")
    last_commit_days = 999
    if pushed_at:
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        last_commit_days = (datetime.now(last_push.tzinfo) - last_push).days
    
    # Good first issues
    cmd = f'gh issue list --repo {repo} --label "good first issue" --state open --limit 50 --json number'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    
    gfi_count = 0
    if result.returncode == 0 and result.stdout:
        try:
            issues = json.loads(result.stdout)
            gfi_count = len(issues) if isinstance(issues, list) else 0
        except:
            pass
    
    return {
        "repo": repo,
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "last_commit_days": last_commit_days,
        "good_first_issues": gfi_count,
    }

def main():
    print("检查项目友好度...\n")
    
    token = get_token()
    
    # 要检查的项目
    projects = [
        "pandas-dev/pandas",
        "numpy/numpy",
        "pytest-dev/pytest",
        "python-telegram-bot/python-telegram-bot",
        "openai/openai-python",
        "modelcontextprotocol/python-sdk",
        "google/adk-python",
        "TheAlgorithms/Python",
        "faif/python-patterns",
        "python-telegram-bot/python-telegram-bot",
        "pallets/click",
        "pallets/flask",
        "psf/requests",
        "django/django",
        "fastapi/fastapi",
        "tiangolo/fastapi",
        "Textualize/textual",
        "pypa/pip",
        "pypa/pipx",
        "astral-sh/ruff",
    ]
    
    # 去重
    projects = list(set(projects))
    
    results = []
    
    for repo in projects:
        print(f"检查: {repo}")
        info = check_repo(token, repo)
        
        if info:
            # 计算分数
            score = 0
            if info["good_first_issues"] >= 5:
                score += min(info["good_first_issues"] * 3, 40)
            if info["last_commit_days"] <= 30:
                score += 30 - info["last_commit_days"]
            if info["stars"] >= 1000:
                score += min(info["stars"] // 1000, 30)
            
            info["score"] = score
            
            # 判断是否友好
            is_friendly = (
                info["good_first_issues"] >= 3 and
                info["last_commit_days"] <= 60
            )
            info["friendly"] = is_friendly
            
            if is_friendly:
                print(f"  [FRIENDLY] Stars={info['stars']:,}, GFI={info['good_first_issues']}, 分数={score}")
            elif info["good_first_issues"] > 0:
                print(f"  [Potential] Stars={info['stars']:,}, GFI={info['good_first_issues']}")
            else:
                print(f"  [Skip] Stars={info['stars']:,}, 无GFI")
            
            results.append(info)
        
        import time
        time.sleep(0.3)
    
    # 排序
    results.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    # 显示结果
    print(f"\n{'='*70}")
    print("友好项目列表 (按分数排序):")
    print(f"{'='*70}")
    print(f"{'项目':<40} {'Stars':>10} {'GFI':>5} {'活跃':>6} {'分数':>6}")
    print("-" * 70)
    
    for r in results:
        if r.get("friendly") or r["good_first_issues"] > 0:
            active = f"{r['last_commit_days']}d"
            friendly_mark = "*" if r.get("friendly") else " "
            print(f"{friendly_mark} {r['repo']:<38} {r['stars']:>10,} {r['good_first_issues']:>5} {active:>6} {r['score']:>6}")
    
    print(f"\n* = 友好项目 (GFI>=3, 活跃<=60天)")
    
    # 保存
    from pathlib import Path
    output = Path(r"C:\Users\Administrator\.openclaw\workspace\logs\projects_checked.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {output}")

if __name__ == "__main__":
    main()
