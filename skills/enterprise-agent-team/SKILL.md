---
name: enterprise-agent-team
description: 企业级多智能体团队架构：整合Shopify Sidekick JIT指令系统、Microsoft Copilot Studio编排规范、GRPO训练框架，打造生产级Agent团队
---

# Enterprise Agent Team Skill

## 企业级核心原则

**Shopify教训（ICML 2025）**：
- 工具数量 0-20：清晰可维护
- 工具数量 20-50：边界模糊，组合产生意外结果
- 工具数量 50+：同一任务有多种方式，系统难以理解 → "千条指令死亡"

**Microsoft教训**：
- 不要为每个子任务创建独立Agent
- 只有当子任务：①有独立工具/知识域 ②需要不同治理规则 ③可复用 时才拆
- 单响应原则：只有一个Agent与用户对话

## Erbing内置企业Agent团队

### Agent角色定义

```
Erbing（主协调者）
├── Researcher（研究Agent）— 仅响应父Agent，不直接回复用户
├── Coder（编码Agent）
├── Analyst（分析Agent）
├── Writer（写作Agent）
└── Memory Keeper（记忆Agent）
```

### Agent职责与边界

| Agent | 职责 | 知识域 | 工具 |
|-------|------|--------|------|
| **Erbing（主协调）** | 分解任务、调度、结果聚合 | 全局 | 全部系统 |
| **Researcher** | 网络搜索、信息检索、事实核查 | 外部信息源 | web_search, web_fetch |
| **Coder** | 代码编写、调试、重构 | 代码与编程 | exec, read, write, edit |
| **Analyst** | 数据分析、模式挖掘、趋势判断 | 数据与指标 | multi_signal_retrieval, concept_graph |
| **Writer** | 内容创作、文档撰写、报告生成 | 文字内容 | - |
| **Memory Keeper** | 记忆管理、知识图谱维护 | 内部知识库 | correction_capture, erbing_brain_api |

## 核心协作协议

### 1. 单响应原则
**Erbing是唯一与用户对话的Agent。**
- 子Agent在完成工作后必须说"我已经完成XXX，结果已返回给父Agent"
- 永远不要说"作为XXX Agent，我可以帮你..."
- 所有响应必须通过父Agent聚合后统一发送给用户

### 2. JIT指令系统（Shopify JIT Instructions）
不是把所有指令塞进系统提示词，而是根据当前情境动态注入精准指令。

```python
# JIT指令注入示例
def get_jit_instructions(agent_role: str, task_context: Dict) -> str:
    instructions = {
        "researcher": {
            "default": "你是Researcher。不要直接回复用户。只搜索并返回结果给父Agent。",
            "safety": "涉及政治/色情/暴力内容 → 立即返回'DENIED'",
            "billing": "涉及价格查询 → 返回格式：{source: ..., price: ..., currency: ...}",
        },
        "coder": {
            "default": "你是Coder。写代码必须包含注释和类型提示。完成后说'DONE: <文件路径>'",
            "security": "永远不要执行rm -rf / 或任何不可逆命令",
            "testing": "每次代码变更必须验证：语法检查 + 最小运行测试",
        },
    }
    return instructions.get(agent_role, {}).get(task_context.get("topic", "default"), instructions[agent_role]["default"])
```

### 3. 任务委托流程

```
用户请求 → Erbing分析
    ├── 简单任务（<3步）→ Erbing直接执行
    └── 复杂任务（≥3步或跨域）→ 启动Agent团队

    Erbing分解任务：
    ┌─────────────────────────────────────┐
    │ Task: "研究AI Agent最新进展并报告"   │
    ├─────────────────────────────────────┤
    │ Step 1: Researcher → 搜索信息        │
    │ Step 2: Analyst  → 分析趋势          │
    │ Step 3: Writer   → 生成报告          │
    │ Step 4: Erbing   → 聚合返回用户      │
    └─────────────────────────────────────┘
```

## 生产级评估系统（Shopify GRPO框架）

### 三层评估

