# AgentGPT Integration for OpenClaw

## 概述

AgentGPT 是一个强大的自主 AI 代理框架，允许用户配置和部署自主 AI 代理。本集成文档描述了如何将 AgentGPT 框架整合到 OpenClaw 平台中。

## 架构设计

```
integrations/agentgpt/
├── INTEGRATION.md          # 集成文档（本文件）
├── web/                    # Web 界面集成
│   ├── index.html          # 主界面
│   ├── app.js              # 前端逻辑
│   └── styles.css          # 样式文件
├── visualization/          # 任务可视化
│   ├── task-monitor.js     # 任务监控组件
│   ├── graph-view.js       # 图形化展示
│   └── progress-tracker.js # 进度追踪器
├── deployment/             # 部署管理
│   ├── docker-compose.yml  # Docker 部署配置
│   ├── kubernetes.yaml     # K8s 部署配置
│   └── config.yaml         # 配置文件
└── examples/               # 示例代码
    ├── basic-agent.js      # 基础代理示例
    ├── task-example.js     # 任务示例
    └── test-runner.js      # 测试运行器
```

## 核心功能

### 1. Web 界面集成
- 提供用户友好的图形界面
- 支持代理配置和部署
- 实时任务监控

### 2. 任务可视化
- 任务执行流程图
- 进度追踪面板
- 日志实时展示

### 3. 部署管理
- Docker 容器化部署
- Kubernetes 集群部署
- 配置管理

## 集成步骤

### 前置要求
- OpenClaw 运行环境
- Node.js >= 18.0.0
- Docker (可选，用于容器部署)

### 安装

```bash
# 进入集成目录
cd integrations/agentgpt

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置必要的参数

# 启动服务
npm start
```

### 配置说明

在 `deployment/config.yaml` 中配置以下参数：

```yaml
agentgpt:
  api_endpoint: "http://localhost:3000"
  model: "gpt-4"
  max_tokens: 4000
  temperature: 0.7

openclaw:
  gateway_url: "http://localhost:8080"
  auth_token: "${OPENCLAW_AUTH_TOKEN}"

visualization:
  enabled: true
  update_interval: 1000
  max_history: 100
```

## API 接口

### 创建代理
```http
POST /api/agents/create
Content-Type: application/json

{
  "name": "MyAgent",
  "goal": "完成任务X",
  "model": "gpt-4"
}
```

### 启动任务
```http
POST /api/tasks/start
Content-Type: application/json

{
  "agent_id": "agent_123",
  "task": "执行任务描述"
}
```

### 获取任务状态
```http
GET /api/tasks/{task_id}/status
```

## 与 OpenClaw 集成点

### 1. 通过 Gateway API
AgentGPT 通过 OpenClaw Gateway 进行通信：
- 使用 WebSocket 实现实时状态更新
- 通过 REST API 进行任务管理

### 2. 事件订阅
订阅 OpenClaw 事件：
- 任务完成通知
- 错误处理
- 资源状态变更

### 3. 技能调用
AgentGPT 代理可以调用 OpenClaw 技能：
- 文件操作
- 代码执行
- 外部 API 调用

## 监控与日志

### 日志配置
日志文件位置：`logs/agentgpt/`
- `agent-{date}.log` - 代理执行日志
- `task-{date}.log` - 任务执行日志
- `error-{date}.log` - 错误日志

### 监控指标
- 任务成功率
- 平均执行时间
- 资源使用情况
- 代理活跃数量

## 故障排除

### 常见问题

1. **连接失败**
   - 检查 Gateway 是否运行
   - 验证 auth_token 是否有效

2. **任务超时**
   - 调整 `task_timeout` 配置
   - 检查网络连接

3. **内存不足**
   - 减少 `max_concurrent_tasks`
   - 增加容器内存限制

## 最佳实践

1. 使用环境变量管理敏感配置
2. 定期清理历史任务数据
3. 设置合理的超时和重试策略
4. 监控资源使用情况

## 版本兼容性

| AgentGPT 版本 | OpenClaw 版本 | 状态 |
|--------------|--------------|------|
| 1.0.x        | 0.9.0+       | 支持 |
| 1.1.x        | 0.10.0+      | 推荐 |

## 更新日志

- 2026-04-16: 初始集成版本
