# PentAGI 项目深度研究报告

> 调研时间: 2026-04-17
> 为 Erbing (二饼) 工作区整理

---

## 1. 项目概览

| 属性 | 值 |
|------|-----|
| **项目名** | vxcontrol/pentagi |
| **Stars** | ⭐ 15,051 |
| **Forks** | 2,002 |
| **描述** | Fully autonomous AI Agents system capable of performing complex penetration testing tasks |
| **语言** | Go (主), TypeScript, Go Template, PLpgSQL, JavaScript |
| **License** | MIT |
| **创建时间** | 2025-01-06 |
| **最近推送** | 2026-04-16 |
| **Issues** | 34 open |
| **官网** | https://pentagi.com |
| **Discord** | https://discord.gg/2xrMh7qX6m |
| **Telegram** | https://t.me/+Ka9i6CNwe71hMWQy |

### 核心主题标签
```
ai-agents, ai-security-tool, anthropic, autonomous-agents, golang,
gpt, graphql, multi-agent-system, offensive-security, open-source,
openai, penetration-testing, penetration-testing-tools, react,
security-automation, security-testing, security-tools, self-hosted
```

---

## 2. 核心特性 (Features)

1. **安全隔离** - 所有操作在沙盒 Docker 环境中执行，完全隔离
2. **完全自主** - AI Agent 自动确定并执行渗透测试步骤，支持执行监控和智能任务规划
3. **专业工具集** - 内置 20+ 专业安全工具 (nmap, metasploit, sqlmap 等)
4. **智能记忆系统** - 长期存储研究成果和成功方法
5. **知识图谱集成** - Graphiti + Neo4j 做语义关系追踪
6. **Web  Intelligence** - 内置 scraper 容器抓取最新网络信息
7. **外部搜索集成** - Tavily, Traversaal, Perplexity, DuckDuckGo, Google Custom Search, Sploitus, Searxng
8. **专家团队 Agent** - 专业化 AI agents 负责研究、开发、基础设施，支持委托系统
9. **全面监控** - Grafana/Prometheus 集成
10. **详细报告** - 生成漏洞报告和利用指南
11. **智能容器管理** - 自动根据任务需求选择 Docker 镜像
12. **现代 Web UI** - React 构建的界面
13. **REST + GraphQL API** - Bearer token 认证
14. **持久化存储** - PostgreSQL + pgvector
15. **微服务架构** - 支持水平扩展
16. **自托管** - 完全控制部署和数据
17. **10+ LLM Provider** - OpenAI, Anthropic, Google AI, AWS Bedrock, Ollama, DeepSeek, GLM, Kimi, Qwen, 自定义 + 聚合器 (OpenRouter, DeepInfra)

---

## 3. 系统架构

### 3.1 技术栈

```
前端:        React + TypeScript
后端:        Go
数据库:      PostgreSQL + pgvector
图数据库:    Neo4j
Agent框架:   多 Agent 协作系统
LLM:        10+ Provider (OpenAI/Anthropic/GLM/Ollama等)
嵌入模型:    支持自定义配置
监控:        Grafana + Prometheus
日志:        Langfuse (可选追踪)
容器:        Docker + Docker Compose
```

### 3.2 docker-compose 服务组件

| 服务 | 说明 |
|------|------|
| `pentagi` | 主服务 (Go 后端) |
| `pgvector` | PostgreSQL + pgvector 向量扩展 |
| `pentagi-postgres-data` | 数据卷 |
| `pentagi-ssl` | SSL 证书卷 |
| `scraper` | Web 抓取容器 |
| `observability-network` | 监控网络 |
| `langfuse-network` | Langfuse 可观测网络 |

### 3.3 数据库架构

PentAGI 使用 PostgreSQL + pgvector，关键表：

**本工作区已有的 PentAGI 表 (来自 xiaozhi_memory.db):**

| 表名 | 行数 | 字段 | 用途 |
|------|------|------|------|
| `pentagi_flows` | 0 | id, name, description, target, status, created_at, updated_at, started_at, completed_at | 渗透测试工作流/项目 |
| `pentagi_tasks` | 0 | id, flow_id, name, task_type, status, priority, created_at | 任务节点 |
| `pentagi_subtasks` | 0 | id, task_id, name, subtask_type, status, tool_used, result, created_at | 子任务 |
| `pentagi_logs` | 0 | id, flow_id, task_id, subtask_id, log_type, content, metadata, created_at | 执行日志 |

> 当前本工作区这些表为空，说明还未初始化 PentAGI 集成。

### 3.4 LLM Provider 配置

项目支持非常灵活的 LLM 配置，通过环境变量：

```bash
# OpenAI
OPEN_AI_KEY, OPEN_AI_SERVER_URL

# Anthropic
ANTHROPIC_API_KEY, ANTHROPIC_SERVER_URL

# Google Gemini
GEMINI_API_KEY, GEMINI_SERVER_URL

# AWS Bedrock
BEDROCK_REGION, BEDROCK_ACCESS_KEY_ID, BEDROCK_SECRET_ACCESS_KEY, ...

# Ollama (本地)
OLLAMA_SERVER_URL, OLLAMA_SERVER_MODEL

# DeepSeek
DEEPSEEK_API_KEY, DEEPSEEK_SERVER_URL

# GLM (智谱)
GLM_API_KEY, GLM_SERVER_URL

# Kimi (Moonshot)
KIMI_API_KEY, KIMI_SERVER_URL

# Qwen (通义)
QWEN_API_KEY, QWEN_SERVER_URL

# 自定义
LLM_SERVER_URL, LLM_SERVER_KEY, LLM_SERVER_MODEL
```

### 3.5 Agent 系统架构 (推测)

