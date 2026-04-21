#!/usr/bin/env python3
"""
Auto PR System v2 - 真正有用的 PR 生成器

改进：
1. 动态搜索 good first issue
2. 网络重试机制
3. 真正的代码分析（用 AI）
4. 进度保存和恢复
5. 模块化设计
"""

import subprocess
import json
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# ==================== 配置 ====================
WORK_DIR = Path(r"D:\CODE\auto-pr-work")
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
PROGRESS_FILE = LOG_DIR / "auto_pr_progress.json"
MAX_RETRIES = 3
RETRY_DELAY = 5

# 排除简单文档 PR 的关键词
SIMPLE_DOC_KEYWORDS = [
    "SECURITY.md",
    "CONTRIBUTING.md", 
    "CODE_OF_CONDUCT.md",
    "添加文档",
    "add documentation",
]

# ==================== 工具函数 ====================
def run_cmd(cmd: str, retry: bool = True) -> subprocess.CompletedProcess:
    """执行命令，支持重试"""
    for attempt in range(MAX_RETRIES if retry else 1):
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace'
        )
        if result.returncode == 0 or not retry:
            return result
        print(f"  Retry {attempt + 1}/{MAX_RETRIES}: {cmd[:50]}...")
        time.sleep(RETRY_DELAY * (attempt + 1))
    return result

def save_progress(data: Dict):
    """保存进度"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_progress() -> Dict:
    """加载进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "current": None, "results": []}

def get_username() -> str:
    """获取 GitHub 用户名"""
    result = run_cmd("gh api user --jq .login")
    return result.stdout.strip()

# ==================== Issue 搜索 ====================
def search_good_first_issues(limit: int = 10) -> List[Dict]:
    """搜索真正的 good first issue，排除简单文档"""
    print("\n[Search] 搜索 good first issue...")
    
    issues = []
    
    # 目标仓库列表 - 选择活跃度高、维护积极的项目
    target_repos = [
        ("python/cpython", "easy"),           # Python 用 "easy" 标签
        ("pallets/click", "good first issue"),
        ("psf/requests", "good first issue"),
        ("numpy/numpy", "good first issue"),
        ("pandas-dev/pandas", "good first issue"),
        ("pytest-dev/pytest", "good first issue"),
    ]
    
    for repo, label in target_repos:
        print(f"\n  检查 {repo}...")
        
        # 搜索 issue
        result = run_cmd(
            f'gh issue list --repo {repo} '
            f'--label "{label}" '
            f'--state open '
            f'--limit 5 '
            f'--json number,title,labels,body'
        )
        
        if result.returncode != 0:
            continue
            
        repo_issues = json.loads(result.stdout)
        
        for issue in repo_issues:
            title = issue.get("title", "")
            body = issue.get("body", "")
            
            # 排除简单文档问题
            is_simple_doc = any(
                kw.lower() in title.lower() or kw.lower() in body.lower()[:500]
                for kw in SIMPLE_DOC_KEYWORDS
            )
            
            if is_simple_doc:
                print(f"    [X] Skip #{issue['number']}: {title[:40]} (简单文档)")
                continue
                
            # 检查是否已处理
            progress = load_progress()
            if issue["number"] in [p.get("issue_num") for p in progress.get("processed", [])]:
                print(f"    ⏭️ Skip #{issue['number']}: 已处理过")
                continue
            
            print(f"    [OK] Found #{issue['number']}: {title[:40]}")
            issues.append({
                "repo": repo,
                "issue_num": issue["number"],
                "title": title,
                "body": body[:1000],
                "type": "bug" if "bug" in title.lower() or "fix" in title.lower() else "feature"
            })
            
            if len(issues) >= limit:
                return issues
    
    return issues

def analyze_issue_complexity(issue: Dict) -> Dict:
    """分析 issue 复杂度"""
    title = issue["title"].lower()
    body = issue.get("body", "").lower()
    
    # 简单问题特征
    simple_keywords = ["typo", "spelling", "comment", "rename", "remove unused"]
    # 中等复杂度特征  
    medium_keywords = ["fix", "update", "change", "add", "improve"]
    # 复杂问题特征
    complex_keywords = ["refactor", "implement", "design", "architecture"]
    
    complexity = "medium"
    if any(kw in title or kw in body[:500] for kw in simple_keywords):
        complexity = "simple"
    elif any(kw in title or kw in body[:500] for kw in complex_keywords):
        complexity = "complex"
    
    return {
        **issue,
        "complexity": complexity,
        "estimated_effort": "1h" if complexity == "simple" else "4h" if complexity == "medium" else "1d"
    }

