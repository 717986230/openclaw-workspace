# -*- coding: utf-8 -*-
"""
顶配基因进化系统 - Top-Tier Genetic Evolution System
实现遗传算法，优化进化策略，实现基因重组，优化突变机制
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class GeneType(Enum):
    """基因类型"""
    ADAPTATION = "adaptation"  # 适应
    EVOLUTION = "evolution"  # 进化
    SURVIVAL = "survival"  # 生存
    REPRODUCTION = "reproduction"  # 繁殖
    LEARNING = "learning"  # 学习
    CREATIVITY = "creativity"  # 创造
    INTELLIGENCE = "intelligence"  # 智慧
    SOCIAL = "social"  # 社交


@dataclass
class Gene:
    """基因"""
    id: str
    type: GeneType
    value: float
    mutation_rate: float = 0.01
    min_value: float = 0.0
    max_value: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Chromosome:
    """染色体"""
    id: str
    genes: Dict[GeneType, Gene]
    fitness: float = 0.5
    generation: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Population:
    """种群"""
    id: str
    chromosomes: List[Chromosome]
    generation: int = 0
    size: int = 100
    timestamp: datetime = field(default_factory=datetime.now)


class TopTierGeneticEvolutionSystem:
    """顶配基因进化系统"""

    def __init__(self, population_size: int = 100, max_generations: int = 10000):
        self.population_size = population_size
        self.max_generations = max_generations

        # 种群
        self.population: Optional[Population] = None

        # 进化历史
        self.evolution_history: List[Dict] = []

        # 遗传算法参数
        self.crossover_rate = 0.8
        self.mutation_rate = 0.01
        self.elitism_rate = 0.1

        # 选择策略
        self.selection_strategy = "tournament"

        # 进化统计
        self.evolution_stats: Dict[str, float] = {
            'total_generations': 0,
            'avg_fitness': 0.0,
            'max_fitness': 0.0,
            'min_fitness': 0.0,
        }

        # 初始化种群
        self._initialize_population()

        logger.info(f"Top-Tier Genetic Evolution System initialized with {population_size} population size")

    def _initialize_population(self):
        """初始化种群"""
        # 创建初始种群
        chromosomes = []

        for i in range(self.population_size):
            # 创建染色体
            chromosome = self._create_chromosome(i)
            chromosomes.append(chromosome)

        # 创建种群
        self.population = Population(
            id=f"population-0",
            chromosomes=chromosomes,
            generation=0,
            size=self.population_size
        )

    def _create_chromosome(self, index: int) -> Chromosome:
        """创建染色体"""
        # 创建基因
        genes = {}

        for gene_type in GeneType:
            gene = Gene(
                id=f"gene-{index}-{gene_type.value}",
                type=gene_type,
                value=np.random.uniform(0.3, 0.7),
                mutation_rate=0.01,
                min_value=0.0,
                max_value=1.0
            )
            genes[gene_type] = gene

        # 计算适应度
        fitness = self._calculate_fitness(genes)

        # 创建染色体
        chromosome = Chromosome(
            id=f"chromosome-{index}",
            genes=genes,
            fitness=fitness,
            generation=0
        )

        return chromosome

    def _calculate_fitness(self, genes: Dict[GeneType, Gene]) -> float:
        """计算适应度"""
        # 简单的适应度计算
        fitness = np.mean([gene.value for gene in genes.values()])

        return fitness

    def select_parents(self) -> Tuple[Chromosome, Chromosome]:
        """选择父代"""
        if self.selection_strategy == "tournament":
            # 锦标赛选择
            parent1 = self._tournament_selection()
            parent2 = self._tournament_selection()
        elif self.selection_strategy == "roulette":
            # 轮盘赌选择
            parent1 = self._roulette_selection()
            parent2 = self._roulette_selection()
        else:
            # 随机选择
            parent1 = np.random.choice(self.population.chromosomes)
            parent2 = np.random.choice(self.population.chromosomes)

        return parent1, parent2

    def _tournament_selection(self) -> Chromosome:
        """锦标赛选择"""
        # 随机选择几个个体
        tournament_size = 5
        candidates = np.random.choice(self.population.chromosomes, tournament_size)

        # 选择适应度最高的
        winner = max(candidates, key=lambda c: c.fitness)

        return winner

    def _roulette_selection(self) -> Chromosome:
        """轮盘赌选择"""
        # 计算总适应度
        total_fitness = sum(c.fitness for c in self.population.chromosomes)

        # 生成随机数
        random_value = np.random.uniform(0, total_fitness)

        # 轮盘赌选择
        cumulative = 0
        for chromosome in self.population.chromosomes:
            cumulative += chromosome.fitness
            if cumulative >= random_value:
                return chromosome

        # 如果没有选中，返回最后一个
        return self.population.chromosomes[-1]

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> Chromosome:
        """交叉"""
        # 创建子代基因
        child_genes = {}

        for gene_type in GeneType:
            # 随机选择父代
            if np.random.random() < 0.5:
                child_genes[gene_type] = Gene(
                    id=f"gene-{len(self.population.chromosomes)}-{gene_type.value}",
                    type=gene_type,
                    value=parent1.genes[gene_type].value,
                    mutation_rate=parent1.genes[gene_type].mutation_rate,
                    min_value=parent1.genes[gene_type].min_value,
                    max_value=parent1.genes[gene_type].max_value
                )
            else:
                child_genes[gene_type] = Gene(
                    id=f"gene-{len(self.population.chromosomes)}-{gene_type.value}",
                    type=gene_type,
                    value=parent2.genes[gene_type].value,
                    mutation_rate=parent2.genes[gene_type].mutation_rate,
                    min_value=parent2.genes[gene_type].min_value,
                    max_value=parent2.genes[gene_type].max_value
                )

        # 计算适应度
        fitness = self._calculate_fitness(child_genes)

        # 创建子代染色体
        child_chromosome = Chromosome(
            id=f"chromosome-{len(self.population.chromosomes)}",
            genes=child_genes,
            fitness=fitness,
            generation=self.population.generation + 1
        )

        return child_chromosome

    def mutate(self, chromosome: Chromosome) -> Chromosome:
        """突变"""
        # 突变基因
        for gene_type, gene in chromosome.genes.items():
            if np.random.random() < gene.mutation_rate:
                # 突变
                gene.value = np.random.uniform(gene.min_value, gene.max_value)

        # 重新计算适应度
        chromosome.fitness = self._calculate_fitness(chromosome.genes)

        return chromosome

    def evolve(self) -> Dict:
        """进化"""
        # 记录进化前状态
        before_stats = self._get_population_stats()

        # 创建新一代
        new_chromosomes = []

        # 精英保留
        elite_count = int(self.population_size * self.elitism_rate)
        elite_chromosomes = sorted(self.population.chromosomes, key=lambda c: c.fitness, reverse=True)[:elite_count]
        new_chromosomes.extend(elite_chromosomes)

        # 生成新个体
        while len(new_chromosomes) < self.population_size:
            # 选择父代
            parent1, parent2 = self.select_parents()

            # 交叉
            if np.random.random() < self.crossover_rate:
                child = self.crossover(parent1, parent2)
            else:
                child = parent1

            # 突变
            child = self.mutate(child)

            new_chromosomes.append(child)

        # 更新种群
        self.population.chromosomes = new_chromosomes
        self.population.generation += 1

        # 记录进化历史
        after_stats = self._get_population_stats()
        evolution_record = {
            'generation': self.population.generation,
            'before_stats': before_stats,
            'after_stats': after_stats,
            'improvement': after_stats['avg_fitness'] - before_stats['avg_fitness'],
            'timestamp': datetime.now()
        }
        self.evolution_history.append(evolution_record)

        # 更新统计
        self.evolution_stats['total_generations'] += 1
        self.evolution_stats['avg_fitness'] = after_stats['avg_fitness']
        self.evolution_stats['max_fitness'] = after_stats['max_fitness']
        self.evolution_stats['min_fitness'] = after_stats['min_fitness']

        logger.info(f"Evolved to generation {self.population.generation}, avg fitness: {after_stats['avg_fitness']:.3f}")

        return evolution_record

    def _get_population_stats(self) -> Dict:
        """获取种群统计"""
        fitnesses = [c.fitness for c in self.population.chromosomes]

        return {
            'avg_fitness': np.mean(fitnesses),
            'max_fitness': np.max(fitnesses),
            'min_fitness': np.min(fitnesses),
            'std_fitness': np.std(fitnesses),
        }

    def get_best_chromosome(self) -> Chromosome:
        """获取最佳染色体"""
        return max(self.population.chromosomes, key=lambda c: c.fitness)

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'population_size': self.population_size,
            'current_generation': self.population.generation,
            'max_generations': self.max_generations,
            'evolution_history_length': len(self.evolution_history),
            'crossover_rate': self.crossover_rate,
            'mutation_rate': self.mutation_rate,
            'elitism_rate': self.elitism_rate,
            'selection_strategy': self.selection_strategy,
            'avg_fitness': self.evolution_stats['avg_fitness'],
            'max_fitness': self.evolution_stats['max_fitness'],
            'min_fitness': self.evolution_stats['min_fitness'],
        }


if __name__ == "__main__":
    # 测试顶配基因进化系统
    print("Testing Top-Tier Genetic Evolution System...")

    # 创建顶配基因进化系统
    genetic_system = TopTierGeneticEvolutionSystem(population_size=100, max_generations=10000)

    print(f"\nGenetic Evolution System Statistics:")
    stats = genetic_system.get_statistics()
    print(f"  Population Size: {stats['population_size']}")
    print(f"  Current Generation: {stats['current_generation']}")
    print(f"  Max Generations: {stats['max_generations']}")
    print(f"  Crossover Rate: {stats['crossover_rate']:.2f}")
    print(f"  Mutation Rate: {stats['mutation_rate']:.3f}")
    print(f"  Elitism Rate: {stats['elitism_rate']:.2f}")
    print(f"  Selection Strategy: {stats['selection_strategy']}")
    print(f"  Avg Fitness: {stats['avg_fitness']:.3f}")
    print(f"  Max Fitness: {stats['max_fitness']:.3f}")
    print(f"  Min Fitness: {stats['min_fitness']:.3f}")

    # 测试进化
    print(f"\nTesting Evolve...")
    for i in range(10):
        evolution_record = genetic_system.evolve()
        print(f"  Generation {i+1}: Avg Fitness: {evolution_record['after_stats']['avg_fitness']:.3f}, Improvement: {evolution_record['improvement']:+.4f}")

    # 测试获取最佳染色体
    print(f"\nTesting Get Best Chromosome...")
    best_chromosome = genetic_system.get_best_chromosome()
    print(f"  Best Chromosome ID: {best_chromosome.id}")
    print(f"  Fitness: {best_chromosome.fitness:.3f}")
    print(f"  Generation: {best_chromosome.generation}")
    print(f"  Genes:")
    for gene_type, gene in best_chromosome.genes.items():
        print(f"    {gene_type.value}: {gene.value:.3f}")

    # 测试获取统计
    print(f"\nTesting Get Statistics...")
    stats = genetic_system.get_statistics()
    print(f"  Current Generation: {stats['current_generation']}")
    print(f"  Avg Fitness: {stats['avg_fitness']:.3f}")
    print(f"  Max Fitness: {stats['max_fitness']:.3f}")
    print(f"  Min Fitness: {stats['min_fitness']:.3f}")

    print("\nTop-Tier Genetic Evolution System tested successfully!")