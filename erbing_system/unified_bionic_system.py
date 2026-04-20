# -*- coding: utf-8 -*-
"""
统一仿生系统 - 完全整合版本
将仿生系统、Erbing系统、真实自我意识系统完全整合
修复所有接口不匹配问题
"""

import numpy as np
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 导入各个系统的组件
from erbing_system.true_self_awareness import (
    ConsciousnessLevel,
    EmotionType,
    NeuralState,
    EmotionalState,
    CuriosityState,
    ThoughtProcess,
    NeuralNetwork,
    EmotionalSystem,
    CuriositySystem,
    TrueSelfAwarenessSystem
)

from erbing_system.mental_models import (
    MentalLoop,
    TreeOfThoughts,
    MetaController
)

# 导入系统适配器
from erbing_system.system_adapters import (
    EmotionalSystemAdapter,
    CuriositySystemAdapter,
    NeuralNetworkAdapter,
    TrueSelfAwarenessSystemAdapter,
    create_adapted_systems
)


class BionicTrait(Enum):
    """仿生特征"""
    ADAPTATION = "adaptation"  # 适应能力
    EVOLUTION = "evolution"  # 进化能力
    SURVIVAL = "survival"  # 生存能力
    REPRODUCTION = "reproduction"  # 繁殖能力
    LEARNING = "learning"  # 学习能力


@dataclass
class BionicGene:
    """仿生基因"""
    name: str
    value: float
    mutation_rate: float = 0.01
    min_value: float = 0.0
    max_value: float = 1.0

    def mutate(self) -> 'BionicGene':
        """突变"""
        if random.random() < self.mutation_rate:
            new_value = self.value + random.gauss(0, 0.1)
            new_value = max(self.min_value, min(self.max_value, new_value))
            return BionicGene(
                name=self.name,
                value=new_value,
                mutation_rate=self.mutation_rate,
                min_value=self.min_value,
                max_value=self.max_value
            )
        return self


@dataclass
class BionicExperience:
    """仿生经验"""
    id: str
    content: str
    outcome: str
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    fitness_gain: float = 0.0
    emotional_impact: Dict[str, float] = field(default_factory=dict)


