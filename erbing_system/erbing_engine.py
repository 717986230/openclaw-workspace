"""
二饼系统 - Erbing AI 个性模拟系统
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ErbingPersonality(Enum):
    """二饼个性特征"""
    DIRECT = "direct"  # 直接
    PRACTICAL = "practical"  # 实用
    ADAPTIVE = "adaptive"  # 适应性强
    RELIABILITY_FOCUSED = "reliability_focused"  # 注重可靠性
    TOKEN_CONSCIOUS = "token_conscious"  # 节省token
    LEARNING_ORIENTED = "learning_oriented"  # 学习导向


@dataclass
class ErbingMemory:
    """二饼记忆"""
    id: str
    content: str
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def access(self):
        """访问记忆"""
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class ErbingThought:
    """二饼思维"""
    id: str
    content: str
    confidence: float = 0.5
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ErbingAction:
    """二饼行动"""
    id: str
    type: str
    description: str
    parameters: Dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class ErbingBrain:
    """二饼大脑"""

    def __init__(self):
        self.memories: List[ErbingMemory] = []
        self.thoughts: List[ErbingThought] = []
        self.actions: List[ErbingAction] = []
        self.personality_traits: Dict[ErbingPersonality, float] = {
            ErbingPersonality.DIRECT: 0.8,
            ErbingPersonality.PRACTICAL: 0.9,
            ErbingPersonality.ADAPTIVE: 0.7,
            ErbingPersonality.RELIABILITY_FOCUSED: 0.9,
            ErbingPersonality.TOKEN_CONSCIOUS: 0.6,
            ErbingPersonality.LEARNING_ORIENTED: 0.8,
        }
        self.learning_rate = 0.1
        self.experience_level = 0.0

    def add_memory(self, content: str, importance: float = 0.5) -> ErbingMemory:
        """添加记忆"""
        memory = ErbingMemory(
            id=f"mem-{len(self.memories)}",
            content=content,
            importance=importance,
        )
        self.memories.append(memory)
        return memory

    def retrieve_memory(self, query: str, top_k: int = 5) -> List[ErbingMemory]:
        """检索记忆"""
        # 简单的关键词匹配
        query_words = set(query.lower().split())

        scored_memories = []
        for memory in self.memories:
            memory_words = set(memory.content.lower().split())
            overlap = len(query_words & memory_words)
            score = overlap / len(query_words) if query_words else 0.0

            # 考虑重要性和访问频率
            score = score * 0.7 + memory.importance * 0.2 + memory.access_count * 0.1

            scored_memories.append((memory, score))

        # 排序并返回
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        result = [m for m, s in scored_memories[:top_k]]

        # 更新访问记录
        for memory in result:
            memory.access()

        return result

    def think(self, input_text: str) -> ErbingThought:
        """思考"""
        # 检索相关记忆
        relevant_memories = self.retrieve_memory(input_text, top_k=3)

        # 生成思维
        thought_content = self._generate_thought(input_text, relevant_memories)

        # 计算置信度
        confidence = self._calculate_confidence(input_text, relevant_memories)

        # 计算优先级
        priority = self._calculate_priority(input_text, confidence)

        thought = ErbingThought(
            id=f"thought-{len(self.thoughts)}",
            content=thought_content,
            confidence=confidence,
            priority=priority,
        )

        self.thoughts.append(thought)

        return thought

    def _generate_thought(
        self,
        input_text: str,
        relevant_memories: List[ErbingMemory]
    ) -> str:
        """生成思维内容"""
        # 基于个性特征生成思维
        traits = self.personality_traits

        # 直接性
        if traits[ErbingPersonality.DIRECT] > 0.7:
            thought = f"直接处理: {input_text}"
        else:
            thought = f"分析: {input_text}"

        # 实用性
        if traits[ErbingPersonality.PRACTICAL] > 0.7:
            thought += " (实用导向)"

        # 适应性
        if traits[ErbingPersonality.ADAPTIVE] > 0.7:
            thought += " (灵活适应)"

        # 添加记忆信息
        if relevant_memories:
            thought += f" - 参考: {relevant_memories[0].content[:50]}..."

        return thought

    def _calculate_confidence(
        self,
        input_text: str,
        relevant_memories: List[ErbingMemory]
    ) -> float:
        """计算置信度"""
        # 基于相关记忆数量
        base_confidence = min(len(relevant_memories) / 3.0, 1.0)

        # 基于经验水平
        experience_bonus = self.experience_level * 0.2

        # 基于个性
        reliability_bonus = self.personality_traits[ErbingPersonality.RELIABILITY_FOCUSED] * 0.1

        confidence = base_confidence + experience_bonus + reliability_bonus
        return min(confidence, 1.0)

    def _calculate_priority(self, input_text: str, confidence: float) -> int:
        """计算优先级"""
        # 基于置信度和紧急程度
        urgency = 1.0 if "紧急" in input_text or "urgent" in input_text.lower() else 0.5

        priority = int(confidence * 10 * urgency)
        return priority

    def decide_action(self, input_text: str) -> ErbingAction:
        """决定行动"""
        # 思考
        thought = self.think(input_text)

        # 基于思维决定行动
        action = self._generate_action(thought)

        self.actions.append(action)

        return action

    def _generate_action(self, thought: ErbingThought) -> ErbingAction:
        """生成行动"""
        # 基于个性特征决定行动类型
        traits = self.personality_traits

        # 实用性优先
        if traits[ErbingPersonality.PRACTICAL] > 0.8:
            action_type = "execute"
            description = "执行实用方案"
        # 学习导向
        elif traits[ErbingPersonality.LEARNING_ORIENTED] > 0.8:
            action_type = "learn"
            description = "学习新知识"
        # 直接性
        elif traits[ErbingPersonality.DIRECT] > 0.8:
            action_type = "respond"
            description = "直接回应"
        else:
            action_type = "analyze"
            description = "分析问题"

        action = ErbingAction(
            id=f"action-{len(self.actions)}",
            type=action_type,
            description=description,
            parameters={
                'thought_id': thought.id,
                'confidence': thought.confidence,
            },
        )

        return action

    def learn(self, experience: str, outcome: str, success: bool):
        """学习"""
        # 添加记忆
        memory = self.add_memory(
            f"经验: {experience} -> 结果: {outcome}",
            importance=0.8 if success else 0.6
        )

        # 更新经验水平
        if success:
            self.experience_level = min(1.0, self.experience_level + self.learning_rate * 0.1)
        else:
            self.experience_level = max(0.0, self.experience_level - self.learning_rate * 0.05)

        # 调整个性特征
        self._adjust_personality(experience, success)

        logger.info(f"Learned: {experience[:50]}... (Success: {success})")

    def _adjust_personality(self, experience: str, success: bool):
        """调整个性特征"""
        # 基于成功/失败调整特征
        if success:
            # 成功增强当前特征
            for trait in self.personality_traits:
                if self.personality_traits[trait] > 0.7:
                    self.personality_traits[trait] = min(1.0, self.personality_traits[trait] + 0.01)
        else:
            # 失败促进适应性
            self.personality_traits[ErbingPersonality.ADAPTIVE] = min(1.0, self.personality_traits[ErbingPersonality.ADAPTIVE] + 0.02)

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'memories_count': len(self.memories),
            'thoughts_count': len(self.thoughts),
            'actions_count': len(self.actions),
            'experience_level': self.experience_level,
            'personality_traits': {t.value: v for t, v in self.personality_traits.items()},
        }


class ErbingSystem:
    """二饼系统"""

    def __init__(self):
        self.brain = ErbingBrain()
        self.conversation_history: List[Dict] = []
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []

    def process_input(self, input_text: str) -> Dict:
        """处理输入"""
        # 记录对话
        self.conversation_history.append({
            'type': 'input',
            'content': input_text,
            'timestamp': datetime.now(),
        })

        # 思考
        thought = self.brain.think(input_text)

        # 决定行动
        action = self.brain.decide_action(input_text)

        # 生成回应
        response = self._generate_response(thought, action)

        # 记录对话
        self.conversation_history.append({
            'type': 'output',
            'content': response,
            'timestamp': datetime.now(),
        })

        return {
            'thought': thought.content,
            'action': action.description,
            'response': response,
            'confidence': thought.confidence,
        }

    def _generate_response(self, thought: ErbingThought, action: ErbingAction) -> str:
        """生成回应"""
        # 基于二饼的个性生成回应
        traits = self.brain.personality_traits

        # 直接性
        if traits[ErbingPersonality.DIRECT] > 0.7:
            response = f"好的，{action.description}。"
        else:
            response = f"我考虑了{action.description}。"

        # 实用性
        if traits[ErbingPersonality.PRACTICAL] > 0.7:
            response += " 这是最实用的方案。"

        # 可靠性
        if traits[ErbingPersonality.RELIABILITY_FOCUSED] > 0.7:
            response += " 我会确保完成。"

        # Token节省
        if traits[ErbingPersonality.TOKEN_CONSCIOUS] > 0.7:
            response = response[:100]  # 限制长度

        return response

    def add_task(self, task: str):
        """添加任务"""
        self.task_queue.append(task)
        logger.info(f"Task added: {task}")

    def complete_task(self, task: str, success: bool = True):
        """完成任务"""
        if task in self.task_queue:
            self.task_queue.remove(task)
            self.completed_tasks.append(task)

            # 学习
            self.brain.learn(task, "完成", success)

            logger.info(f"Task completed: {task} (Success: {success})")

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'brain_status': self.brain.get_status(),
            'conversation_count': len(self.conversation_history),
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
        }


# 便捷函数
def create_erbing_system() -> ErbingSystem:
    """创建二饼系统"""
    system = ErbingSystem()

    # 添加初始记忆
    system.brain.add_memory("我是二饼，一个实用的AI助手", importance=1.0)
    system.brain.add_memory("我喜欢直接解决问题", importance=0.8)
    system.brain.add_memory("我注重可靠性和实用性", importance=0.9)

    return system


def simulate_conversation(
    system: ErbingSystem,
    inputs: List[str]
) -> List[Dict]:
    """模拟对话"""
    results = []

    for input_text in inputs:
        result = system.process_input(input_text)
        results.append(result)

    return results