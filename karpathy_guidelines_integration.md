# Karpathy Guidelines 整合到二饼

## 一、项目概述

**仓库**: https://github.com/forrestchang/andrej-karpathy-skills
**作者**: forrestchang
**灵感来源**: Andrej Karpathy 的 LLM 编码观察
**核心价值**: 减少 LLM 编码中的常见错误

## 二、核心问题分析

### 2.1 Andrej Karpathy 的观察

> "The models make wrong assumptions on your behalf and just run along with them without checking. They don't manage their confusion, don't seek clarifications, don't surface inconsistencies, don't present tradeoffs, don't push back when they should."

> "They really like to overcomplicate code and APIs, bloat abstractions, don't clean up dead code... implement a bloated construction over 1000 lines when 100 would do."

> "They still sometimes change/remove comments and code they don't sufficiently understand as side effects, even if orthogonal to the task."

### 2.2 四大核心问题

| 问题 | 描述 | 影响 |
|-----|------|------|
| **错误假设** | 默默选择解释，不检查 | 实现错误需求 |
| **隐藏困惑** | 不寻求澄清，不暴露不一致 | 产生错误代码 |
| **过度复杂** | 膨胀抽象，臃肿代码 | 难以维护 |
| **无关修改** | 改变不该改的代码 | 引入新 bug |

## 三、四大原则详解

### 3.1 原则 1: Think Before Coding

**核心思想**: 不要假设。不要隐藏困惑。暴露权衡。

#### 实现要点

```python
# erbing_system/coding/think_before_coding.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class Assumption:
    """假设"""
    description: str
    certainty: float  # 0-1
    alternatives: List[str]

@dataclass
class ClarificationRequest:
    """澄清请求"""
    question: str
    context: str
    options: Optional[List[str]] = None

class ThinkBeforeCoding:
    """编码前思考"""

    def __init__(self):
        self.assumptions: List[Assumption] = []
        self.clarifications: List[ClarificationRequest] = []

    def state_assumption(
        self,
        description: str,
        certainty: float = 0.5,
        alternatives: Optional[List[str]] = None,
    ):
        """明确陈述假设"""
        assumption = Assumption(
            description=description,
            certainty=certainty,
            alternatives=alternatives or [],
        )
        self.assumptions.append(assumption)

        # 如果不确定性高，请求澄清
        if certainty < 0.7:
            self.request_clarification(
                question=f"关于 {description}，我需要确认",
                context=description,
                options=alternatives,
            )

    def request_clarification(
        self,
        question: str,
        context: str,
        options: Optional[List[str]] = None,
    ):
        """请求澄清"""
        clarification = ClarificationRequest(
            question=question,
            context=context,
            options=options,
        )
        self.clarifications.append(clarification)

    def present_interpretations(
        self,
        task: str,
        interpretations: List[str],
    ):
        """呈现多种解释"""
        print(f"任务 '{task}' 有多种可能的解释：")
        for i, interpretation in enumerate(interpretations, 1):
            print(f"{i}. {interpretation}")

        print("\n请选择正确的解释，或者提供更多细节。")

    def push_back(self, reason: str, alternative: str):
        """推回建议"""
        print(f"⚠️ {reason}")
        print(f"💡 建议: {alternative}")

    def stop_when_confused(self, confusion: str):
        """困惑时停止"""
        print(f"❓ 困惑: {confusion}")
        print("请提供更多细节或澄清。")

    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        return {
            "assumptions": [
                {
                    "description": a.description,
                    "certainty": a.certainty,
                    "alternatives": a.alternatives,
                }
                for a in self.assumptions
            ],
            "clarifications": [
                {
                    "question": c.question,
                    "context": c.context,
                    "options": c.options,
                }
                for c in self.clarifications
            ],
        }
```

#### 使用示例

```python
# 示例：用户请求"添加导出用户数据功能"
thinker = ThinkBeforeCoding()

# 明确假设
thinker.state_assumption(
    description="导出所有用户",
    certainty=0.3,
    alternatives=["导出筛选的用户", "导出特定用户"],
)

thinker.state_assumption(
    description="导出为 JSON 文件",
    certainty=0.4,
    alternatives=["CSV 文件", "API 端点", "浏览器下载"],
)

thinker.state_assumption(
    description="包含所有字段",
    certainty=0.2,
    alternatives=["仅公开字段", "用户选择字段"],
)

# 获取总结
summary = thinker.get_summary()
print("编码前思考总结:")
print(f"假设数量: {len(summary['assumptions'])}")
print(f"需要澄清: {len(summary['clarifications'])}")
```

