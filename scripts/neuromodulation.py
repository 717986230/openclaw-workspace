#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神经调制 - Neuromodulation
神经调质和全局状态控制
"""

import numpy as np
from typing import Dict, List
from genetic_core import ConnectionGene, NodeGene

class Neuromodulation:
    """神经调制系统"""
    
    def __init__(self):
        # 神经调质水平
        self.dopamine = 0.5      # 多巴胺（奖励/动机）
        self.serotonin = 0.5     # 血清素（情绪/睡眠）
        self.norepinephrine = 0.5 # 去甲肾上腺素（注意力/唤醒）
        self.acetylcholine = 0.5  # 乙酰胆碱（学习/记忆）
        self.gaba = 0.5          # GABA（抑制）
        self.glutamate = 0.5      # 谷氨酸（兴奋）
        
        # 调质受体
        self.receptors: Dict[str, float] = {
            'd1': 1.0, 'd2': 1.0,  # 多巴胺受体
            '5ht1a': 1.0, '5ht2a': 1.0,  # 血清素受体
            'alpha1': 1.0, 'beta': 1.0,  # 肾上腺素受体
            'muscarinic': 1.0, 'nicotinic': 1.0  # 乙酰胆碱受体
        }
        
        # 调质历史
        self.modulation_history: Dict[str, List[float]] = {
            'dopamine': [],
            'serotonin': [],
            'norepinephrine': [],
            'acetylcholine': []
        }
    
    def release_dopamine(self, amount: float = 0.1):
        """释放多巴胺（奖励信号）"""
        self.dopamine += amount
        self.dopamine = np.clip(self.dopamine, 0, 1)
        self._update_history('dopamine')
    
    def release_serotonin(self, amount: float = 0.1):
        """释放血清素（情绪调节）"""
        self.serotonin += amount
        self.serotonin = np.clip(self.serotonin, 0, 1)
        self._update_history('serotonin')
    
    def release_norepinephrine(self, amount: float = 0.1):
        """释放去甲肾上腺素（注意力增强）"""
        self.norepinephrine += amount
        self.norepinephrine = np.clip(self.norepinephrine, 0, 1)
        self._update_history('norepinephrine')
    
    def release_acetylcholine(self, amount: float = 0.1):
        """释放乙酰胆碱（学习增强）"""
        self.acetylcholine += amount
        self.acetylcholine = np.clip(self.acetylcholine, 0, 1)
        self._update_history('acetylcholine')
    
    def modulate_learning_rate(self, base_rate: float) -> float:
        """调制学习率"""
        # 多巴胺增强学习
        dopamine_factor = 1.0 + self.dopamine * 0.5
        
        # 乙酰胆碱增强学习
        ach_factor = 1.0 + self.acetylcholine * 0.3
        
        modulated_rate = base_rate * dopamine_factor * ach_factor
        return np.clip(modulated_rate, 0, 1)
    
    def modulate_plasticity(self, base_plasticity: float) -> float:
        """调制可塑性"""
        # 乙酰胆碱增强可塑性
        ach_factor = 1.0 + self.acetylcholine * 0.5
        
        # 血清素调节可塑性
        serotonin_factor = 1.0 + (self.serotonin - 0.5) * 0.3
        
        modulated_plasticity = base_plasticity * ach_factor * serotonin_factor
        return np.clip(modulated_plasticity, 0, 1)
    
    def modulate_activation(self, node: NodeGene, base_activation: float) -> float:
        """调制激活"""
        # 去甲肾上腺素增强激活
        ne_factor = 1.0 + self.norepinephrine * 0.3
        
        # GABA抑制激活
        gaba_factor = 1.0 - self.gaba * 0.3
        
        modulated_activation = base_activation * ne_factor * gaba_factor
        return np.clip(modulated_activation, 0, 1)
    
    def modulate_weight(self, conn: ConnectionGene, base_weight: float) -> float:
        """调制权重"""
        # 多巴胺增强权重
        dopamine_factor = 1.0 + self.dopamine * 0.2
        
        # 谷氨酸增强权重
        glutamate_factor = 1.0 + self.glutamate * 0.2
        
        modulated_weight = base_weight * dopamine_factor * glutamate_factor
        return np.clip(modulated_weight, -8, 8)
    
    def decay_modulators(self, decay_rate: float = 0.01):
        """调质衰减"""
        self.dopamine -= decay_rate
        self.serotonin -= decay_rate
        self.norepinephrine -= decay_rate
        self.acetylcholine -= decay_rate
        
        self.dopamine = np.clip(self.dopamine, 0, 1)
        self.serotonin = np.clip(self.serotonin, 0, 1)
        self.norepinephrine = np.clip(self.norepinephrine, 0, 1)
        self.acetylcholine = np.clip(self.acetylcholine, 0, 1)
    
    def _update_history(self, modulator: str):
        """更新调质历史"""
        if modulator not in self.modulation_history:
            self.modulation_history[modulator] = []
        
        value = getattr(self, modulator)
        self.modulation_history[modulator].append(value)
        
        if len(self.modulation_history[modulator]) > 100:
            self.modulation_history[modulator].pop(0)
    
    def get_modulation_state(self) -> Dict:
        """获取调制状态"""
        return {
            'dopamine': self.dopamine,
            'serotonin': self.serotonin,
            'norepinephrine': self.norepinephrine,
            'acetylcholine': self.acetylcholine,
            'gaba': self.gaba,
            'glutamate': self.glutamate
        }
    
    def reset_modulators(self):
        """重置调质水平"""
        self.dopamine = 0.5
        self.serotonin = 0.5
        self.norepinephrine = 0.5
        self.acetylcholine = 0.5
        self.gaba = 0.5
        self.glutamate = 0.5

print("Neuromodulation Module Loaded Successfully!")
