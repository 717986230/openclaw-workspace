# SWE-agent Integration for OpenClaw

## 概述

SWE-agent (Software Engineering Agent) 是一个基于 AI 的自动化软件开发工具，能够自动处理 GitHub Issues、创建 Pull Requests、修复 Bug 和执行代码审查。本文档描述了如何将 SWE-agent 集成到 OpenClaw 生态系统中。

## 架构设计

```
integrations/swe-agent/
├── INTEGRATION.md          # 集成文档 (本文件)
├── README.md               # 快速开始指南
├── github/                 # GitHub 集成模块
│   ├── issue_handler.py    # Issue 处理逻辑
│   ├── pr_manager.py       # PR 管理逻辑
│   ├── repo_analyzer.py    # 仓库分析工具
│   └── workflow_client.py  # GitHub Actions 集成
├── issues/                 # Issue 处理模块
│   ├── issue_classifier.py # Issue 分类器
│   ├── bug_detector.py     # Bug 检测器
│   ├── priority_analyzer.py# 优先级分析
│   └── templates/          # Issue 模板
│       ├── bug_report.md
│       ├── feature_request.md
│       └── improvement.md
├── pr/                     # PR 管理模块
│   ├── pr_creator.py       # PR 创建器
│   ├── code_reviewer.py    # 代码审查器
│   ├── merge_handler.py    # 合并处理器
│   └── templates/          # PR 模板
│       ├── bug_fix.md
│       ├── feature.md
│       └── refactor.md
├── core/                   # 核心引擎
│   ├── agent.py            # SWE-agent 主引擎
│   ├── context_manager.py  # 上下文管理器
│   ├── llm_interface.py    # LLM 接口
│   └── execution_engine.py # 执行引擎
├── utils/                  # 工具函数
│   ├── git_operations.py   # Git 操作
│   ├── file_manager.py     # 文件管理
│   ├── logger.py           # 日志系统
│   └── config.py           # 配置管理
└── tests/                  # 测试文件
    ├── test_issue_handler.py
    ├── test_pr_manager.py
    └── test_agent.py
```

## 核心功能

### 1. GitHub Issue 处理

- **Issue 自动分类**: 基于 LLM 的智能分类 (bug/feature/improvement)
- **Bug 自动检测**: 从 Issue 描述中提取错误信息
- **优先级评估**: 根据 Issue 影响范围和紧急程度分配优先级
- **自动分配**: 根据代码库知识图谱分配给合适的开发者

### 2. PR 创建和管理

- **自动 PR 创建**: 从 Bug 修复自动生成 PR
- **智能代码审查**: 基于 LLM 的代码审查建议
- **CI/CD 集成**: 与 GitHub Actions 深度集成
- **合并策略**: 智能合并冲突解决

### 3. Bug 修复自动化

- **错误定位**: 基于堆栈跟踪和日志定位错误
- **补丁生成**: 自动生成修复补丁
- **测试生成**: 为修复生成单元测试
- **回归测试**: 确保修复不引入新问题

### 4. 代码审查

- **静态分析**: 集成 ESLint, Pylint 等工具
- **安全扫描**: 检测常见安全漏洞
- **性能分析**: 识别性能瓶颈
- **最佳实践**: 检查代码规范和最佳实践

## 与 OpenClaw 的集成点

### 1. LLM 路由

SWE-agent 使用 OpenClaw 的 `ask_local_ai_routed` 工具进行 LLM 调用:

```python
from openclaw.tools import ask_local_ai_routed

# 使用 Claude 进行复杂推理
response = ask_local_ai_routed(
    prompt="分析这个 GitHub Issue 并生成修复方案",
    mode="claude_only"
)

# 使用 Claude + Codex 进行代码审查
review = ask_local_ai_routed(
    prompt="审查这段代码的安全性和性能",
    mode="claude_then_codex_review"
)
```

### 2. Memory 系统

SWE-agent 的知识存储在 OpenClaw Memory 系统中:

- **代码库知识**: 存储代码结构、依赖关系
- **修复历史**: 记录过去的 Bug 修复案例
- **最佳实践**: 积累代码审查经验

### 3. TaskFlow 集成

复杂的多步骤任务通过 TaskFlow 管理:

