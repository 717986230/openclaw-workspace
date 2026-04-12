#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神经进化 - 拓扑和权重同时进化
Neuroevolution - Topology and Weight Evolution
灵感来源: PyTorch-NEAT, Deep Neuroevolution
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Set, Callable
from dataclasses import dataclass
from enum import Enum
import copy
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp

class EvolutionStrategy(Enum):
    NEAT = "neat"                           # 标准NEAT
    HYPERNEAT = "hyperneat"                 # HyperNEAT（几何模式生成）
    ES = "es"                               # 进化策略
    CMA_ES = "cma_es"                       # CMA-ES
    OPENAI_ES = "openai_es"                 # OpenAI进化策略
    NSGA2 = "nsga2"                         # 多目标进化
    QUALITY_DIVERSITY = "quality_diversity" # 质量多样性

@dataclass
class Species:
    """物种"""
    id: int
    representative_genome: 'Genome'
    members: List['Genome']
    age: int
    avg_fitness: float
    max_fitness: float
    staleness: int  # 停滞代数
    
    def __post_init__(self):
        if self.avg_fitness is None:
            self.avg_fitness = 0.0
        if self.max_fitness is None:
            self.max_fitness = 0.0

class NeuralNetwork:
    """表现型神经网络"""
    
    def __init__(self, genome: 'Genome'):
        self.genome = genome
        self.nodes: Dict[int, Dict] = {}
        self.connections: List[Tuple[int, int, float]] = []
        self.activation_cache: Dict[int, float] = {}
        self.build_network()
    
    def build_network(self):
        """从基因组构建网络"""
        # 构建节点
        for node_id, node_gene in self.genome.node_genes.items():
            self.nodes[node_id] = {
                'type': node_gene.node_type,
                'activation': self._get_activation(node_gene.activation),
                'bias': node_gene.bias,
                'response': node_gene.response,
                'plasticity': node_gene.plasticity,
                'neurotransmitter': node_gene.neurotransmitter,
                'receptor_sensitivity': node_gene.receptor_sensitivity,
                'value': 0.0,
                'activation_history': []
            }
        
        # 构建连接
        for conn_id, conn_gene in self.genome.connection_genes.items():
            if conn_gene.enabled:
                self.connections.append((
                    conn_gene.in_node,
                    conn_gene.out_node,
                    conn_gene.weight
                ))
    
    def _get_activation(self, activation: ActivationFunction) -> Callable:
        """获取激活函数"""
        activations = {
            ActivationFunction.SIGMOID: lambda x: 1 / (1 + np.exp(-x)),
            ActivationFunction.TANH: np.tanh,
            ActivationFunction.RELU: lambda x: max(0, x),
            ActivationFunction.LEAKY_RELU: lambda x: x if x > 0 else 0.01 * x,
            ActivationFunction.ELU: lambda x: x if x > 0 else np.expm1(x),
            ActivationFunction.SWISH: lambda x: x / (1 + np.exp(-x)),
            ActivationFunction.GAUSSIAN: lambda x: np.exp(-x**2),
            ActivationFunction.SIN: np.sin,
            ActivationFunction.COS: np.cos,
            ActivationFunction.ABS: abs,
            ActivationFunction.STEP: lambda x: 1 if x > 0 else 0,
            ActivationFunction.IDENTITY: lambda x: x,
        }
        return activations.get(activation, lambda x: x)
    
    def activate(self, inputs: Dict[int, float]) -> Dict[int, float]:
        """前向传播"""
        # 设置输入
        for node_id, value in inputs.items():
            if node_id in self.nodes:
                self.nodes[node_id]['value'] = value
        
        # 按拓扑顺序计算（简单实现：多次迭代）
        for _ in range(10):  # 迭代10次
            new_values = {}
            for node_id, node_data in self.nodes.items():
                if node_data['type'] != NodeType.SENSOR:
                    # 收集输入
                    total_input = node_data['bias']
                    for in_id, out_id, weight in self.connections:
                        if out_id == node_id:
                            total_input += self.nodes[in_id]['value'] * weight
                    
                    # 应用激活函数
                    activated = node_data['activation'](total_input * node_data['response'])
                    new_values[node_id] = activated
            
            # 更新值
            for node_id, value in new_values.items():
                self.nodes[node_id]['value'] = value
                self.nodes[node_id]['activation_history'].append(value)
                # 限制历史长度
                if len(self.nodes[node_id]['activation_history']) > 100:
                    self.nodes[node_id]['activation_history'].pop(0)
        
        # 收集输出
        outputs = {}
        for node_id, node_data in self.nodes.items():
            if node_data['type'] == NodeType.OUTPUT:
                outputs[node_id] = node_data['value']
        
        return outputs

class NeuroevolutionTrainer:
    """神经进化训练器"""
    
    def __init__(
        self,
        num_inputs: int,
        num_outputs: int,
        population_size: int = 150,
        max_species: int = 15,
        compatibility_threshold: float = 3.0,
        strategy: EvolutionStrategy = EvolutionStrategy.NEAT
    ):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.population_size = population_size
        self.max_species = max_species
        self.compatibility_threshold = compatibility_threshold
        self.strategy = strategy
        
        # 种群
        self.population: List[Genome] = []
        self.species: Dict[int, Species] = {}
        self.generation = 0
        self.global_innovation = 0
        self.genome_id = 0
        
        # 创新号历史（用于追踪连接基因）
        self.innovation_history: Dict[Tuple[int, int], int] = {}
        
        # 最佳个体
        self.best_genome: Optional[Genome] = None
        self.best_fitness = float('-inf')
        
        # 自适应参数
        self.compatibility_threshold = compatibility_threshold
        self.target_species = max_species
        
        # NEAT参数
        self.mutation_rates = {
            'weight_mutate_rate': 0.8,
            'weight_replace_rate': 0.1,
            'add_node_rate': 0.03,
            'add_conn_rate': 0.05,
            'toggle_rate': 0.01,
            'node_param_rate': 0.1
        }
        
        # CMA-ES参数（如果使用）
        self.cma_es_state = None
        
        # OpenAI-ES参数（如果使用）
        self.es_population = None
        self.es_sigma = 0.1
        self.es_alpha = 0.01
    
    def create_initial_population(self):
        """创建初始种群"""
        for _ in range(self.population_size):
            genome = self._create_minimal_genome()
            self.population.append(genome)
    
    def _create_minimal_genome(self) -> Genome:
        """创建最小基因组（无隐藏层）"""
        genome = Genome(self.genome_id)
        self.genome_id += 1
        
        # 创建输入节点
        for i in range(self.num_inputs):
            node = NodeGene(
                id=i,
                node_type=NodeType.SENSOR,
                activation=ActivationFunction.IDENTITY,
                bias=0.0,
                response=1.0,
                x=i / (self.num_inputs - 1) if self.num_inputs > 1 else 0.5,
                y=0.0,
                generation=0
            )
            genome.add_node(node)
        
        # 创建输出节点
        for i in range(self.num_outputs):
            node = NodeGene(
                id=self.num_inputs + i,
                node_type=NodeType.OUTPUT,
                activation=ActivationFunction.TANH,
                bias=0.0,
                response=1.0,
                x=i / (self.num_outputs - 1) if self.num_outputs > 1 else 0.5,
