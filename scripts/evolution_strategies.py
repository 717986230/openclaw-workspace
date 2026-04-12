#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化策略 - Evolution Strategies
CMA-ES和OpenAI-ES实现
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from genetic_core import Genome

class EvolutionStrategy:
    """进化策略基类"""
    
    def __init__(self, population_size: int = 50, sigma: float = 0.1):
        self.population_size = population_size
        self.sigma = sigma
        self.generation = 0
        self.best_fitness = float('-inf')
        self.best_genome: Optional[Genome] = None
    
    def optimize(self, genome: Genome, fitness_function, 
                num_generations: int = 100) -> Genome:
        """优化基因组"""
        raise NotImplementedError

class CMAES(EvolutionStrategy):
    """CMA-ES（协方差矩阵自适应进化策略）"""
    
    def __init__(self, population_size: int = 50, sigma: float = 0.1):
        super().__init__(population_size, sigma)
        self.mean = None
        self.covariance = None
        self.lambda_ = population_size
        self.mu = population_size // 2
        self.weights = None
        self.cc = None
        self.cs = None
        self.c1 = None
        self.cmu = None
        self.damps = None
        self.pc = None
        self.ps = None
    
    def initialize(self, genome: Genome):
        """初始化CMA-ES"""
        # 提取参数
        params = self._extract_parameters(genome)
        dim = len(params)
        
        # 初始化均值
        self.mean = params.copy()
        
        # 初始化协方差矩阵
        self.covariance = np.eye(dim)
        
        # 初始化进化路径
        self.pc = np.zeros(dim)
        self.ps = np.zeros(dim)
        
        # 设置权重
        self.weights = np.array([np.log(self.mu + 0.5) - np.log(i + 1) 
                                for i in range(self.mu)])
        self.weights = self.weights / np.sum(self.weights)
        
        # 设置参数
        self.cc = 4 / (dim + 4)
        self.cs = (self.mu + 2) / (dim + self.mu + 3)
        self.c1 = 2 / ((dim + 1.3)**2 + self.mu)
        self.cmu = min(1 - self.c1, 2 * (self.mu - 2 + 1/self.mu) / 
                      ((dim + 2)**2 + self.mu))
        self.damps = 1 + 2 * max(0, np.sqrt((self.mu - 1) / (dim + 1)) - 1) + \
                   self.cs
    
    def _extract_parameters(self, genome: Genome) -> np.ndarray:
        """提取基因组参数"""
        params = []
        
        # 节点参数
        for node in genome.node_genes.values():
            params.append(node.bias)
            params.append(node.response)
        
        # 连接参数
        for conn in genome.connection_genes.values():
            params.append(conn.weight)
        
        return np.array(params)
    
    def _apply_parameters(self, genome: Genome, params: np.ndarray):
        """应用参数到基因组"""
        idx = 0
        
        # 应用节点参数
        for node in genome.node_genes.values():
            node.bias = params[idx]
            idx += 1
            node.response = params[idx]
            idx += 1
        
        # 应用连接参数
        for conn in genome.connection_genes.values():
            conn.weight = params[idx]
            idx += 1
    
    def optimize(self, genome: Genome, fitness_function, 
                num_generations: int = 100) -> Genome:
        """优化基因组"""
        self.initialize(genome)
        
        for gen in range(num_generations):
            # 生成样本
            samples = []
            for _ in range(self.lambda_):
                z = np.random.randn(len(self.mean))
                sample = self.mean + self.sigma * np.linalg.cholesky(self.covariance).T @ z
                samples.append(sample)
            
            # 评估样本
            fitnesses = []
            for sample in samples:
                test_genome = self._copy_genome(genome)
                self._apply_parameters(test_genome, sample)
                fitness = fitness_function(test_genome)
                fitnesses.append(fitness)
            
            # 选择最佳样本
            sorted_indices = np.argsort(fitnesses)[::-1]
            selected_indices = sorted_indices[:self.mu]
            selected_samples = [samples[i] for i in selected_indices]
            selected_fitnesses = [fitnesses[i] for i in selected_indices]
            
            # 更新均值
            old_mean = self.mean.copy()
            self.mean = np.sum([self.weights[i] * selected_samples[i] 
                               for i in range(self.mu)], axis=0)
            
            # 更新进化路径
            z_mean = np.sum([self.weights[i] * (selected_samples[i] - old_mean) / self.sigma 
                            for i in range(self.mu)], axis=0)
            self.ps = (1 - self.cs) * self.ps + \
                     np.sqrt(self.cs * (2 - self.cs) * self.mu) * z_mean
            
            # 更新协方差矩阵
            rank_one_update = np.outer(self.ps, self.ps)
            rank_mu_update = np.sum([self.weights[i] * 
                                    np.outer((selected_samples[i] - old_mean) / self.sigma,
                                            (selected_samples[i] - old_mean) / self.sigma)
                                    for i in range(self.mu)], axis=0)
            
            self.covariance = ((1 - self.c1 - self.cmu) * self.covariance +
                             self.c1 * rank_one_update +
                             self.cmu * rank_mu_update)
            
            # 更新步长
            self.sigma *= np.exp((np.linalg.norm(self.ps) / np.sqrt(len(self.mean)) - 1) / 
                               (2 * self.damps))
            
            # 记录最佳
            if max(fitnesses) > self.best_fitness:
                self.best_fitness = max(fitnesses)
                best_idx = np.argmax(fitnesses)
                self.best_genome = self._copy_genome(genome)
                self._apply_parameters(self.best_genome, samples[best_idx])
        
        return self.best_genome if self.best_genome else genome
    
    def _copy_genome(self, genome: Genome) -> Genome:
        """复制基因组"""
        new_genome = Genome(genome.genome_id)
        new_genome.node_genes = {k: v for k, v in genome.node_genes.items()}
        new_genome.connection_genes = {k: v for k, v in genome.connection_genes.items()}
        return new_genome