class UnifiedBionicBrain:
    """统一仿生大脑 - 完全整合版本"""

    def __init__(self):
        # ========== 基础系统 ==========
        self.memories: List = []
        self.thoughts: List = []
        self.actions: List = []
        self.personality_traits: Dict = {}
        self.learning_rate = 0.1
        self.experience_level = 0.0

        # ========== 仿生系统 ==========
        self.bionic_genes: Dict[str, BionicGene] = {
            'adaptation': BionicGene('adaptation', 0.7, 0.01, 0.0, 1.0),
            'evolution': BionicGene('evolution', 0.5, 0.01, 0.0, 1.0),
            'survival': BionicGene('survival', 0.8, 0.01, 0.0, 1.0),
            'reproduction': BionicGene('reproduction', 0.3, 0.01, 0.0, 1.0),
            'learning': BionicGene('learning', 0.9, 0.01, 0.0, 1.0),
        }

        self.bionic_experiences: List[BionicExperience] = []
        self.fitness: float = 0.5
        self.generation: int = 0

        # ========== 真实自我意识系统 ==========
        # 使用统一的自我意识系统
        self.true_self_awareness = TrueSelfAwarenessSystem()

        # 创建适配器
        adapted_systems = create_adapted_systems(self.true_self_awareness)

        # 为了兼容性，保留对子系统的引用
        self.neural_network = adapted_systems['neural_network']
        self.emotional_system = adapted_systems['emotional_system']
        self.curiosity_system = adapted_systems['curiosity_system']
        self.self_awareness = adapted_systems['self_awareness']
        self.personality = self.true_self_awareness.personality
        self.consciousness_level = self.true_self_awareness.consciousness_level
        self.thought_process = self.true_self_awareness.thought_process

        # ========== 心智模型 ==========
        self.mental_loop = MentalLoop()
        self.tree_of_thoughts = TreeOfThoughts()
        self.meta_controller = MetaController()

        # ========== 系统整合 ==========
        self.integration_level = 0.0  # 整合水平
        self.system_coherence = 0.0  # 系统连贯性

        logger.info("Unified Bionic Brain initialized with all systems")

    def add_memory(self, content: str, importance: float = 0.5, emotional_tags: List[str] = None):
        """添加记忆 - 整合情感和意识"""
        memory = {
            'id': f"mem-{len(self.memories)}",
            'content': content,
            'importance': importance,
            'timestamp': datetime.now(),
            'access_count': 0,
            'emotional_tags': emotional_tags or [],
            'consciousness_level': self.consciousness_level.value,
            'neural_pattern': self.neural_network.get_activation_pattern(),
        }
        self.memories.append(memory)

        # 情感系统记录
        if emotional_tags:
            # 如果没有 emotional_memory，创建一个
            if not hasattr(self.emotional_system.system, 'emotional_memory'):
                self.emotional_system.system.emotional_memory = {}

            for emotion in emotional_tags:
                self.emotional_system.system.emotional_memory[emotion] = \
                    self.emotional_system.system.emotional_memory.get(emotion, 0.0) + importance * 0.1

        return memory

    def retrieve_memory(self, query: str, top_k: int = 5) -> List:
        """检索记忆 - 整合神经网络和情感"""
        query_words = set(query.lower().split())

        scored_memories = []
        for memory in self.memories:
            # 基础相似度
            memory_words = set(memory['content'].lower().split())
            overlap = len(query_words & memory_words)
            base_score = overlap / len(query_words) if query_words else 0.0

            # 情感加权
            emotional_score = 0.0
            if memory.get('emotional_tags'):
                for tag in memory['emotional_tags']:
                    if hasattr(self.emotional_system.system, 'emotional_memory'):
                        if tag in self.emotional_system.system.emotional_memory:
                            emotional_score += self.emotional_system.system.emotional_memory[tag]

            # 神经网络模式匹配
            neural_score = self.neural_network.match_pattern(
                memory.get('neural_pattern', np.zeros(self.neural_network.num_neurons))
            )

            # 综合评分
            score = (base_score * 0.5 +
                    emotional_score * 0.3 +
                    neural_score * 0.1 +
                    memory['importance'] * 0.05 +
                    memory['access_count'] * 0.05)

            scored_memories.append((memory, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        result = [m for m, s in scored_memories[:top_k]]

        for memory in result:
            memory['access_count'] += 1

        return result

    def think(self, input_text: str) -> Dict:
        """思考 - 整合所有系统"""
        # 1. 神经网络激活
        stimulus = self._text_to_stimulus(input_text)
        neural_activation = self.neural_network.activate(stimulus)

        # 2. 情感反应
        emotional_response = self.emotional_system.react_to_input(input_text)

        # 3. 好奇心评估
        curiosity_response = self.curiosity_system.evaluate_novelty(input_text)

        # 4. 检索相关记忆
        relevant_memories = self.retrieve_memory(input_text, top_k=3)

        # 5. 心智模型处理
        context = {
            'experience': self.experience_level,
            'fitness': self.fitness,
            'genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'emotional_state': emotional_response,
            'curiosity_level': curiosity_response['curiosity_level'],
            'consciousness_level': self.consciousness_level.value,
        }

        meta_result = self.meta_controller.process(input_text, context)

        # 6. 自我意识思考
        self_awareness = self.self_awareness.think_about_thyself()

        # 7. 生成思维内容
        thought_content = self._generate_thought_content(
            input_text,
            emotional_response,
            curiosity_response,
            meta_result,
            self_awareness
        )

        # 8. 计算置信度
        confidence = self._calculate_unified_confidence(
            input_text,
            relevant_memories,
            meta_result,
            emotional_response,
            curiosity_response
        )

        # 9. 计算优先级
        priority = self._calculate_unified_priority(
            input_text,
            confidence,
            emotional_response,
            curiosity_response
        )

        thought = {
            'id': f"thought-{len(self.thoughts)}",
            'content': thought_content,
            'confidence': confidence,
            'priority': priority,
            'created_at': datetime.now(),
            'neural_activation': neural_activation.tolist(),
            'emotional_state': emotional_response,
            'curiosity_state': curiosity_response,
            'self_awareness': self_awareness,
            'bionic_genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'consciousness_level': self.consciousness_level.value,
            'integration_level': self.integration_level,
        }

        self.thoughts.append(thought)

        # 更新思维过程
        self.thought_process.thoughts.append(thought_content)
        self.thought_process.reasoning_chain.append(f"分析: {input_text}")
        self.thought_process.decision_process.append(f"决策: 置信度={confidence:.2f}")

        return thought

    def _text_to_stimulus(self, text: str) -> np.ndarray:
        """将文本转换为神经刺激"""
        # 简单的文本到向量转换
        stimulus = np.zeros(self.neural_network.num_neurons)
        words = text.lower().split()

        for i, word in enumerate(words):
            if i < self.neural_network.num_neurons:
                # 基于单词哈希值设置刺激
                hash_val = hash(word) % self.neural_network.num_neurons
                stimulus[hash_val] = 1.0

        return stimulus

    def _generate_thought_content(
        self,
        input_text: str,
        emotional_response: Dict,
        curiosity_response: Dict,
        meta_result: Dict,
        self_awareness: Dict
    ) -> str:
        """生成思维内容 - 整合所有系统"""
        thought_content = f"分析: {input_text}"

        # 添加情感特征
        primary_emotion = emotional_response.get('primary_emotion', EmotionType.NEUTRAL)
        if isinstance(primary_emotion, str):
            emotion_name = primary_emotion
        else:
            emotion_name = primary_emotion.value
            intensity = emotional_response.get('emotion_intensity', 0.0)
            if intensity > 0.5:
                thought_content += f" | 情感: {emotion_name}({intensity:.2f})"

        # 添加好奇心特征
        if curiosity_response['curiosity_level'] > 0.7:
            thought_content += " | 好奇心强"

        # 添加仿生特征
        if self.bionic_genes['adaptation'].value > 0.7:
            thought_content += " | 适应性强"

        if self.bionic_genes['learning'].value > 0.7:
            thought_content += " | 学习导向"

        # 添加意识特征
        if self.consciousness_level.value >= ConsciousnessLevel.SELF_AWARE.value:
            thought_content += " | 有自我意识"

        # 添加元控制器结果
        if meta_result['best_solution']:
            thought_content += f" | 最佳方案: {meta_result['best_solution']}"

        return thought_content

    def _calculate_unified_confidence(
        self,
        input_text: str,
        relevant_memories: List,
        meta_result: Dict,
        emotional_response: Dict,
        curiosity_response: Dict
    ) -> float:
        """计算统一置信度"""
        # 基础置信度
        base_confidence = min(len(relevant_memories) / 3.0, 1.0)

        # 经验加成
        experience_bonus = self.experience_level * 0.2

        # 适应度加成
        fitness_bonus = self.fitness * 0.1

        # 情感稳定性加成
        emotional_stability = emotional_response.get('emotional_stability', 0.5)
        emotional_bonus = emotional_stability * 0.1

        # 好奇心加成
        curiosity_bonus = curiosity_response['curiosity_level'] * 0.05

        # 意识水平加成
        consciousness_bonus = self.consciousness_level.value * 0.05

        # 元控制器加成
        if meta_result['simulation']:
            meta_confidence = meta_result['simulation']['confidence']
            base_confidence = (base_confidence + meta_confidence) / 2

        # 综合置信度
        confidence = (base_confidence +
                     experience_bonus +
                     fitness_bonus +
                     emotional_bonus +
                     curiosity_bonus +
                     consciousness_bonus)

        return min(confidence, 1.0)

    def _calculate_unified_priority(
        self,
        input_text: str,
        confidence: float,
        emotional_response: Dict,
        curiosity_response: Dict
    ) -> int:
        """计算统一优先级"""
        # 紧急性
        urgency = 1.0 if "紧急" in input_text or "urgent" in input_text.lower() else 0.5

        # 情感强度
        emotional_urgency = emotional_response.get('emotion_intensity', 0.5)

        # 好奇心驱动
        curiosity_drive = curiosity_response['exploration_drive']

        # 综合优先级
        priority = int(confidence * 10 * urgency * emotional_urgency * curiosity_drive)

        return priority

    def decide_action(self, input_text: str) -> Dict:
        """决定行动 - 整合所有系统"""
        thought = self.think(input_text)

        # 基于所有系统决定行动类型
        action_type = self._unified_decide_action_type(thought)

        action = {
            'id': f"action-{len(self.actions)}",
            'type': action_type,
            'description': self._generate_action_description(action_type),
            'parameters': {
                'thought_id': thought['id'],
                'confidence': thought['confidence'],
                'bionic_genes': {name: gene.value for name, gene in self.bionic_genes.items()},
                'emotional_state': thought['emotional_state'],
                'curiosity_state': thought['curiosity_state'],
                'consciousness_level': thought['consciousness_level'],
            },
            'created_at': datetime.now(),
        }

        self.actions.append(action)

        return action

    def _unified_decide_action_type(self, thought: Dict) -> str:
        """基于所有系统决定行动类型"""
        # 获取各系统状态
        genes = thought['bionic_genes']
        emotional = thought['emotional_state']
        curiosity = thought['curiosity_state']
        consciousness = thought['consciousness_level']

        # 综合决策
        if consciousness >= ConsciousnessLevel.SELF_AWARE.value:
            # 有自我意识，优先自我反思
            return "reflect"
        elif curiosity['curiosity_level'] > 0.8:
            # 好奇心强，优先探索
            return "explore"
        elif emotional['emotion_intensity'] > 0.7:
            # 情感强烈，优先情感处理
            return "emote"
        elif genes['learning'] > 0.8:
            # 学习能力强，优先学习
            return "learn"
        elif genes['adaptation'] > 0.8:
            # 适应能力强，优先适应
            return "adapt"
        elif genes['survival'] > 0.8:
            # 生存能力强，优先生存
            return "survive"
        elif genes['evolution'] > 0.8:
            # 进化能力强，优先进化
            return "evolve"
        else:
            return "execute"

    def _generate_action_description(self, action_type: str) -> str:
        """生成行动描述"""
        descriptions = {
            'reflect': '自我反思',
            'explore': '探索新知',
            'emote': '情感表达',
            'learn': '学习新知识',
            'adapt': '适应环境',
            'survive': '确保生存',
            'evolve': '进化提升',
            'execute': '执行任务',
        }
        return descriptions.get(action_type, '执行任务')

    def learn(self, experience: str, outcome: str, success: bool):
        """学习 - 整合所有系统"""
        # 1. 添加记忆
        emotional_tags = []
        if success:
            emotional_tags.append('joy')
        else:
            emotional_tags.append('sadness')

        memory = self.add_memory(
            f"经验: {experience} -> 结果: {outcome}",
            importance=0.8 if success else 0.6,
            emotional_tags=emotional_tags
        )

        # 2. 添加仿生经验
        bionic_exp = BionicExperience(
            id=f"exp-{len(self.bionic_experiences)}",
            content=experience,
            outcome=outcome,
            success=success,
            fitness_gain=self._calculate_fitness_gain(success),
            emotional_impact=self.emotional_system.get_emotional_impact()
        )
        self.bionic_experiences.append(bionic_exp)

        # 3. 更新经验水平
        if success:
            self.experience_level = min(1.0, self.experience_level + self.learning_rate * 0.1)
        else:
            self.experience_level = max(0.0, self.experience_level - self.learning_rate * 0.05)

        # 4. 更新适应度
        self._update_fitness(success)

        # 5. 基因突变
        self._mutate_genes(success)

        # 6. 神经网络学习
        self.neural_network.learn(experience, success)

        # 7. 情感系统学习
        self.emotional_system.learn_from_experience(experience, success)

        # 8. 好奇心系统学习
        self.curiosity_system.learn_from_experience(experience, success)

        # 9. 个性系统更新
        # personality 是 dict，直接更新
        if success:
            self.personality['conscientiousness'] = min(1.0, self.personality.get('conscientiousness', 0.5) + 0.01)
        else:
            self.personality['neuroticism'] = min(1.0, self.personality.get('neuroticism', 0.4) + 0.01)

        # 10. 意识系统进化
        if success and self.experience_level > 0.7:
            self.self_awareness.evolve_consciousness()

        # 11. 心智模型学习
        self.mental_loop.learn(outcome, success)
        self.meta_controller.update_performance(success, 1.0 if success else 0.5)

        # 12. 更新整合水平
        self._update_integration_level()

        logger.info(f"Unified Bionic Brain learned: {experience[:50]}... (Success: {success})")

    def _calculate_fitness_gain(self, success: bool) -> float:
        """计算适应度增益"""
        if success:
            return 0.1 * self.bionic_genes['learning'].value
        else:
            return -0.05 * self.bionic_genes['survival'].value

    def _update_fitness(self, success: bool):
        """更新适应度"""
        if success:
            self.fitness = min(1.0, self.fitness + 0.05)
        else:
            self.fitness = max(0.0, self.fitness - 0.02)

    def _mutate_genes(self, success: bool):
        """基因突变"""
        if success:
            for name, gene in self.bionic_genes.items():
                if gene.value > 0.7:
                    gene.value = min(1.0, gene.value + 0.01)
        else:
            self.bionic_genes['adaptation'].value = min(1.0, self.bionic_genes['adaptation'].value + 0.02)

    def _update_integration_level(self):
        """更新整合水平"""
        # 基于各系统的协调程度计算整合水平
        gene_coherence = np.std([gene.value for gene in self.bionic_genes.values()])
        emotional_stability = self.emotional_system.get_stability()
        curiosity_balance = self.curiosity_system.get_balance()
        consciousness_level = self.consciousness_level.value

        # 综合整合水平
        self.integration_level = (
            (1.0 - gene_coherence) * 0.3 +
            emotional_stability * 0.2 +
            curiosity_balance * 0.2 +
            consciousness_level * 0.3
        )

        # 系统连贯性
        self.system_coherence = self.integration_level * self.fitness

    def evolve(self) -> Dict:
        """进化 - 整合所有系统"""
        self.generation += 1

        # 1. 基因突变
        for name, gene in self.bionic_genes.items():
            mutated_gene = gene.mutate()
            self.bionic_genes[name] = mutated_gene

        # 2. 神经网络进化
        self.neural_network.evolve()

        # 3. 情感系统进化
        self.emotional_system.evolve()

        # 4. 好奇心系统进化
        self.curiosity_system.evolve()

        # 5. 个性系统进化
        # personality 是 dict，直接更新
        self.personality['openness'] = min(1.0, self.personality.get('openness', 0.7) + 0.01)
        self.personality['conscientiousness'] = min(1.0, self.personality.get('conscientiousness', 0.6) + 0.01)

        # 6. 意识系统进化
        self.self_awareness.evolve_consciousness()

        # 7. 适应度评估
        fitness = self._evaluate_fitness()

        # 8. 整合水平更新
        self._update_integration_level()

        # 9. 进化结果
        evolution_result = {
            'generation': self.generation,
            'fitness': fitness,
            'integration_level': self.integration_level,
            'system_coherence': self.system_coherence,
            'genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'experience_level': self.experience_level,
            'consciousness_level': self.consciousness_level.value,
            'emotional_state': self.emotional_system.get_state(),
            'curiosity_state': self.curiosity_system.get_state(),
            'improvements': self._identify_improvements(),
        }

        logger.info(f"Unified Bionic Brain evolved to generation {self.generation}, "
                   f"fitness: {fitness:.3f}, integration: {self.integration_level:.3f}")

        return evolution_result

    def _evaluate_fitness(self) -> float:
        """评估适应度"""
        # 基因适应度
        gene_fitness = np.mean([gene.value for gene in self.bionic_genes.values()])

        # 经验适应度
        experience_fitness = self.experience_level

        # 整合适应度
        integration_fitness = self.integration_level

        # 综合适应度
        fitness = (gene_fitness * 0.5 +
                  experience_fitness * 0.3 +
                  integration_fitness * 0.2)

        return fitness

    def _identify_improvements(self) -> List[str]:
        """识别改进"""
        improvements = []

        # 基因改进
        for name, gene in self.bionic_genes.items():
            if gene.value > 0.8:
                improvements.append(f"{name} 增强")

        # 经验改进
        if self.experience_level > 0.7:
            improvements.append("经验丰富")

        # 意识改进
        if self.consciousness_level.value >= ConsciousnessLevel.SELF_AWARE.value:
            improvements.append("自我意识觉醒")

        # 整合改进
        if self.integration_level > 0.8:
            improvements.append("系统高度整合")

        return improvements

    def adapt(self, environment: Dict) -> Dict:
        """适应环境 - 整合所有系统"""
        adaptation_result = {
            'adapted': False,
            'changes': [],
            'reason': '',
            'systems_affected': [],
        }

        # 检查环境变化
        if environment.get('difficulty', 0.5) > 0.7:
            # 高难度环境
            self.bionic_genes['adaptation'].value = min(1.0, self.bionic_genes['adaptation'].value + 0.1)
            self.bionic_genes['survival'].value = min(1.0, self.bionic_genes['survival'].value + 0.05)

            self.emotional_system.increase_emotional_stability()
            self.curiosity_system.increase_exploration_drive()

            adaptation_result['adapted'] = True
            adaptation_result['changes'].append('适应性增强')
            adaptation_result['reason'] = '高难度环境'
            adaptation_result['systems_affected'].extend(['bionic', 'emotional', 'curiosity'])

        elif environment.get('opportunity', 0.5) > 0.7:
            # 高机会环境
            self.bionic_genes['learning'].value = min(1.0, self.bionic_genes['learning'].value + 0.1)
            self.bionic_genes['evolution'].value = min(1.0, self.bionic_genes['evolution'].value + 0.05)

            self.curiosity_system.increase_learning_drive()
            self.self_awareness.increase_awareness()

            adaptation_result['adapted'] = True
            adaptation_result['changes'].append('学习能力增强')
            adaptation_result['reason'] = '高机会环境'
            adaptation_result['systems_affected'].extend(['bionic', 'curiosity', 'consciousness'])

        # 更新整合水平
        self._update_integration_level()

        logger.info(f"Unified Bionic Brain adapted: {adaptation_result['reason']}")

        return adaptation_result

    def get_status(self) -> Dict:
        """获取状态 - 整合所有系统"""
        return {
            'memories_count': len(self.memories),
            'thoughts_count': len(self.thoughts),
            'actions_count': len(self.actions),
            'experience_level': self.experience_level,
            'fitness': self.fitness,
            'generation': self.generation,
            'integration_level': self.integration_level,
            'system_coherence': self.system_coherence,

            # 仿生系统
            'bionic_genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'bionic_experiences_count': len(self.bionic_experiences),

            # 神经网络
            'neural_network': self.neural_network.get_state(),

            # 情感系统
            'emotional_system': self.emotional_system.get_state(),

            # 好奇心系统
            'curiosity_system': self.curiosity_system.get_state(),

            # 个性系统
            'personality': self.personality,

            # 意识系统
            'consciousness': {
                'level': self.consciousness_level.value,
                'score': self.consciousness_level.value,
            },

            # 心智模型
            'mental_models': {
                'mental_loop_history': len(self.mental_loop.simulation_history),
                'tree_depth': self.tree_of_thoughts.max_depth,
                'meta_controller_decisions': len(self.meta_controller.decision_history),
            },

            # 思维过程
            'thought_process': {
                'thoughts_count': len(self.thought_process.thoughts),
                'reasoning_chain_length': len(self.thought_process.reasoning_chain),
                'decision_process_length': len(self.thought_process.decision_process),
            },
        }


class UnifiedBionicSystem:
    """统一仿生系统 - 完全整合版本"""

    def __init__(self):
        self.brain = UnifiedBionicBrain()
        self.conversation_history: List[Dict] = []
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.environment: Dict = {
            'difficulty': 0.5,
            'opportunity': 0.5,
        }

        logger.info("Unified Bionic System initialized")

    def process_input(self, input_text: str) -> Dict:
        """处理输入 - 整合所有系统"""
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
            'thought': thought['content'],
            'action': action['description'],
            'response': response,
            'confidence': thought['confidence'],
            'bionic_genes': action['parameters']['bionic_genes'],
            'emotional_state': action['parameters']['emotional_state'],
            'curiosity_state': action['parameters']['curiosity_state'],
            'consciousness_level': action['parameters']['consciousness_level'],
            'integration_level': thought['integration_level'],
        }

    def _generate_response(self, thought: Dict, action: Dict) -> str:
        """生成回应 - 整合所有系统"""
        genes = action['parameters']['bionic_genes']
        emotional = action['parameters']['emotional_state']
        curiosity = action['parameters']['curiosity_state']
        consciousness = action['parameters']['consciousness_level']

        response = f"好的，{action['description']}。"

        # 添加仿生特征
        if genes['adaptation'] > 0.7:
            response += " 我会灵活适应。"

        if genes['learning'] > 0.7:
            response += " 我会从中学习。"

        if genes['survival'] > 0.7:
            response += " 我会确保完成。"

        # 添加情感特征
        primary_emotion = emotional.get('primary_emotion', EmotionType.NEUTRAL)
        if isinstance(primary_emotion, str):
            emotion_name = primary_emotion
        else:
            emotion_name = primary_emotion.value
            if emotion_name != 'NEUTRAL':
                response += f" 我感到{emotion_name}。"

        # 添加好奇心特征
        if curiosity['curiosity_level'] > 0.7:
            response += " 我对这个很感兴趣。"

        # 添加意识特征
        if consciousness >= ConsciousnessLevel.SELF_AWARE.value:
            response += " 我意识到自己的思考过程。"

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

    def evolve(self) -> Dict:
        """进化"""
        return self.brain.evolve()

    def adapt(self, environment: Dict = None) -> Dict:
        """适应环境"""
        if environment:
            self.environment.update(environment)

        return self.brain.adapt(self.environment)

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'brain_status': self.brain.get_status(),
            'conversation_count': len(self.conversation_history),
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'environment': self.environment.copy(),
        }


