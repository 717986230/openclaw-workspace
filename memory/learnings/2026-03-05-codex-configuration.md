# Codex 连接配置指南

## 📋 当前状态

### ✅ 已完成
1. **OpenClaw ACP 配置已启用**
   - `acp.enabled: true`
   - `acp.backend: "acpx"`
   - `acp.defaultAgent: "pi"`
   - `acp.allowedAgents: ["pi", "claude", "codex", "opencode", "gemini"]`

2. **acpx 插件已安装**
   - 版本：0.1.13
   - 位置：`C:\Users\admin\AppData\Local\nvm\v22.22.0\node_modules\openclaw\extensions\acpx`

3. **配置文件已就绪**
   - `~/.openclaw/openclaw.json` 已配置 codex 在允许列表中

### ❌ 待完成
1. **`@zed-industries/codex-acp` 包未安装**
   - 这是 codex 的 ACP adapter
   - 需要安装才能使用 codex

## 🔧 配置步骤

### 方案一：使用 OpenClaw ACP 运行时（推荐）

如果有 Discord 或其他支持线程的渠道：

```json
// 使用 sessions_spawn
{
  "task": "Your task here",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

### 方案二：直接使用 acpx CLI

```powershell
# 进入 acpx 目录
cd "C:\Users\admin\AppData\Local\nvm\v22.22.0\node_modules\openclaw\extensions\acpx"

# 查看帮助
.\node_modules\.bin\acpx --help

# 使用 codex
.\node_modules\.bin\acpx codex "your prompt"

# 创建会话
.\node_modules\.bin\acpx codex sessions new --name my-session

# 查看状态
.\node_modules\.bin\acpx codex status
```

## 📝 acpx 常用命令

| 命令 | 说明 |
|------|------|
| `acpx codex "prompt"` | 使用 codex 执行提示 |
| `acpx codex sessions new` | 创建新会话 |
| `acpx codex sessions new --name NAME` | 创建命名会话 |
| `acpx codex sessions` | 列出所有会话 |
| `acpx codex status` | 查看 codex 状态 |
| `acpx codex exec "prompt"` | 一次性执行 |
| `acpx codex cancel` | 取消当前任务 |
| `acpx config show` | 显示配置 |
| `acpx config init` | 初始化配置 |

## 🎯 其他可用的 ACP agents

acpx 支持多个 coding agents：

- `pi` - Pi agent
- `claude` - Claude Code
- `codex` - Codex (需要安装 adapter)
- `opencode` - OpenCode
- `gemini` - Gemini CLI

## 📌 注意事项

1. **webchat 限制**：webchat 不支持线程绑定，所以 `mode="session"` 需要 `thread=true`，但 webchat 不支持。可以使用 `mode="run"` 进行 one-shot 执行。

2. **Adapter 安装**：codex 需要 `@zed-industries/codex-acp` 这个 npm 包，当前未安装。

3. **配置位置**：
   - 全局配置：`C:\Users\admin\.acpx\config.json`
   - 项目配置：`.acpxrc.json`

## 🚀 下一步

1. 安装 `@zed-industries/codex-acp` 包（如果需要）
2. 或者使用其他已配置的 agent（pi, claude, opencode, gemini）
3. 在支持线程的渠道（如 Discord）中使用完整的 ACP 会话功能

---
*记录时间：2026-03-05*
