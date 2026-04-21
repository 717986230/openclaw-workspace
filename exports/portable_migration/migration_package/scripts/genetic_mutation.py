#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基因突变 - Genetic Mutation
实现多种突变操作符
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from genetic_core import Genome, NodeGene, ConnectionGene, NodeType, ActivationFunction

class GeneticMutation:
    """基因突变操作"""
    
    def __init__(self, mutation_rates: Dict[str, float] = None):
        self.mutation_rates = mutation_rates or {
            'weight_mutate_rate': 0.8,
            'weight_replace_rate': 0.1,
            'add_node_rate': 0.03,
            'add_conn_rate': 0.05,
            'toggle_rate': 0.01,
            'node_param_rate': 0.1,
            'activation_mutate_rate': 0.1,
            'bias_mutate_rate': 0.5
        }
    
    def mutate_genome(self, genome: Genome) -> Genome:
        """对基因组进行全面突变"""
        # 权重突变
        if np.random.random() < self.mutation_rates['weight_mutate_rate']:
            self._mutate_weights(genome)
        
        # 添加节点突变
        if np.random.random() < self.mutation_rates['add_node_rate']:
            self._mutate_add_node(genome)
        
        # 添加连接突变
        if np.random.random() < self.mutation_rates['add_conn_rate']:
            self._mutate_add_connection(genome)
        
        # 启用/禁用突变
        if np.random.random() < self.mutation_rates['toggle_rate']:
            self._mutate_toggle_connection(genome)
        
        # 节点参数突变
        if np.random.random() < self.mutation_rates['node_param_rate']:
            self._mutate_node_params(genome)
        
        # 激活函数突变
        if np.random.random() < self.mutation_rates['activation_mutate_rate']:
            self._mutate_activation(genome)
        
        return genome
    
    def _mutate_weights(self, genome: Genome):
        """突触权重突变"""
        for conn in genome.connection_genes.values():
            if not conn.enabled:
                continue
            if np.random.random() < self.mutation_rates['weight_replace_rate']:
                # 完全替换
                conn.weight = np.random.uniform(-2, 2)
            else:
                # 扰动
                conn.weight += np.random.normal(0, 0.5)
            conn.weight = np.clip(conn.weight, -8, 8)
    
    def _mutate_add_node(self, genome: Genome):
        """添加新节点（分割现有连接）"""
        enabled_conns = [c for c in genome.connection_genes.values() if c.enabled]
        if not enabled_conns:
            return
        
        conn_to_split = enabled_conns[np.random.randint(len(enabled_conns))]
        conn_to_split.enabled = False
        
        # 获取新节点ID
        new_node_id = max(genome.node_genes.keys()) + 1 if genome.node_genes else 0
        
        # 计算位置（中点）
        in_node = genome.node_genes[conn_to_split.in_node]
        out_node = genome.node_genes[conn_to_split.out_node]
        
        # 创建新节点
        new_node = NodeGene(
            id=new_node_id,
            node_type=NodeType.HIDDEN,
            activation=np.random.choice(list(ActivationFunction)),
            bias=np.random.normal(0, 0.5),
            response=1.0,
            x=(in_node.x + out_node.x) / 2,
            y=(in_node.y + out_node.y) / 2 + 0.1,
            generation=genome.generation,
            plasticity=np.random.uniform(0.1, 0.5)
        )
        genome.add_node(new_node)
        
        # 创建两个新连接
        innov1 = genome.get_innovation_number()
        new_conn1 = ConnectionGene(
            in_node=conn_to_split.in_node,
            out_node=new_node_id,
            weight=1.0,
            enabled=True,
            innov_id=innov1
        )
        
        innov2 = genome.get_innovation_number()
        new_conn2 = ConnectionGene(
            in_node=new_node_id,
            out_node=conn_to_split.out_node,
            weight=conn_to_split.weight,
            enabled=True,
            innov_id=innov2
        )
        
        genome.add_connection(new_conn1)
        genome.add_connection(new_conn2)
    
    def _mutate_add_connection(self, genome: Genome):
        """添加新连接"""
        # 获取可用节点
        node_ids = list(genome.node_genes.keys())
        if len(node_ids) < 2:
            return
        
        # 尝试添加连接（限制尝试次数）
        for _ in range(20):
            in_node = int(np.random.choice(node_ids))
            out_node = int(np.random.choice(node_ids))
            
            if in_node == out_node:
                continue
            
            # 检查是否已存在
            exists = False
            for conn in genome.connection_genes.values():
                if conn.in_node == in_node and conn.out_node == out_node:
                    exists = True
                    break
            
            if exists:
                continue
            
            # 检查是否形成循环（简化版）
            if self._would_create_cycle(genome, in_node, out_node):
                continue
            
            # 创建新连接
            innov = genome.get_innovation_number()
            new_conn = ConnectionGene(
                in_node=in_node,
                out_node=out_node,
                weight=np.random.uniform(-1, 1),
                enabled=True,
                innov_id=innov
            )
            genome.add_connection(new_conn)
            break
    
    def _would_create_cycle(self, genome: Genome, in_node: int, out_node: int) -> bool:
        """检查是否会形成循环"""
        visited = set()
        stack = [out_node]
        
        while stack:
            current = stack.pop()
            if current == in_node:
                return True
            if current in visited:
                continue
            visited.add(current)
            
            for conn in genome.connection_genes.values():
                if conn.enabled and conn.in_node == current:
                    stack.append(conn.out_node)
        
        return False
    
    def _mutate_toggle_connection(self, genome: Genome):
        """切换连接启用状态"""
        if not genome.connection_genes:
            return
        conn = np.random.choice(list(genome.connection_genes.values()))
        conn.enabled = not conn.enabled
    
    def _mutate_node_params(self, genome: Genome):
        """突变节点参数"""
        for node in genome.node_genes.values():
            if np.random.random() < self.mutation_rates['bias_mutate_rate']:
                node.bias += np.random.normal(0, 0.5)
                node.bias = np.clip(node.bias, -10, 10)
            
            if np.random.random() < 0.1:
                node.response += np.random.normal(0, 0.1)
                node.response = np.clip(node.response, 0.1, 5)
    
    def _mutate_activation(self, genome: Genome):
        """突变激活函数"""
        hidden_nodes = [n for n in genome.node_genes.values() 
                       if n.node_type == NodeType.HIDDEN]
        if hidden_nodes and np.random.random() < 0.1:
            node = np.random.choice(hidden_nodes)
            available = [a for a in ActivationFunction if a != ActivationFunction.IDENTITY]
            node.activation = np.random.choice(available)

print("Genetic Mutation Module Loaded Successfully!")