# ==================== 代码分析 ====================
def analyze_codebase(repo: str, issue: Dict, work_path: Path) -> Dict:
    """分析代码库，找出需要修改的文件"""
    print(f"\n[Analyze] 分析代码库...")
    
    analysis = {
        "relevant_files": [],
        "suggested_fix": None,
        "needs_ai_help": True
    }
    
    # 根据问题类型找相关文件
    issue_keywords = issue["title"].lower().split()
    
    # 搜索相关文件
    for ext in ["*.py", "*.js", "*.ts", "*.go", "*.rs"]:
        for file in work_path.rglob(ext):
            if file.stat().st_size > 100000:  # 跳过大文件
                continue
            
            try:
                content = file.read_text(encoding='utf-8', errors='ignore')
                # 检查是否包含问题关键词
                matches = sum(1 for kw in issue_keywords if kw in content.lower())
                if matches > 0:
                    analysis["relevant_files"].append({
                        "path": str(file.relative_to(work_path)),
                        "matches": matches,
                        "size": file.stat().st_size
                    })
            except:
                pass
    
    # 按匹配度排序
    analysis["relevant_files"].sort(key=lambda x: x["matches"], reverse=True)
    analysis["relevant_files"] = analysis["relevant_files"][:5]  # 只保留前5个
    
    return analysis

# ==================== PR 创建 ====================
def create_fix_commit(repo: str, issue: Dict, work_path: Path, analysis: Dict) -> bool:
    """创建修复提交"""
    print(f"\n[Fix] 创建修复...")
    
    if not analysis["relevant_files"]:
        print("  [X] 没有找到相关文件")
        return False
    
    # 这里应该有实际的修复逻辑
    # 现在只是标记需要人工干预
    print(f"  [!] 需要人工分析以下文件：")
    for f in analysis["relevant_files"][:3]:
        print(f"    - {f['path']} ({f['matches']} matches)")
    
    return False  # 暂时返回 False，表示需要人工干预

def create_pr_for_issue(issue: Dict) -> Optional[Dict]:
    """为单个 issue 创建 PR"""
    repo = issue["repo"]
    issue_num = issue["issue_num"]
    
    print(f"\n{'='*60}")
    print(f"处理 {repo} #{issue_num}")
    print(f"标题: {issue['title']}")
    print(f"复杂度: {issue.get('complexity', 'unknown')}")
    print(f"{'='*60}")
    
    # 获取用户名
    username = get_username()
    fork_repo = f"{username}/{repo.split('/')[-1]}"
    
    # 检查 fork
    print(f"\n1. 检查 fork...")
    check = run_cmd(f"gh repo view {fork_repo}", retry=False)
    if check.returncode != 0:
        print(f"  创建 fork: {fork_repo}")
        run_cmd(f"gh repo fork {repo} --clone=false")
        time.sleep(3)
    
    # 准备工作目录
    work_path = WORK_DIR / f"{repo.replace('/', '-')}-{issue_num}"
    
    # Clone
    print(f"\n2. Clone 仓库...")
    if work_path.exists():
        import shutil
        try:
            shutil.rmtree(work_path)
        except:
            pass
    
    work_path.mkdir(parents=True, exist_ok=True)
    
    # 使用 --depth 1 加速
    result = run_cmd(f"git clone --depth 1 https://github.com/{fork_repo}.git {work_path}")
    if result.returncode != 0:
        print(f"  [X] Clone 失败")
        return None
    
    if not (work_path / ".git").exists():
        print(f"  [X] Clone 失败（没有 .git）")
        return None
    
    print(f"  [OK] Clone 成功")
    
    # 分析代码
    analysis = analyze_codebase(repo, issue, work_path)
    
    # 创建修复
    success = create_fix_commit(repo, issue, work_path, analysis)
    
    if not success:
        # 保存需要人工处理的信息
        return {
            "repo": repo,
            "issue_num": issue_num,
            "title": issue["title"],
            "url": f"https://github.com/{repo}/issues/{issue_num}",
            "status": "needs_manual_fix",
            "relevant_files": [f["path"] for f in analysis["relevant_files"]],
            "complexity": issue.get("complexity"),
            "analyzed_at": datetime.now().isoformat()
        }
    
    return None

# ==================== 主流程 ====================
def main():
    print("=" * 60)
    print("Auto PR System v2")
    print("查找真正的 bug，避免简单文档 PR")
    print("=" * 60)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 加载进度
    progress = load_progress()
    print(f"\n已处理: {len(progress.get('processed', []))} 个 issue")
    
    # 搜索 issue
    issues = search_good_first_issues(limit=5)
    
    if not issues:
        print("\n[X] 没有找到合适的 issue")
        return
    
    print(f"\n[OK] 找到 {len(issues)} 个待处理的 issue")
    
    # 处理每个 issue
    for issue in issues:
        # 分析复杂度
        issue = analyze_issue_complexity(issue)
        
        # 创建 PR（或记录需要人工处理）
        result = create_pr_for_issue(issue)
        
        if result:
            progress["processed"].append(result)
            progress["results"].append(result)
            save_progress(progress)
    
    # 总结
    print(f"\n{'='*60}")
    print("总结:")
    print(f"  处理了 {len(issues)} 个 issue")
    print(f"  需要人工修复: {sum(1 for r in progress['results'] if r.get('status') == 'needs_manual_fix')}")
    print(f"\n详细结果: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
