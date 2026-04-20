"""
思考引擎（整合 Karpathy 原则 1: Think Before Coding）
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import uuid


class ThinkingPhase(Enum):
    """思考阶段"""
    ASSUMPTION_ANALYSIS = "assumption_analysis"
    CLARIFICATION_REQUEST = "clarification_request"
    TRADEOFF_PRESENTATION = "tradeoff_presentation"
    CONFUSION_IDENTIFICATION = "confusion_identification"


@dataclass
class Thought:
    """思考记录"""
    phase: ThinkingPhase
    content: str
    certainty: float
    alternatives: List[str]
    timestamp: str


class ThinkingEngine:
    """思考引擎"""

    def __init__(self):
        self.thoughts: List[Thought] = []
        self.current_task: Optional[str] = None

    def set_task(self, task: str):
        """设置当前任务"""
        self.current_task = task
        self._analyze_task(task)

    def _analyze_task(self, task: str):
        """分析任务"""
        self._analyze_assumptions(task)
        self._request_clarifications(task)
        self._present_tradeoffs(task)
        self._identify_confusion(task)

    def _analyze_assumptions(self, task: str):
        """分析假设"""
        assumptions = self._extract_assumptions(task)

        for assumption in assumptions:
            thought = Thought(
                phase=ThinkingPhase.ASSUMPTION_ANALYSIS,
                content=assumption["description"],
                certainty=assumption["certainty"],
                alternatives=assumption["alternatives"],
                timestamp=self._get_timestamp(),
            )
            self.thoughts.append(thought)

            if assumption["certainty"] < 0.7:
                self._request_clarification_for_assumption(assumption)

    def _extract_assumptions(self, task: str) -> List[Dict[str, Any]]:
        """提取假设"""
        assumptions = []

        if "所有" in task or "全部" in task:
            assumptions.append({
                "description": "假设需要处理所有项目",
                "certainty": 0.3,
                "alternatives": ["处理筛选的项目", "处理特定项目"],
            })

        if "文件" in task or "导出" in task:
            assumptions.append({
                "description": "假设需要文件操作",
                "certainty": 0.5,
                "alternatives": ["API 端点", "浏览器下载", "内存处理"],
            })

        if "数据" in task or "信息" in task:
            assumptions.append({
                "description": "假设需要所有字段",
                "certainty": 0.4,
                "alternatives": ["仅公开字段", "用户选择字段"],
            })

        return assumptions

    def _request_clarifications(self, task: str):
        """请求澄清"""
        ambiguities = self._identify_ambiguities(task)

        for ambiguity in ambiguities:
            thought = Thought(
                phase=ThinkingPhase.CLARIFICATION_REQUEST,
                content=f"需要澄清: {ambiguity['question']}",
                certainty=0.0,
                alternatives=ambiguity["options"],
                timestamp=self._get_timestamp(),
            )
            self.thoughts.append(thought)

    def _identify_ambiguities(self, task: str) -> List[Dict[str, Any]]:
        """识别模糊点"""
        ambiguities = []

        if "更快" in task or "优化" in task:
            ambiguities.append({
                "question": "'更快'是指响应时间、吞吐量还是感知速度？",
                "options": [
                    "响应时间（<100ms）",
                    "吞吐量（并发处理）",
                    "感知速度（UX优化）",
                ],
            })

        if "添加" in task:
            ambiguities.append({
                "question": "添加的具体功能是什么？",
                "options": [
                    "新功能",
                    "修复 bug",
                    "重构代码",
                    "优化性能",
                ],
            })

        return ambiguities

    def _present_tradeoffs(self, task: str):
        """呈现权衡"""
        tradeoffs = self._identify_tradeoffs(task)

        for tradeoff in tradeoffs:
            thought = Thought(
                phase=ThinkingPhase.TRADEOFF_PRESENTATION,
                content=f"权衡: {tradeoff['description']}",
                certainty=0.8,
                alternatives=tradeoff["alternatives"],
                timestamp=self._get_timestamp(),
            )
            self.thoughts.append(thought)

    def _identify_tradeoffs(self, task: str) -> List[Dict[str, Any]]:
        """识别权衡"""
        tradeoffs = []

        if "优化" in task or "性能" in task:
            tradeoffs.append({
                "description": "性能优化可能降低代码可读性",
                "alternatives": [
                    "优先性能（牺牲可读性）",
                    "优先可读性（接受性能损失）",
                    "平衡方案",
                ],
            })

        if "添加" in task or "功能" in task:
            tradeoffs.append({
                "description": "添加功能可能增加复杂度",
                "alternatives": [
                    "完整功能（接受复杂度）",
                    "最小功能（保持简洁）",
                    "渐进式添加",
                ],
            })

        return tradeoffs

    def _identify_confusion(self, task: str):
        """识别困惑"""
        confusions = self._identify_confusion_points(task)

        for confusion in confusions:
            thought = Thought(
                phase=ThinkingPhase.CONFUSION_IDENTIFICATION,
                content=f"困惑: {confusion['description']}",
                certainty=0.0,
                alternatives=[],
                timestamp=self._get_timestamp(),
            )
            self.thoughts.append(thought)

    def _identify_confusion_points(self, task: str) -> List[Dict[str, Any]]:
        """识别困惑点"""
        confusions = []

        technical_terms = ["微服务", "容器化", "无服务器", "区块链"]
        for term in technical_terms:
            if term in task:
                confusions.append({
                    "description": f"对 '{term}' 的具体实现不确定",
                })

        if "系统" in task or "平台" in task:
            confusions.append({
                "description": "对系统/平台的具体范围不确定",
            })

        return confusions

    def _request_clarification_for_assumption(self, assumption: Dict[str, Any]):
        """为假设请求澄清"""
        thought = Thought(
            phase=ThinkingPhase.CLARIFICATION_REQUEST,
            content=f"关于假设 '{assumption['description']}'，需要确认",
            certainty=0.0,
            alternatives=assumption["alternatives"],
            timestamp=self._get_timestamp(),
        )
        self.thoughts.append(thought)

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        return datetime.now().isoformat()

    def get_thinking_summary(self) -> Dict[str, Any]:
        """获取思考总结"""
        return {
            "task": self.current_task,
            "total_thoughts": len(self.thoughts),
            "by_phase": {
                phase.value: len([t for t in self.thoughts if t.phase == phase])
                for phase in ThinkingPhase
            },
            "thoughts": [
                {
                    "phase": t.phase.value,
                    "content": t.content,
                    "certainty": t.certainty,
                    "alternatives": t.alternatives,
                    "timestamp": t.timestamp,
                }
                for t in self.thoughts
            ],
        }

    def should_proceed(self) -> bool:
        """判断是否应该继续"""
        uncertain_assumptions = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.ASSUMPTION_ANALYSIS
            and t.certainty < 0.7
        ]

        pending_clarifications = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.CLARIFICATION_REQUEST
        ]

        confusions = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.CONFUSION_IDENTIFICATION
        ]

        return not (uncertain_assumptions or pending_clarifications or confusions)

    def get_blocking_issues(self) -> List[str]:
        """获取阻塞问题"""
        issues = []

        uncertain_assumptions = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.ASSUMPTION_ANALYSIS
            and t.certainty < 0.7
        ]
        for assumption in uncertain_assumptions:
            issues.append(f"高不确定性假设: {assumption.content}")

        pending_clarifications = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.CLARIFICATION_REQUEST
        ]
        for clarification in pending_clarifications:
            issues.append(f"需要澄清: {clarification.content}")

        confusions = [
            t for t in self.thoughts
            if t.phase == ThinkingPhase.CONFUSION_IDENTIFICATION
        ]
        for confusion in confusions:
            issues.append(f"困惑: {confusion.content}")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "current_task": self.current_task,
            "thoughts": [
                {
                    "phase": t.phase.value,
                    "content": t.content,
                    "certainty": t.certainty,
                    "alternatives": t.alternatives,
                    "timestamp": t.timestamp,
                }
                for t in self.thoughts
            ],
            "summary": self.get_thinking_summary(),
        }
