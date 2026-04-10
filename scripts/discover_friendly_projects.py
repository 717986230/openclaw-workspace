#!/usr/bin/env python3
"""
发现友好项目 - 寻找对新人友好的开源项目
"""

import subprocess
import json
import time
from pathlib import Path
import requests

LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
OUTPUT_FILE = LOG_DIR / "friendly_projects_list.json"

# 搜索关键词
SEARCH_TOPICS = [
    "python cli",
    "python library",
    "python testing",
    "python data",
    "python web",
]

# 友好标准
CRITERIA = {
    "min_stars": 500,
    "max_last_commit_days": 60,
    "min_good_first_issues": 3,
}


def get_token():
    result = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    return result.stdout.strip()


def search_projects(topic: str, limit: int = 20) -> list:
    """搜索项目"""
    cmd = f'gh search repos --language python --limit {limit} --json full_name,stargazers_count,description "{topic} stars:>500"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    
    if result.returncode == 0 and result.stdout:
        try:
            return json.loads(result.stdout)
        except:
            pass
    return []


def check_project_friendly(token: str, repo: str) -> dict:
    """检查项目是否友好"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    
    info = {
        "repo": repo,
        "friendly": False,
        "stars": 0,
        "good_first_issues": 0,
        "last_commit_days": 999,
        "score": 0,
        "reasons": [],
    }
    
    # 获取基本信息
    url = f"https://api.github.com/repos/{repo}"
    resp = requests.get(url, headers=headers)
    
    if resp.status_code != 200:
        return info
    
    data = resp.json()
    
    # Stars
    info["stars"] = data.get("stargazers_count", 0)
    
    # 活跃度
    pushed_at = data.get("pushed_at")
    if pushed_at:
        from datetime import datetime
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        info["last_commit_days"] = (datetime.now(last_push.tzinfo) - last_push).days
    
    # Good first issues
    cmd = f'gh issue list --repo {repo} --label "good first issue" --state open --limit 100 --json number'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0 and result.stdout:
        try:
            issues = json.loads(result.stdout)
            info["good_first_issues"] = len(issues) if isinstance(issues, list) else 0
        except:
            pass
    
    # 判断是否友好
    if info["stars"] >= CRITERIA["min_stars"]:
        info["reasons"].append(f"Stars: {info['stars']:,}")
    
    if info["last_commit_days"] <= CRITERIA["max_last_commit_days"]:
        info["reasons"].append(f"活跃: {info['last_commit_days']}天前提交")
    
    if info["good_first_issues"] >= CRITERIA["min_good_first_issues"]:
        info["reasons"].append(f"GFI: {info['good_first_issues']}个")
    
    info["friendly"] = (
        info["stars"] >= CRITERIA["min_stars"] and
        info["last_commit_days"] <= CRITERIA["max_last_commit_days"] and
        info["good_first_issues"] >= CRITERIA["min_good_first_issues"]
    )
    
    # 计算分数
    if info["friendly"]:
        info["score"] = (
            min(info["good_first_issues"] * 3, 50) +
            max(0, 30 - info["last_commit_days"]) +
            min(info["stars"] // 100, 20)
        )
    
    return info


def main():
    print("=" * 60)
    print("发现友好项目")
    print("=" * 60)
    
    token = get_token()
    all_projects = {}
    
    # 搜索项目
    for topic in SEARCH_TOPICS:
        print(f"\n搜索: {topic}")
        projects = search_projects(topic, limit=30)
        
        for p in projects:
            repo = p.get("full_name")
            if repo and repo not in all_projects:
                all_projects[repo] = p
    
    print(f"\n找到 {len(all_projects)} 个项目")
    
    # 检查友好度
    friendly_projects = []
    checked = 0
    
    for repo in all_projects:
        checked += 1
        print(f"\n[{checked}/{len(all_projects)}] 检查 {repo}...")
        
        info = check_project_friendly(token, repo)
        
        if info["friendly"]:
            print(f"  [FRIENDLY] 分数: {info['score']}")
            friendly_projects.append(info)
        else:
            if info["good_first_issues"] > 0 or info["stars"] > 1000:
                print(f"  [ Potential] GFI={info['good_first_issues']}, Stars={info['stars']}")
        
        time.sleep(0.5)
        
        # 限制检查数量
        if checked >= 50:
            break
    
    # 排序
    friendly_projects.sort(key=lambda x: x["score"], reverse=True)
    
    # 保存结果
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(friendly_projects, f, ensure_ascii=False, indent=2)
    
    # 显示结果
    print(f"\n{'='*60}")
    print(f"发现 {len(friendly_projects)} 个友好项目:")
    print(f"{'='*60}")
    print(f"{'项目':<35} {'Stars':>8} {'GFI':>5} {'分数':>6}")
    print("-" * 60)
    
    for p in friendly_projects[:15]:
        print(f"{p['repo']:<35} {p['stars']:>8,} {p['good_first_issues']:>5} {p['score']:>6}")
    
    print(f"\n结果已保存: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
