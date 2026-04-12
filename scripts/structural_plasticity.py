#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结构可塑性 - Structural Plasticity
动态连接重塑和拓扑变化
"""

import numpy as np
from typing import Dict, List, Set, Tuple
from genetic_core import Genome, ConnectionGene

class StructuralPlasticity:
    """结构可塑性系统"""
    
    def __init__(self, connection_threshold: float = 0.5, 
                 pruning_rate: float = 0.01, growth_rate: float = 0.02):
        self.connection_threshold = connection_threshold
        self.pruning_rate = pruning_rate
        self.growth_rate = growth_rate
        
        # 连接使用统计
        self.connection_usage: Dict[int, int] = {}
        self.connection_strength: Dict[int, float] = {}
    
    def update_connection_usage(self, conn_id: int, used: bool):
        """更新连接使用情况"""
        if conn_id not in self.connection_usage:
            self.connection_usage[conn_id] = 0
        
        if used:
            self.connection_usage[conn_id] += 1
    
    def update_connection_strength(self, conn_id: int, activity: float):
        """更新连接强度"""
        if conn_id not in self.connection_strength:
            self.connection_strength[conn_id] = 0.0
        
        # 指数移动平均
        self.connection_strength[conn_id] = (
            0.9 * self.connection_strength[conn_id] + 0.1 * activity
        )
    
    def prune_weak_connections(self, genome: Genome) -> List[int]:
        """修剪弱连接"""
        pruned = []
        
        for conn_id, conn in list(genome.connection_genes.items()):
            if not conn.enabled:
                continue
            
            # 检查连接强度
            strength = self.connection_strength.get(conn_id, 0.0)
            
            # 检查使用频率
            usage = self.connection_usage.get(conn_id, 0)
            
            # 决定是否修剪
            if (strength < self.connection_threshold and 
                np.random.random() < self.pruning_rate):
                conn.enabled = False
                pruned.append(conn_id)
        
        return pruned
    
    def grow_new_connections(self, genome: Genome, max_new: int = 5) -> List[int]:
        """生长新连接"""
        new_connections = []
        
        # 获取所有节点
        node_ids = list(genome.node_genes.keys())
        if len(node_ids) < 2:
            return new_connections
        
        # 尝试添加新连接
        attempts = 0
        while len(new_connections) < max_new and attempts < 20:
            attempts += 1
            
            # 随机选择两个节点
            in_node = np.random.choice(node_ids)
            out_node = np.random.choice(node_ids)
            
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
            
            # 检查是否形成循环
            if self._would_create_cycle(genome, in_node, out_node):
                continue
            
            # 创建新连接
            if np.random.random() < self.growth_rate:
                innov = genome.get_innovation_number()
                new_conn = ConnectionGene(
                    in_node=in_node,
                    out_node=out_node,
                    weight=np.random.uniform(-0.5, 0.5),
                    enabled=True,
                    innov_id=innov
                )
                
                if genome.add_connection(new_conn):
                    new_connections.append(innov)
                    self.connection_strength[innov] = 0.5
                    self.connection_usage[innov] = 0
        
        return new_connections
    
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
    
    def reorganize_network(self, genome: Genome) -> Dict:
        """重组网络（修剪+生长）"""
        # 修剪弱连接
        pruned = self.prune_weak_connections(genome)
        
        # 生长新连接
        grown = self.grow_new_connections(genome)
        
        return {
            'pruned': len(pruned),
            'grown': len(grown),
            'pruned_ids': pruned,
            'grown_ids': grown
        }
    
    def get_network_density(self, genome: Genome) -> float:
        """获取网络密度"""
        num_nodes = len(genome.node_genes)
        num_edges = len([c for c in genome.connection_genes.values() if c.enabled])
        
        if num_nodes < 2:
            return 0.0
        
        max_edges = num_nodes * (num_nodes - 1)
        return num_edges / max_edges if max_edges > 0 else 0.0
    
    def get_clustering_coefficient(self, genome: Genome) -> float:
        """获取聚类系数"""
        if not genome.node_genes:
            return 0.0
        
        # 构建邻接表
        adjacency = {nid: set() for nid in genome.node_genes.keys()}
        for conn in genome.connection_genes.values():
            if conn.enabled:
                adjacency[conn.in_node].add(conn.out_node)
        
        # 计算聚类系数
        coefficients = []
        for node_id, neighbors in adjacency.items():
            if len(neighbors) < 2:
                continue
            
            # 计算邻居之间的连接数
            neighbor_pairs = 0
            connected_pairs = 0
            
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 < n2:
                        neighbor_pairs += 1
                        if n2 in adjacency[n1]:
                            connected_pairs += 1
            
            if neighbor_pairs > 0:
                coeff = connected_pairs / neighbor_pairs
                coefficients.append(coeff)
        
        return np.mean(coefficients) if coefficients else 0.0
    
    def get_path_length(self, genome: Genome) -> float:
        """获取平均路径长度"""
        if not genome.node_genes:
            return 0.0
        
        # 构建邻接表
        adjacency = {nid: set() for nid in genome.node_genes.keys()}
        for conn in genome.connection_genes.values():
            if conn.enabled:
                adjacency[conn.in_node].add(conn.out_node)
        
        # 计算所有节点对的最短路径
        total_length = 0
        count = 0
        
        for start in genome.node_genes.keys():
            # BFS
            distances = {start: 0}
            queue = [start]
            
            while queue:
                current = queue.pop(0)
                for neighbor in adjacency[current]:
                    if neighbor not in distances:
                        distances[neighbor] = distances[current] + 1
                        queue.append(neighbor)
            
            # 累加距离
            for end, dist in distances.items():
                if start < end:
                    total_length += dist
                    count += 1
        
        return total_length / count if count > 0 else 0.0

print("Structural Plasticity Module Loaded Successfully!")
