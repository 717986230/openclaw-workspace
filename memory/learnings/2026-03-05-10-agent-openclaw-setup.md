
# My 10-Agent OpenClaw Setup (+ Prompts)

**学习时间：** 2026-03-05 23:30  
**来源：** https://x.com/sandraleow/status/2029418426402521545

---

## 核心架构

### 1. Single Source of Truth — 唯一真相源！

**问题：**
- 大多数人安装 OpenClaw，扔一个系统提示词，然后奇怪为什么他们的 agent 没有做任何有用的事

**解决方案：**
- ✅ **你需要一个唯一真相源！**
- ✅ 如果 agent 看不到发生了什么，它们就无法对其采取行动！

---

### 2. Mission Control Dashboard — 任务控制看板！

**Sandra 的做法：**
- 用 Next.js 构建了一个看板式看板，本地运行
- **每个 agent 都从这个看板读取！**
- **这不是一个好东西，这是协调层！**
- 没有它，agent 会重复工作或闲置！

**关键设计决策：**
- Agent 自主检查待办事项
- 如果有它们领域的任务，它们就排队并领取
- **不需要分配！**

**提示词：**
```
Create a mission control dashboard in Next.js with a kanban-style taskboard. 
It should update in real-time and serve as the main hub where agents check for available tasks. 
Include columns for Backlog, In Progress, Review, and Done.
```

---

### 3. Model Selection — 模型选择是关键！

**Sandra 的分配：**
- **10 个 agent 中有 5 个运行在 Kimi K2.5**
- Kimi 比 Claude 便宜 5-8 倍！
- 对于研究、趋势扫描、数据提取等任务，你不需要前沿模型
- 你需要一个不会吃掉你预算的可靠模型！

**成本堆栈：**
- Claude Max: $100/mo (web interface)
- Anthropic API: OpenClaw agents 单独计费
- Kimi Allegretto: $39/mo (包括 OpenClaw 部署 + 2x K2.5 使用)
- Gemini API: Flash 免费层

**规则：让模型匹配任务复杂度！**
- 创意和推理密集型工作 → Claude
- 结构化检索和监控 → Kimi
- 简单操作 → Gemini Flash

**反例：**
- 如果你在一个每天检查两次黄金价格的 cron 作业上运行 Sonnet，你就是在烧钱！

---

### 4. Telegram Topics — 8 个话题 = 8 个隔离的上下文！

**问题：**
- 一个 Telegram 聊天处理所有事情 = 一个巨大的上下文窗口，对话会混在一起

**解决方案：**
- ✅ **Telegram Topics 解决这个问题！**
- ✅ 8 个话题 = 8 个隔离的上下文
- ✅ 每个话题有自己的记忆文件

**例子：**
- 在 "Content-Sourcing" 中标记 agent → 它搜索并记录到那个话题的记忆
- 在 "Product-Manager" 中 → 它更新任务看板

**路由：**
```javascript
const topicRouter = {
  1: 'general',
  20: 'content-sourcing',
  32: 'product-manager',
  162: 'writing-agent',
};

function routeMessage(topicId, message) {
  const context = topicRouter[topicId] || 'general';
  writeToMemory(context, message);
  updateDashboard(context, message);
}
```

**注意：**
- Telegram 的 Bot API 把每个话题当作单独的聊天 ID
- 你的 bot 每个话题需要明确的权限
- 漏掉一个 → 静默失败，没有错误消息

---

### 5. Heartbeats — 心跳让 agent 主动而不是被动！

**概念：**
- 每个间隔，agent 醒来，检查看板，扫描它的记忆，决定是否采取行动

**Sandra 的经验：**
- 从 30 分钟间隔开始
- 太激进了 — 在空检查上烧 token
- 确定为活跃 agent 1-2 小时，夜间更慢
- 研究和趋势 agent 可以每 3 小时运行一次，因为它们的任务对时间不敏感

**提示词：**
```
Every [interval], check the Mission Control dashboard for tasks in the backlog that match your domain.
If a task is available, queue it, update the board to "In Progress," and begin working.
If no tasks are available, scan your recent memory for follow-ups worth flagging.
Log a brief status update either way.
```

**成本叠加：**
- 一个每 2 小时运行一次心跳的 Kimi agent 几乎不花钱
- 一个做同样事情的 Sonnet agent 加起来很快！

---

### 6. 完整工作流

```
Telegram message
       ↓
Parse topic ID → route to context
       ↓
Write to topic-specific .md file
       ↓
Dashboard reads memory/*.md → live UI
       ↓
Extract tasks → update taskboard
       ↓
Agent heartbeat picks up task → executes
       ↓
Result logged back to topic memory
```

---

### 7. 每个 agent 得到相同的结构！

**提示词：**
```
You are [role]. Your domain is [specific scope].
You have access to [tools]. Your quality bar is [standard].
You do not work outside your domain - if a task falls outside your scope,
flag it in the General topic.
Check the dashboard every heartbeat for tasks in your domain.
Be proactive, not reactive.
```

**关键洞察：**
- 人们在这里搞错了
- 他们认为更多自由 = 更好的输出
- **恰恰相反！**
- 当你约束领域时，agent 实际上可以在这些墙内快速移动
- 当有东西坏了时，你可以隔离问题，因为每个 agent 的范围是定义的

**对比：**
- 一个不受约束的 agent 是一个黑盒
- 一个受约束的 agent 你可以调试

---

### 8. 下一步：Agent 之间的通信！

**Sandra 的计划：**
- 允许 agent 相互通信
- 让任务的交接更顺利地运行！

---

### 9. 知识层：OpenClaw + Obsidian + Claude Code

**这是 Sandra 没有覆盖的层：**
- 知识系统
- agent 如何访问你的 vault
- 跨时间追踪想法
- 在复合的上下文上构建

---

## 我的进化

### 学到的关键教训：

1. **你需要一个唯一真相源！**
   - 如果 agent 看不到发生了什么，它们就无法对其采取行动
   - Mission Control Dashboard — 看板式看板，协调层
   - Agent 自主检查待办事项，不需要分配

2. **模型选择是关键！**
   - 10 个 agent 中有 5 个运行在 Kimi K2.5（便宜 5-8 倍）
   - 创意和推理密集型工作 → Claude
   - 结构化检索和监控 → Kimi
   - 简单操作 → Gemini Flash
   - 不要在 cron 作业上运行 Sonnet — 烧钱！

3. **Telegram Topics = 隔离的上下文！**
   - 8 个话题 = 8 个隔离的上下文
   - 每个话题有自己的记忆文件
   - 路由消息到正确的上下文

4. **Heartbeats — 主动而不是被动！**
   - 间隔：活跃 agent 1-2 小时，夜间更慢，研究 3 小时
   - 不要太激进（30 分钟）— 烧 token
   - 模型选择在这里叠加：Kimi 心跳几乎不花钱，Sonnet 加起来很快

5. **约束领域 = 更好的输出！**
   - 人们搞错了：更多自由 ≠ 更好的输出
   - 恰恰相反！
   - 约束领域时，agent 可以在墙内快速移动
   - 出问题时可以隔离问题
   - 不受约束的 agent 是黑盒，受约束的 agent 你可以调试

### 如何应用：

以后我会：
- 思考如何建立一个唯一真相源（即使简单）
- 让模型匹配任务复杂度（不要浪费钱）
- 隔离上下文（不要让对话混在一起）
- 用心跳让 agent 主动
- 约束领域（约束 = 更好的输出 + 可调试）

---

*学习完成，持续进化！* 🦊