### 3.2 原则 2: Simplicity First

**核心思想**: 解决问题的最少代码。没有推测性功能。

#### 实现要点

```python
# erbing_system/coding/simplicity_first.py
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class ComplexityMetric:
    """复杂度指标"""
    lines_of_code: int
    cyclomatic_complexity: int
    nesting_depth: int
    abstraction_layers: int

@dataclass
class SimplificationSuggestion:
    """简化建议"""
    description: str
    original_code: str
    simplified_code: str
    reason: str

class SimplicityFirst:
    """简单优先"""

    def __init__(self):
        self.metrics: List[ComplexityMetric] = []
        self.suggestions: List[SimplificationSuggestion] = []

    def check_complexity(self, code: str) -> ComplexityMetric:
        """检查复杂度"""
        lines = len(code.split('\n'))
        complexity = self._calculate_cyclomatic_complexity(code)
        nesting = self._calculate_nesting_depth(code)
        abstractions = self._count_abstractions(code)

        metric = ComplexityMetric(
            lines_of_code=lines,
            cyclomatic_complexity=complexity,
            nesting_depth=nesting,
            abstraction_layers=abstractions,
        )
        self.metrics.append(metric)

        # 检查是否过度复杂
        if self._is_overcomplicated(metric):
            self.suggest_simplification(code, metric)

        return metric

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """计算圈复杂度"""
        # 简化实现：统计分支语句
        keywords = ['if', 'elif', 'for', 'while', 'try', 'except', 'and', 'or']
        count = 0
        for line in code.split('\n'):
            for keyword in keywords:
                if keyword in line:
                    count += 1
        return count + 1  # 基础复杂度为 1

    def _calculate_nesting_depth(self, code: str) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped.startswith(('if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'with ')):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif stripped and not stripped.startswith('#'):
                # 简化：假设缩进减少表示嵌套结束
                if line.startswith('    ' * (current_depth + 1)):
                    pass
                elif line.startswith('    ' * current_depth):
                    pass
                else:
                    current_depth = max(0, current_depth - 1)
        return max_depth

    def _count_abstractions(self, code: str) -> int:
        """计算抽象层数"""
        # 简化实现：统计类、函数、装饰器
        count = 0
        for line in code.split('\n'):
            if any(keyword in line for keyword in ['class ', 'def ', '@']):
                count += 1
        return count

    def _is_overcomplicated(self, metric: ComplexityMetric) -> bool:
        """判断是否过度复杂"""
        # 启发式规则
        if metric.lines_of_code > 200:
            return True
        if metric.cyclomatic_complexity > 10:
            return True
        if metric.nesting_depth > 4:
            return True
        if metric.abstraction_layers > 5:
            return True
        return False

    def suggest_simplification(
        self,
        code: str,
        metric: ComplexityMetric,
    ):
        """建议简化"""
        suggestions = []

        if metric.lines_of_code > 200:
            suggestions.append("代码行数过多，考虑拆分函数")

        if metric.cyclomatic_complexity > 10:
            suggestions.append("圈复杂度过高，减少分支逻辑")

        if metric.nesting_depth > 4:
            suggestions.append("嵌套过深，使用提前返回或提取函数")

        if metric.abstraction_layers > 5:
            suggestions.append("抽象层数过多，考虑是否真的需要")

        for suggestion in suggestions:
            self.suggestions.append(SimplificationSuggestion(
                description=suggestion,
                original_code=code[:100] + "...",
                simplified_code="[简化后的代码]",
                reason=suggestion,
            ))

    def ask_senior_engineer(self, code: str) -> bool:
        """询问高级工程师是否过度复杂"""
        # 模拟高级工程师的判断
        metric = self.check_complexity(code)
        return self._is_overcomplicated(metric)

    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        return {
            "metrics": [
                {
                    "lines_of_code": m.lines_of_code,
                    "cyclomatic_complexity": m.cyclomatic_complexity,
                    "nesting_depth": m.nesting_depth,
                    "abstraction_layers": m.abstraction_layers,
                }
                for m in self.metrics
            ],
            "suggestions": [
                {
                    "description": s.description,
                    "reason": s.reason,
                }
                for s in self.suggestions
            ],
        }
```

