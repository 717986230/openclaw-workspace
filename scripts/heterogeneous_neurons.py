#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异质神经元 - Heterogeneous Neurons
多种神经元类型和特性
"""

import numpy as np
from typing import Dict, List, Optional
from enum import Enum
from genetic_core import NodeGene, NodeType, ActivationFunction

class NeuronType(Enum):
    """神经元类型"""
    EXCITATORY = "excitatory"      # 兴奋性神经元
    INHIBITORY = "inhibitory"      # 抑制性神经元
    MODULATORY = "modulatory"      # 调制性神经元
    SENSORY = "sensory"            # 感觉神经元
    MOTOR = "motor"                # 运动神经元
    INTERNEURON = "interneuron"    # 中间神经元
    PYRAMIDAL = "pyramidal"        # 锥体神经元
    GRANULE = "granule"            # 颗粒细胞
    PURKINJE = "purkinje"          # 浦肯野细胞
    GOLGI = "golgi"                # 高尔基细胞

class HeterogeneousNeuron:
    """异质神经元"""
    
    def __init__(self, node_gene: NodeGene, neuron_type: NeuronType):
        self.node_gene = node_gene
        self.neuron_type = neuron_type
        
        # 神经元特性
        self.threshold = self._get_default_threshold()
        self.resting_potential = self._get_default_resting_potential()
        self.time_constant = self._get_default_time_constant()
        
        # 神经递质
        self.neurotransmitter = self._get_default_neurotransmitter()
        
        # 受体
        self.receptors = self._get_default_receptors()
        
        # 活动历史
        self.activity_history: List[float] = []
        self.max_history = 100
    
    def _get_default_threshold(self) -> float:
        """获取默认阈值"""
        thresholds = {
            NeuronType.EXCITATORY: 1.0,
            NeuronType.INHIBITORY: 0.8,
            NeuronType.MODULATORY: 0.6,
            NeuronType.SENSORY: 0.5,
            NeuronType.MOTOR: 1.2,
            NeuronType.INTERNEURON: 0.9,
            NeuronType.PYRAMIDAL: 1.0,
            NeuronType.GRANULE: 0.7,
            NeuronType.PURKINJE: 0.8,
            NeuronType.GOLGI: 0.9
        }
        return thresholds.get(self.neuron_type, 1.0)
    
    def _get_default_resting_potential(self) -> float:
        """获取默认静息电位"""
        potentials = {
            NeuronType.EXCITATORY: -70.0,
            NeuronType.INHIBITORY: -65.0,
            NeuronType.MODULATORY: -60.0,
            NeuronType.SENSORY: -65.0,
            NeuronType.MOTOR: -70.0,
            NeuronType.INTERNEURON: -68.0,
            NeuronType.PYRAMIDAL: -70.0,
            NeuronType.GRANULE: -75.0,
            NeuronType.PURKINJE: -65.0,
            NeuronType.GOLGI: -68.0
        }
        return potentials.get(self.neuron_type, -70.0)
    
    def _get_default_time_constant(self) -> float:
        """获取默认时间常数"""
        constants = {
            NeuronType.EXCITATORY: 10.0,
            NeuronType.INHIBITORY: 8.0,
            NeuronType.MODULATORY: 15.0,
            NeuronType.SENSORY: 5.0,
            NeuronType.MOTOR: 12.0,
            NeuronType.INTERNEURON: 7.0,
            NeuronType.PYRAMIDAL: 10.0,
            NeuronType.GRANULE: 6.0,
            NeuronType.PURKINJE: 9.0,
            NeuronType.GOLGI: 8.0
        }
        return constants.get(self.neuron_type, 10.0)
    
    def _get_default_neurotransmitter(self) -> str:
        """获取默认神经递质"""
        transmitters = {
            NeuronType.EXCITATORY: "glutamate",
            NeuronType.INHIBITORY: "gaba",
            NeuronType.MODULATORY: "dopamine",
            NeuronType.SENSORY: "glutamate",
            NeuronType.MOTOR: "acetylcholine",
            NeuronType.INTERNEURON: "gaba",
            NeuronType.PYRAMIDAL: "glutamate",
            NeuronType.GRANULE: "glutamate",
            NeuronType.PURKINJE: "gaba",
            NeuronType.GOLGI: "gaba"
        }
        return transmitters.get(self.neuron_type, "glutamate")
    
    def _get_default_receptors(self) -> List[str]:
        """获取默认受体"""
        receptors = {
            NeuronType.EXCITATORY: ["AMPA", "NMDA"],
            NeuronType.INHIBITORY: ["GABA_A", "GABA_B"],
            NeuronType.MODULATORY: ["D1", "D2"],
            NeuronType.SENSORY: ["AMPA"],
            NeuronType.MOTOR: ["nicotinic"],
            NeuronType.INTERNEURON: ["GABA_A"],
            NeuronType.PYRAMIDAL: ["AMPA", "NMDA"],
            NeuronType.GRANULE: ["AMPA"],
            NeuronType.PURKINJE: ["GABA_A"],
            NeuronType.GOLGI: ["GABA_A"]
        }
        return receptors.get(self.neuron_type, ["AMPA"])
    
    def compute_output(self, inputs: List[float]) -> float:
        """计算输出"""
        # 加权求和
        total = sum(inputs) + self.node_gene.bias
        
        # 应用激活函数
        activation = self._get_activation_function()
        output = activation(total * self.node_gene.response)
        
        # 记录活动
        self.activity_history.append(output)
        if len(self.activity_history) > self.max_history:
            self.activity_history.pop(0)
        
        return output
    
    def _get_activation_function(self):
        """获取激活函数"""
        activations = {
            ActivationFunction.SIGMOID: lambda x: 1 / (1 + np.exp(-x)),
            ActivationFunction.TANH: np.tanh,
            ActivationFunction.RELU: lambda x: max(0, x),
            ActivationFunction.ELU: lambda x: x if x > 0 else np.expm1(x),
            ActivationFunction.SWISH: lambda x: x / (1 + np.exp(-x)),
            ActivationFunction.GAUSSIAN: lambda x: np.exp(-x**2),
            ActivationFunction.SIN: np.sin,
            ActivationFunction.STEP: lambda x: 1 if x > 0 else 0,
            ActivationFunction.SPIKE: lambda x: 1 if x > self.threshold else 0
        }
        return activations.get(self.node_gene.activation, lambda x: x)
    
    def get_activity_statistics(self) -> Dict:
        """获取活动统计"""
        if not self.activity_history:
            return {
                'mean': 0.0,
                'std': 0.0,
                'max': 0.0,
                'min': 0.0
            }
        
        return {
            'mean': np.mean(self.activity_history),
            'std': np.std(self.activity_history),
            'max': np.max(self.activity_history),
            'min': np.min(self.activity_history)
        }

class HeterogeneousNetwork:
    """异质网络"""
    
    def __init__(self):
        self.neurons: Dict[int, HeterogeneousNeuron] = {}
        self.neuron_types: Dict[int, NeuronType] = {}
    
    def add_neuron(self, node_gene: NodeGene, neuron_type: NeuronType):
        """添加神经元"""
        neuron = HeterogeneousNeuron(node_gene, neuron_type)
        self.neurons[node_gene.id] = neuron
        self.neuron_types[node_gene.id] = neuron_type
    
    def get_neuron_type(self, node_id: int) -> Optional[NeuronType]:
        """获取神经元类型"""
        return self.neuron_types.get(node_id)
    
    def get_excitatory_neurons(self) -> List[int]:
        """获取兴奋性神经元"""
        return [nid for nid, ntype in self.neuron_types.items() 
                if ntype == NeuronType.EXCITATORY]
    
    def get_inhibitory_neurons(self) -> List[int]:
        """获取抑制性神经元"""
        return [nid for nid, ntype in self.neuron_types.items() 
                if ntype == NeuronType.INHIBITORY]
    
    def get_network_statistics(self) -> Dict:
        """获取网络统计"""
        type_counts = {}
        for ntype in self.neuron_types.values():
            type_counts[ntype.value] = type_counts.get(ntype.value, 0) + 1
        
        return {
            'total_neurons': len(self.neurons),
            'type_distribution': type_counts,
            'excitatory_ratio': len(self.get_excitatory_neurons()) / len(self.neurons) if self.neurons else 0,
            'inhibitory_ratio': len(self.get_inhibitory_neurons()) / len(self.neurons) if self.neurons else 0
        }

print("Heterogeneous Neurons Module Loaded Successfully!")
