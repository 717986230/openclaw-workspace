# PentAGI 整合 - AI 渗透测试框架

整合自：vxcontrol/pentagi

## 一、项目概述

PentAGI 是一个**完全自主的 AI 渗透测试系统**，使用 Go 语言开发，架构非常完善。

### 核心特性
- **自主渗透测试** - 无需人工干预
- **Flow/Task/Subtask 架构** - 多层任务编排
- **多 Provider 支持** - 支持 OpenAI、Anthropic 等
- **实时事件推送** - GraphQL Subscriptions
- **Docker 集成** - 安全隔离执行
- **向量存储** - RAG 知识检索

---

## 二、核心架构

### 1. Flow → Task → Subtask 三层任务模型

```
Flow (渗透测试流程)
  └── Task (具体任务，如：侦察、扫描、利用)
        └── Subtask (子任务，如：端口扫描、目录枚举)
              └── Logs (日志：agent/msg/search/term/vector/screenshot)
```

### 2. 状态机管理

**Flow 状态：**
- pending → running → completed/failed/cancelled

**Task 状态：**
- pending → running → completed/failed/cancelled

**Subtask 状态：**
- pending → running → completed/failed/cancelled

### 3. 控制器模式

```
FlowController → FlowWorker
TaskController → TaskWorker
SubtaskController → SubtaskWorker
LogController (多种类型)
```

### 4. 事件发布

- GraphQL Subscriptions 实时推送
- 支持多种日志类型：
  - AgentLog - Agent 输出
  - AssistantLog - 助手回复
  - MsgLog - 消息
  - SearchLog - 搜索
  - TermLog - 终端输出
  - VectorStoreLog - 向量存储
  - Screenshot - 截图

---

## 三、数据库设计（借鉴）

### 1. Flow 表

```sql
CREATE TABLE pentagi_flows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    target TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME
);
```

### 2. Task 表

```sql
CREATE TABLE pentagi_tasks (
    id TEXT PRIMARY KEY,
    flow_id TEXT NOT NULL,
    name TEXT NOT NULL,
    task_type TEXT,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (flow_id) REFERENCES pentagi_flows(id)
);
```

### 3. Subtask 表

```sql
CREATE TABLE pentagi_subtasks (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    name TEXT NOT NULL,
    subtask_type TEXT,
    status TEXT DEFAULT 'pending',
    tool_used TEXT,
    result TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES pentagi_tasks(id)
);
```

### 4. Event Logs 表

```sql
CREATE TABLE pentagi_logs (
    id INTEGER PRIMARY KEY,
    flow_id TEXT NOT NULL,
    task_id TEXT,
    subtask_id TEXT,
    log_type TEXT NOT NULL,  -- agent/assistant/msg/search/term/vector/screenshot
    content TEXT,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 四、整合到终极记忆系统

### 新增表

已添加到数据库：
- `pentagi_flows` - 渗透测试流程
- `pentagi_tasks` - 任务
- `pentagi_subtasks` - 子任务
- `pentagi_logs` - 事件日志

### 使用示例

```python
from ultimate_memory import get_ultimate_memory

mem = get_ultimate_memory()

# 创建渗透测试流程
flow_id = mem.create_flow('Web App Pentest', 'https://target.com')

# 添加任务
task_id = mem.add_task(flow_id, 'Reconnaissance', 'recon')

# 添加子任务
subtask_id = mem.add_subtask(task_id, 'Port Scan', 'nmap')

# 记录日志
mem.add_log(flow_id, task_id, subtask_id, 'term', 'Port 80 open')

# 更新状态
mem.update_subtask_status(subtask_id, 'completed', result='Found 3 open ports')
```

---

## 五、关键设计借鉴

### 1. 三层任务模型
- Flow: 整体目标
- Task: 具体阶段
- Subtask: 原子操作

### 2. 事件驱动
- GraphQL Subscriptions 实时推送
- 多种日志类型分类

### 3. 状态机管理
- 明确的状态转换
- 错误处理和恢复

### 4. Provider 抽象
- 支持多种 LLM
- 工具执行器

---

整合时间: 2026-04-08
来源: github.com/vxcontrol/pentagi
