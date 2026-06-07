# 2026-06-07 Claude Code + Hermes Agent 源码架构学习

## 来源
- Claude Code: npm source map 泄漏分析 + DeepWiki 官方架构文档
- Hermes Agent: Nous Research 官方文档 + GitHub 历史提交分析

---

## Claude Code 架构要点

### 核心技术
- **Runtime**: Bun（比 Node.js 启动更快）
- **Language**: TypeScript strict mode
- **UI**: React 18 + Ink（终端渲染 React 组件）
- **Agent Loop**: `async function* query()` — async generator 统一事件流/终止/错误
- **MCP Client**: @modelcontextprotocol/sdk
- **Feature Flags**: GrowthBook（服务端 A/B 测试）

### Agentic Loop 设计（核心！）

```typescript
// async generator 模式 — 比 EventEmitter 更优雅
export async function* query(params: QueryParams): AsyncGenerator<
  StreamEvent | RequestStartEvent | Message | ToolUseSummaryMessage,
  Terminal  // 终止原因作为返回值
>
```

**对比三种模式**：
- EventEmitter: 事件流分散在回调注册中
- Callback: onEvent/onDone/onError 分散在不同通道
- Async Generator: 统一在 `for await...of` 中处理

### 4层消息压缩
1. Tool output pruning（工具输出裁剪成1行摘要）
2. Token budget tail protection（预算保护）
3. Structured 13-section handoff summary（结构化交接）
4. Iterative summary updates（跨压缩迭代更新）

### 8层安全
- 命令审批（52KB permissions.ts）
- 路径遍历保护
- Git 参数注入防护
- 52K 超大文件专用于安全

### Open Source vs Reality
- 官方 GitHub: 279 文件（只是 plugin shell）
- 实际核心引擎: 4600+ 文件
- 许可证: Anthropic Commercial ToS（不是真正的开源）

---

## Hermes Agent 架构要点

### 系统架构
```
Entry Points → AIAgent
                ├── Prompt Builder (prompt_builder.py)
                ├── Provider Resolution (runtime_provider.py)
                └── Tool Dispatch (model_tools.py, registry.py)
                    ├── 70+ tools
                    ├── 28 toolsets
                    └── Compression & Caching
```

### 关键子系统

**1. Session Storage**
- SQLite + FTS5（hermes_state.py）
- 跨会话记忆 + 全文检索

**2. Context Engine（可插拔！）**
```python
class ContextEngine(ABC):
    def compress(messages, token_limit) -> CompressedMessages
    def on_turn_start(turn_context)
    def on_pre_compress(messages)
```

**3. Memory Provider（插件化）**
- 生命周期: initialize → prefetch → sync_turn → shutdown
- 可选钩子: on_turn_start, on_session_end, on_pre_compress, on_delegation

**4. Cron 系统**
- jobs.json 调度
- 每次创建 fresh AIAgent（无历史）
- 附加 skills 作为上下文

**5. Gateway（20+平台）**
- telegram / discord / slack / whatsapp / signal / matrix / email / sms
- dingtalk / feishu / wecom / weixin / qqbot / yuanbao
- bluebubbles / homeassistant / webhook / api_server

---

## 自我进化机制（Hermes 核心！）

1. **Skill creation**: 从经验中创建新 skill
2. **Skill self-improvement**: 使用中持续改进
3. **Cross-session memory**: FTS5 检索
4. **User modeling**: Honcho dialectic

---

## 对 Erbing 的具体启发

### 立即可用
1. **async generator 模式**: 现有的 exec 流可以用 async generator 重构
2. **4层压缩**: ErbingContextCompressor 已实现，可以对照补充第3、4层
3. **可插拔 ContextEngine**: 现有的压缩逻辑可以抽象成 ABC

### 架构层面
4. **多 provider 路由**: Hermes 的 runtime_provider 模式 → OpenClaw 可以学习多模型切换
5. **Gateway 架构**: 对应 OpenClaw 的 channel 系统（但 Hermes 更统一）
6. **Cron 调度**: 每 job 创建 fresh agent → 类似 sessions_spawn isolated

### 技能层面
7. **Skill self-improvement**: 当前 skill_workshop 只有创建/改进流程，缺少"从使用经验中自动改进"的能力
8. **Memory plugin 机制**: Hermes 的 plugins/memory/ → Erbing 的 database/ 已经类似，但可以更插件化

### Claude Code 启发
9. **Agentic loop 模式**: 深入理解 async generator 驱动的 agent loop
10. **Tool output pruning**: 对应 Erbing 的 tool 结果压缩
11. **Feature flags**: 可以用配置控制实验性功能的灰度

---

## 下一步行动
- [ ] 对照 Claude Code 的 4层压缩，检查 ErbingContextCompressor 缺失层
- [ ] 研究 async generator 能否用于改善 sessions_spawn 的结果收集
- [ ] Hermes MemoryProvider 插件机制 → 思考 Erbing 是否需要类似的插件架构
- [ ] Skill self-improvement loop → 融入 skill_workshop 的 update 流程