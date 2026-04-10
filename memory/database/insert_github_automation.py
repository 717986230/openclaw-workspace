#!/usr/bin/env python3
"""
Insert GitHub PR Automation into database
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")

def main():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Insert GitHub PR Automation skill
    cursor.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('skill', 'GitHub Trending PR Automation', '''
## GitHub Trending PR Automation System

### 能力描述
自动发现 GitHub 热门项目，分析贡献机会，提交 PR。

### 工作流程
1. **Discovery**: 发现热门项目 (gh search repos)
2. **Analysis**: 分析项目结构 (gh repo view)
3. **Opportunity**: 寻找贡献机会 (good first issue, docs)
4. **Execution**: 执行 PR (需 Claude Code 协作)

### 脚本位置
`scripts/github-trending-pr.py`

### 依赖
- GitHub CLI (gh) - 需要认证: `gh auth login`
- Python 3.13

### 使用方式
```bash
# 认证 GitHub CLI
gh auth login

# 运行每日分析
python scripts/github-trending-pr.py
```

### 进化阶段
- [x] Phase 1: 发现项目
- [x] Phase 2: 分析项目
- [x] Phase 3: 寻找机会
- [ ] Phase 4: 执行 PR (需要 Claude Code 集成)
- [ ] Phase 5: 自动化调度 (cron / Windows Task Scheduler)

### 配合技能
- `gh-issues` skill - Issue 处理
- `github` skill - GitHub 操作
- `codex-skill` - 代码实现
''', 'automation', json.dumps(['github', 'pr', 'trending', 'automation', 'evolution']), 8, datetime.now().isoformat()))

    # Insert pending improvement for this capability
    cursor.execute('''
        INSERT INTO memories (type, title, content, category, tags, importance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('improvement', 'GitHub PR Automation - Phase 4', '''
## GitHub PR Automation - 待完成

### Phase 4: 执行 PR
- [ ] GitHub CLI 认证 (`gh auth login`)
- [ ] 与 Claude Code 集成 (代码生成)
- [ ] 自动 Fork + Branch + Commit + Push + PR
- [ ] PR 模板生成
- [ ] Code Review 响应处理

### Phase 5: 自动化调度
- [ ] Windows Task Scheduler 配置
- [ ] 每日自动运行
- [ ] 结果通知 (Feishu/Discord)
- [ ] 进化报告生成

### 预期结果
每天自动:
1. 发现 3-5 个热门项目
2. 分析贡献机会
3. 提交 1-2 个 PR (文档修复、bug 修复)
4. 记录到数据库
5. 通知用户
''', 'improvement', json.dumps(['github', 'automation', 'pr', 'phase4']), 8, datetime.now().isoformat()))

    conn.commit()
    print("Inserted: GitHub Trending PR Automation")
    print("Inserted: GitHub PR Automation - Phase 4")

    # Show current skills
    cursor.execute("SELECT title, importance FROM memories WHERE type='skill' ORDER BY importance DESC")
    print("\n=== Current Skills ===")
    for row in cursor.fetchall():
        print(f"[{row[1]}] {row[0]}")

    conn.close()

if __name__ == "__main__":
    main()
