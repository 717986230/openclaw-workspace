# GitHub Trending 持续追踪和 PR 提交系统

## 概述

这是一个自动化系统，用于每日持续跟踪 GitHub trending 项目，并自动寻找贡献机会和提交 PR。

## 功能特性

### 1. 热门项目追踪
- 每日自动获取 GitHub trending 项目
- 支持按语言筛选
- 记录项目历史数据

### 2. 贡献机会分析
- 自动分析每个项目的贡献机会
- 识别 open issues
- 检查文档完善度
- 评估测试覆盖率
- 发现 bug reports

### 3. 自动 PR 提交
- 自动为热门项目创建 PR
- 支持自定义 PR 标题和描述
- 跟踪 PR 状态

### 4. 统计和报告
- 扫描历史记录
- 贡献统计
- 趋势分析

## 系统架构

```
GitHub Trending 追踪系统
├── erbing_system/
│   └── social/
│       └── github_trending_tracker.py  # 核心追踪器
├── scripts/
│   ├── github_trending_daily.py        # 每日自动化脚本
│   ├── github_trending_cron.txt        # Cron 配置
│   └── github_trending_windows_scheduler.md  # Windows 任务计划配置
└── test_github_trending.py             # 测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python test_github_trending.py
```

### 3. 手动运行每日扫描

```bash
python scripts/github_trending_daily.py
```

### 4. 配置自动化任务

#### Linux/Mac (Cron)
```bash
# 编辑 crontab
crontab -e

# 添加以下行
0 9 * * * cd /path/to/workspace && python scripts/github_trending_daily.py >> logs/github_trending.log 2>&1
```

#### Windows (任务计划程序)
参考 `scripts/github_trending_windows_scheduler.md`

## 使用方法

### Python API

```python
from erbing_system.social.github_trending_tracker import (
    fetch_trending,
    daily_scan,
    auto_contribute,
    get_scan_history,
    get_statistics,
)

# 获取热门项目
trending = await fetch_trending()

# 每日扫描
scan_result = await daily_scan()

# 自动贡献
prs = await auto_contribute(max_prs=3)

# 获取扫描历史
history = get_scan_history(days=7)

# 获取统计信息
stats = get_statistics()
```

### 命令行

```bash
# 每日扫描
python scripts/github_trending_daily.py

# 查看日志
tail -f logs/github_trending.log
```

## 配置选项

### 环境变量

```bash
# GitHub API Token (可选，用于提高 API 限制)
export GITHUB_TOKEN=your_github_token

# 扫描周期
export SCAN_PERIOD=daily  # daily, weekly, monthly

# 最大 PR 数量
export MAX_PRS=3

# 语言筛选
export LANGUAGE=python  # python, javascript, typescript, etc.
```

### 配置文件

创建 `config.json`:

```json
{
  "github": {
    "token": "your_github_token",
    "api_base": "https://api.github.com"
  },
  "scan": {
    "period": "daily",
    "languages": ["python", "typescript", "javascript"],
    "max_repos": 10
  },
  "contribution": {
    "max_prs": 3,
    "auto_approve": false,
    "branch_prefix": "feature/contribution"
  },
  "logging": {
    "level": "INFO",
    "file": "logs/github_trending.log"
  }
}
```

## 工作流程

### 每日扫描流程

1. **获取热门项目**
   - 调用 GitHub API 获取 trending 项目
   - 按语言和周期筛选
   - 记录项目信息

2. **分析贡献机会**
   - 检查 open issues
   - 分析文档完善度
   - 评估测试覆盖率
   - 发现 bug reports

3. **生成报告**
   - 汇总扫描结果
   - 按优先级排序机会
   - 生成可执行建议

4. **自动贡献（可选）**
   - 为高优先级项目创建 PR
   - 跟踪 PR 状态
   - 记录贡献历史

### PR 提交流程

1. **Fork 项目**
   - 自动 fork 目标项目
   - 创建功能分支

2. **修改代码**
   - 根据贡献机会修改代码
   - 添加测试
   - 更新文档

3. **创建 PR**
   - 提交 PR 到原项目
   - 添加详细描述
   - 引用相关 issue

4. **跟踪状态**
   - 监控 PR 状态
   - 响应 review 意见
   - 更新代码

## 统计和报告

### 扫描统计

```python
stats = get_statistics()

print(f"总扫描次数: {stats['total_scans']}")
print(f"总贡献机会: {stats['total_opportunities']}")
print(f"平均机会/扫描: {stats['avg_opportunities_per_scan']:.2f}")
```

### 贡献统计

```python
from erbing_system.social.github_trending_tracker import trending_tracker

summary = trending_tracker.get_summary()

print(f"追踪仓库数: {summary['tracked_repos']}")
print(f"总贡献数: {summary['total_contributions']}")
print(f"Open PRs: {summary['open_prs']}")
print(f"Merged PRs: {summary['merged_prs']}")
```

## 故障排除

### GitHub API 限制

**问题**: API rate limit exceeded

**解决方案**:
1. 配置 GitHub API token
2. 减少扫描频率
3. 使用缓存机制

### 网络问题

**问题**: 无法连接到 GitHub

**解决方案**:
1. 检查网络连接
2. 配置代理
3. 使用镜像站点

### 权限问题

**问题**: 无法创建 PR

**解决方案**:
1. 检查 GitHub token 权限
2. 确认项目接受 PR
3. 检查分支保护规则

## 最佳实践

### 1. 贡献策略

- **优先级**: 先选择高优先级项目
- **质量**: 确保代码质量，添加测试
- **文档**: 更新相关文档
- **沟通**: 积极响应 review 意见

### 2. 时间管理

- **频率**: 每日扫描，每周贡献
- **时间**: 选择项目活跃时间
- **跟踪**: 定期检查 PR 状态

### 3. 质量控制

- **测试**: 确保所有测试通过
- **代码风格**: 遵循项目代码风格
- **文档**: 添加必要的文档
- **review**: 主动请求 review

## 扩展功能

### 1. 多语言支持

```python
# 获取 Python 热门项目
trending = await fetch_trending(language="python")

# 获取 TypeScript 热门项目
trending = await fetch_trending(language="typescript")
```

### 2. 自定义贡献策略

```python
from erbing_system.social.github_trending_tracker import GitHubTrendingTracker

tracker = GitHubTrendingTracker()

# 自定义分析逻辑
async def custom_analysis(repo):
    opportunities = []
    # 自定义分析逻辑
    return opportunities

# 使用自定义分析
tracker.analyze_repo_for_contribution = custom_analysis
```

### 3. 集成其他工具

```python
# 集成到二饼系统
from erbing_system.erbing import Erbing

erbing = Erbing()

# 使用 GitHub Trending 数据
trending = await fetch_trending()
for repo in trending:
    # 分析项目
    opportunities = await analyze_repo_for_contribution(repo)
    # 创建贡献计划
    plan = erbing.pae.create_plan(
        task=f"Contribute to {repo.name}",
        steps=opportunities,
    )
```

## 贡献指南

### 如何贡献

1. Fork 本项目
2. 创建功能分支
3. 提交更改
4. 创建 PR

### 开发指南

- 遵循现有代码风格
- 添加测试
- 更新文档
- 响应 review

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/yourusername/github-trending-tracker
- 问题反馈: https://github.com/yourusername/github-trending-tracker/issues

## 更新日志

### v1.0.0 (2026-04-20)
- 初始版本发布
- 实现基本追踪功能
- 实现自动 PR 提交
- 实现统计和报告
