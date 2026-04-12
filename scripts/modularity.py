#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块复用 - Modularity
功能模块和子网络复用
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from genetic_core import Genome, NodeGene, ConnectionGene, NodeType

class FunctionalModule:
    """功能模块"""
    
    def __init__(self, module_id: int, name: str):
        self.module_id = module_id
        self.name = name
        self.input_nodes: Set[int] = set()
        self.output_nodes: Set[int] = set()
        self.internal_nodes: Set[int] = set()
        self.internal_connections: Set[int] = set()
        self.usage_count = 0
        self.fitness_score = 0.0
    
    def add_input_node(self, node_id: int):
        """添加输入节点"""
        self.input_nodes.add(node_id)
    
    def add_output_node(self, node_id: int):
        """添加输出节点"""
        self.output_nodes.add(node_id)
    
    def add_internal_node(self, node_id: int):
        """添加内部节点"""
        self.internal_nodes.add(node_id)
    
    def add_internal_connection(self, conn_id: int):
        """添加内部连接"""
        self.internal_connections.add(conn_id)
    
    def get_all_nodes(self) -> Set[int]:
        """获取所有节点"""
        return self.input_nodes | self.output_nodes | self.internal_nodes
    
    def get_size(self) -> int:
        """获取模块大小"""
        return len(self.get_all_nodes())

class Modularity:
    """模块化系统"""
    
    def __init__(self):
        self.modules: Dict[int, FunctionalModule] = {}
        self.module_counter = 0
        self.node_to_module: Dict[int, int] = {}
        self.connection_to_module: Dict[int, int] = {}
    
    def create_module(self, name: str) -> FunctionalModule:
        """创建新模块"""
        module_id = self.module_counter
        self.module_counter += 1
        
        module = FunctionalModule(module_id, name)
        self.modules[module_id] = module
        
        return module
    
    def assign_node_to_module(self, node_id: int, module_id: int):
        """分配节点到模块"""
        if module_id in self.modules:
            self.node_to_module[node_id] = module_id
    
    def assign_connection_to_module(self, conn_id: int, module_id: int):
        """分配连接到模块"""
        if module_id in self.modules:
            self.connection_to_module[conn_id] = module_id
    
    def detect_modules(self, genome: Genome, threshold: float = 0.3) -> List[FunctionalModule]:
        """检测模块（基于连接密度）"""
        # 构建邻接矩阵
        node_ids = list(genome.node_genes.keys())
        n = len(node_ids)
        adjacency = np.zeros((n, n))
        
        for conn in genome.connection_genes.values():
            if conn.enabled:
                i = node_ids.index(conn.in_node)
                j = node_ids.index(conn.out_node)
                adjacency[i, j] = 1
        
        # 计算模块度
        modules = []
        visited = set()
        
        for i, node_id in enumerate(node_ids):
            if node_id in visited:
                continue
            
            # 找到紧密连接的节点
            module_nodes = {node_id}
            queue = [node_id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                
                # 查找邻居
                for conn in genome.connection_genes.values():
                    if conn.enabled:
                        if conn.in_node == current and conn.out_node not in module_nodes:
                            # 检查连接密度
                            density = self._calculate_local_density(genome, module_nodes | {conn.out_node})
                            if density > threshold:
                                module_nodes.add(conn.out_node)
                                queue.append(conn.out_node)
                        elif conn.out_node == current and conn.in_node not in module_nodes:
                            density = self._calculate_local_density(genome, module_nodes | {conn.in_node})
                            if density > threshold:
                                module_nodes.add(conn.in_node)
                                queue.append(conn.in_node)
            
            # 创建模块
            if len(module_nodes) > 1:
                module = self.create_module(f"module_{len(modules)}")
                for node in module_nodes:
                    module.add_internal_node(node)
                    self.assign_node_to_module(node, module.module_id)
                
                modules.append(module)
        
        return modules
    
    def _calculate_local_density(self, genome: Genome, nodes: Set[int]) -> float:
        """计算局部连接密度"""
        if len(nodes) < 2:
            return 0.0
        
        # 计算内部连接数
        internal_edges = 0
        for conn in genome.connection_genes.values():
            if conn.enabled:
                if conn.in_node in nodes and conn.out_node in nodes:
                    internal_edges += 1
        
        # 计算最大可能连接数
        max_edges = len(nodes) * (len(nodes) - 1)
        
        return internal_edges / max_edges if max_edges > 0 else 0.0
    
    def reuse_module(self, genome: Genome, module: FunctionalModule, 
                    new_inputs: List[int], new_outputs: List[int]) -> bool:
        """复用模块"""
        # 创建模块的副本
        node_mapping = {}
        
        # 复制内部节点
        for old_node_id in module.internal_nodes:
            new_node_id = max(genome.node_genes.keys()) + 1 if genome.node_genes else 0
            old_node = genome.node_genes[old_node_id]
            
            new_node = NodeGene(
                id=new_node_id,
                node_type=old_node.node_type,
                activation=old_node.activation,
                bias=old_node.bias,
                response=old_node.response,
                x=old_node.x + np.random.uniform(-0.1, 0.1),
                y=old_node.y + np.random.uniform(-0.1, 0.1),
                generation=genome.generation,
                plasticity=old_node.plasticity
            )
            
            genome.add_node(new_node)
            node_mapping[old_node_id] = new_node_id
        
        # 复制内部连接
        for conn_id in module.internal_connections:
            old_conn = genome.connection_genes[conn_id]
            
            new_in_node = node_mapping.get(old_conn.in_node, old_conn.in_node)
            new_out_node = node_mapping.get(old_conn.out_node, old_conn.out_node)
            
            innov = genome.get_innovation_number()
            new_conn = ConnectionGene(
                in_node=new_in_node,
                out_node=new_out_node,
                weight=old_conn.weight,
                enabled=True,
                innov_id=innov
            )
            
            genome.add_connection(new_conn)
        
        # 连接新输入
        for new_input in new_inputs:
            for internal_node in module.internal_nodes:
                innov = genome.get_innovation_number()
                conn = ConnectionGene(
                    in_node=new_input,
                    out_node=node_mapping[internal_node],
                    weight=np.random.uniform(-0.5, 0.5),
                    enabled=True,
                    innov_id=innov
                )
                genome.add_connection(conn)
        
        # 连接新输出
        for new_output in new_outputs:
            for internal_node in module.internal_nodes:
                innov = genome.get_innovation_number()
                conn = ConnectionGene(
                    in_node=node_mapping[internal_node],
                    out_node=new_output,
                    weight=np.random.uniform(-0.5, 0.5),
                    enabled=True,
                    innov_id=innov
                )
                genome.add_connection(conn)
        
        module.usage_count += 1
        return True
    
    def get_module_statistics(self) -> Dict:
        """获取模块统计"""
        if not self.modules:
            return {
                'total_modules': 0,
                'avg_size': 0.0,
                'max_size': 0,
                'total_usage': 0
            }
        
        sizes = [module.get_size() for module in self.modules.values()]
        total_usage = sum(module.usage_count for module in self.modules.values())
        
        return {
            'total_modules': len(self.modules),
            'avg_size': np.mean(sizes),
            'max_size': max(sizes),
            'total_usage': total_usage
        }

print("Modularity Module Loaded Successfully!")
