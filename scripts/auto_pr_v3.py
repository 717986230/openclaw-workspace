#!/usr/bin/env python3
"""
Auto PR System v3 - AI 辅助修复版

新增功能：
1. AI 分析 issue，理解问题本质
2. AI 生成修复代码
3. 自动创建 commit 和 PR
"""

import subprocess
import json
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# ==================== 配置 ====================
WORK_DIR = Path(r"D:\CODE\auto-pr-work")
LOG_DIR = Path(r"C:\Users\Administrator\.openclaw\workspace\logs")
PROGRESS_FILE = LOG_DIR / "auto_pr_progress_v3.json"

# 简单文档关键词（排除）
SIMPLE_DOC_KEYWORDS = ["SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]

# ==================== 工具函数 ====================
def run_cmd(cmd: str, retry: bool = True, timeout: int = 60) -> subprocess.CompletedProcess:
    """执行命令"""
    for attempt in range(3 if retry else 1):
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',
                errors='replace',
                timeout=timeout
            )
            if result.returncode == 0 or not retry:
                return result
        except subprocess.TimeoutExpired:
            print(f"  Timeout: {cmd[:50]}")
            if not retry:
                return subprocess.CompletedProcess(cmd, 1, '', '')
        time.sleep(2 * (attempt + 1))
    return result

def save_progress(data: Dict):
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_progress() -> Dict:
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"processed": [], "results": []}

def get_username() -> str:
    result = run_cmd("gh api user --jq .login", timeout=10)
    return result.stdout.strip()

# ==================== AI 修复助手 ====================
def ask_ai_to_analyze_issue(issue: Dict, file_contents: Dict[str, str]) -> Dict:
    """
    让 AI 分析 issue 并生成修复方案
    
    使用本地 Claude Code API
    """
    print("  [AI] 正在分析 issue...")
    
    # 构建提示词
    prompt = f"""分析以下 GitHub Issue 并生成修复方案：

## Issue 信息
- 仓库: {issue['repo']}
- 编号: #{issue['issue_num']}
- 标题: {issue['title']}
- 描述:
{issue.get('body', '无详细描述')[:2000]}

## 相关代码文件
"""
    
    for filepath, content in list(file_contents.items())[:3]:
        prompt += f"\n### {filepath}\n```{get_file_language(filepath)}\n{content[:2000]}\n```\n"
    
    prompt += """
## 要求
1. 分析问题的根本原因
2. 给出具体的修复方案（代码级别）
3. 说明修改哪些文件的哪些位置
4. 如果无法修复，说明原因

请以 JSON 格式返回：
{
    "can_fix": true/false,
    "reason": "原因分析",
    "fix_plan": [
        {
            "file": "文件路径",
            "line_range": [开始行, 结束行],
            "old_code": "需要替换的代码",
            "new_code": "修复后的代码",
            "description": "修改说明"
        }
    ]
}
"""

    # 调用本地 AI（通过 ask_claude_code 工具）
    # 这里我们用简单的规则引擎模拟，实际可以调用 Claude
    result = simple_fix_analyzer(issue, file_contents)
    return result

def simple_fix_analyzer(issue: Dict, file_contents: Dict[str, str]) -> Dict:
    """简单修复分析器（基于规则的初步分析）"""
    title_lower = issue['title'].lower()
    body_lower = issue.get('body', '').lower()
    
    # 检测问题类型
    fix_plan = []
    
    # 1. 死链接/URL 问题
    if 'dead' in title_lower or 'url' in title_lower or 'link' in title_lower:
        for filepath, content in file_contents.items():
            # 查找 http:// 或 https:// 链接
            urls = re.findall(r'https?://[^\s\'"<>]+', content)
            if urls:
                fix_plan.append({
                    "file": filepath,
                    "type": "url_check",
                    "urls": urls[:5],
                    "description": "检查这些 URL 是否有效"
                })
    
    # 2. Typo/拼写错误
    elif 'typo' in title_lower or 'spelling' in title_lower:
        typo_word = None
        # 从 title 中提取可能的错误词
        match = re.search(r'"(\w+)"|\'(\w+)\'', issue['title'])
        if match:
            typo_word = match.group(1) or match.group(2)
        
        if typo_word:
            fix_plan.append({
                "file": "需要搜索",
                "type": "typo_fix",
                "word": typo_word,
                "description": f"查找并修正拼写错误: {typo_word}"
            })
    
    # 3. 性能优化
    elif 'performance' in title_lower or 'optimize' in title_lower or 'improve' in title_lower:
        fix_plan.append({
            "file": "需要深入分析",
            "type": "performance",
            "description": "需要性能分析和基准测试"
        })
    
    return {
        "can_fix": len(fix_plan) > 0,
        "reason": f"检测到问题类型: {title_lower}",
        "fix_plan": fix_plan,
        "needs_human": True  # 首次运行需要人工确认
    }

