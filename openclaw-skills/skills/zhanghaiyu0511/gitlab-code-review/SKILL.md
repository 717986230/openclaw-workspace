---
name: gitlab-code-review
description: GitLab 定时代码审查，自动获取新提交并生成 Review 报告。触发场景：(1) 用户说"配置 GitLab code review"、"设置代码审查"、"帮我监控 GitLab 提交"； (2) 用户提到 GitLab code review 或需要定时审查代码；(3) Heartbeat 执行定时检查时。
---

# GitLab Code Review

定时获取 GitLab 新提交，自动生成代码审查报告并推送通知。

## 用户配置流程

当用户说「配置 GitLab code review」或类似意图时：

### 1. 引导用户输入配置

逐个询问以下信息：

```
我需要几个配置信息：

1. GitLab URL 是什么？（例如：https://gitlab.example.com）

2. 项目路径是什么？（group/project 格式）

3. 分支名称是什么？（默认 main）

4. Personal Access Token 是什么？
   需要的权限：read_api
   获取方式：GitLab → 用户设置 → Access Tokens
```

### 2. 创建配置文件

收集完信息后，创建 `workspace/.env` 文件：

```
GITLAB_URL=<用户输入的URL>
GITLAB_TOKEN=<用户输入的Token>
GITLAB_PROJECT=<用户输入的项目路径>
GITLAB_BRANCH=<用户输入的分支>
```

### 3. 更新 HEARTBEAT.md

在 `HEARTBEAT.md` 中添加定时任务（注意使用正确的脚本路径）：

```markdown
## GitLab Code Review（整点执行）
**检查条件**：当前时间接近整点（xx:00 ± 10分钟）
**执行步骤**：
1. 运行 `python3 skills/gitlab-code-review/scripts/fetch_commits.py`
2. 检查 `memory/pending_review_*.json` 是否存在
3. 有待处理文件：按时间排序逐个 review → 推送简化报告和完整报告文件到当前用户 → 删除 pending 文件
4. 无新提交：回复 HEARTBEAT_OK
```

### 4. 执行首次审查

配置完成后，**立即执行首次审查**：

1. 运行 `python3 skills/gitlab-code-review/scripts/fetch_commits.py` 获取待审查提交
2. 检查 `memory/pending_review_*.json` 是否存在
3. 如果有待处理文件：
   - 按文件名排序（时间正序）
   - 逐个进行深度 code review
   - 生成完整报告 `memory/code_review_<short_id>.md`
   - 使用 message 工具推送到当前用户：
     - 发送简化版报告文本
     - 发送完整报告文件（.md 附件）
   - 删除已处理的 pending 文件
4. 如果无提交，提示用户

### 5. 确认完成

```
✅ 配置完成！

- 已创建 .env 文件
- 已更新 HEARTBEAT.md
- 已完成首次审查并推送报告

之后每小时整点将自动检查新提交并推送审查报告。
```

## 定时执行逻辑

Heartbeat 触发时（整点附近）：

1. **检查配置**：读取 `workspace/.env`
2. **获取提交**：执行 `skills/gitlab-code-review/scripts/fetch_commits.py`
3. **检查结果**：查看 `memory/pending_review_*.json`
4. **有新提交**：
   - 读取 pending 文件内容
   - 进行深度 code review
   - 生成报告 `memory/code_review_<short_id>.md`
   - 推送简化版报告和完整报告文件到当前对话用户
   - 删除 pending 文件
5. **无新提交**：回复 `HEARTBEAT_OK`

## 推送方式

使用 message 工具推送两条消息：

**1. 简化版报告文本**：
```json
{
  "action": "send",
  "channel": "feishu",
  "target": "当前用户ID",
  "message": "简化版报告内容"
}
```

**2. 完整报告文件**：
```json
{
  "action": "send",
  "channel": "feishu",
  "target": "当前用户ID",
  "media": "memory/code_review_<short_id>.md",
  "filename": "code_review_<short_id>.md",
  "caption": "📋 完整的 Code Review 报告"
}
```

### 自定义推送目标

如需推送到群聊，在 `HEARTBEAT.md` 中配置推送目标。

## 脚本说明

### scripts/fetch_commits.py

获取 GitLab 未审查的提交。

**执行方式**：
```bash
python skills/gitlab-code-review/scripts/fetch_commits.py
```

**首次运行**：只获取最近 2 个提交
**后续运行**：获取上次审查之后的所有新提交（最多 50 个）

**依赖**：
- 配置文件：`workspace/.env`
- Python 包：`requests`, `python-dotenv`

**输出**：
- `memory/pending_review_<short_id>.json` - 待审查提交数据
- `memory/gitlab_review_state.json` - 审查状态记录

## Code Review 维度

审查提交时，关注以下维度：

### 🔒 安全性
- SQL 注入、XSS、CSRF 漏洞
- 敏感信息泄露（密码、Token 硬编码）
- 权限校验缺失

### ⚡ 性能
- N+1 查询问题
- 循环内数据库操作
- 大数据集内存问题
- 缓存策略合理性

### 📦 代码质量
- 命名规范与可读性
- 注释完整性
- 错误处理与边界检查
- 重复代码

### 🧪 可测试性
- 依赖注入
- 单一职责
- 测试覆盖

## 报告格式

完整报告保存到 `memory/code_review_<short_id>.md`。

简化版推送格式：

```markdown
📋 GitLab Code Review - 新提交审查

提交: <short_id>
标题: <title>
作者: <author>
时间: <time>
变更: <N> 个文件

⚠️ 发现 <严重程度> 问题

🔴 主要问题:
1. <问题描述>
   📄 <文件路径>:<行号范围>

💡 改进建议:
1. <建议内容>

📊 状态: <状态说明>
🔗 查看详情: <commit_url>
```

## 故障排查

### Skill 未识别

确保 skill 安装在正确位置：
- ClawHub 安装：`workspace/skills/gitlab-code-review/`
- 手动安装：解压到 `workspace/skills/`

### 脚本执行失败

```bash
# 检查依赖
pip3 install requests python-dotenv

# 测试连接
python skills/gitlab-code-review/scripts/fetch_commits.py
```

### Token 权限不足

确保 Token 有 `read_api` 权限：
- GitLab → 用户设置 → Access Tokens
- 勾选 `read_api`
- 创建新 Token

### 无新提交被检测

检查 `memory/gitlab_review_state.json` 中的 `last_reviewed_commit_id`：
```bash
cat memory/gitlab_review_state.json
```

如果需要重新检测，删除该文件后重新运行脚本。
