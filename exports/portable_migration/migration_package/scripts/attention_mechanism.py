#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注意力机制 - Attention Mechanism
生物启发的选择性注意
"""

import numpy as np
from typing import Dict, List, Tuple
from genetic_core import NodeGene

class AttentionMechanism:
    """注意力机制"""
    
    def __init__(self, num_heads: int = 4, attention_window: int = 10):
        self.num_heads = num_heads
        self.attention_window = attention_window
        self.attention_weights: Dict[int, np.ndarray] = {}
        self.attention_history: Dict[int, List[float]] = {}
        self.saliency_map: Dict[int, float] = {}
    
    def compute_attention(self, query: np.ndarray, keys: np.ndarray, 
                        values: np.ndarray) -> np.ndarray:
        """计算注意力（简化版）"""
        # 计算相似度
        similarity = np.dot(query, keys.T)
        
        # Softmax归一化
        attention = np.exp(similarity) / np.sum(np.exp(similarity))
        
        # 加权求和
        output = np.dot(attention, values)
        
        return output
    
    def multi_head_attention(self, query: np.ndarray, keys: np.ndarray, 
                           values: np.ndarray) -> np.ndarray:
        """多头注意力"""
        outputs = []
        
        for _ in range(self.num_heads):
            # 随机投影（简化版）
            proj_q = query * np.random.randn(*query.shape)
            proj_k = keys * np.random.randn(*keys.shape)
            proj_v = values * np.random.randn(*values.shape)
            
            # 计算注意力
            output = self.compute_attention(proj_q, proj_k, proj_v)
            outputs.append(output)
        
        # 拼接所有头
        return np.concatenate(outputs)
    
    def update_saliency(self, node_id: int, activity: float):
        """更新显著性"""
        if node_id not in self.saliency_map:
            self.saliency_map[node_id] = 0.0
        
        # 指数移动平均
        self.saliency_map[node_id] = 0.9 * self.saliency_map[node_id] + 0.1 * activity
    
    def get_top_k_salient(self, k: int = 10) -> List[Tuple[int, float]]:
        """获取Top-K显著节点"""
        sorted_nodes = sorted(self.saliency_map.items(), 
                           key=lambda x: x[1], reverse=True)
        return sorted_nodes[:k]
    
    def selective_attention(self, node_activities: Dict[int, float], 
                          top_k: int = 5) -> Dict[int, float]:
        """选择性注意（只关注Top-K节点）"""
        # 获取Top-K节点
        top_nodes = self.get_top_k_salient(top_k)
        
        # 只保留Top-K节点的活动
        selected = {}
        for node_id, saliency in top_nodes:
            if node_id in node_activities:
                selected[node_id] = node_activities[node_id]
        
        return selected
    
    def spatial_attention(self, nodes: Dict[int, NodeGene], 
                        activities: Dict[int, float]) -> Dict[int, float]:
        """空间注意力（基于位置）"""
        if not nodes:
            return {}
        
        # 计算中心点
        x_coords = [node.x for node in nodes.values()]
        y_coords = [node.y for node in nodes.values()]
        center_x = np.mean(x_coords)
        center_y = np.mean(y_coords)
        
        # 计算距离权重
        weighted = {}
        for node_id, node in nodes.items():
            if node_id not in activities:
                continue
            
            distance = np.sqrt((node.x - center_x)**2 + (node.y - center_y)**2)
            weight = np.exp(-distance / 0.5)  # 高斯衰减
            
            weighted[node_id] = activities[node_id] * weight
        
        return weighted
    
    def temporal_attention(self, node_id: int, current_activity: float) -> float:
        """时间注意力（基于历史）"""
        if node_id not in self.attention_history:
            self.attention_history[node_id] = []
        
        history = self.attention_history[node_id]
        history.append(current_activity)
        
        if len(history) > self.attention_window:
            history.pop(0)
        
        # 计算时间权重（近期更重要）
        weights = np.exp(np.arange(len(history)) / len(history))
        weights = weights / np.sum(weights)
        
        weighted_activity = np.dot(weights, np.array(history))
        
        return weighted_activity
    
    def get_attention_statistics(self) -> Dict:
        """获取注意力统计"""
        if not self.saliency_map:
            return {
                'total_nodes': 0,
                'avg_saliency': 0.0,
                'max_saliency': 0.0
            }
        
        saliencies = list(self.saliency_map.values())
        return {
            'total_nodes': len(self.saliency_map),
            'avg_saliency': np.mean(saliencies),
            'max_saliency': np.max(saliencies)
        }

print("Attention Mechanism Module Loaded Successfully!")
