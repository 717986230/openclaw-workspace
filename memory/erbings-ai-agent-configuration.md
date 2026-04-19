# AI Agent 系统配置 — 整合自 Hermes/Claude Code/MasterClaw/OpenClaw Template

> 来源：Hermes Agent (99k★), Claude Code Production (88+ skills), MasterClaw Core, OpenClaw 4-layer Template, ModularIntellect
> 生成：2026-04-19

---

## 一、核心架构原则

### 从五大系统提炼的金律

| 金律 | 来源 | 说明 |
|------|------|------|
| **关闭学习循环** | Hermes Agent | prefetch → LLM → sync → checkpoint 永动 |
| **记忆即一切** | Claude Code | 无持久记忆 = 每次从零开始 |
| **专业化优于全能** | Claude Code | 11个专家 Agent > 1个全能 Agent |
| **按权限写入** | OpenClaw Template | 子 Agent 只能写 PROPOSALS，Coordinator 升入 MEMORY.md |
| **数据向上流动** | OpenClaw Template | Daily → Working → Rolling → Curated，永不反向 |
| **Always-on 胜于按需** | Claude Code | 交易/监控/定时任务需要专用机器 |
| **安全默认** | Claude Code | 150+ 白名单模式，关键操作黑名单 |
| **定期提醒自醒** | Hermes | periodic_nudge 防止 Agent 躺平 |

---

## 二、四层记忆栈（已实现）

```
Layer 1: Working Memory   → working_memory 表   → TTL 自动过期，瞬时会话
Layer 2: Episodic Memory  → episodic_memories 表 → 事件 + 情绪 + 重要性
Layer 3: Semantic Memory  → semantic_memories 表 → 知识三元组（主-谓-宾）
Layer 4: Procedural Memory → procedural_memories 表 → 技能 + 成功率统计
```

### 读写闭环

```
prefetch(query)           → 从 4 层召回相关记忆
sync_turn(user, assit)    → 将对话轮次写入各层
checkpoint_save(tag)      → 状态快照存 evolution_log
periodic_nudge()          → 周期性自醒提醒
skill_self_improve()      → 技能使用后更新统计，阈值触发复盘
```

---

## 三、ErbingMemoryManager（已实现）

核心模块：`hermes/erbing_memory_manager.py`

```python
# 调度中心（Hermes MemoryManager 模式）
MemoryManager
├── add_provider()         # 注册记忆 Provider（最多1个外部）
├── build_system_prompt()  # 生成系统提示词块
├── prefetch_all()         # 读取所有层
├── sync_all()             # 写入所有层
├── queue_prefetch_all()   # 异步预取下一轮
├── on_pre_compress()      # 压缩前回调
├── checkpoint_save/restore # 快照保存/恢复
└── periodic_nudge()       # 周期性自醒
```

---

## 四、多专家 Agent 协作（待实现）

从 Claude Code Production 提炼的 11 Agent 模式 → 精简为 5 个核心角色：

| Agent | 职责 | 约束（Must NOT） |
|-------|------|----------------|
| **Coordinator** | 任务分解、记忆管理、结果审核 | 不直接写生产代码 |
| **Researcher** | 技术调研、API 评估、最佳实践 | 不做实现决策 |
| **Developer** | 代码实现、测试、调试 | 不决定技术选型 |
| **QA** | 代码审查、测试、bug 分析 | 不写功能代码 |
| **Memory Architect** | 记忆系统维护、整理、蒸馏 | 不参与业务任务 |

### 数据流（OpenClaw Template 模式）

```
User chat → daily log → PROPOSALS.md → Coordinator reviews → MEMORY.md
                               ↑
                    Sub-agents only write here
```

---

## 五、Hook 系统（待实现）

从 Claude Code 提炼的事件钩子：

| 钩子 | 触发 | 动作 |
|------|------|------|
| `on_turn_start` | 每轮开始 | prefetch + 上下文注入 |
| `on_turn_end` | 每轮结束 | sync_turn 写入记忆 |
| `on_session_end` | 会话结束 | 蒸馏 → SUMMARY.md |
| `on_pre_compress` | 上下文压缩前 | 提取长期记忆摘要 |
| `on_delegation` | 子 Agent 完成后 | 合并子 Agent 记忆 |
| `on_checkpoint` | 重要事件 | 快照保存 + 通知 |

---

## 六、技能自主进化（已实现）

```python
skill_auto_create(name, type, desc, steps)
  → pm_record() 写入程序记忆
  → em_add() 记录为事件
  → checkpoint_save()

skill_self_improve(name, success, feedback)
  → 更新成功率统计
  → 阈值触发复盘 checkpoint（N次使用后）
```

阈值配置：`SKILL_AUTOSAVE_THRESHOLD = 3`

---

## 七、定时自动化

从 Claude Code 和 Hermes 提炼：

| 任务 | 频率 | 动作 |
|------|------|------|
| 记忆整理 | 每 10-20 轮 | SUMMARY + LOOPS 更新 |
| 上下文压缩 | Token 超阈值 | compress_context() |
| 健康检查 | 每小时 | 数据库完整性 + 向量同步 |
| 快照保存 | 重要事件后 | checkpoint_save() |
| 遗忘清理 | 每日 | wm_cleanup() 删除过期 WM |
| 技能复盘 | 使用 N 次后 | skill_self_improve() |
| 周报生成 | 每周一 10:00 | 从 episodic 汇总 |

---

## 八、安全加固

从 Claude Code Production 提炼：

```python
# 允许名单模式（OWASP 原则）
allow_patterns = [
    "git add", "git commit", "git push",  # 版本控制
    "sqlite3", "python", "node",           # 已知安全工具
    "gh api", "gh repo",                   # GitHub CLI
]

# 关键操作黑名单
deny_patterns = [
    "rm -rf /",           # 递归删除根目录
    "chmod 777",          # 全权限开放
    "curl.*|bash.*",      # 管道注入
]
```

---

## 九、配置清单（待完成项）

| 功能 | 状态 | 路径 |
|------|------|------|
| 四层记忆栈 | ✅ 已实现 | `scripts/four_layers_manager.py` |
| ErbingMemoryManager | ✅ 已实现 | `hermes/erbing_memory_manager.py` |
| Checkpoint 快照 | ✅ 已实现 | `evolution_log` 表 |
| 技能自进化 | ✅ 已实现 | `skill_auto_create/skill_self_improve` |
| Periodic Nudge | ✅ 已实现 | `periodic_nudge()` |
| Hook 系统 | 🔧 待实现 | 需接入 OpenClaw 事件总线 |
| 多 Agent 协作 | 🔧 待实现 | 需配置 sessions_spawn 流程 |
| 定时自动化 | 🔧 待实现 | 需配置 cron |
| 安全加固 | 🔧 待实现 | 需配置 allow/deny patterns |
| 向量同步桥 | 🔧 待实现 | SQLite → LanceDB 双向同步 |

---

## 十、对照：钱学森 × Hermes

| 钱学森系统科学 | Hermes Agent | Erbing 状态 |
|--------------|-------------|------------|
| 从定性到定量综合集成法 | prefetch → LLM → sync 闭环 | ✅ 已实现 |
| 开放的复杂巨系统 | 80+ fork 生态自生长 | ✅ 知识已存入 |
| 人机结合 | Agent + 人类反馈共进化 | 🔧 待加反馈机制 |
| 实践-认识-再实践 | skill 自提炼 + checkpoint 迭代 | ✅ 已实现 |
| 系统学工程 | 分层记忆 + 专业分工 | 🔧 多 Agent 待配 |