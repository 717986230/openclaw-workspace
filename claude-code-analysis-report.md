# Claude Code 架构分析报告
## 用于自身进化的设计模式与实现技巧提取

**分析日期**: 2026-04-09  
**分析目标**: 从 Claude Code 官方插件系统中提取可借鉴的架构思想和设计模式  
**分析范围**: 插件系统、配置管理、Agent工作流程、脚本工具、架构思想

---

## 一、插件系统设计模式

### 1.1 核心架构：组件化 + 自动发现

Claude Code 采用**约定优于配置**的目录结构，实现零配置自动发现：

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json        # 必需：插件清单
├── commands/              # 斜杠命令（.md文件）
├── agents/                # 子代理定义（.md文件）
├── skills/                # 技能包
│   └── skill-name/
│       └── SKILL.md       # 必需
├── hooks/
│   └── hooks.json         # 事件处理器配置
├── .mcp.json              # MCP服务器定义
└── scripts/               # 辅助脚本
```

**关键设计原则**：
1. **分层解耦**：命令（用户触发）、代理（自主执行）、技能（知识注入）、钩子（事件拦截）各司其职
2. **自动发现**：所有组件按约定目录放置，系统启动时自动扫描加载
3. **声明式配置**：YAML frontmatter 定义组件元数据，Markdown body 定义行为

### 1.2 渐进式披露原则（Progressive Disclosure）

三层加载系统管理上下文效率：

| 层级 | 内容 | 加载时机 | 大小限制 |
|------|------|----------|----------|
| Metadata | name + description | 始终加载 | ~100 words |
| SKILL.md body | 核心知识 | 技能触发时 | < 2,000 words |
| Bundled Resources | 详细参考 | 按需加载 | 无限制 |

**实现方式**：
- 核心概念放在 SKILL.md
- 详细模式放在 `references/`
- 工作示例放在 `examples/`
- 工具脚本放在 `scripts/`

### 1.3 可移植性设计：${CLAUDE_PLUGIN_ROOT}

所有插件内路径引用使用环境变量：

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

**好处**：
- 插件可安装到任意位置
- 支持多种安装方式（marketplace、local、npm）
- 跨操作系统兼容

---

## 二、配置管理机制

### 2.1 分层配置体系

```
Enterprise Settings（企业级）
    ↓
Managed Settings（托管设置）
    ↓
User Settings（用户级）
    ↓
Project Settings（项目级）
    ↓
Plugin Settings（插件级）
```

每层可被上层覆盖，实现灵活的权限控制。

### 2.2 .local.md 配置模式

项目级配置使用 `.claude/plugin-name.local.md` 文件：

```markdown
---
enabled: true
strict_mode: false
max_retries: 3
dependencies: ["Task 3.4"]
---
# 任务描述
实现JWT认证...
```

**解析技术**：
```bash
# 提取YAML frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# 读取单个字段
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//')

# 读取Markdown body
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

**关键特性**：
- 配置与代码分离
- 支持结构化数据（YAML）+ 自由文本（Markdown）
- Gitignore 友好（.local.md 不提交）
- 快速激活/禁用（enabled: true/false）

### 2.3 临时激活模式

钩子可通过检查标志文件实现条件激活：

```bash
#!/bin/bash
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"
if [ ! -f "$FLAG_FILE" ]; then
    exit 0  # 未激活，跳过
fi
# 执行验证逻辑...
```

**应用场景**：
- 按需启用严格验证
- 临时调试钩子
- 项目特定行为

---

## 三、Agent 工作流程

### 3.1 Agent 文件结构

```markdown
--- 
name: code-reviewer
description: Use this agent when... Examples:
  <example>
  Context: [场景描述]
  user: "[用户请求]"
  assistant: "[如何响应]"
  <commentary>[为什么触发]</commentary>
  </example>
model: inherit
color: green
tools: ["Read", "Grep"]
---

You are an expert code reviewer...
**Your Core Responsibilities:**
1. [职责1]
2. [职责2]

**Analysis Process:**
[步骤流程]

**Output Format:**
[输出规范]
```

### 3.2 触发机制设计

**description 字段是最关键的部分**，必须包含：
1. 明确的触发条件
2. 2-4个具体示例（`<example>` 块）
3. 上下文、用户请求、助手响应、注释

**示例格式**：
```yaml
description: Use this agent when reviewing code for adherence to project guidelines.
Examples:
<example>
Context: The user has just implemented a new feature.
user: "Can you check if everything looks good?"
assistant: "I'll use the code-reviewer agent to review your changes."
<commentary>Proactive use after feature completion.</commentary>
</example>
```

### 3.3 系统提示设计模式

**标准结构**：

1. **角色定义**：`You are [role] specializing in [domain].`
2. **核心职责**：编号列表（1-5条）
3. **分析流程**：步骤化工作流程
4. **质量标准**：明确的质量要求
5. **输出格式**：结构化输出模板
6. **边缘情况**：特殊情况处理