```yaml
taskflow:
  name: "swe-agent-issue-fix"
  steps:
    - name: "classify_issue"
      action: "issues/classify"
    - name: "analyze_codebase"
      action: "github/analyze_repo"
    - name: "generate_fix"
      action: "core/generate_patch"
    - name: "create_pr"
      action: "pr/create"
    - name: "monitor_ci"
      action: "github/check_workflow"
```

### 4. 技能系统

SWE-agent 作为 OpenClaw 技能注册:

```yaml
skill:
  name: swe-agent
  description: 自动化软件工程任务处理
  triggers:
    - "修复 bug"
    - "处理 issue"
    - "创建 PR"
    - "代码审查"
  capabilities:
    - issue_handling
    - pr_management
    - bug_fixing
    - code_review
```

## 配置

### 环境变量

```bash
# GitHub 配置
GITHUB_TOKEN=your_github_token
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# SWE-agent 配置
SWE_AGENT_MODEL=claude-3-sonnet
SWE_AGENT_MAX_ITERATIONS=10
SWE_AGENT_TIMEOUT=300

# OpenClaw 集成
OPENCLAW_API_URL=http://localhost:3000
OPENCLAW_MEMORY_PATH=~/.openclaw/memory
```

### 配置文件

```yaml
# swe-agent/config.yaml
agent:
  name: "swe-agent"
  version: "1.0.0"
  
llm:
  default_model: "claude-3-sonnet"
  fallback_model: "gpt-4"
  temperature: 0.7
  
github:
  default_branch: "main"
  auto_merge: false
  require_reviews: 2
  
issue:
  auto_assign: true
  label_threshold: 0.8
  
pr:
  template_dir: "templates/"
  require_tests: true
  
logging:
  level: "INFO"
  file: "logs/swe-agent.log"
```

## 使用示例

### 1. 处理 GitHub Issue

```python
from swe_agent import SWEAgent

agent = SWEAgent()
result = agent.handle_issue(
    repo="owner/repo",
    issue_number=123,
    auto_fix=True
)
```

### 2. 创建 PR

```python
pr = agent.create_pr(
    repo="owner/repo",
    title="Fix: Resolve null pointer exception",
    branch="fix/null-pointer",
    files=["src/main.py", "tests/test_main.py"],
    description="自动修复 Issue #123"
)
```

### 3. 代码审查

```python
review = agent.review_code(
    repo="owner/repo",
    pr_number=456,
    check_security=True,
    check_performance=True
)
```

## 最佳实践

### 1. Issue 处理流程

1. 接收 Issue 通知
2. 分类和优先级评估
3. 分析相关代码
4. 生成修复方案
5. 创建 PR
6. 监控 CI 结果
7. 根据反馈迭代

### 2. 安全考虑

- 所有代码修改需要通过安全扫描
- 敏感信息不得提交到版本控制
- 使用 GitHub App 而非 Personal Access Token
- 限制对关键分支的直接推送

### 3. 性能优化

- 缓存代码库分析结果
- 批量处理多个 Issue
- 异步执行 CI 检查
- 使用增量分析

## 故障排除

### 常见问题

1. **GitHub API 限流**
   - 使用条件请求
   - 实现指数退避
   - 缓存响应

2. **LLM 超时**
   - 调整 timeout 配置
   - 使用流式响应
   - 分拆大任务

3. **合并冲突**
   - 定期同步主分支
   - 使用 rebase 而非 merge
   - 自动冲突检测

## 监控和日志

### 关键指标

- Issue 处理时间
- PR 创建成功率
- CI 通过率
- 用户满意度

### 日志格式

```json
{
  "timestamp": "2026-04-16T13:46:00Z",
  "level": "INFO",
  "component": "issue_handler",
  "action": "classify",
  "repo": "owner/repo",
  "issue": 123,
  "result": "bug",
  "confidence": 0.95
}
```

## 未来扩展

- [ ] 支持更多 Git 托管平台 (GitLab, Bitbucket)
- [ ] 增强 LLM 推理能力
- [ ] 集成更多静态分析工具
- [ ] 支持多语言代码库
- [ ] 实现学习型代码修复

## 参考资源

- [SWE-agent 论文](https://arxiv.org/abs/2405.15793)
- [OpenClaw 文档](https://openclaw.ai/docs)
- [GitHub API 文档](https://docs.github.com)
- [Claude API 文档](https://docs.anthropic.com)

## 许可证

MIT License - 与 OpenClaw 主项目保持一致