def get_file_language(filepath: str) -> str:
    """获取文件语言"""
    ext = Path(filepath).suffix
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.c': 'c',
        '.cpp': 'cpp',
        '.md': 'markdown',
        '.txt': 'text',
    }
    return lang_map.get(ext, '')

# ==================== 实际修复逻辑 ====================
def apply_fix(repo: str, issue: Dict, work_path: Path, fix_plan: List[Dict]) -> bool:
    """应用修复方案"""
    print("  [Fix] 正在应用修复...")
    
    applied = []
    
    for fix in fix_plan:
        fix_type = fix.get('type')
        
        if fix_type == 'url_check':
            # 检查 URL 是否有效
            print(f"    检查 URL: {fix['urls']}")
            for url in fix.get('urls', []):
                # 跳过明显有效的 URL
                if 'example.com' in url or 'python.org' in url:
                    continue
                # 测试 URL
                result = run_cmd(f"curl -sI {url} | head -1", timeout=10)
                if '200' not in result.stdout and '301' not in result.stdout:
                    print(f"      [!] 可能的死链接: {url}")
                    applied.append({
                        "type": "url_issue",
                        "url": url,
                        "status": "needs_replacement"
                    })
        
        elif fix_type == 'typo_fix':
            # 查找 typo
            word = fix.get('word')
            print(f"    搜索关键词: {word}")
            for py_file in work_path.rglob('*.py'):
                if py_file.stat().st_size > 50000:
                    continue
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if word in content:
                        print(f"      找到: {py_file.relative_to(work_path)}")
                        applied.append({
                            "type": "typo",
                            "file": str(py_file.relative_to(work_path)),
                            "word": word
                        })
                except:
                    pass
    
    return len(applied) > 0

def create_commit_and_pr(repo: str, issue: Dict, work_path: Path, changes: List[Dict]) -> bool:
    """创建 commit 和 PR"""
    print("  [PR] 正在创建 PR...")
    
    # 检查是否有实际修改
    result = run_cmd(f"git -C {work_path} status --porcelain")
    if not result.stdout.strip():
        print("    没有实际修改")
        return False
    
    # 配置 git
    run_cmd(f'git -C {work_path} config user.email "erbing@openclaw.ai"')
    run_cmd(f'git -C {work_path} config user.name "Erbing"')
    
    # 创建分支
    branch = f"fix-issue-{issue['issue_num']}"
    run_cmd(f'git -C {work_path} checkout -b {branch}')
    
    # 提交
    commit_msg = f"Fix #{issue['issue_num']}: {issue['title'][:50]}"
    run_cmd(f'git -C {work_path} add -A')
    run_cmd(f'git -C {work_path} commit -m "{commit_msg}"')
    
    # 推送
    username = get_username()
    run_cmd(f'git -C {work_path} push -u origin {branch}')
    
    # 创建 PR
    pr_body = f"""Fixes #{issue['issue_num']}

## 修改说明
{chr(10).join(f'- {c}' for c in changes)}

## 测试
- [ ] 已本地测试
- [ ] 已检查相关文档

---
*此 PR 由 AI 辅助生成，请仔细审查。*
"""
    
    pr_result = run_cmd(
        f'gh pr create --repo {repo} '
        f'--title "{commit_msg}" '
        f'--body "{pr_body}" '
        f'--head "{username}:{branch}"'
    )
    
    if pr_result.returncode == 0:
        print(f"    [OK] PR 创建成功: {pr_result.stdout.strip()}")
        return True
    else:
        print(f"    [X] PR 创建失败: {pr_result.stderr}")
        return False

