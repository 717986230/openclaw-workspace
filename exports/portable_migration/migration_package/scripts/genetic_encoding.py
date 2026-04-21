#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基因编码 - 遗传编码与基因型-表现型映射
Genetic Encoding - Genotype-Phenotype Mapping
灵感来源: NEAT (NeuroEvolution of Augmenting Topologies)
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class NodeType(Enum):
    SENSOR = "sensor"      # 输入节点
    HIDDEN = "hidden"      # 隐藏节点
    OUTPUT = "output"      # 输出节点
    MEMORY = "memory"      # 记忆节点（特有）
    CONTEXT = "context"    # 上下文节点（特有）
    GENE_MARKER = "gene_marker"  # 基因标记节点

class ActivationFunction(Enum):
    SIGMOID = "sigmoid"
    TANH = "tanh"
    RELU = "relu"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SWISH = "swish"
    GAUSSIAN = "gaussian"
    SIN = "sin"
    COS = "cos"
    ABS = "abs"
    CLAMPED = "clamped"
    IDENTITY = "identity"
    INV = "inv"
    LOG = "log"
    EXP = "exp"
    STEP = "step"
    PULSE = "pulse"
    SPIKE = "spike"  # 脉冲激活

@dataclass
class NodeGene:
    """节点基因"""
    id: int
    node_type: NodeType
    activation: ActivationFunction
    bias: float
    response: float  # 响应系数
    x: float  # 空间位置（用于可视化）
    y: float
    generation: int  # 生成代数
    # 基因特有属性
    plasticity: float = 0.1  # 可塑性
    neurotransmitter: str = "glutamate"  # 神经递质类型
    receptor_sensitivity: float = 1.0  # 受体敏感度
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'node_type': self.node_type.value,
            'activation': self.activation.value,
            'bias': self.bias,
            'response': self.response,
            'x': self.x,
            'y': self.y,
            'generation': self.generation,
            'plasticity': self.plasticity,
            'neurotransmitter': self.neurotransmitter,
            'receptor_sensitivity': self.receptor_sensitivity
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NodeGene':
        return cls(
            id=data['id'],
            node_type=NodeType(data['node_type']),
            activation=ActivationFunction(data['activation']),
            bias=data['bias'],
            response=data['response'],
            x=data['x'],
            y=data['y'],
            generation=data['generation'],
            plasticity=data.get('plasticity', 0.1),
            neurotransmitter=data.get('neurotransmitter', 'glutamate'),
            receptor_sensitivity=data.get('receptor_sensitivity', 1.0)
        )

