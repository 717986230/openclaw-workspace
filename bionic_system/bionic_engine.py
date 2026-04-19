"""
仿生系统 - 生物模拟与进化引擎
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import logging

logger = logging.getLogger(__name__)


class OrganismType(Enum):
    """生物类型"""
    PLANT = "plant"
    HERBIVORE = "herbivore"
    CARNIVORE = "carnivore"
    OMNIVORE = "omnivore"


@dataclass
class Gene:
    """基因"""
    name: str
    value: float
    mutation_rate: float = 0.01
    min_value: float = 0.0
    max_value: float = 1.0

    def mutate(self) -> 'Gene':
        """突变"""
        if random.random() < self.mutation_rate:
            new_value = self.value + random.gauss(0, 0.1)
            new_value = max(self.min_value, min(self.max_value, new_value))
            return Gene(
                name=self.name,
                value=new_value,
                mutation_rate=self.mutation_rate,
                min_value=self.min_value,
                max_value=self.max_value
            )
        return self


@dataclass
class Organism:
    """生物个体"""
    id: str
    species: str
    organism_type: OrganismType
    genes: Dict[str, Gene] = field(default_factory=dict)
    energy: float = 100.0
    age: int = 0
    max_age: int = 100
    alive: bool = True
    fitness: float = 0.0

    def __post_init__(self):
        """初始化基因"""
        if not self.genes:
            self.genes = {
                'speed': Gene('speed', 0.5, 0.01, 0.0, 1.0),
                'strength': Gene('strength', 0.5, 0.01, 0.0, 1.0),
                'intelligence': Gene('intelligence', 0.5, 0.01, 0.0, 1.0),
                'size': Gene('size', 0.5, 0.01, 0.0, 1.0),
                'reproduction_rate': Gene('reproduction_rate', 0.5, 0.01, 0.0, 1.0),
            }

    def act(self, environment: 'Environment') -> str:
        """行动"""
        if not self.alive:
            return 'dead'

        # 消耗能量
        energy_cost = 0.1 * (1 + self.genes['size'].value)
        self.energy -= energy_cost

        # 检查死亡
        if self.energy <= 0 or self.age >= self.max_age:
            self.alive = False
            return 'dead'

        # 年龄增长
        self.age += 1

        # 根据类型行动
        if self.organism_type == OrganismType.PLANT:
            return self._act_plant(environment)
        elif self.organism_type == OrganismType.HERBIVORE:
            return self._act_herbivore(environment)
        elif self.organism_type == OrganismType.CARNIVORE:
            return self._act_carnivore(environment)
        else:
            return self._act_omnivore(environment)

    def _act_plant(self, environment: 'Environment') -> str:
        """植物行动"""
        # 光合作用
        sunlight = environment.get_resource('sunlight')
        energy_gain = sunlight * self.genes['size'].value * 0.5
        self.energy += energy_gain

        # 生长
        if self.energy > 150:
            self.genes['size'].value = min(1.0, self.genes['size'].value + 0.01)

        return 'photosynthesis'

    def _act_herbivore(self, environment: 'Environment') -> str:
        """食草动物行动"""
        # 寻找食物
        food = environment.find_food(self.organism_type)
        if food:
            energy_gain = food * self.genes['strength'].value * 0.3
            self.energy += energy_gain
            return 'eat'

        # 移动
        movement_cost = 0.05 * self.genes['speed'].value
        self.energy -= movement_cost
        return 'move'

    def _act_carnivore(self, environment: 'Environment') -> str:
        """食肉动物行动"""
        # 狩猎
        prey = environment.find_prey(self)
        if prey:
            energy_gain = prey.energy * self.genes['strength'].value * 0.5
            self.energy += energy_gain
            prey.alive = False
            return 'hunt'

        # 移动
        movement_cost = 0.05 * self.genes['speed'].value
        self.energy -= movement_cost
        return 'move'

    def _act_omnivore(self, environment: 'Environment') -> str:
        """杂食动物行动"""
        # 随机选择
        if random.random() < 0.5:
            return self._act_herbivore(environment)
        else:
            return self._act_carnivore(environment)

    def reproduce(self) -> Optional['Organism']:
        """繁殖"""
        if not self.alive:
            return None

        # 检查繁殖条件
        if self.energy < 50 or self.age < 10:
            return None

        # 繁殖概率
        reproduction_prob = self.genes['reproduction_rate'].value * 0.1
        if random.random() > reproduction_prob:
            return None

        # 创建后代
        child_genes = {}
        for name, gene in self.genes.items():
            child_genes[name] = gene.mutate()

        child = Organism(
            id=f"{self.id}-{random.randint(1000, 9999)}",
            species=self.species,
            organism_type=self.organism_type,
            genes=child_genes,
            energy=50.0,
        )

        # 消耗能量
        self.energy -= 30.0

        return child

    def calculate_fitness(self) -> float:
        """计算适应度"""
        if not self.alive:
            return 0.0

        # 基于年龄和能量
        fitness = (self.age / self.max_age) * 0.5 + (self.energy / 200.0) * 0.5
        self.fitness = fitness
        return fitness


class Environment:
    """环境"""

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height
        self.organisms: List[Organism] = []
        self.resources: Dict[str, float] = {
            'sunlight': 1.0,
            'water': 1.0,
            'plants': 0.5,
        }
        self.time_step = 0

    def add_organism(self, organism: Organism):
        """添加生物"""
        self.organisms.append(organism)

    def get_resource(self, resource_name: str) -> float:
        """获取资源"""
        return self.resources.get(resource_name, 0.0)

    def find_food(self, organism_type: OrganismType) -> float:
        """寻找食物"""
        if organism_type == OrganismType.HERBIVORE:
            return self.resources['plants']
        elif organism_type == OrganismType.CARNIVORE:
            return 0.0  # 需要找到猎物
        else:
            return self.resources['plants'] * 0.5

    def find_prey(self, predator: Organism) -> Optional[Organism]:
        """寻找猎物"""
        for organism in self.organisms:
            if organism.id == predator.id:
                continue
            if not organism.alive:
                continue

            # 食肉动物捕食食草动物
            if predator.organism_type == OrganismType.CARNIVORE:
                if organism.organism_type == OrganismType.HERBIVORE:
                    # 捕食成功率
                    success_rate = predator.genes['strength'].value * 0.8
                    if random.random() < success_rate:
                        return organism

        return None

    def update(self):
        """更新环境"""
        self.time_step += 1

        # 更新资源
        self.resources['sunlight'] = 0.5 + 0.5 * np.sin(self.time_step * 0.1)
        self.resources['water'] = 0.5 + 0.5 * np.cos(self.time_step * 0.1)
        self.resources['plants'] = min(1.0, self.resources['plants'] + 0.01)

        # 更新生物
        new_organisms = []
        for organism in self.organisms:
            action = organism.act(self)

            # 繁殖
            child = organism.reproduce()
            if child:
                new_organisms.append(child)

        # 添加新生物
        self.organisms.extend(new_organisms)

        # 移除死亡生物
        self.organisms = [o for o in self.organisms if o.alive]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        alive_organisms = [o for o in self.organisms if o.alive]

        type_counts = {}
        for organism in alive_organisms:
            org_type = organism.organism_type.value
            type_counts[org_type] = type_counts.get(org_type, 0) + 1

        avg_fitness = np.mean([o.calculate_fitness() for o in alive_organisms]) if alive_organisms else 0.0

        return {
            'time_step': self.time_step,
            'total_organisms': len(alive_organisms),
            'type_counts': type_counts,
            'avg_fitness': avg_fitness,
            'resources': self.resources.copy(),
        }


class EvolutionEngine:
    """进化引擎"""

    def __init__(self, environment: Environment):
        self.environment = environment
        self.generation = 0
        self.history: List[Dict] = []

    def run(self, max_generations: int = 100, steps_per_generation: int = 100):
        """运行进化"""
        logger.info(f"Starting evolution for {max_generations} generations")

        for gen in range(max_generations):
            self.generation = gen

            # 运行一代
            for _ in range(steps_per_generation):
                self.environment.update()

            # 记录统计
            stats = self.environment.get_statistics()
            stats['generation'] = gen
            self.history.append(stats)

            # 输出进度
            if gen % 10 == 0:
                logger.info(
                    f"Generation {gen}: "
                    f"Organisms={stats['total_organisms']}, "
                    f"AvgFitness={stats['avg_fitness']:.3f}"
                )

            # 检查灭绝
            if stats['total_organisms'] == 0:
                logger.warning("All organisms extinct!")
                break

        logger.info("Evolution completed")

    def get_history(self) -> pd.DataFrame:
        """获取历史记录"""
        return pd.DataFrame(self.history)

    def analyze_evolution(self) -> Dict:
        """分析进化"""
        df = self.get_history()

        if df.empty:
            return {}

        analysis = {
            'total_generations': len(df),
            'final_population': df['total_organisms'].iloc[-1],
            'max_population': df['total_organisms'].max(),
            'avg_fitness_trend': df['avg_fitness'].mean(),
            'dominant_species': df['type_counts'].apply(lambda x: max(x.values()) if x else 0).max(),
        }

        return analysis


def create_initial_population(
    environment: Environment,
    population_size: int = 50
) -> List[Organism]:
    """创建初始种群"""
    organisms = []

    for i in range(population_size):
        # 随机选择类型
        org_type = random.choice(list(OrganismType))

        organism = Organism(
            id=f"org-{i}",
            species=f"species-{random.randint(1, 10)}",
            organism_type=org_type,
        )

        environment.add_organism(organism)

    return organisms


# 便捷函数
def run_simulation(
    generations: int = 100,
    population_size: int = 50,
    steps_per_generation: int = 100
) -> Tuple[EvolutionEngine, pd.DataFrame]:
    """运行模拟"""
    # 创建环境
    environment = Environment(width=100, height=100)

    # 创建初始种群
    create_initial_population(environment, population_size)

    # 创建进化引擎
    engine = EvolutionEngine(environment)

    # 运行进化
    engine.run(generations, steps_per_generation)

    # 获取历史
    history = engine.get_history()

    return engine, history