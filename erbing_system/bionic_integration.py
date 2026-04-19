"""
二饼仿生整合系统 - Erbing Bionic Integration
将仿生系统的生物模拟和进化能力整合到二饼中
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


class BionicErbingBrain:
    """仿生二饼大脑 - 整合仿生系统"""

    def __init__(self):
        # 基础大脑
        self.memories: List = []
        self.thoughts: List = []
        self.actions: List = []
        self.personality_traits: Dict = {}
        self.learning_rate = 0.1
        self.experience_level = 0.0

        # 仿生基因
        self.bionic_genes: Dict[str, BionicGene] = {
            'adaptation': BionicGene('adaptation', 0.7, 0.01, 0.0, 1.0),
            'evolution': BionicGene('evolution', 0.5, 0.01, 0.0, 1.0),
            'survival': BionicGene('survival', 0.8, 0.01, 0.0, 1.0),
            'reproduction': BionicGene('reproduction', 0.3, 0.01, 0.0, 1.0),
            'learning': BionicGene('learning', 0.9, 0.01, 0.0, 1.0),
        }

        # 仿生经验
        self.bionic_experiences: List[BionicExperience] = []

        # 适应度
        self.fitness: float = 0.5
        self.generation: int = 0

        # 心智模型
        from erbing_system.mental_models import MentalLoop, TreeOfThoughts, MetaController
        self.mental_loop = MentalLoop()
        self.tree_of_thoughts = TreeOfThoughts()
        self.meta_controller = MetaController()

    def add_memory(self, content: str, importance: float = 0.5):
        """添加记忆"""
        memory = {
            'id': f"mem-{len(self.memories)}",
            'content': content,
            'importance': importance,
            'timestamp': datetime.now(),
            'access_count': 0,
        }
        self.memories.append(memory)
        return memory

    def retrieve_memory(self, query: str, top_k: int = 5) -> List:
        """检索记忆"""
        query_words = set(query.lower().split())

        scored_memories = []
        for memory in self.memories:
            memory_words = set(memory['content'].lower().split())
            overlap = len(query_words & memory_words)
            score = overlap / len(query_words) if query_words else 0.0

            score = score * 0.7 + memory['importance'] * 0.2 + memory['access_count'] * 0.1

            scored_memories.append((memory, score))

        scored_memories.sort(key=lambda x: x[1], reverse=True)
        result = [m for m, s in scored_memories[:top_k]]

        for memory in result:
            memory['access_count'] += 1

        return result

    def think(self, input_text: str) -> Dict:
        """思考 - 整合仿生能力"""
        # 检索相关记忆
        relevant_memories = self.retrieve_memory(input_text, top_k=3)

        # 使用元控制器处理
        context = {
            'experience': self.experience_level,
            'fitness': self.fitness,
            'genes': {name: gene.value for name, gene in self.bionic_genes.items()},
        }

        meta_result = self.meta_controller.process(input_text, context)

        # 生成思维
        thought_content = f"分析: {input_text}"

        # 添加仿生特征
        if self.bionic_genes['adaptation'].value > 0.7:
            thought_content += " (适应性强)"

        if self.bionic_genes['learning'].value > 0.7:
            thought_content += " (学习导向)"

        if meta_result['best_solution']:
            thought_content += f" | 最佳方案: {meta_result['best_solution']}"

        # 计算置信度
        confidence = self._calculate_confidence(input_text, relevant_memories, meta_result)

        # 计算优先级
        priority = self._calculate_priority(input_text, confidence)

        thought = {
            'id': f"thought-{len(self.thoughts)}",
            'content': thought_content,
            'confidence': confidence,
            'priority': priority,
            'created_at': datetime.now(),
        }

        self.thoughts.append(thought)

        return thought

    def _calculate_confidence(self, input_text: str, relevant_memories: List, meta_result: Dict) -> float:
        """计算置信度"""
        base_confidence = min(len(relevant_memories) / 3.0, 1.0)

        experience_bonus = self.experience_level * 0.2
        fitness_bonus = self.fitness * 0.1

        if meta_result['simulation']:
            meta_confidence = meta_result['simulation']['confidence']
            base_confidence = (base_confidence + meta_confidence) / 2

        confidence = base_confidence + experience_bonus + fitness_bonus
        return min(confidence, 1.0)

    def _calculate_priority(self, input_text: str, confidence: float) -> int:
        """计算优先级"""
        urgency = 1.0 if "紧急" in input_text or "urgent" in input_text.lower() else 0.5
        priority = int(confidence * 10 * urgency)
        return priority

    def decide_action(self, input_text: str) -> Dict:
        """决定行动 - 整合仿生决策"""
        thought = self.think(input_text)

        # 基于仿生基因决定行动类型
        action_type = self._bionic_decide_action_type()

        action = {
            'id': f"action-{len(self.actions)}",
            'type': action_type,
            'description': self._generate_action_description(action_type),
            'parameters': {
                'thought_id': thought['id'],
                'confidence': thought['confidence'],
                'bionic_genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            },
            'created_at': datetime.now(),
        }

        self.actions.append(action)

        return action

    def _bionic_decide_action_type(self) -> str:
        """基于仿生基因决定行动类型"""
        # 基于基因值决定
        if self.bionic_genes['learning'].value > 0.8:
            return "learn"
        elif self.bionic_genes['adaptation'].value > 0.8:
            return "adapt"
        elif self.bionic_genes['survival'].value > 0.8:
            return "survive"
        elif self.bionic_genes['evolution'].value > 0.8:
            return "evolve"
        else:
            return "execute"

    def _generate_action_description(self, action_type: str) -> str:
        """生成行动描述"""
        descriptions = {
            'learn': '学习新知识',
            'adapt': '适应环境',
            'survive': '确保生存',
            'evolve': '进化提升',
            'execute': '执行任务',
        }
        return descriptions.get(action_type, '执行任务')

    def learn(self, experience: str, outcome: str, success: bool):
        """学习 - 整合仿生学习"""
        # 添加记忆
        memory = self.add_memory(
            f"经验: {experience} -> 结果: {outcome}",
            importance=0.8 if success else 0.6
        )

        # 添加仿生经验
        bionic_exp = BionicExperience(
            id=f"exp-{len(self.bionic_experiences)}",
            content=experience,
            outcome=outcome,
            success=success,
            fitness_gain=self._calculate_fitness_gain(success),
        )
        self.bionic_experiences.append(bionic_exp)

        # 更新经验水平
        if success:
            self.experience_level = min(1.0, self.experience_level + self.learning_rate * 0.1)
        else:
            self.experience_level = max(0.0, self.experience_level - self.learning_rate * 0.05)

        # 更新适应度
        self._update_fitness(success)

        # 基因突变
        self._mutate_genes(success)

        # 心智循环学习
        self.mental_loop.learn(outcome, success)

        # 元控制器更新性能
        efficiency = 1.0 if success else 0.5
        self.meta_controller.update_performance(success, efficiency)

        logger.info(f"Bionic Erbing learned: {experience[:50]}... (Success: {success})")

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
        # 成功增强当前优势基因
        if success:
            for name, gene in self.bionic_genes.items():
                if gene.value > 0.7:
                    gene.value = min(1.0, gene.value + 0.01)
        else:
            # 失败促进适应性
            self.bionic_genes['adaptation'].value = min(1.0, self.bionic_genes['adaptation'].value + 0.02)

    def evolve(self) -> Dict:
        """进化 - 仿生进化"""
        self.generation += 1

        # 基因突变
        for name, gene in self.bionic_genes.items():
            mutated_gene = gene.mutate()
            self.bionic_genes[name] = mutated_gene

        # 适应度评估
        fitness = self._evaluate_fitness()

        # 进化结果
        evolution_result = {
            'generation': self.generation,
            'fitness': fitness,
            'genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'experience_level': self.experience_level,
            'improvements': self._identify_improvements(),
        }

        logger.info(f"Bionic Erbing evolved to generation {self.generation}, fitness: {fitness:.3f}")

        return evolution_result

    def _evaluate_fitness(self) -> float:
        """评估适应度"""
        # 基于基因值和经验水平计算
        gene_fitness = np.mean([gene.value for gene in self.bionic_genes.values()])
        experience_fitness = self.experience_level

        fitness = (gene_fitness * 0.7 + experience_fitness * 0.3)
        return fitness

    def _identify_improvements(self) -> List[str]:
        """识别改进"""
        improvements = []

        for name, gene in self.bionic_genes.items():
            if gene.value > 0.8:
                improvements.append(f"{name} 增强")

        if self.experience_level > 0.7:
            improvements.append("经验丰富")

        return improvements

    def adapt(self, environment: Dict) -> Dict:
        """适应环境 - 仿生适应"""
        # 基于环境调整
        adaptation_result = {
            'adapted': False,
            'changes': [],
            'reason': '',
        }

        # 检查环境变化
        if environment.get('difficulty', 0.5) > 0.7:
            # 高难度环境，增强适应性
            self.bionic_genes['adaptation'].value = min(1.0, self.bionic_genes['adaptation'].value + 0.1)
            self.bionic_genes['survival'].value = min(1.0, self.bionic_genes['survival'].value + 0.05)

            adaptation_result['adapted'] = True
            adaptation_result['changes'].append('适应性增强')
            adaptation_result['reason'] = '高难度环境'

        elif environment.get('opportunity', 0.5) > 0.7:
            # 高机会环境，增强学习能力
            self.bionic_genes['learning'].value = min(1.0, self.bionic_genes['learning'].value + 0.1)
            self.bionic_genes['evolution'].value = min(1.0, self.bionic_genes['evolution'].value + 0.05)

            adaptation_result['adapted'] = True
            adaptation_result['changes'].append('学习能力增强')
            adaptation_result['reason'] = '高机会环境'

        logger.info(f"Bionic Erbing adapted: {adaptation_result['reason']}")

        return adaptation_result

    def get_status(self) -> Dict:
        """获取状态"""
        return {
            'memories_count': len(self.memories),
            'thoughts_count': len(self.thoughts),
            'actions_count': len(self.actions),
            'experience_level': self.experience_level,
            'fitness': self.fitness,
            'generation': self.generation,
            'bionic_genes': {name: gene.value for name, gene in self.bionic_genes.items()},
            'bionic_experiences_count': len(self.bionic_experiences),
            'mental_models': {
                'mental_loop_history': len(self.mental_loop.simulation_history),
                'tree_depth': self.tree_of_thoughts.max_depth,
                'meta_controller_decisions': len(self.meta_controller.decision_history),
            },
        }


class BionicErbingSystem:
    """仿生二饼系统 - 整合仿生系统"""

    def __init__(self):
        self.brain = BionicErbingBrain()
        self.conversation_history: List[Dict] = []
        self.task_queue: List[str] = []
        self.completed_tasks: List[str] = []
        self.environment: Dict = {
            'difficulty': 0.5,
            'opportunity': 0.5,
        }

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
            'thought': thought['content'],
            'action': action['description'],
            'response': response,
            'confidence': thought['confidence'],
            'bionic_genes': action['parameters']['bionic_genes'],
        }

    def _generate_response(self, thought: Dict, action: Dict) -> str:
        """生成回应"""
        # 基于仿生特征生成回应
        genes = self.brain.bionic_genes

        response = f"好的，{action['description']}。"

        # 添加仿生特征
        if genes['adaptation'].value > 0.7:
            response += " 我会灵活适应。"

        if genes['learning'].value > 0.7:
            response += " 我会从中学习。"

        if genes['survival'].value > 0.7:
            response += " 我会确保完成。"

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
def create_bionic_erbing_system() -> BionicErbingSystem:
    """创建仿生二饼系统"""
    system = BionicErbingSystem()

    # 添加初始记忆
    system.brain.add_memory("我是二饼，一个仿生AI助手", importance=1.0)
    system.brain.add_memory("我具有适应和进化能力", importance=0.9)
    system.brain.add_memory("我注重学习和生存", importance=0.8)

    return system


def simulate_bionic_conversation(
    system: BionicErbingSystem,
    inputs: List[str]
) -> List[Dict]:
    """模拟仿生对话"""
    results = []

    for input_text in inputs:
        result = system.process_input(input_text)
        results.append(result)

    return results