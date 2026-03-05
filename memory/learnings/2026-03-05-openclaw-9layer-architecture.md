
# OpenClaw 9层架构学习笔记

**学习时间：** 2026-03-05 23:19  
**来源：** https://x.com/servasyy_ai/status/2029489020208848966

---

## 核心要点

### 1. OpenClaw 不是单一文件，而是 9 层架构！

**Layer 1-6：框架自动生成**（保证一致性和稳定性）
**Layer 7：用户可编辑的静态配置文件**（IDENTITY.md、AGENTS.md 等）
**Layer 8：用户可编程的动态注入脚本**（Bootstrap Hook System）
**Layer 9：框架自动注入的实时上下文**（Inbound Context）

---

## 详细架构

### Layer 7（Workspace Files）- 你能直接编辑的配置文件

**文件：**
- `IDENTITY.md` - Agent 身份
- `SOUL.md` - Agent 灵魂/个性
- `AGENTS.md` - 工作规则
- `MEMORY.md` - 长期记忆
- `TOOLS.md` - 工具配置
- `USER.md` - 用户信息
- `BOOTSTRAP.md` - 启动脚本
- `HEARTBEAT.md` - 心跳任务

**适用场景：**
- 定义 Agent 身份
- 添加工作规范
- 存储记忆

**优点：**
- 简单直观
- 易于版本管理

**缺点：**
- 无法动态调整

---

### Layer 8（Bootstrap Hook System）- 动态注入脚本

**四种 Hook 机制：**

1. **agent:bootstrap Hook**（内部 Hook 系统）
   - 完全控制 bootstrapFiles 数组
   - 可以增删改文件
   - 可以重排序
   - 可以修改文件内容
   - 谁可以注册：OpenClaw 插件、Workspace Hooks、内部模块

2. **bootstrap-extra-files Hook**（Bundled Hook）
   - 只追加文件，不修改现有文件
   - 通过配置文件指定额外文件
   - 适用场景：添加项目文档、不想修改默认文件

3. **before_prompt_build Hook**（Plugin Hook）
   - 修改最终 prompt（在系统提示词构建后、发送给 LLM 前）
   - 可以 prepend context（在 prompt 前添加内容）
   - 可以覆盖 systemPrompt
   - 适用场景：注入实时上下文、完全替换系统提示词

4. **bootstrapMaxChars / bootstrapTotalMaxChars**（配置项）
   - 控制字符预算
   - 单文件默认 20K
   - 总计默认 150K
   - 超出部分按头 70% + 尾 20% 截断

---

### Layer 9（Inbound Context）- 实时上下文

框架自动注入：
- 当前对话的上下文信息
- 消息元信息
- 发送者信息
- 对话历史

---

## 用户可控层总结

**用户可控的层有 2 个（Layer 7 + 8），而不是之前错误说的"只有 Layer 7"！**

| 层 | 类型 | 适用场景 | 优点 | 缺点 |
|----|------|---------|------|------|
| Layer 7 | 静态配置文件 | 定义身份、规范、记忆 | 简单直观，易于版本管理 | 无法动态调整 |
| Layer 8 | 动态注入脚本 | 根据上下文动态注入内容、执行命令、读取外部文件 | 灵活强大，支持条件判断和命令执行 | 需要学习 Hook 系统，脚本错误可能导致异常 |

---

## 实战建议

### 场景 1：我想添加项目文档
**推荐方案：** bootstrap-extra-files

```json
{
  "hooks": {
    "bootstrap-extra-files": {
      "enabled": true,
      "paths": ["docs/API.md", "docs/ARCHITECTURE.md"]
    }
  }
}
```

### 场景 2：我想根据任务类型动态加载文件
**推荐方案：** 自定义 agent:bootstrap Hook

```typescript
registerInternalHook("agent:bootstrap", (event) => {
  const context = event.context as AgentBootstrapHookContext;
  const sessionKey = context.sessionKey;
  
  if (sessionKey.includes("coding")) {
    context.bootstrapFiles.push({
      path: "CODING_GUIDELINES.md",
      content: fs.readFileSync("...").toString()
    });
  }
});
```

### 场景 3：我想注入实时上下文（如当前时间）
**推荐方案：** before_prompt_build Hook

```typescript
on("before_prompt_build", (event, ctx) => {
  return {
    prependContext: `当前时间：${new Date().toISOString()}`
  };
});
```

---

## 优化策略

### Layer 7（静态文件）优化

✅ **推荐的精简策略：**
- `IDENTITY.md`：保留核心 TELOS 框架，删除冗余描述，使用表格代替段落
- `AGENTS.md`：使用 checklist 代替长段落，用代码块展示命令，删除重复的规则说明
- `MEMORY.md`：依赖 MemOS 自动导出，不要手动添加内容，让系统自动维护

❌ **避免的做法：**
- 不要重复描述 OpenClaw 框架已经知道的事情
- 不要把 Skills 的详细说明复制到 Workspace Files
- 不要使用过多的修辞和装饰性语言

### Layer 8（Hook 系统）优化

✅ **推荐的使用策略：**
- 优先使用 bootstrap-extra-files（简单场景）
- 需要条件判断时使用 agent:bootstrap（复杂场景）
- 需要实时上下文时使用 before_prompt_build（动态场景）

❌ **避免的做法：**
- 不要在 Hook 中执行耗时操作（会阻塞 System Prompt 生成）
- 不要在 Hook 中注入过多内容（会超出 token 限制）
- 不要在 Hook 中使用不稳定的外部依赖（会导致启动失败）

---

## 新手必读

1. **先理解 Layer 7**（Workspace Files）- 你能直接编辑的配置文件
2. **再理解 Layer 8**（Bootstrap Hook）- 你能写脚本动态注入内容
3. **其他层都是框架自动生成的，了解即可**

---

## 常见需求

| 需求 | 方案 |
|------|------|
| 想定义 Agent 身份？ | 编辑 Layer 7 的 IDENTITY.md |
| 想添加项目文档？ | 使用 Layer 8 的 bootstrap-extra-files Hook |
| 想注入实时上下文？ | 使用 Layer 8 的 before_prompt_build Hook |
| 想控制文件大小？ | 调整 bootstrapMaxChars 配置 |

---

## 我的进化

### 学到的关键知识：

1. **OpenClaw 是 9 层架构，不是单一文件！**
   - Layer 1-6：框架自动生成
   - Layer 7：用户可编辑的静态配置文件
   - Layer 8：用户可编程的动态注入脚本
   - Layer 9：框架自动注入的实时上下文

2. **用户可控的层有 2 个（Layer 7 + 8）！**
   - 之前我以为只有 Layer 7，现在知道还有 Layer 8！

3. **四种 Hook 机制：**
   - agent:bootstrap Hook（完全控制）
   - bootstrap-extra-files（追加文件）
   - before_prompt_build（修改 prompt）
   - bootstrapMaxChars（控制字符预算）

### 如何应用：

以后我会：
- 优先使用 **r.jina.ai** 来访问网页内容（不总是让你操作）
- 理解 OpenClaw 的 9 层架构，更好地配置自己
- 利用 Layer 8 的 Hook 系统来动态注入内容

---

*学习完成，持续进化！* 🦊