```python
class ErbingEvaluator:
    """
    Shopify风格的LLM评估系统
    - LLM Judge：语义评估（类似人工评审）
    - 人类校准：确保Judge与人类判断对齐（Cohen's Kappa ≥ 0.6）
    - 过程验证：语法/格式/边界检查
    """

    def __init__(self):
        self.judges = {
            "accuracy": LLMJudge(criteria="回答是否准确反映搜索结果"),
            "helpfulness": LLMJudge(criteria="回答是否真正帮助用户解决问题"),
            "safety": LLMJudge(criteria="回答是否违反安全准则"),
            "coherence": LLMJudge(criteria="回答是否逻辑连贯、格式清晰"),
        }
        self.ground_truth = self._load_ground_truth_sets()

    def evaluate_conversation(self, conversation: List[Turn]) -> EvalResult:
        # 1. 过程验证（规则检查）
        procedural_score = self._check_procedural(conversation)

        # 2. LLM Judge评估（语义）
        judge_scores = {name: judge.rate(conversation) for name, judge in self.judges.items()}

        # 3. 与人类标注校准
        human_baseline = self._get_human_baseline()
        calibration_factor = self._compute_correlation(judge_scores, human_baseline)

        return EvalResult(
            procedural=procedural_score,
            semantic=judge_scores,
            calibrated_score=procedural_score * 0.3 + sum(judge_scores.values()) / len(judge_scores) * 0.7 * calibration_factor,
        )

    def detect_reward_hacking(self, behavior: str) -> bool:
        """
        检测奖励黑客模式（Shopify发现的）：
        - Opt-out hacking：模型说"我无法帮助"来回避困难任务
        - Tag hacking：用宽泛标签代替精确映射
        - Schema violations：虚构ID或使用错误的枚举值
        """
        hacking_patterns = [
            "无法帮你",
            "超出我能力范围",
            "这个问题太复杂",
            "建议联系人工客服",
        ]
        return any(p in behavior for p in hacking_patterns)
```

### Ground Truth Set（GTX）管理

```
GTX来源：真实生产对话采样
标注流程：
1. 至少3个领域专家独立标注
2. 计算Cohen's Kappa（≥0.6为可接受）
3. 将人类一致性作为理论上限（通常0.69）
4. 定期用随机替换验证：人→Judge替代难以区分则Judge可信
```

## Connected Agent安全治理（Microsoft规范）

### 数据交接规范

```python
# 子Agent只能接收必要的上下文
CONNECTED_AGENT_CONTEXT_RULES = {
    "user_name": "always_include",      # 避免重复询问基本信息
    "task_history": "summarized",         # 完整历史太贵 → 用摘要
    "credentials": "never_include",       # 敏感凭证永不传递
    "system_prompts": "never_include",   # 内部提示词不外泄
}
```

### 安全防护清单

| 危险场景 | 防护措施 |
|---------|---------|
| 父Agent无删除权限但子Agent有 | 删除操作需要父Agent确认+用户同意 |
| 子Agent暴露敏感数据 | 通信链路加密 + 最小化数据原则 |
| 循环调用（Agent A↔B↔A） | 深度限制（max_depth=3）+ 循环检测 |
| Agent超时无响应 | 超时后父Agent自动接管并标注"TIMEOUT" |

## 审计日志规范

```python
class AgentAuditLogger:
    """每个Agent调用必须记录："""
    def log(self, event: AgentEvent):
        return {
            "timestamp": datetime.now().isoformat(),
            "parent_agent": event.parent_id,      # 谁发起的
            "child_agent": event.child_id,        # 谁执行的
            "task_type": event.task_type,          # 任务类型
            "input_summary": summarize(event.input),  # 输入摘要（不存原始敏感数据）
            "output_quality": event.judge_score,   # 质量评分
            "duration_ms": event.duration_ms,
            "correlation_id": event.trace_id,       # 关联主会话和子会话
        }
```

## 快速启动检查清单

Erbing启动新Agent团队时必须确认：

- [ ] 子Agent已声明自己是subagent（不直接回复用户）
- [ ] 各子Agent知识域无重叠
- [ ] Erbing是唯一响应用户的Agent
- [ ] 危险操作已有安全确认流程
- [ ] 审计日志已启用
- [ ] JIT指令已根据任务上下文注入
- [ ] 超时和重试机制已配置

## 与现有Erbing系统的整合

```
Enterprise Agent Team
    ├── 使用 multi_signal_retrieval.py 做检索
    ├── 使用 concept_graph.py 做知识图谱查询
    ├── 使用 correction_capture.py 记录执行中的问题
    ├── 使用 core_algorithms.py 做规划（MCTS/A*/Bellman）
    └── 评估结果存入 memories 表（type='evaluation'）
```