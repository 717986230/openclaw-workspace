#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
突触可塑性 - Synaptic Plasticity
Hebbian学习和STDP实现
"""

import numpy as np
from typing import Dict, List, Tuple
from genetic_core import ConnectionGene

class SynapticPlasticity:
    """突触可塑性系统"""
    
    def __init__(self, learning_rate: float = 0.01, decay_rate: float = 0.001):
        self.learning_rate = learning_rate
        self.decay_rate = decay_rate
        self.pre_trace: Dict[int, List[float]] = {}
        self.post_trace: Dict[int, List[float]] = {}
        self.trace_window = 20
    
    def hebbian_update(self, conn: ConnectionGene, pre_activity: float, post_activity: float):
        """Hebbian学习：一起激发的神经元连接在一起"""
        delta = self.learning_rate * (pre_activity * post_activity - conn.hebbian_strength)
        conn.hebbian_strength += delta
        conn.hebbian_strength = np.clip(conn.hebbian_strength, 0, 1)
    
    def stdp_update(self, conn: ConnectionGene, pre_spike_time: float, post_spike_time: float):
        """STDP：脉冲时序依赖可塑性"""
        dt = post_spike_time - pre_spike_time
        
        if dt > 0:
            # 后突触先激发 -> 长时程增强（LTP）
            delta = self.learning_rate * np.exp(-dt / 20.0)
        else:
            # 前突触先激发 -> 长时程抑制（LTD）
            delta = -self.learning_rate * np.exp(dt / 20.0)
        
        conn.weight += delta
        conn.weight = np.clip(conn.weight, -8, 8)
    
    def update_trace(self, node_id: int, activity: float, is_pre: bool):
        """更新神经活动轨迹"""
        trace_dict = self.pre_trace if is_pre else self.post_trace
        
        if node_id not in trace_dict:
            trace_dict[node_id] = []
        
        trace_dict[node_id].append(activity)
        if len(trace_dict[node_id]) > self.trace_window:
            trace_dict[node_id].pop(0)
    
    def get_trace_correlation(self, pre_id: int, post_id: int) -> float:
        """计算前后突触轨迹相关性"""
        if pre_id not in self.pre_trace or post_id not in self.post_trace:
            return 0.0
        
        pre_trace = self.pre_trace[pre_id]
        post_trace = self.post_trace[post_id]
        
        min_len = min(len(pre_trace), len(post_trace))
        if min_len < 2:
            return 0.0
        
        pre_trace = pre_trace[-min_len:]
        post_trace = post_trace[-min_len:]
        
        correlation = np.corrcoef(pre_trace, post_trace)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    
    def consolidate_synapse(self, conn: ConnectionGene, correlation: float):
        """突触巩固"""
        if correlation > conn.consolidation_threshold:
            conn.synaptic_tag += 0.1
            conn.synaptic_tag = np.clip(conn.synaptic_tag, 0, 1)
        else:
            conn.synaptic_tag -= self.decay_rate
            conn.synaptic_tag = np.clip(conn.synaptic_tag, 0, 1)
    
    def apply_plasticity(self, connections: Dict[int, ConnectionGene], 
                        activities: Dict[int, float]):
        """应用可塑性到所有连接"""
        for conn in connections.values():
            if not conn.enabled:
                continue
            
            pre_act = activities.get(conn.in_node, 0)
            post_act = activities.get(conn.out_node, 0)
            
            # 更新轨迹
            self.update_trace(conn.in_node, pre_act, True)
            self.update_trace(conn.out_node, post_act, False)
            
            # Hebbian更新
            self.hebbian_update(conn, pre_act, post_act)
            
            # STDP更新（简化版）
            if pre_act > 0.5 and post_act > 0.5:
                self.stdp_update(conn, 0, 1)
            
            # 巩固
            correlation = self.get_trace_correlation(conn.in_node, conn.out_node)
            self.consolidate_synapse(conn, correlation)

print("Synaptic Plasticity Module Loaded Successfully!")
