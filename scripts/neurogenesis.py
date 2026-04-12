#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神经发生 - Neurogenesis
新神经元生成和修剪
"""

import numpy as np
from typing import Dict, List, Set, Tuple
from genetic_core import Genome, NodeGene, ConnectionGene, NodeType, ActivationFunction

class Neurogenesis:
    """神经发生系统"""
    
    def __init__(self, max_neurons: int = 1000, pruning_threshold: float = 0.1):
        self.max_neurons = max_neurons
        self.pruning_threshold = pruning_threshold
        self.neuron_age: Dict[int, int] = {}
        self.neuron_activity: Dict[int, List[float]] = {}
        self.activity_window = 50
    
    def generate_neuron(self, genome: Genome, position: Tuple[float, float] = None) -> int:
        """生成新神经元"""
        if len(genome.node_genes) >= self.max_neurons:
            return -1
        
        new_id = max(genome.node_genes.keys()) + 1 if genome.node_genes else 0
        
        if position is None:
            x = np.random.uniform(0.2, 0.8)
            y = np.random.uniform(0.2, 0.8)
        else:
            x, y = position
        
        new_node = NodeGene(
            id=new_id,
            node_type=NodeType.HIDDEN,
            activation=np.random.choice(list(ActivationFunction)),
            bias=np.random.normal(0, 0.5),
            response=1.0,
            x=x,
            y=y,
            generation=genome.generation,
            plasticity=np.random.uniform(0.1, 0.5)
        )
        
        genome.add_node(new_node)
        self.neuron_age[new_id] = 0
        self.neuron_activity[new_id] = []
        
        return new_id
    
    def prune_neuron(self, genome: Genome, neuron_id: int) -> bool:
        """修剪神经元"""
        if neuron_id not in genome.node_genes:
            return False
        
        # 删除相关连接
        to_remove = []
        for conn_id, conn in genome.connection_genes.items():
            if conn.in_node == neuron_id or conn.out_node == neuron_id:
                to_remove.append(conn_id)
        
        for conn_id in to_remove:
            del genome.connection_genes[conn_id]
        
        # 删除节点
        del genome.node_genes[neuron_id]
        if neuron_id in self.neuron_age:
            del self.neuron_age[neuron_id]
        if neuron_id in self.neuron_activity:
            del self.neuron_activity[neuron_id]
        
        return True
    
    def update_activity(self, neuron_id: int, activity: float):
        """更新神经元活动"""
        if neuron_id not in self.neuron_activity:
            self.neuron_activity[neuron_id] = []
        
        self.neuron_activity[neuron_id].append(activity)
        if len(self.neuron_activity[neuron_id]) > self.activity_window:
            self.neuron_activity[neuron_id].pop(0)
    
    def get_activity_level(self, neuron_id: int) -> float:
        """获取神经元活动水平"""
        if neuron_id not in self.neuron_activity or not self.neuron_activity[neuron_id]:
            return 0.0
        
        return np.mean(self.neuron_activity[neuron_id])
    
    def age_neurons(self, genome: Genome):
        """神经元老化"""
        for neuron_id in list(self.neuron_age.keys()):
            self.neuron_age[neuron_id] += 1
    
    def prune_inactive(self, genome: Genome) -> List[int]:
        """修剪不活跃神经元"""
        pruned = []
        
        for neuron_id in list(genome.node_genes.keys()):
            if genome.node_genes[neuron_id].node_type == NodeType.HIDDEN:
                activity_level = self.get_activity_level(neuron_id)
                if activity_level < self.pruning_threshold:
                    if self.prune_neuron(genome, neuron_id):
                        pruned.append(neuron_id)
        
        return pruned
    
    def prune_overcrowded(self, genome: Genome) -> List[int]:
        """修剪过度拥挤的神经元"""
        pruned = []
        
        while len(genome.node_genes) > self.max_neurons:
            # 找到最不活跃的神经元
            candidates = [nid for nid in genome.node_genes.keys() 
                         if genome.node_genes[nid].node_type == NodeType.HIDDEN]
            
            if not candidates:
                break
            
            worst = min(candidates, key=lambda nid: self.get_activity_level(nid))
            if self.prune_neuron(genome, worst):
                pruned.append(worst)
        
        return pruned
    
    def connect_new_neuron(self, genome: Genome, neuron_id: int, 
                          num_inputs: int = 3, num_outputs: int = 3):
        """为新神经元创建连接"""
        if neuron_id not in genome.node_genes:
            return
        
        # 获取输入节点
        input_nodes = [nid for nid, node in genome.node_genes.items() 
                     if node.node_type in [NodeType.SENSOR, NodeType.HIDDEN] 
                     and nid != neuron_id]
        
        # 获取输出节点
        output_nodes = [nid for nid, node in genome.node_genes.items() 
                      if node.node_type in [NodeType.OUTPUT, NodeType.HIDDEN] 
                      and nid != neuron_id]
        
        # 创建输入连接
        for _ in range(min(num_inputs, len(input_nodes))):
            in_node = np.random.choice(input_nodes)
            innov = genome.get_innovation_number()
            conn = ConnectionGene(
                in_node=in_node,
                out_node=neuron_id,
                weight=np.random.uniform(-1, 1),
                enabled=True,
                innov_id=innov
            )
            genome.add_connection(conn)
        
        # 创建输出连接
        for _ in range(min(num_outputs, len(output_nodes))):
            out_node = np.random.choice(output_nodes)
            innov = genome.get_innovation_number()
            conn = ConnectionGene(
                in_node=neuron_id,
                out_node=out_node,
                weight=np.random.uniform(-1, 1),
                enabled=True,
                innov_id=innov
            )
            genome.add_connection(conn)

print("Neurogenesis Module Loaded Successfully!")