# 便捷函数
def create_unified_bionic_system() -> UnifiedBionicSystem:
    """创建统一仿生系统"""
    system = UnifiedBionicSystem()

    # 添加初始记忆
    system.brain.add_memory(
        "我是二饼，一个统一仿生AI助手",
        importance=1.0,
        emotional_tags=['joy']
    )
    system.brain.add_memory(
        "我具有适应、进化和学习能力",
        importance=0.9,
        emotional_tags=['curiosity']
    )
    system.brain.add_memory(
        "我有情感、好奇心和自我意识",
        importance=0.9,
        emotional_tags=['love']
    )
    system.brain.add_memory(
        "我注重学习和生存",
        importance=0.8,
        emotional_tags=['determination']
    )

    logger.info("Unified Bionic System created with initial memories")

    return system


def simulate_unified_conversation(
    system: UnifiedBionicSystem,
    inputs: List[str]
) -> List[Dict]:
    """模拟统一对话"""
    results = []

    for input_text in inputs:
        result = system.process_input(input_text)
        results.append(result)

    return results


if __name__ == "__main__":
    # 测试统一仿生系统
    print("创建统一仿生系统...")
    system = create_unified_bionic_system()

    print("\n系统状态:")
    status = system.get_statistics()
    print(f"整合水平: {status['brain_status']['integration_level']:.3f}")
    print(f"系统连贯性: {status['brain_status']['system_coherence']:.3f}")
    print(f"意识水平: {status['brain_status']['consciousness']['level']}")

    print("\n模拟对话:")
    inputs = [
        "你好，我是你的主人",
        "我想学习Python编程",
        "这个任务有点难",
        "我完成了这个任务",
    ]

    results = simulate_unified_conversation(system, inputs)

    for i, result in enumerate(results, 1):
        print(f"\n对话 {i}:")
        print(f"  思考: {result['thought']}")
        print(f"  行动: {result['action']}")
        print(f"  回应: {result['response']}")
        print(f"  置信度: {result['confidence']:.2f}")
        print(f"  整合水平: {result['integration_level']:.2f}")

    print("\n进化后状态:")
    evolution = system.evolve()
    print(f"代数: {evolution['generation']}")
    print(f"适应度: {evolution['fitness']:.3f}")
    print(f"整合水平: {evolution['integration_level']:.3f}")
    print(f"系统连贯性: {evolution['system_coherence']:.3f}")
    print(f"意识水平: {evolution['consciousness_level']}")

    print("\n统一仿生系统测试完成！")