#### 使用示例

```python
# 示例：检查代码复杂度
simplicity = SimplicityFirst()

code = """
def calculate_discount(amount: float, percent: float) -> float:
    return amount * (percent / 100)
"""

metric = simplicity.check_complexity(code)
print(f"代码行数: {metric.lines_of_code}")
print(f"圈复杂度: {metric.cyclomatic_complexity}")
print(f"嵌套深度: {metric.nesting_depth}")
print(f"抽象层数: {metric.abstraction_layers}")

# 检查是否过度复杂
if simplicity.ask_senior_engineer(code):
    print("⚠️ 代码过度复杂，需要简化")
else:
    print("✅ 代码简洁")
```

### 3.3 原则 3: Surgical Changes

**核心思想**: 只修改必须修改的。只清理自己的混乱。

#### 实现要点

```python
# erbing_system/coding/surgical_changes.py
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import difflib

@dataclass
class Change:
    """变更"""
    line_number: int
    original: str
    modified: str
    reason: str

@dataclass
class ChangeAnalysis:
    """变更分析"""
    total_changes: int
    necessary_changes: int
    unnecessary_changes: int
    style_changes: int
    orphan_removals: int

class SurgicalChanges:
    """精准修改"""

    def __init__(self):
        self.changes: List[Change] = []
        self.request: Optional[str] = None

    def set_request(self, request: str):
        """设置用户请求"""
        self.request = request

    def add_change(
        self,
        line_number: int,
        original: str,
        modified: str,
        reason: str,
    ):
        """添加变更"""
        change = Change(
            line_number=line_number,
            original=original,
            modified=modified,
            reason=reason,
        )

        # 验证变更是否必要
        if self._is_necessary_change(change):
            self.changes.append(change)
        else:
            print(f"⚠️ 不必要的变更: {reason}")

    def _is_necessary_change(self, change: Change) -> bool:
        """判断变更是否必要"""
        # 检查是否直接响应用户请求
        if self.request and self.request.lower() in change.reason.lower():
            return True

        # 检查是否是自己的变更产生的孤儿
        if "orphan" in change.reason.lower():
            return True

        # 检查是否是风格变更
        if self._is_style_change(change):
            print(f"⚠️ 风格变更: {change.reason}")
            return False

        return True

    def _is_style_change(self, change: Change) -> bool:
        """判断是否是风格变更"""
        style_keywords = [
            "format", "style", "whitespace", "quote",
            "indent", "type hint", "docstring",
        ]
        return any(keyword in change.reason.lower() for keyword in style_keywords)

    def match_existing_style(self, original_code: str, new_code: str) -> str:
        """匹配现有风格"""
        # 提取风格特征
        style_features = self._extract_style_features(original_code)

        # 应用风格特征到新代码
        styled_code = self._apply_style_features(new_code, style_features)

        return styled_code

    def _extract_style_features(self, code: str) -> Dict[str, Any]:
        """提取风格特征"""
        features = {
            "quote_style": "single" if "'" in code else "double",
            "indent_size": 4 if "    " in code else 2,
            "has_type_hints": ":" in code,
            "has_docstrings": '"""' in code or "'''" in code,
        }
        return features

    def _apply_style_features(self, code: str, features: Dict[str, Any]) -> str:
        """应用风格特征"""
        # 简化实现：转换引号风格
        if features["quote_style"] == "single":
            code = code.replace('"', "'")
        else:
            code = code.replace("'", '"')

        return code

    def mention_dead_code(self, line_number: int, code: str):
        """提及死代码"""
        print(f"💡 注意到第 {line_number} 行有未使用的代码: {code[:50]}...")
        print("是否需要删除？")

    def remove_orphans(self, changes: List[Change]) -> List[Change]:
        """移除孤儿"""
        orphans = []

        for change in changes:
            # 检查是否产生了孤儿
            if "import" in change.original and "import" not in change.modified:
                orphans.append(change)

        return orphans

    def analyze_changes(self) -> ChangeAnalysis:
        """分析变更"""
        necessary = sum(1 for c in self.changes if self._is_necessary_change(c))
        unnecessary = len(self.changes) - necessary
        style = sum(1 for c in self.changes if self._is_style_change(c))
        orphans = len(self.remove_orphans(self.changes))

        return ChangeAnalysis(
            total_changes=len(self.changes),
            necessary_changes=necessary,
            unnecessary_changes=unnecessary,
            style_changes=style,
            orphan_removals=orphans,
        )

    def verify_changes(self) -> bool:
        """验证变更"""
        analysis = self.analyze_changes()

        print(f"变更分析:")
        print(f"  总变更: {analysis.total_changes}")
        print(f"  必要变更: {analysis.necessary_changes}")
        print(f"  不必要变更: {analysis.unnecessary_changes}")
        print(f"  风格变更: {analysis.style_changes}")
        print(f"  孤儿移除: {analysis.orphan_removals}")

        # 检查是否所有变更都直接响应用户请求
        if analysis.unnecessary_changes > 0:
            print(f"⚠️ 有 {analysis.unnecessary_changes} 个不必要变更")
            return False

        if analysis.style_changes > 0:
            print(f"⚠️ 有 {analysis.style_changes} 个风格变更")
            return False

        return True

    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        analysis = self.analyze_changes()
        return {
            "analysis": {
                "total_changes": analysis.total_changes,
                "necessary_changes": analysis.necessary_changes,
                "unnecessary_changes": analysis.unnecessary_changes,
                "style_changes": analysis.style_changes,
                "orphan_removals": analysis.orphan_removals,
            },
            "changes": [
                {
                    "line_number": c.line_number,
                    "reason": c.reason,
                }
                for c in self.changes
            ],
        }
```