**写作风格**：
- ✅ 使用第二人称（"You are...", "You will..."）
- ✅ 具体明确的职责
- ✅ 步骤化流程
- ❌ 避免模糊描述
- ❌ 避免第一人称

### 3.4 AI辅助Agent生成

使用结构化提示生成Agent：

```markdown
Create an agent configuration based on this request: "[DESCRIPTION]"

Requirements:
1. Extract core intent and responsibilities
2. Design expert persona for the domain
3. Create comprehensive system prompt with:
   - Clear behavioral boundaries
   - Specific methodologies
   - Edge case handling
   - Output format
4. Create identifier (lowercase, hyphens, 3-50 chars)
5. Write description with triggering conditions
6. Include 2-3 <example> blocks

Return JSON with:
{
  "identifier": "agent-name",
  "whenToUse": "Use this agent when... <example>...</example>",
  "systemPrompt": "You are..."
}
```

---

## 四、脚本工具实现方式

### 4.1 Hook脚本模式

**命令钩子（确定性验证）**：

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 路径遍历检测
if [[ "$file_path" == *".."* ]]; then
    echo '{"decision": "deny", "reason": "Path traversal detected"}' >&2
    exit 2
fi

# 敏感文件检测
if [[ "$file_path" == *".env"* ]]; then
    echo '{"decision": "deny", "reason": "Sensitive file"}' >&2
    exit 2
fi

exit 0  # 允许操作
```

**提示钩子（LLM决策）**：

```json
{
    "type": "prompt",
    "prompt": "Validate file write safety. Check: system paths, credentials, path traversal, sensitive content. Return 'approve' or 'deny'.",
    "timeout": 30
}
```

### 4.2 Hook事件类型

| 事件 | 触发时机 | 用途 |
|------|----------|------|
| PreToolUse | 工具执行前 | 验证、修改、阻止 |
| PostToolUse | 工具执行后 | 反馈、日志 |
| Stop | Agent想停止时 | 完成性检查 |
| SessionStart | 会话开始 | 加载上下文 |
| UserPromptSubmit | 用户提交提示 | 上下文注入 |

### 4.3 验证工具链

```
scripts/
├── validate-hook-schema.sh    # 验证hooks.json结构
├── test-hook.sh               # 测试钩子脚本
├── hook-linter.sh             # 钩子最佳实践检查
├── validate-agent.sh          # Agent结构验证
└── parse-frontmatter.sh       # YAML解析工具
```

**验证流程**：
1. 编辑配置文件
2. 运行 `validate-hook-schema.sh hooks/hooks.json`
3. 测试钩子 `test-hook.sh my-hook.sh test-input.json`
4. 代码检查 `hook-linter.sh my-hook.sh`

### 4.4 安全最佳实践

**输入验证**：
```bash
# 验证工具名格式
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
    echo '{"decision": "deny", "reason": "Invalid tool name"}' >&2
    exit 2
fi
```

**变量引用**：
```bash
# GOOD: 引号保护
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"

# BAD: 注入风险
echo $file_path
```

**超时设置**：
```json
{
    "type": "command",
    "command": "bash script.sh",
    "timeout": 10  // 秒
}
```

---

## 五、可借鉴的架构思想

### 5.1 声明式组件定义

**优势**：
- 人机可读（Markdown + YAML）
- 版本控制友好
- 易于生成和验证
- 支持AI辅助创建

**实现模式**：
```markdown
---
# 元数据（机器可解析）
name: component-name
description: When to use...
tools: ["Read", "Write"]
---

# 行为定义（AI可理解）
You are tasked with...
```

### 5.2 事件驱动架构

**钩子系统设计**：

```
[事件发生] → [匹配器过滤] → [并行执行钩子] → [决策输出]
     ↓              ↓               ↓              ↓
 PreToolUse    "Write|Edit"     hook1, hook2   allow/deny