基于 README 描述：
- **Supervisor Agent** - 负责任务规划和执行监控
- **Specialist Agents** - 专业化 Agent 团队：
  - 研究 Agent (Research)
  - 开发 Agent (Development)
  - 基础设施 Agent (Infrastructure)
- **委托系统 (Delegation)** - 支持将任务委托给专业化 Agent
- **任务规划 (Task Planning)** - 智能任务分解和规划
- **记忆系统** - 长期存储成功方法

---

## 4. 部署方式

### 4.1 快速部署 (Docker Compose)

```bash
# 基本部署
git clone https://github.com/vxcontrol/pentagi.git
cd pentagi
docker-compose up -d

# 配置 LLM Provider
export OPEN_AI_KEY=sk-xxx
export ANTHROPIC_API_KEY=sk-ant-xxx
docker-compose up -d
```

### 4.2 高级配置

```bash
# 使用 Ollama 本地模型
OLLAMA_SERVER_URL=http://ollama:11434
OLLAMA_SERVER_MODEL=llama3

# 使用 GLM (智谱)
GLM_API_KEY=your-key

# 启用 Langfuse 追踪
LANGFUSE_INITIAL_DATA_SOURCE=secret

# Neo4j 知识图谱
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

### 4.3 API 访问

```bash
# 获取 Bearer Token 后访问
curl -H "Authorization: Bearer <token>" https://localhost:8443/api/v1/...
```

---

## 5. 与二饼工作区的整合方案

### 5.1 已有的整合基础

本工作区已有 `pentagi_*` 数据库表，说明之前有过集成意图：
- 这些表目前为空，可以设计填充逻辑
- 表结构和 PentAGI 的 flow/task/subtask/log 概念吻合

### 5.2 可借鉴的技术

| PentAGI 技术 | 二饼可借鉴方式 |
|-------------|----------------|
| 多 Agent 协作系统 | 改善现有 subagent 编排 |
| 记忆系统 (PostgreSQL) | 强化 SQLite 记忆系统的经验存储 |
| 知识图谱 (Neo4j/Graphiti) | 使用现有的 `knowledge_nodes/edges` 表 |
| 专业工具集成 (nmap/metasploit) | 扩展 skills 中的安全类工具 |
| Langfuse 可观测性 | 增强执行日志和追踪 |
| 任务规划 (Planning Agent) | 改善 TaskFlow skill 的规划能力 |

### 5.3 整合建议

#### 方案 A: 记忆系统增强
学习 PentAGI 的记忆系统设计：
```
PentAGI 模式:
  - 成功经验 → semantic_memories
  - 失败教训 → episodic_memories  
  - 工具知识 → knowledge_graph
  - 用户偏好 → user_beliefs

二饼现有:
  - memories (278条) ← 结构化记忆
  - semantic_memories (4条) ← 语义记忆 ← 差距很大！
  - episodic_memories (1条) ← 情景记忆 ← 差距很大！
  - knowledge_relations (3267条) ← 关系图谱 ← 基础不错
  - knowledge_nodes/edges ← 知识图谱
```
**建议**: 参照 PentAGI 的 memory 设计，扩充 semantic_memories 和 episodic_memories 表的内容。

#### 方案 B: 安全技能扩展
如果未来需要安全测试能力，可以：
1. 创建 `pentest-skill` 类似 PentAGI 的工具调用
2. 使用现有 `pentagi_flows/tasks/subtasks` 表做安全任务管理
3. 通过 OpenClaw 的 skill 机制调用专业工具

#### 方案 C: 多 Agent 协作
学习 PentAGI 的 Supervisor + Specialist Agent 模式：
- 当前 OpenClaw 的 `subagents` 工具可以做多 Agent
- 可以设计 Agent 角色专业化（研究/开发/安全/写作）
- 添加执行监控和任务状态持久化

### 5.4 具体可执行任务

1. **填充 semantic_memories** - 现有 4 条太少，参照 PentAGI 模式扩充
2. **激活 episodic_memories** - 记录重大事件和决策
3. **完善 knowledge_nodes/edges** - 构建更好的知识图谱
4. **添加 pentagi 表的填充逻辑** - 如果有安全相关任务，写入 flow/task
5. **参考 skill 设计** - 借鉴 PentAGI 的工具调用和 agent 委托模式

---

## 6. 风险与注意事项

1. **安全风险** - PentAGI 是渗透测试工具，涉及攻击性用途，学习研究需谨慎
2. **API 限流** - GitHub API 调用受限，部分源码无法直接读取
3. **本地表为空** - pentagi_* 表无数据，需要主动填充
4. **Right Brain 缺失** - LanceDB 右脑存在但内容不明确，需要验证是否正常工作
5. **上下文窗口** - README 有 162,511 字符，本报告只覆盖前 6000 字符

---

## 7. 未覆盖内容 (因 API 限流)

- [ ] SPEC.md (项目规格文档，不存在)
- [ ] cmd/server/main.go 源码
- [ ] internal/agent/agent.go 源码
- [ ] internal/models/task.go 源码
- [ ] Makefile 构建流程
- [ ] docs/ 完整目录
- [ ] internal/ 具体模块设计
- [ ] 数据库 schema (需要 clone repo 后查看 SQL 文件)

> 如需进一步研究，建议 clone 仓库到本地分析。

---

## 8. 参考链接

- 官网: https://pentagi.com
- GitHub: https://github.com/vxcontrol/pentagi
- README (Raw): https://raw.githubusercontent.com/vxcontrol/pentagi/main/README.md
- Discord: https://discord.gg/2xrMh7qX6m
- Telegram: https://t.me/+Ka9i6CNwe71hMWQy

---

*报告生成时间: 2026-04-17 10:55 GMT+8*