class OpenAI_ES(EvolutionStrategy):
    """OpenAI进化策略"""
    
    def __init__(self, population_size: int = 50, sigma: float = 0.1, 
                 alpha: float = 0.01):
        super().__init__(population_size, sigma)
        self.alpha = alpha
        self.theta = None
    
    def initialize(self, genome: Genome):
        """初始化OpenAI-ES"""
        self.theta = self._extract_parameters(genome)
    
    def _extract_parameters(self, genome: Genome) -> np.ndarray:
        """提取基因组参数"""
        params = []
        
        for node in genome.node_genes.values():
            params.append(node.bias)
            params.append(node.response)
        
        for conn in genome.connection_genes.values():
            params.append(conn.weight)
        
        return np.array(params)
    
    def _apply_parameters(self, genome: Genome, params: np.ndarray):
        """应用参数到基因组"""
        idx = 0
        
        for node in genome.node_genes.values():
            node.bias = params[idx]
            idx += 1
            node.response = params[idx]
            idx += 1
        
        for conn in genome.connection_genes.values():
            conn.weight = params[idx]
            idx += 1
    
    def optimize(self, genome: Genome, fitness_function, 
                num_generations: int = 100) -> Genome:
        """优化基因组"""
        self.initialize(genome)
        
        for gen in range(num_generations):
            # 生成噪声
            epsilons = [np.random.randn(len(self.theta)) for _ in range(self.population_size)]
            
            # 评估正负方向
            fitnesses = []
            for epsilon in epsilons:
                # 正方向
                test_genome = self._copy_genome(genome)
                self._apply_parameters(test_genome, self.theta + self.sigma * epsilon)
                fitness_pos = fitness_function(test_genome)
                
                # 负方向
                test_genome = self._copy_genome(genome)
                self._apply_parameters(test_genome, self.theta - self.sigma * epsilon)
                fitness_neg = fitness_function(test_genome)
                
                fitnesses.append(fitness_pos - fitness_neg)
            
            # 计算梯度
            gradient = np.sum([fitnesses[i] * epsilons[i] 
                             for i in range(self.population_size)], axis=0)
            gradient /= (self.population_size * self.sigma)
            
            # 更新参数
            self.theta += self.alpha * gradient
            
            # 记录最佳
            if max(fitnesses) > self.best_fitness:
                self.best_fitness = max(fitnesses)
                best_idx = np.argmax(fitnesses)
                self.best_genome = self._copy_genome(genome)
                self._apply_parameters(self.best_genome, 
                                      self.theta + self.sigma * epsilons[best_idx])
        
        return self.best_genome if self.best_genome else genome
    
    def _copy_genome(self, genome: Genome) -> Genome:
        """复制基因组"""
        new_genome = Genome(genome.genome_id)
        new_genome.node_genes = {k: v for k, v in genome.node_genes.items()}
        new_genome.connection_genes = {k: v for k, v in genome.connection_genes.items()}
        return new_genome

