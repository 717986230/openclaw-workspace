#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆巩固 - Memory Consolidation
长时程增强和记忆稳定化
"""

import numpy as np
from typing import Dict, List, Tuple
from genetic_core import ConnectionGene

class MemoryConsolidation:
    """记忆巩固系统"""
    
    def __init__(self, consolidation_rate: float = 0.01, decay_rate: float = 0.001):
        self.consolidation_rate = consolidation_rate
        self.decay_rate = decay_rate
        self.memory_strength: Dict[int, float] = {}
        self.replay_buffer: List[Tuple[int, int, float]] = []
        self.max_replay_size = 1000
    
    def strengthen_memory(self, conn_id: int, amount: float = 0.1):
        """增强记忆"""
        if conn_id not in self.memory_strength:
            self.memory_strength[conn_id] = 0.0
        
        self.memory_strength[conn_id] += amount
        self.memory_strength[conn_id] = np.clip(self.memory_strength[conn_id], 0, 1)
    
    def weaken_memory(self, conn_id: int, amount: float = 0.05):
        """减弱记忆"""
        if conn_id not in self.memory_strength:
            self.memory_strength[conn_id] = 0.0
        
        self.memory_strength[conn_id] -= amount
        self.memory_strength[conn_id] = np.clip(self.memory_strength[conn_id], 0, 1)
    
    def add_replay(self, in_node: int, out_node: int, activity: float):
        """添加回放样本"""
        self.replay_buffer.append((in_node, out_node, activity))
        if len(self.replay_buffer) > self.max_replay_size:
            self.replay_buffer.pop(0)
    
    def replay_memory(self, connections: Dict[int, ConnectionGene]):
        """记忆回放（巩固）"""
        if not self.replay_buffer:
            return
        
        # 随机采样回放
        sample_size = min(10, len(self.replay_buffer))
        samples = np.random.choice(len(self.replay_buffer), sample_size, replace=False)
        
        for idx in samples:
            in_node, out_node, activity = self.replay_buffer[idx]
            
            # 找到对应连接
            for conn_id, conn in connections.items():
                if conn.in_node == in_node and conn.out_node == out_node:
                    # 根据活动强度调整权重
                    delta = self.consolidation_rate * activity
                    conn.weight += delta
                    conn.weight = np.clip(conn.weight, -8, 8)
                    
                    # 增强记忆强度
                    self.strengthen_memory(conn_id, delta)
                    break
    
    def decay_memory(self, connections: Dict[int, ConnectionGene]):
        """记忆衰减"""
        for conn_id, conn in connections.items():
            if conn_id in self.memory_strength:
                # 记忆强度衰减
                self.memory_strength[conn_id] -= self.decay_rate
                self.memory_strength[conn_id] = np.clip(self.memory_strength[conn_id], 0, 1)
                
                # 根据记忆强度调整权重
                if self.memory_strength[conn_id] < 0.3:
                    conn.weight *= 0.99
                    conn.weight = np.clip(conn.weight, -8, 8)
    
    def get_consolidated_connections(self, connections: Dict[int, ConnectionGene], 
                                    threshold: float = 0.7) -> List[int]:
        """获取已巩固的连接"""
        consolidated = []
        for conn_id, conn in connections.items():
            if conn_id in self.memory_strength:
                if self.memory_strength[conn_id] >= threshold:
                    consolidated.append(conn_id)
        return consolidated
    
    def get_weak_connections(self, connections: Dict[int, ConnectionGene], 
                           threshold: float = 0.2) -> List[int]:
        """获取弱连接"""
        weak = []
        for conn_id, conn in connections.items():
            if conn_id in self.memory_strength:
                if self.memory_strength[conn_id] < threshold:
                    weak.append(conn_id)
        return weak
    
    def sleep_consolidation(self, connections: Dict[int, ConnectionGene], 
                          sleep_cycles: int = 5):
        """睡眠巩固（模拟睡眠时的记忆巩固）"""
        for _ in range(sleep_cycles):
            # 回放重要记忆
            self.replay_memory(connections)
            
            # 衰减弱记忆
            self.decay_memory(connections)
    
    def get_memory_statistics(self) -> Dict:
        """获取记忆统计"""
        if not self.memory_strength:
            return {
                'total_memories': 0,
                'avg_strength': 0.0,
                'strong_memories': 0,
                'weak_memories': 0
            }
        
        strengths = list(self.memory_strength.values())
        return {
            'total_memories': len(self.memory_strength),
            'avg_strength': np.mean(strengths),
            'strong_memories': sum(1 for s in strengths if s > 0.7),
            'weak_memories': sum(1 for s in strengths if s < 0.3)
        }

print("Memory Consolidation Module Loaded Successfully!")