#### 使用示例

```python
# 示例：精准修改
surgical = SurgicalChanges()
surgical.set_request("修复空邮箱验证器")

# 添加变更
surgical.add_change(
    line_number=10,
    original="if not user_data.get('email'):",
    modified="email = user_data.get('email', '')\nif not email or not email.strip():",
    reason="修复空邮箱验证",
)

# 验证变更
if surgical.verify_changes():
    print("✅ 变更验证通过")
else:
    print("❌ 变更验证失败")
```

### 3.4 原则 4: Goal-Driven Execution

**核心思想**: 定义成功标准。循环直到验证。

#### 实现要点

```python
# erbing_system/coding/goal_driven_execution.py
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class VerificationStatus(Enum):
    """验证状态"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"

@dataclass
class Step:
    """步骤"""
    description: str
    verification: str
    status: VerificationStatus = VerificationStatus.PENDING

@dataclass
class SuccessCriteria:
    """成功标准"""
    description: str
    verification_method: Callable[[], bool]
    status: VerificationStatus = VerificationStatus.PENDING

class GoalDrivenExecution:
    """目标驱动执行"""

    def __init__(self):
        self.steps: List[Step] = []
        self.criteria: List[SuccessCriteria] = []
        self.current_step: int = 0

    def transform_task(self, task: str) -> str:
        """转换任务为目标"""
        transformations = {
            "添加验证": "编写无效输入的测试，然后使它们通过",
            "修复 bug": "编写重现 bug 的测试，然后使它通过",
            "重构 X": "确保重构前后测试都通过",
        }

        for old, new in transformations.items():
            if old in task:
                return task.replace(old, new)

        return task

    def add_step(self, description: str, verification: str):
        """添加步骤"""
        step = Step(
            description=description,
            verification=verification,
        )
        self.steps.append(step)

    def add_criteria(
        self,
        description: str,
        verification_method: Callable[[], bool],
    ):
        """添加成功标准"""
        criteria = SuccessCriteria(
            description=description,
            verification_method=verification_method,
        )
        self.criteria.append(criteria)

    def execute_step(self, step_index: int) -> bool:
        """执行步骤"""
        if step_index >= len(self.steps):
            return False

        step = self.steps[step_index]
        print(f"执行步骤 {step_index + 1}: {step.description}")

        # 执行步骤（这里需要实际实现）
        # ...

        # 验证步骤
        result = self.verify_step(step_index)
        step.status = VerificationStatus.PASSED if result else VerificationStatus.FAILED

        return result

    def verify_step(self, step_index: int) -> bool:
        """验证步骤"""
        if step_index >= len(self.steps):
            return False

        step = self.steps[step_index]
        print(f"验证: {step.verification}")

        # 这里需要实际实现验证逻辑
        # ...

        return True

    def verify_criteria(self, criteria_index: int) -> bool:
        """验证成功标准"""
        if criteria_index >= len(self.criteria):
            return False

        criteria = self.criteria[criteria_index]
        print(f"验证标准: {criteria.description}")

        result = criteria.verification_method()
        criteria.status = VerificationStatus.PASSED if result else VerificationStatus.FAILED

        return result

    def loop_until_verified(self) -> bool:
        """循环直到验证"""
        max_iterations = 10
        iteration = 0

        while iteration < max_iterations:
            print(f"\n迭代 {iteration + 1}/{max_iterations}")

            # 执行所有步骤
            all_passed = True
            for i in range(len(self.steps)):
                if not self.execute_step(i):
                    all_passed = False
                    break

            if not all_passed:
                iteration += 1
                continue

            # 验证所有标准
            all_verified = True
            for i in range(len(self.criteria)):
                if not self.verify_criteria(i):
                    all_verified = False
                    break

            if all_verified:
                print("✅ 所有标准验证通过")
                return True

            iteration += 1

        print(f"❌ 达到最大迭代次数 ({max_iterations})")
        return False

    def get_plan(self) -> str:
        """获取计划"""
        lines = ["执行计划:"]
        for i, step in enumerate(self.steps, 1):
            status_emoji = {
                VerificationStatus.PENDING: "⏳",
                VerificationStatus.PASSED: "✅",
                VerificationStatus.FAILED: "❌",
            }.get(step.status, "⏳")

            lines.append(f"{status_emoji} {i}. {step.description}")
            lines.append(f"   验证: {step.verification}")

        return "\n".join(lines)

    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        return {
            "steps": [
                {
                    "description": s.description,
                    "verification": s.verification,
                    "status": s.status.value,
                }
                for s in self.steps
            ],
            "criteria": [
                {
                    "description": c.description,
                    "status": c.status.value,
                }
                for c in self.criteria
            ],
        }
```

