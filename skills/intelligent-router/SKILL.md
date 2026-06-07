---
name: "intelligent-router"
description: "智能5池路由系统 - Router路由/Decomposer分解/ScriptPool脚本/SkillPool技能/AgentPool智能体。触发：复杂任务自动分配执行时使用。"
---

# Intelligent Router - 智能路由系统

## 概述

5 层智能体系，完成"任务 → 分解 → 分配 → 执行 → 聚合"全流程自动化。

## 核心架构

```
用户任务 → [1]Router → [2]Decomposer → [3]Dispatcher → [4]Executor → [5]Aggregator
                ↓            ↓              ↓
           任务类型/      原子子任务      脚本/技能/Agent池
           复杂度/紧急度    纵向/横向/混合    动态匹配
```

---

## 组件一：智能分配路由 (Router)

### 判断维度

- **类型**: coding/research/messaging/web/file/general
- **复杂度**: simple(1步)/medium(3步内)/complex(3步+)
- **紧急度**: urgent/normal/background

### 路由决策表

| 类型 | 复杂度 | 路由目标 |
|-----|-------|---------|
| coding | high | Claude Code |
| coding | low | OpenClaw exec |
| research | any | collector→researcher→main |
| multi-step | complex | 分解引擎 |
| recurring | any | cron job |
| file | any | OpenClaw tools |
| web | any | browser/web_fetch |
| analysis | medium | phidata-style agent |

---

## 组件二：智能分解引擎 (Decomposer)

### 分解策略

- **纵向**: 按步骤顺序执行 (A→B→C→D)
- **横向**: 可并行任务同时执行 (A‖B‖C→D)
- **混合**: 横向+纵向组合 (A‖B→C‖D→E)

### 子任务模板

| 任务类型 | 默认分解 |
|---------|---------|
| research_report | 采集→分析→整理→报告 |
| market_analysis | 并行采集→串行分析→图表→汇总 |
| coding_task | 需求→代码→测试→审查 |
| daily_brief | 采集→筛选→摘要→推送 |

---

## 组件三：智能脚本池 (ScriptPool)

管理可复用脚本，按关键词动态匹配。

### 脚本索引

```
scripts/brain/:    init_brain_database.py / populate_brain.py / evolve_brain_system.py / erbing_brain_api.py
scripts/news/:     daily-news.ps1 / get_hn_news.ps1 / fetch_news.ps1
scripts/agent/:    hybrid_swarm.py / aco_agent.py / feedback_system.py
scripts/refresh:   refresh_live_data.py
```

### 匹配表

| 触发词 | 脚本 |
|-------|-----|
| 初始化记忆 | init_brain_database.py |
| 填充大脑 | populate_brain.py |
| 每日新闻 | daily-news.ps1 |
| HN新闻 | get_hn_news.ps1 |
| 蜂群任务 | hybrid_swarm.py |
| 反馈分析 | feedback_system.py |

---

## 组件四：智能技能池 (SkillPool)

管理所有可用 Skill，动态选择最匹配技能。

### 技能索引

```python
SKILL_POOL = {
    "coding":      ["codex-skill", "skill_claude_code"],
    "research":     ["market-news", "free-news-brief", "news-search"],
    "memory":       ["enhanced-memory", "skill_memory_db"],
    "automation":   ["auto-workflow", "cron_job", "skill_auto_workflow"],
    "trading":      ["binance-pro", "china-futures"],
    "creative":     ["diagram-maker", "meme-maker", "office"],
    "browser":      ["pinchtab", "browser-automation"],
    "multi_agent":  ["multi-agent-collab"],
    "self_improve": ["self-improving"],
    "discovery":    ["find-skills"],
}
```

### 优先级匹配

| 场景 | 技能 | 优先级 |
|-----|------|-------|
| 期货行情 | china-futures | P0 |
| 新闻搜索 | market-news / free-news-brief | P0 |
| 代码任务 | codex-skill + skill_claude_code | P0 |
| 浏览器操作 | pinchtab | P0 |
| 多角色协作 | multi-agent-collab | P1 |
| 自动化工作流 | auto-workflow + cron_job | P1 |
| 记忆管理 | enhanced-memory + skill_memory_db | P1 |
| 自我改进 | self-improving | P1 |
| 小红书 | xiaohongshu | P2 |
| 发推 | skill_twitter_ai | P2 |

---

## 组件五：智能智能体池 (AgentPool)

管理可用 AI 执行单元，动态分配。

### Agent 能力矩阵

```python
AGENT_POOL = {
    "openclaw_main":    {"best_for": "general/routing/simple", "cost": "low", "speed": "fast"},
    "claude_code":      {"best_for": "coding/implementation/bug_fix", "cost": "medium", "speed": "medium"},
    "codex":            {"best_for": "review/security/architecture", "cost": "medium", "speed": "medium"},
    "subagent_isolated": {"best_for": "parallel/isolated/background", "cost": "per_task", "speed": "fast"},
    "subagent_fork":    {"best_for": "collaborative/context_needed", "cost": "per_task", "speed": "fast"},
}
```

### 分配决策树

```
任务进入
  ↓
复杂度=simple? → YES → OpenClaw直接执行
  ↓ NO
类型=coding+complex? → YES → Claude Code
  ↓ NO
需要并行+不需共享上下文? → YES → subagent_isolated×N
  ↓ NO
其他 → OpenClaw main协调
```

### 组合示例

```python
# 市场分析+推送
{
    "steps": [
        {"agent": "subagent_isolated", "task": "采集BTC", "parallel_with": ["ETH","LTC"]},
        {"agent": "openclaw_main", "task": "分析数据生成报告"},
        {"agent": "message", "task": "推送通知"}
    ]
}

# 代码实现+审查
{
    "steps": [
        {"agent": "claude_code", "task": "实现功能"},
        {"agent": "codex", "task": "安全审查"},
        {"agent": "claude_code", "task": "修复问题"}
    ]
}
```

---

## 完整工作流

```
用户: "做一个 BTC/ETH/LTC 每日技术分析，然后推送给我"

[1] Router → research + multi-step + complex

[2] Decomposer
  G1(并行): [采集BTC‖采集ETH‖采集LTC]
  G2(串行): [分析数据→生成报告]
  G3(串行): [推送通知]

[3] Dispatcher
  G1 → subagent_isolated×3
  G2 → openclaw_main
  G3 → message tool

[4] Executor → G1并行→汇总→G2→G3

[5] Aggregator → memory沉淀 → 通知用户
```

---

## 触发条件

- "帮我做xxx"
- "自动处理"
- "多角色协作完成"
- "一键分析"
- 任何复杂任务(3步以上)
- 需要并行处理时

## 依赖技能

- `multi-agent-collab` (已升级)
- `auto-workflow`
- `skill_memory_db`
- `skill_claude_code`