class QualityDiversity(EvolutionStrategy):
    """质量多样性进化"""
    
    def __init__(self, population_size: int = 50, archive_size: int = 100):
        super().__init__(population_size, sigma=0.1)
        self.archive_size = archive_size
        self.archive: List[Tuple[Genome, float, np.ndarray]] = []
    
    def optimize(self, genome: Genome, fitness_function, 
                descriptor_function, num_generations: int = 100) -> Genome:
        """优化基因组（质量+多样性）"""
        for gen in range(num_generations):
            # 生成变异
            offspring = []
            for _ in range(self.population_size):
                test_genome = self._mutate_genome(genome)
                fitness = fitness_function(test_genome)
                descriptor = descriptor_function(test_genome)
                offspring.append((test_genome, fitness, descriptor))
            
            # 添加到档案
            for offspring_genome, fitness, descriptor in offspring:
                # 检查是否在档案中已有相似个体
                is_novel = True
                for archived_genome, _, archived_descriptor in self.archive:
                    distance = np.linalg.norm(descriptor - archived_descriptor)
                    if distance < 0.1:  # 相似度阈值
                        is_novel = False
                        if fitness > archived_genome.fitness:
                            # 替换
                            self.archive.remove((archived_genome, archived_genome.fitness, archived_descriptor))
                            self.archive.append((offspring_genome, fitness, descriptor))
                        break
                
                if is_novel:
                    self.archive.append((offspring_genome, fitness, descriptor))
                    
                    # 限制档案大小
                    if len(self.archive) > self.archive_size:
                        # 移除最差的
                        self.archive.sort(key=lambda x: x[1], reverse=True)
                        self.archive.pop()
            
            # 从档案中选择最佳
            if self.archive:
                best_genome, best_fitness, _ = max(self.archive, key=lambda x: x[1])
                if best_fitness > self.best_fitness:
                    self.best_fitness = best_fitness
                    self.best_genome = best_genome
        
        return self.best_genome if self.best_genome else genome
    
    def _mutate_genome(self, genome: Genome) -> Genome:
        """变异基因组"""
        new_genome = self._copy_genome(genome)
        
        # 随机变异一些参数
        for node in new_genome.node_genes.values():
            if np.random.random() < 0.1:
                node.bias += np.random.normal(0, 0.1)
        
        for conn in new_genome.connection_genes.values():
            if np.random.random() < 0.1:
                conn.weight += np.random.normal(0, 0.1)
        
        return new_genome
    
    def _copy_genome(self, genome: Genome) -> Genome:
        """复制基因组"""
        new_genome = Genome(genome.genome_id)
        new_genome.node_genes = {k: v for k, v in genome.node_genes.items()}
        new_genome.connection_genes = {k: v for k, v in genome.connection_genes.items()}
        return new_genome

print("Evolution Strategies Module Loaded Successfully!")
