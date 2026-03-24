# OpenClaw多代理协同实战教程

## 来源
- 作者: Researcher_王十三
- 日期: 2026-03-14
- 链接: https://x.com/researchwang/status/2032716395709141223

---

## 为什么要拒绝单Agent工作流？

### 单Agent问题统计
| 问题 | 占比 | 说明 |
|------|------|------|
| Prompt过长质量下降 | 28% | 指令冲突导致模型混淆场景 |
| 业务场景混淆 | 24% | 缺乏多角色隔离 |
| 记忆污染 | 20% | 敏感信息跨权限泄露 |
| 效率瓶颈 | 15% | 串行处理，无法并行 |
| 专业化不足 | 13% | 无法在特定领域积累深度经验 |

### 核心结论
> 样样通！样样松！！！

把每一步拆出单独Agent，放在群组里效率成倍数上升！

---

## 核心概念

### Agent
- OpenClaw中最基本的执行单元
- 每个Agent是完整作用域的大脑
- 拥有自己的Workspace、会话存储、身份定义
- 通过唯一ID标识

### Workspace
- Agent的存储空间
- 包含核心文件：
  - SOUL.md
  - IDENTITY.md
  - MEMORY.md
  - AGENTS.md
  - skills目录

### Binding
- 连接消息来源与Agent的桥梁
- 实现精准路由
- 判断由哪个Agent响应请求

---

## 配置多Agent实战

### 1. 创建第二个Agent
```bash
openclaw agents add wang13Search --workspace /root/.openclaw/Research13boss
openclaw agents list
```

### 2. 创建第二个Telegram机器人
- 在TG群组发送 /newbot

### 3. 关闭机器人隐私模式
- BotFather → /mybots → BotSetting → Group Privacy → Turn Off

### 4. 修改 .openclaw.json
```json
{
  "agents": {
    "defaults": {
      "model": {"primary": "openai-codex/gpt-5.3-codex"},
      "workspace": "/root/.openclaw/workspace"
    },
    "list": [
      {"id": "main"},
      {"id": "wang13search", "name": "wang13Search", "workspace": "/root/.openclaw/Research13boss"}
    ]
  },
  "bindings": [
    {"agentId": "main", "match": {"channel": "telegram", "accountId": "default"}},
    {"agentId": "wang13search", "match": {"channel": "telegram", "accountId": "wang13search"}}
  ]
}
```

### 5. 重启网关
```bash
openclaw gateway restart
```

---

## 推荐角色库资源

- 103个OpenClaw角色模板
- 144个专业领域代理模板
- 55+预设AI专家角色
- UI/UX设计角色库
- 市场营销领域技能集
- 科研工作者技能集

---

*学习时间: 2026-03-14*