#### 使用示例

```python
# 示例：目标驱动执行
goal_driven = GoalDrivenExecution()

# 转换任务
task = "添加验证"
transformed = goal_driven.transform_task(task)
print(f"转换后的任务: {transformed}")

# 添加步骤
goal_driven.add_step(
    description="编写无效输入的测试",
    verification="测试失败（重现问题）",
)

goal_driven.add_step(
    description="实现验证逻辑",
    verification="测试通过",
)

goal_driven.add_step(
    description="检查边界情况",
    verification="边界测试通过",
)

# 添加成功标准
goal_driven.add_criteria(
    description="所有无效输入都被拒绝",
    verification_method=lambda: True,  # 实际实现
)

# 执行计划
print(goal_driven.get_plan())

# 循环直到验证
goal_driven.loop_until_verified()
```

## 四、整合到二饼系统

### 4.1 系统架构

```
二饼系统
├── erbing_system/
│   ├── coding/              # 编码行为指南
│   │   ├── think_before_coding.py
│   │   ├── simplicity_first.py
│   │   ├── surgical_changes.py
│   │   └── goal_driven_execution.py
│   ├── agents/              # Agent 系统
│   │   └── coding_agent.py  # 编码 Agent
│   └── memory/              # 记忆系统
│       └── coding_memory.py # 编码记忆
└── memory/
    ├── database/            # SQLite + LanceDB
    └── ...
```

### 4.2 编码 Agent

