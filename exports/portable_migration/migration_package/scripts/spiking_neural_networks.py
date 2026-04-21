#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脉冲神经网络 - Spiking Neural Networks
生物真实的脉冲神经元模型
"""

import numpy as np
from typing import Dict, List, Tuple
from genetic_core import NodeGene, ConnectionGene

class SpikingNeuron:
    """脉冲神经元"""
    
    def __init__(self, node_id: int, threshold: float = 1.0, 
                 resting_potential: float = -70.0, 
                 reset_potential: float = -65.0):
        self.node_id = node_id
        self.threshold = threshold
        self.resting_potential = resting_potential
        self.reset_potential = reset_potential
        
        # 膜电位
        self.membrane_potential = resting_potential
        
        # 脉冲历史
        self.spike_times: List[float] = []
        self.last_spike_time = -1.0
        
        # 突触电流
        self.synaptic_current = 0.0
        
        # 膜时间常数
        self.tau_m = 10.0  # ms
        
        # 突触时间常数
        self.tau_s = 5.0   # ms
    
    def update(self, dt: float, input_current: float = 0.0) -> bool:
        """更新神经元状态"""
        # 更新膜电位
        dV = (-self.membrane_potential + self.resting_potential + 
              self.synaptic_current) / self.tau_m
        self.membrane_potential += dV * dt
        
        # 更新突触电流
        dI = -self.synaptic_current / self.tau_s
        self.synaptic_current += dI * dt
        self.synaptic_current += input_current
        
        # 检查是否达到阈值
        if self.membrane_potential >= self.threshold:
            self.spike()
            return True
        
        return False
    
    def spike(self):
        """发放脉冲"""
        self.spike_times.append(self.last_spike_time)
        self.membrane_potential = self.reset_potential
    
    def get_firing_rate(self, time_window: float = 100.0) -> float:
        """获取发放率"""
        if not self.spike_times:
            return 0.0
        
        recent_spikes = [t for t in self.spike_times 
                        if t >= self.last_spike_time - time_window]
        return len(recent_spikes) / time_window

class SpikingNeuralNetwork:
    """脉冲神经网络"""
    
    def __init__(self):
        self.neurons: Dict[int, SpikingNeuron] = {}
        self.connections: Dict[int, ConnectionGene] = {}
        self.time = 0.0
        self.dt = 1.0  # ms
    
    def add_neuron(self, neuron: SpikingNeuron):
        """添加神经元"""
        self.neurons[neuron.node_id] = neuron
    
    def add_connection(self, conn: ConnectionGene):
        """添加连接"""
        self.connections[conn.in_node * 1000 + conn.out_node] = conn
    
    def step(self, external_inputs: Dict[int, float] = None) -> Dict[int, bool]:
        """前进一步"""
        if external_inputs is None:
            external_inputs = {}
        
        spikes = {}
        
        # 更新所有神经元
        for neuron_id, neuron in self.neurons.items():
            # 计算输入电流
            input_current = 0.0
            
            # 外部输入
            if neuron_id in external_inputs:
                input_current += external_inputs[neuron_id]
            
            # 突触输入
            for conn in self.connections.values():
                if conn.out_node == neuron_id and conn.enabled:
                    pre_neuron = self.neurons.get(conn.in_node)
                    if pre_neuron and pre_neuron.last_spike_time == self.time - self.dt:
                        input_current += conn.weight
            
            # 更新神经元
            spiked = neuron.update(self.dt, input_current)
            spikes[neuron_id] = spiked
        
        self.time += self.dt
        return spikes
    
    def simulate(self, duration: float, 
                external_inputs: Dict[int, float] = None) -> List[Dict[int, bool]]:
        """模拟一段时间"""
        steps = int(duration / self.dt)
        spike_history = []
        
        for _ in range(steps):
            spikes = self.step(external_inputs)
            spike_history.append(spikes)
        
        return spike_history
    
    def get_spike_trains(self) -> Dict[int, List[float]]:
        """获取脉冲序列"""
        return {nid: neuron.spike_times for nid, neuron in self.neurons.items()}
    
    def get_firing_rates(self, time_window: float = 100.0) -> Dict[int, float]:
        """获取发放率"""
        return {nid: neuron.get_firing_rate(time_window) 
                for nid, neuron in self.neurons.items()}
    
    def reset(self):
        """重置网络"""
        self.time = 0.0
        for neuron in self.neurons.values():
            neuron.membrane_potential = neuron.resting_potential
            neuron.synaptic_current = 0.0
            neuron.spike_times = []
            neuron.last_spike_time = -1.0

class STDP:
    """脉冲时序依赖可塑性"""
    
    def __init__(self, learning_rate: float = 0.01, 
                 tau_plus: float = 20.0, tau_minus: float = 20.0):
        self.learning_rate = learning_rate
        self.tau_plus = tau_plus
        self.tau_minus = tau_minus
    
    def update_weight(self, conn: ConnectionGene, 
                     pre_spike_time: float, post_spike_time: float):
        """更新权重（STDP）"""
        dt = post_spike_time - pre_spike_time
        
        if dt > 0:
            # LTP（长时程增强）
            delta = self.learning_rate * np.exp(-dt / self.tau_plus)
        else:
            # LTD（长时程抑制）
            delta = -self.learning_rate * np.exp(dt / self.tau_minus)
        
        conn.weight += delta
        conn.weight = np.clip(conn.weight, -8, 8)

print("Spiking Neural Networks Module Loaded Successfully!")