```

**关键特性**：
- 松耦合：钩子独立运行，互不依赖
- 并行执行：所有匹配钩子同时运行
- 确定性输出：exit code决定行为

### 5.3 渐进式能力增强

**三层能力模型**：

1. **命令层**（用户显式触发）
   - 明确的用户意图
   - 结构化工作流程
   - 参数化输入

2. **代理层**（自主决策执行）
   - 基于上下文触发
   - 多步骤自主完成
   - 工具调用链

3. **技能层**（知识注入）
   - 自动激活
   - 领域专业知识
   - 可复用最佳实践

### 5.4 MCP集成模式

**多服务器类型支持**：

| 类型 | 传输协议 | 认证方式 | 适用场景 |
|------|----------|----------|----------|
| stdio | 子进程 | 环境变量 | 本地工具、自定义服务器 |
| SSE | HTTP | OAuth | 云服务、托管API |
| HTTP | REST | Token | API后端 |
| WebSocket | 双向 | Token | 实时数据、推送 |

**工具命名规范**：
```
mcp__plugin_<plugin-name>_<server-name>__<tool-name>
```

### 5.5 错误处理与反馈

**Exit Code语义**：
- `0` - 成功，输出显示在会话中
- `2` - 阻塞错误，错误信息反馈给Claude
- 其他 - 非阻塞错误

**输出格式**：
```json
{
    "hookSpecificOutput": {
        "permissionDecision": "allow|deny|ask",
        "updatedInput": {"field": "modified_value"}
    },
    "systemMessage": "Explanation for Claude"
}
```

---

## 六、应用于自身进化的具体建议

### 6.1 技能系统改进

**当前问题**：
- 触发描述不够具体
- 缺乏渐进式披露
- 示例不足

**改进方案**：

```yaml
---
name: Enhanced Memory
description: This skill should be used when the user asks to "remember this", 
  "store in memory", "recall from database", "search past conversations", 
  "what did we discuss about X", or mentions "memory system", "hybrid memory",
  "LanceDB", "SQLite memory". Automatically stores, retrieves, and searches
  structured and semantic memories.
---

# Core Memory Operations
Store and retrieve memories using hybrid SQLite + LanceDB architecture.

## When to Use
- User explicitly asks to remember something
- User asks about past discussions
- Context requires historical information
- Semantic search needed for related concepts

## Quick Operations
[核心操作，<500字]

## Additional Resources
- `references/memory-schema.md` - 数据库表结构
- `references/search-patterns.md` - 高级搜索技巧
- `scripts/query_memory.py` - 命令行查询工具
```

### 6.2 Agent工作流程优化

**创建专门的子代理**：

1. **collector-agent** - 信息采集代理
   ```yaml
   name: collector-agent
   description: Use when user asks to "collect information", "gather data", 
     "scrape website", "fetch content", or needs automated data collection.
   model: haiku
   color: cyan
   tools: ["WebFetch", "Read", "Write"]
   ```

2. **researcher-agent** - 深度研究代理
   ```yaml
   name: researcher-agent
   description: Use when user asks to "analyze", "research deeply", 
     "understand architecture", "extract patterns", or needs comprehensive analysis.
   model: sonnet
   color: blue
   tools: ["Read", "Grep", "Glob"]
   ```

3. **coordinator-agent** - 协调代理
   ```yaml
   name: coordinator-agent
   description: Use when managing multiple parallel tasks, delegating to 
     subagents, or coordinating complex workflows.
   model: inherit
   color: magenta
   tools: ["Task", "Read", "Write"]
   ```

### 6.3 钩子系统增强

**添加完成性检查钩子**：

```json
{
    "Stop": [
        {
            "matcher": "*",
            "hooks": [
                {
                    "type": "prompt",
                    "prompt": "Before stopping, verify: (1) All tasks completed? (2) Results saved to database? (3) User informed? Return 'approve' to stop or 'block' with reason to continue.",
                    "timeout": 30
                }
            ]
        }
    ]
}
```

**添加敏感操作验证钩子**：

```json
{
    "PreToolUse": [
        {
            "matcher": "Write|Edit",
            "hooks": [
                {
                    "type": "command",
                    "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate-sensitive-files.sh",
                    "timeout": 10
                }
            ]
        }
    ]
}
```

### 6.4 配置管理改进

**采用 .local.md 模式**：

```markdown
---
enabled: true
auto_collect: true
collection_interval: 3600
sources:
  - name: hacker_news
    enabled: true
  - name: techcrunch
    enabled: false
memory_retention_days: 30
---

# 自动采集配置
每天自动采集AI新闻和技术动态，存储到数据库。
```

**解析脚本**：
```python
# scripts/parse_config.py
import yaml
import sys

def parse_local_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取YAML frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()
            return frontmatter, body
    return None, content

if __name__ == '__main__':
    config, body = parse_local_md(sys.argv[1])
    print(yaml.dump(config, default_flow_style=False))
```

### 6.5 技能目录结构优化

```
~/.agents/skills/
├── enhanced-memory/
│   ├── SKILL.md              # 核心指南（< 2000字）
│   ├── references/
│   │   ├── memory-schema.md  # 数据库表结构
│   │   ├── search-patterns.md # 高级搜索技巧
│   │   └── best-practices.md  # 记忆管理最佳实践
│   ├── examples/
│   │   ├── store-learning.md  # 存储学习示例
│   │   └── semantic-search.md # 语义搜索示例
│   └── scripts/
│       ├── query_memory.py    # 查询工具
│       └── backup_memory.sh   # 备份工具
├── swarm-orchestration/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
└── agent-reach/
    ├── SKILL.md
    ├── references/
    └── scripts/
```

---

## 七、总结与行动计划

### 7.1 核心收获

1. **架构层面**：
   - 组件化 + 自动发现 = 零配置