@dataclass
class ConnectionGene:
    """连接基因"""
    in_node: int
    out_node: int
    weight: float
    enabled: bool
    innov_id: int  # 创新号（历史标记）
    # 基因特有属性
    learning_rate: float = 0.01  # 学习率
    hebbian_strength: float = 0.0  # Hebbian学习强度
    stdp_window: int = 20  # STDP时间窗口
    synaptic_tag: float = 0.0  # 突触标记
    consolidation_threshold: float = 0.8  # 巩固阈值
    
    def to_dict(self) -> Dict:
        return {
            'in_node': self.in_node,
            'out_node': self.out_node,
            'weight': self.weight,
            'enabled': self.enabled,
            'innov_id': self.innov_id,
            'learning_rate': self.learning_rate,
            'hebbian_strength': self.hebbian_strength,
            'stdp_window': self.stdp_window,
            'synaptic_tag': self.synaptic_tag,
            'consolidation_threshold': self.consolidation_threshold
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ConnectionGene':
        return cls(
            in_node=data['in_node'],
            out_node=data['out_node'],
            weight=data['weight'],
            enabled=data['enabled'],
            innov_id=data['innov_id'],
            learning_rate=data.get('learning_rate', 0.01),
            hebbian_strength=data.get('hebbian_strength', 0.0),
            stdp_window=data.get('stdp_window', 20),
            synaptic_tag=data.get('synaptic_tag', 0.0),
            consolidation_threshold=data.get('consolidation_threshold', 0.8)
        )

class Genome:
    """基因组 - 存储完整的网络蓝图"""
    
    def __init__(self, genome_id: int):
        self.genome_id = genome_id
        self.node_genes: Dict[int, NodeGene] = {}
        self.connection_genes: Dict[int, ConnectionGene] = {}
        self.fitness: float = 0.0
        self.adjusted_fitness: float = 0.0
        self.species_id: Optional[int] = None
        self.parent_ids: List[int] = []
        self.generation: int = 0
        
        # 基因统计
        self.node_count: int = 0
        self.connection_count: int = 0
        self.enabled_connection_count: int = 0
        
        # 创新号追踪
        self.global_innovation_number: int = 0
    
    def add_node(self, node_gene: NodeGene):
        """添加节点基因"""
        self.node_genes[node_gene.id] = node_gene
        self.node_count = len(self.node_genes)
    
    def add_connection(self, conn_gene: ConnectionGene) -> bool:
        """添加连接基因"""
        key = (conn_gene.in_node, conn_gene.out_node)
        hash_key = hash(key) % (2**31)
        
        # 避免重复连接
        for existing in self.connection_genes.values():
            if existing.in_node == conn_gene.in_node and existing.out_node == conn_gene.out_node:
                return False
        
        self.connection_genes[hash_key] = conn_gene
        self.connection_count = len(self.connection_genes)
        self.enabled_connection_count = sum(1 for c in self.connection_genes.values() if c.enabled)
        return True
    
    def get_innovation_number(self) -> int:
        """获取新的创新号"""
        self.global_innovation_number += 1
        return self.global_innovation_number
    
    def mutate(self, mutation_rates: Dict[str, float]) -> 'Genome':
        """基因突变"""
        # 突触权重突变
        if np.random.random() < mutation_rates.get('weight_mutate_rate', 0.8):
            for conn in self.connection_genes.values():
                if conn.enabled:
                    if np.random.random() < mutation_rates.get('weight_replace_rate', 0.1):
                        # 完全替换权重
                        conn.weight = np.random.uniform(-2, 2)
                    else:
                        # 轻微扰动
                        conn.weight += np.random.normal(0, 0.5)
                    conn.weight = np.clip(conn.weight, -8, 8)
        
        # 添加新节点突变
        if np.random.random() < mutation_rates.get('add_node_rate', 0.03):
            self._mutate_add_node()
        
        # 添加新连接突变
        if np.random.random() < mutation_rates.get('add_conn_rate', 0.05):
            self._mutate_add_connection()
        
        # 启用/禁用连接突变
        if np.random.random() < mutation_rates.get('toggle_rate', 0.01):
            self._mutate_toggle_connection()
        
        # 节点参数突变
        if np.random.random() < mutation_rates.get('node_param_rate', 0.1):
            self._mutate_node_params()
        
        return self
    
    def _mutate_add_node(self):
        """突变：添加新节点（分割现有连接）"""
        enabled_conns = [c for c in self.connection_genes.values() if c.enabled]
        if not enabled_conns:
            return
        
        # 随机选择一个启用连接
        conn_to_split = np.random.choice(enabled_conns)
        conn_to_split.enabled = False
        
        # 创建新节点
        new_node_id = max(self.node_genes.keys()) + 1 if self.node_genes else 0
        new_node = NodeGene(
            id=new_node_id,
            node_type=NodeType.HIDDEN,
            activation=ActivationFunction(np.random.choice(list(ActivationFunction))),
            bias=np.random.normal(0, 0.5),
            response=1.0,
            x=(self.node_genes[conn_to_split.in_node].x + self.node_genes[conn_to_split.out_node].x) / 2,
            y=(self.node_genes[conn_to_split.in_node].y + self.node_genes[