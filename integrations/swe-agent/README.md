# SWE-agent - OpenClaw 集成

快速开始指南，帮助你快速上手 SWE-agent 集成。

## 快速安装

```bash
# 克隆 OpenClaw workspace
cd ~/.openclaw/workspace/integrations/swe-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export GITHUB_TOKEN="your_token_here"
export OPENCLAW_API_URL="http://localhost:3000"
```

## 5 分钟快速开始

### 1. 处理你的第一个 Issue

```python
from swe_agent.github.issue_handler import IssueHandler

handler = IssueHandler()
result = handler.process_issue(
    repo="your-org/your-repo",
    issue_number=1
)

print(f"Issue 分类: {result.category}")
print(f"优先级: {result.priority}")
print(f"建议: {result.suggestion}")
```

### 2. 创建你的第一个 PR

```python
from swe_agent.pr.pr_creator import PRCreator

creator = PRCreator()
pr = creator.create_from_fix(
    repo="your-org/your-repo",
    issue_number=1,
    files_changed=["src/main.py"],
    commit_message="Fix: Resolve issue #1"
)

print(f"PR 创建成功: {pr.url}")
```

### 3. 执行代码审查

```python
from swe_agent.pr.code_reviewer import CodeReviewer

reviewer = CodeReviewer()
review = reviewer.review_pr(
    repo="your-org/your-repo",
    pr_number=1
)

print(f"安全性评分: {review.security_score}/10")
print(f"代码质量: {review.quality_score}/10")
print(f"建议: {review.suggestions}")
```

## 主要功能

| 功能 | 描述 | 状态 |
|------|------|------|
| Issue 分类 | 自动分类 GitHub Issues | ✅ |
| Bug 检测 | 从 Issue 中提取 Bug 信息 | ✅ |
| 自动修复 | 生成修复补丁 | ✅ |
| PR 创建 | 自动创建 Pull Requests | ✅ |
| 代码审查 | LLM 驱动的代码审查 | ✅ |
| CI 集成 | GitHub Actions 集成 | ✅ |

## 配置示例

```yaml
# ~/.openclaw/config/swe-agent.yaml
agent:
  enabled: true
  auto_fix: false  # 首次使用建议关闭自动修复
  
github:
  default_repo: "your-org/your-repo"
  
llm:
  provider: "openclaw"
  model: "claude-3-sonnet"
```

## 下一步

- 阅读 [INTEGRATION.md](./INTEGRATION.md) 了解详细架构
- 查看 [examples/](./examples/) 目录的示例代码
- 运行测试: `pytest tests/`

## 获取帮助

- GitHub Issues: [提交问题](https://github.com/openclaw/swe-agent/issues)
- 文档: [完整文档](https://openclaw.ai/docs/swe-agent)
- 社区: [Discord](https://discord.gg/openclaw)