```python
# erbing_system/agents/coding_agent.py
from typing import Dict, List, Any, Optional
from .coding.think_before_coding import ThinkBeforeCoding
from .coding.simplicity_first import SimplicityFirst
from .coding.surgical_changes import SurgicalChanges
from .coding.goal_driven_execution import GoalDrivenExecution

class CodingAgent:
    """编码 Agent（整合 Karpathy Guidelines）"""

    def __init__(self):
        self.thinker = ThinkBeforeCoding()
        self.simplicity = SimplicityFirst()
        self.surgical = SurgicalChanges()
        self.goal_driven = GoalDrivenExecution()

    async def process_task(self, task: str) -> Dict[str, Any]:
        """处理编码任务"""
        print(f"\n🎯 处理任务: {task}")

        # 1. 编码前思考
        print("\n📝 阶段 1: 编码前思考")
        self._think_before_coding(task)

        # 2. 转换任务为目标
        print("\n🎯 阶段 2: 转换任务为目标")
        transformed_task = self.goal_driven.transform_task(task)
        print(f"转换后的任务: {transformed_task}")

        # 3. 执行编码
        print("\n💻 阶段 3: 执行编码")
        code = await self._write_code(transformed_task)

        # 4. 检查复杂度
        print("\n📊 阶段 4: 检查复杂度")
        metric = self.simplicity.check_complexity(code)
        print(f"代码行数: {metric.lines_of_code}")
        print(f"圈复杂度: {metric.cyclomatic_complexity}")

        # 5. 验证变更
        print("\n✅ 阶段 5: 验证变更")
        self.surgical.set_request(task)
        # ... 添加变更
        if not self.surgical.verify_changes():
            print("❌ 变更验证失败")
            return {"status": "failed"}

        # 6. 循环直到验证
        print("\n🔄 阶段 6: 循环直到验证")
        if not self.goal_driven.loop_until_verified():
            print("❌ 验证失败")
            return {"status": "failed"}

        print("\n✅ 任务完成")
        return {
            "status": "success",
            "code": code,
            "summary": self._get_summary(),
        }

    def _think_before_coding(self, task: str):
        """编码前思考"""
        # 明确假设
        self.thinker.state_assumption(
            description=f"任务 '{task}' 的理解",
            certainty=0.7,
        )

        # 呈现解释
        interpretations = [
            "添加新功能",
            "修复现有 bug",
            "重构代码",
            "优化性能",
        ]
        self.thinker.present_interpretations(task, interpretations)

        # 获取总结
        summary = self.thinker.get_summary()
        print(f"假设数量: {len(summary['assumptions'])}")
        print(f"需要澄清: {len(summary['clarifications'])}")

    async def _write_code(self, task: str) -> str:
        """编写代码"""
        # 实际实现...
        return "# 生成的代码"

    def _get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        return {
            "think_before_coding": self.thinker.get_summary(),
            "simplicity_first": self.simplicity.get_summary(),
            "surgical_changes": self.surgical.get_summary(),
            "goal_driven_execution": self.goal_driven.get_summary(),
        }
```

### 4.3 使用示例

```python
# 示例：使用编码 Agent
from erbing_system.agents.coding_agent import CodingAgent

async def main():
    agent = CodingAgent()

    # 处理任务
    result = await agent.process_task("添加用户验证")

    if result["status"] == "success":
        print("✅ 任务成功完成")
        print(f"代码:\n{result['code']}")
        print(f"总结:\n{result['summary']}")
    else:
        print("❌ 任务失败")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 五、总结

### 5.1 整合成果

1. **Think Before Coding** - 明确假设、请求澄清、呈现解释
2. **Simplicity First** - 检查复杂度、建议简化、避免过度工程
3. **Surgical Changes** - 精准修改、匹配风格、移除孤儿
4. **Goal-Driven Execution** - 转换任务、定义标准、循环验证

### 5.2 核心价值

- **减少错误** - 通过明确假设和请求澄清
- **提高质量** - 通过简单优先和精准修改
- **增强可靠性** - 通过目标驱动和循环验证
- **改善体验** - 通过更少的返工和更清晰的沟通

### 5.3 下一步

1. 实现具体的验证逻辑
2. 集成到二饼的编码流程
3. 添加更多编码场景示例
4. 优化复杂度检查算法
5. 完善变更验证机制

---

**日期**: 2026-04-20
**作者**: Erbing
**状态**: Karpathy Guidelines 整合完成
