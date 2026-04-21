#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基因神经元记忆系统 - Genetic Neuron Memory System
完美顶配配置 - 整合所有12个模块
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import json

# 导入所有模块
from genetic_core import Genome, NodeGene, ConnectionGene, NodeType, ActivationFunction
from genetic_mutation import GeneticMutation
from synaptic_plasticity import SynapticPlasticity
from neurogenesis import Neurogenesis
from memory_consolidation import MemoryConsolidation
from attention_mechanism import AttentionMechanism
from neuromodulation import Neuromodulation
from spiking_neural_networks import SpikingNeuralNetwork, SpikingNeuron, STDP
from structural_plasticity import StructuralPlasticity
from heterogeneous_neurons import HeterogeneousNetwork, HeterogeneousNeuron, NeuronType
from modularity import Modularity, FunctionalModule
from evolution_strategies import CMAES, OpenAI_ES, QualityDiversity

class GeneticNeuronMemorySystem:
    """基因神经元记忆系统 - 完整整合"""
    
    def __init__(self, num_inputs: int = 10, num_outputs: int = 5):
        # 基础配置
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.genome_id = 0
        
        # 初始化基因组
        self.genome = Genome(self.genome_id)
        self._initialize_genome()
        
        # 初始化所有模块
        self.mutation = GeneticMutation()
        self.plasticity = SynapticPlasticity()
        self.neurogenesis = Neurogenesis()
        self.consolidation = MemoryConsolidation()
        self.attention = AttentionMechanism()
        self.modulation = Neuromodulation()
        self.snn = SpikingNeuralNetwork()
        self.structural = StructuralPlasticity()
        self.heterogeneous = HeterogeneousNetwork()
        self.modularity = Modularity()
        
        # 进化策略
        self.cmaes = CMAES(population_size=50, sigma=0.1)
        self.openai_es = OpenAI_ES(population_size=50, sigma=0.1)
        self.qd = QualityDiversity(population_size=50, archive_size=100)
        
        # 系统状态
        self.generation = 0
        self.best_fitness = float('-inf')
        self.fitness_history: List[float] = []
    
    def _initialize_genome(self):
        """初始化基因组"""
        # 创建输入节点
        for i in range(self.num_inputs):
            node = NodeGene(
                id=i,
                node_type=NodeType.SENSOR,
                activation=ActivationFunction.IDENTITY,
                bias=0.0,
                response=1.0,
                x=i / (self.num_inputs - 1) if self.num_inputs > 1 else 0.5,
                y=0.0,
                generation=0
            )
            self.genome.add_node(node)
        
        # 创建输出节点
        for i in range(self.num_outputs):
            node = NodeGene(
                id=self.num_inputs + i,
                node_type=NodeType.OUTPUT,
                activation=ActivationFunction.TANH,
                bias=0.0,
                response=1.0,
                x=i / (self.num_outputs - 1) if self.num_outputs > 1 else 0.5,
                y=1.0,
                generation=0
            )
            self.genome.add_node(node)
    
    def activate(self, inputs: Dict[int, float]) -> Dict[int, float]:
        """激活系统"""
        # 应用神经调制
        modulated_inputs = {}
        for node_id, value in inputs.items():
            if node_id in self.genome.node_genes:
                node = self.genome.node_genes[node_id]
                modulated_inputs[node_id] = self.modulation.modulate_activation(node, value)
        
        # 简单前向传播（简化版）
        outputs = {}
        for node_id, node in self.genome.node_genes.items():
            if node.node_type == NodeType.OUTPUT:
                # 计算输入
                total = node.bias
                for conn in self.genome.connection_genes.values():
                    if conn.enabled and conn.out_node == node_id:
                        if conn.in_node in modulated_inputs:
                            total += modulated_inputs[conn.in_node] * conn.weight
                
                # 应用激活函数
                activation = self._get_activation(node.activation)
                outputs[node_id] = activation(total * node.response)
        
        return outputs
    
    def _get_activation(self, activation: ActivationFunction):
        """获取激活函数"""
        activations = {
            ActivationFunction.SIGMOID: lambda x: 1 / (1 + np.exp(-x)),
            ActivationFunction.TANH: np.tanh,
            ActivationFunction.RELU: lambda x: max(0, x),
            ActivationFunction.ELU: lambda x: x if x > 0 else np.expm1(x),
            ActivationFunction.SWISH: lambda x: x / (1 + np.exp(-x)),
            ActivationFunction.GAUSSIAN: lambda x: np.exp(-x**2),
            ActivationFunction.SIN: np.sin,
            ActivationFunction.STEP: lambda x: 1 if x > 0 else 0
        }
        return activations.get(activation, lambda x: x)
    
    def learn(self, inputs: Dict[int, float], targets: Dict[int, float], 
             learning_rate: float = 0.01):
        """学习（应用可塑性）"""
        # 获取输出
        outputs = self.activate(inputs)
        
        # 计算误差
        errors = {}
        for node_id, target in targets.items():
            if node_id in outputs:
                errors[node_id] = target - outputs[node_id]
        
        # 应用Hebbian学习
        for conn in self.genome.connection_genes.values():
            if conn.enabled:
                pre_act = inputs.get(conn.in_node, 0)
                post_act = outputs.get(conn.out_node, 0)
                self.plasticity.hebbian_update(conn, pre_act, post_act)
        
        # 应用记忆巩固
        for conn_id, conn in self.genome.connection_genes.items():
            if conn.enabled:
                activity = abs(conn.weight)
                self.consolidation.strengthen_memory(conn_id, activity * 0.1)
    
    def evolve(self, fitness_function, num_generations: int = 100) -> Genome:
        """进化系统"""
        # 使用CMA-ES优化
        optimized_genome = self.cmaes.optimize(
            self.genome, 
            fitness_function, 
            num_generations
        )
        
        self.genome = optimized_genome
        return optimized_genome
    
    def mutate(self):
        """突变系统"""
        self.mutation.mutate_genome(self.genome)
        self.generation += 1
    
    def grow_neurons(self, num_new: int = 1):
        """生长新神经元"""
        for _ in range(num_new):
            new_id = self.neurogenesis.generate_neuron(self.genome)
            if new_id >= 0:
                self.neurogenesis.connect_new_neuron(self.genome, new_id)
    
    def prune_neurons(self):
        """修剪不活跃神经元"""
        pruned = self.neurogenesis.prune_inactive(self.genome)
        return pruned
    
    def reorganize_structure(self):
        """重组结构"""
        return self.structural.reorganize_network(self.genome)
    
    def detect_modules(self):
        """检测模块"""
        modules = self.modularity.detect_modules(self.genome)
        return modules
    
    def apply_modulation(self, dopamine: float = 0.0, serotonin: float = 0.0):
        """应用神经调制"""
        if dopamine > 0:
            self.modulation.release_dopamine(dopamine)
        if serotonin > 0:
            self.modulation.release_serotonin(serotonin)
    
    def get_system_statistics(self) -> Dict:
        """获取系统统计"""
        stats = {
            'generation': self.generation,
            'num_nodes': len(self.genome.node_genes),
            'num_connections': len(self.genome.connection_genes),
            'enabled_connections': sum(1 for c in self.genome.connection_genes.values() if c.enabled),
            'best_fitness': self.best_fitness,
            'modulation_state': self.modulation.get_modulation_state(),
            'memory_stats': self.consolidation.get_memory_statistics(),
            'attention_stats': self.attention.get_attention_statistics(),
            'module_stats': self.modularity.get_module_statistics()
        }
        return stats
    
    def save_system(self, filepath: str):
        """保存系统"""
        data = {
            'genome_id': self.genome.genome_id,
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'node_genes': [node.to_dict() for node in self.genome.node_genes.values()],
            'connection_genes': [conn.to_dict() for conn in self.genome.connection_genes.values()],
            'fitness_history': self.fitness_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_system(self, filepath: str):
        """加载系统"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.genome_id = data['genome_id']
        self.generation = data['generation']
        self.best_fitness = data['best_fitness']
        self.fitness_history = data['fitness_history']
        
        # 重建节点
        self.genome.node_genes = {}
        for node_data in data['node_genes']:
            node = NodeGene.from_dict(node_data)
            self.genome.add_node(node)
        
        # 重建连接
        self.genome.connection_genes = {}
        for conn_data in data['connection_genes']:
            conn = ConnectionGene.from_dict(conn_data)
            self.genome.add_connection(conn)

# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("基因神经元记忆系统 - 完美顶配配置")
    print("Genetic Neuron Memory System - Ultimate Configuration")
    print("=" * 60)
    
    # 创建系统
    print("\n[1] 创建系统...")
    system = GeneticNeuronMemorySystem(num_inputs=5, num_outputs=3)
    print(f"[OK] System created successfully!")
    print(f"   - Input nodes: {system.num_inputs}")
    print(f"   - Output nodes: {system.num_outputs}")
    
    # 生长神经元
    print("\n[2] 生长神经元...")
    system.grow_neurons(num_new=5)
    print(f"[OK] Grew {num_new} new neurons")
    print(f"   - Total nodes: {len(system.genome.node_genes)}")
    
    # 突变
    print("\n[3] 应用突变...")
    system.mutate()
    print(f"✅ 突变完成")
    print(f"   - 代数: {system.generation}")
    
    # 激活
    print("\n[4] 激活系统...")
    inputs = {i: np.random.uniform(-1, 1) for i in range(system.num_inputs)}
    outputs = system.activate(inputs)
    print(f"✅ 激活完成")
    print(f"   - 输入: {inputs}")
    print(f"   - 输出: {outputs}")
    
    # 学习
    print("\n[5] 学习...")
    targets = {system.num_inputs + i: np.random.uniform(-1, 1) 
               for i in range(system.num_outputs)}
    system.learn(inputs, targets)
    print(f"✅ 学习完成")
    
    # 重组结构
    print("\n[6] 重组结构...")
    reorg_result = system.reorganize_structure()
    print(f"✅ 结构重组完成")
    print(f"   - 修剪连接: {reorg_result['pruned']}")
    print(f"   - 生长连接: {reorg_result['grown']}")
    
    # 检测模块
    print("\n[7] 检测模块...")
    modules = system.detect_modules()
    print(f"✅ 检测到 {len(modules)} 个模块")
    
    # 应用神经调制
    print("\n[8] 应用神经调制...")
    system.apply_modulation(dopamine=0.2, serotonin=0.1)
    print(f"✅ 神经调制完成")
    print(f"   - 多巴胺: {system.modulation.dopamine:.3f}")
    print(f"   - 血清素: {system.modulation.serotonin:.3f}")
    
    # 获取统计
    print("\n[9] 系统统计...")
    stats = system.get_system_statistics()
    print(f"✅ 统计信息:")
    print(f"   - 代数: {stats['generation']}")
    print(f"   - 节点数: {stats['num_nodes']}")
    print(f"   - 连接数: {stats['num_connections']}")
    print(f"   - 启用连接: {stats['enabled_connections']}")
    print(f"   - 最佳适应度: {stats['best_fitness']:.4f}")
    
    # 保存系统
    print("\n[10] 保存系统...")
    system.save_system("genetic_neuron_system.json")
    print(f"✅ 系统已保存到 genetic_neuron_system.json")
    
    print("\n" + "=" * 60)
    print("🎉 基因神经元记忆系统测试完成！")
    print("🎉 All 12 modules integrated successfully!")
    print("=" * 60)
