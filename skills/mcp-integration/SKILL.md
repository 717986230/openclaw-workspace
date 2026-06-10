---
name: mcp-integration
description: Model Context Protocol（MCP）— 2026年AI Agent与工具连接的USB-C标准，实现标准化工具调用
---

# MCP Integration Skill

## 什么是MCP

Model Context Protocol (MCP) 是Anthropic提出的开放标准（2024年11月），现已获Anthropic/OpenAI/Google/Microsoft/Amazon全面采用。Linux Foundation AAIF托管。

核心类比：**MCP = USB-C for AI** — 统一的工具连接标准

## 三大核心原语

### 1. Tools（工具）
- 模型驱动的动作调用（类似POST）
- 执行操作：搜索数据库、发送邮件、创建记录
- AI主动决定何时调用

### 2. Resources（资源）
- 应用控制的数据暴露（类似GET）
- 读取数据：配置文件、数据库schema、文档
- 应用程序决定暴露哪些资源

### 3. Prompts（提示模板）
- 用户控制的交互模板
- 用户选择激活哪个模板

## MCP架构（三层）

```
Layer 1 - MCP Host/Application
  ↓ (MCP Client)
Layer 2 - MCP Client (Agent)  ← JSON-RPC 2.0
  ↓
Layer 3 - MCP Server (Connector) ← 暴露具体工具/资源
```

## Erbing的MCP集成策略

### 短期：模拟MCP行为
- 在OpenClaw框架下实现MCP-like的tool registry
- 统一工具调用接口（不管底层是API、CLI还是文件）

### 中期：接入真实MCP Server
- 调研已支持MCP的服务（如Raycast、Cursor、VS Code Copilot等）
- 为Erbing的tools创建MCP兼容接口

### 长期：成为MCP Server
- Erbing的记忆系统、检索系统、概念图作为MCP资源暴露
- 其他Agent可以通过MCP接入Erbing的知识库

## MCP Server实现示例

```python
from mcp.server import MCPServer
from mcp.types import Tool, Resource

# 暴露Erbing记忆作为MCP资源
erbing_memory_resource = Resource(
    uri="erbing://memory",
    name="Erbing Memory",
    description="Erbing's long-term memory store",
    mimeType="application/json"
)

# 暴露搜索工具
search_tool = Tool(
    name="erbing_search",
    description="Search Erbing's memory",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 10}
        }
    }
)
```

## A2A vs MCP（重要区分）

| 协议 | 用途 | 对象 |
|------|------|------|
| MCP | Agent → 工具/数据 | Agent-to-Tool |
| A2A (Agent-to-Agent) | Agent → Agent通信 | Agent-to-Agent |

两者互补，共同构成完整的多智能体系统通信基础设施。

## MCP生态现状（2026年6月）

- Python SDK月下载量：97M+
- 生产中的公共MCP服务器：10,000+
- 基准测试：10,000+并发连接，<50ms响应时间
- 主要采用者：Anthropic、OpenAI、Google、Microsoft、Amazon

## Erbing优先接入的MCP服务

1. **Raycast** - 开发者生产力工具集成
2. **GitHub** - 代码仓库和PR管理
3. **File System** - 本地文件操作
4. **Database** - SQLite/矢量数据库访问
5. **Web Browser** - 网页自动化

## 实施步骤

1. 创建MCP-like工具注册表（scripts/mcp_registry.py）
2. 统一工具调用接口（scripts/mcp_tool_dispatcher.py）
3. 为现有tools添加MCP兼容层
4. 创建工具发现机制（自动发现可用工具）
5. 集成到OpenClaw agent loop