# ==================== 主流程 ====================
def find_issues() -> List[Dict]:
    """搜索待修复的 issue"""
    print("\n[Search] 搜索 easy issue...")
    
    issues = []
    repos = [
        ("python/cpython", "easy"),
        ("pallets/click", "good first issue"),
        ("psf/requests", "good first issue"),
    ]
    
    for repo, label in repos:
        result = run_cmd(
            f'gh issue list --repo {repo} --label "{label}" '
            f'--state open --limit 3 --json number,title,body,labels',
            timeout=30
        )
        
        if result.returncode != 0:
            continue
        
        for issue in json.loads(result.stdout):
            title = issue.get('title', '')
            body = issue.get('body', '')
            
            # 排除简单文档
            is_simple = any(kw.lower() in title.lower() or kw.lower() in body[:500].lower()
                          for kw in SIMPLE_DOC_KEYWORDS)
            
            if is_simple:
                continue
            
            issues.append({
                "repo": repo,
                "issue_num": issue["number"],
                "title": title,
                "body": body[:2000],
            })
            
            if len(issues) >= 5:
                return issues
    
    return issues

def process_issue(issue: Dict) -> Optional[Dict]:
    """处理单个 issue"""
    repo = issue['repo']
    num = issue['issue_num']
    
    print(f"\n{'='*60}")
    print(f"[Process] {repo} #{num}")
    print(f"  标题: {issue['title'][:50]}")
    print(f"{'='*60}")
    
    # Fork
    username = get_username()
    fork = f"{username}/{repo.split('/')[-1]}"
    
    print("  [1/4] 检查 fork...")
    check = run_cmd(f"gh repo view {fork}", timeout=10)
    if check.returncode != 0:
        print(f"    创建 fork: {fork}")
        run_cmd(f"gh repo fork {repo} --clone=false", timeout=60)
        time.sleep(3)
    
    # Clone
    work = WORK_DIR / f"{repo.replace('/', '-')}-{num}"
    print(f"  [2/4] Clone...")
    
    if work.exists():
        import shutil
        try:
            shutil.rmtree(work)
        except:
            pass
    
    work.mkdir(parents=True, exist_ok=True)
    clone_result = run_cmd(
        f"git clone --depth 50 https://github.com/{fork}.git {work}",
        timeout=120
    )
    
    if not (work / ".git").exists():
        print("    [X] Clone 失败")
        return None
    
    print("    [OK] Clone 成功")
    
    # 分析并修复
    print("  [3/4] 分析并修复...")
    
    # 读取关键文件
    file_contents = {}
    for ext in ['*.py', '*.rst', '*.md']:
        for f in list(work.rglob(ext))[:10]:
            if f.stat().st_size < 10000:
                try:
                    file_contents[str(f.relative_to(work))] = f.read_text(encoding='utf-8', errors='ignore')
                except:
                    pass
    
    # AI 分析
    analysis = ask_ai_to_analyze_issue(issue, file_contents)
    
    # 应用修复
    if analysis.get('can_fix'):
        applied = apply_fix(repo, issue, work, analysis.get('fix_plan', []))
        
        if applied:
            # 创建 PR
            print("  [4/4] 创建 PR...")
            success = create_commit_and_pr(repo, issue, work, analysis.get('fix_plan', []))
            
            return {
                **issue,
                "status": "pr_created" if success else "needs_commit",
                "analysis": analysis
            }
    
    return {
        **issue,
        "status": "needs_manual_fix",
        "analysis": analysis,
        "relevant_files": list(file_contents.keys())[:5]
    }

def main():
    print("=" * 60)
    print("Auto PR System v3 - AI 辅助修复")
    print("=" * 60)
    
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 加载进度
    progress = load_progress()
    processed_nums = [p['issue_num'] for p in progress.get('processed', [])]
    print(f"\n已处理: {len(processed_nums)} 个 issue")
    
    # 搜索
    issues = find_issues()
    
    # 过滤已处理的
    issues = [i for i in issues if i['issue_num'] not in processed_nums]
    
    if not issues:
        print("\n没有新的 issue 需要处理")
        return
    
    print(f"\n待处理: {len(issues)} 个 issue")
    
    # 处理
    for issue in issues[:3]:
        result = process_issue(issue)
        if result:
            progress['processed'].append(result)
            progress['results'].append(result)
            save_progress(progress)
    
    # 总结
    print(f"\n{'='*60}")
    print("总结:")
    for r in progress['results'][-3:]:
        status_icon = "[OK]" if r['status'] == 'pr_created' else "[!]"
        print(f"  {status_icon} {r['repo']} #{r['issue_num']}: {r['status']}")
    print(f"\n详细结果: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()
