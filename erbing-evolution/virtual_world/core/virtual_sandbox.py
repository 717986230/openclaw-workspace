# 虚拟世界沙盒核心
# 基于钱学森系统理论构建的隔离式进化环境

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue


class TimeScale(Enum):
    """时间压缩比例"""
    NORMAL = 1  # 1:1
    FAST = 60  # 1分钟 = 1小时
    ULTRA = 1440  # 1分钟 = 1天
    EXTREME = 43200  # 1分钟 = 30天


@dataclass
class VirtualTimestamp:
    """虚拟时间戳"""
    real_time: datetime = field(default_factory=datetime.now)
    virtual_time: datetime = field(default_factory=datetime.now)
    time_scale: TimeScale = TimeScale.ULTRA

    def tick(self, real_seconds: float):
        """时间推进"""
        virtual_delta = timedelta(seconds=real_seconds * self.time_scale.value)
        self.virtual_time += virtual_delta
        self.real_time = datetime.now()


class VirtualSandbox:
    """虚拟沙盒世界"""

    def __init__(self, name: str = "Erbing_Virtual_World", time_scale: TimeScale = TimeScale.ULTRA):
        self.name = name
        self.created_at = datetime.now()
        self.timestamp = VirtualTimestamp(time_scale=time_scale)
        self.active = True

        # 子系统
        self.task_simulator = TaskSimulator()
        self.adversarial_arena = AdversarialArena()
        self.edge_case_generator = EdgeCaseGenerator()
        self.stress_test_pool = StressTestPool()
        self.knowledge_phylogeny = KnowledgePhylogeny()

        # 进化群体
        self.population = []
        self.max_population = 100

        # 学习队列
        self.learning_queue = queue.Queue()
        self.experience_buffer = []

        # 监控
        self.metrics = {}
        self.generation = 0

        print(f"虚拟沙盒 '{name}' 已创建")
        print(f"时间压缩比例: 1分钟 = {time_scale.value}分钟虚拟时间")

    def create_erbing_instance(self, config: Dict[str, Any]) -> 'VirtualErbing':
        """创建二饼实例"""
        if len(self.population) >= self.max_population:
            # 淘汰最弱的实例
            self.eliminate_weakest()

        instance = VirtualErbing(
            sandbox=self,
            config=config,
            generation=self.generation
        )

        self.population.append(instance)
        return instance

    def eliminate_weakest(self):
        """淘汰最弱的实例"""
        if not self.population:
            return

        # 按适应度排序
        self.population.sort(key=lambda x: x.fitness, reverse=True)

        # 淘汰后10%
        to_eliminate = int(len(self.population) * 0.1)
        eliminated = self.population[-to_eliminate:]
        self.population = self.population[:-to_eliminate]

        for instance in eliminated:
            instance.archive_experience()
            print(f"实例 {instance.id} 被淘汰，适应度: {instance.fitness:.3f}")

    def run_evolution_cycle(self, duration_virtual_minutes: int = 1440):
        """运行进化周期"""
        print(f"开始进化周期 #{self.generation}")
        print(f"目标时长: {duration_virtual_minutes} 分钟虚拟时间")

        start_virtual = self.timestamp.virtual_time

        # 为每个实例分配任务
        tasks = self.generate_tasks(len(self.population))

        for i, instance in enumerate(self.population):
            task = tasks[i % len(tasks)]
            instance.assign_task(task)

        # 并行执行
        threads = []
        for instance in self.population:
            t = threading.Thread(target=instance.execute_task)
            threads.append(t)
            t.start()

        # 等待完成
        for t in threads:
            t.join(timeout=60)  # 最多等待60秒真实时间

        # 评估结果
        self.evaluate_generation()

        # 选择最优实例
        self.select_elites()

        # 繁殖新一代
        self.reproduce()

        # 更新代际
        self.generation += 1

        # 推进时间
        elapsed_virtual = duration_virtual_minutes
        self.timestamp.tick(elapsed_virtual / self.timestamp.time_scale.value)

        print(f"进化周期完成")
        print(f"真实耗时: 约60秒")
        print(f"虚拟时间推进: {elapsed_virtual} 分钟")
        print(f"最佳适应度: {max(p.fitness for p in self.population):.3f}")

    def generate_tasks(self, count: int) -> List[Dict[str, Any]]:
        """生成任务集"""
        tasks = []

        task_types = [
            "reasoning",
            "creativity",
            "optimization",
            "adaptation",
            "collaboration"
        ]

        difficulties = ["easy", "medium", "hard", "extreme"]

        for i in range(count):
            task = {
                "id": f"task_{self.generation}_{i}",
                "type": random.choice(task_types),
                "difficulty": random.choice(difficulties),
                "constraints": self.generate_constraints(),
                "evaluation_criteria": self.generate_criteria(),
                "time_budget": random.randint(10, 100)
            }
            tasks.append(task)

        return tasks

    def generate_constraints(self) -> Dict[str, Any]:
        """生成约束条件"""
        return {
            "accuracy_min": random.uniform(0.8, 0.99),
            "time_limit": random.randint(1, 10),
            "resource_limit": random.randint(100, 1000),
            "complexity": random.choice(["low", "medium", "high"])
        }

    def generate_criteria(self) -> Dict[str, float]:
        """生成评估标准"""
        return {
            "accuracy_weight": random.uniform(0.2, 0.4),
            "efficiency_weight": random.uniform(0.2, 0.3),
            "creativity_weight": random.uniform(0.1, 0.3),
            "robustness_weight": random.uniform(0.1, 0.2)
        }

    def evaluate_generation(self):
        """评估代际"""
        total_fitness = 0
        best_fitness = 0

        for instance in self.population:
            fitness = instance.calculate_fitness()
            total_fitness += fitness
            if fitness > best_fitness:
                best_fitness = fitness

        avg_fitness = total_fitness / len(self.population) if self.population else 0

        self.metrics[self.generation] = {
            "avg_fitness": avg_fitness,
            "best_fitness": best_fitness,
            "population_size": len(self.population),
            "timestamp": self.timestamp.virtual_time.isoformat()
        }

    def select_elites(self, elite_ratio: float = 0.2):
        """选择精英"""
        if not self.population:
            return []

        # 排序
        self.population.sort(key=lambda x: x.fitness, reverse=True)

        # 选择前20%
        elite_count = int(len(self.population) * elite_ratio)
        elites = self.population[:elite_count]

        # 保存精英经验
        for elite in elites:
            self.knowledge_phylogeny.add_elite(elite)

        return elites

    def reproduce(self, mutation_rate: float = 0.1):
        """繁殖"""
        elites = self.select_elites()

        if len(elites) < 2:
            return

        # 生成新实例
        needed = self.max_population - len(self.population)

        for i in range(needed):
            parent1, parent2 = random.sample(elites, 2)

            # 交叉
            child_config = self.crossover(parent1.config, parent2.config)

            # 变异
            if random.random() < mutation_rate:
                child_config = self.mutate(child_config)

            # 创建新实例
            child = self.create_erbing_instance(child_config)
            child.parents = [parent1.id, parent2.id]

    def crossover(self, config1: Dict, config2: Dict) -> Dict:
        """交叉"""
        child = {}
        for key in config1:
            if random.random() < 0.5:
                child[key] = config1[key]
            else:
                child[key] = config2.get(key, config1[key])
        return child

    def mutate(self, config