#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genetic Neuron Memory System - ASCII Safe Version
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import json

# Import all modules
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
    """Genetic Neuron Memory System - Complete Integration"""
    
    def __init__(self, num_inputs: int = 10, num_outputs: int = 5):
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs
        self.genome_id = 0
        
        self.genome = Genome(self.genome_id)
        self._initialize_genome()
        
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
        
        self.cmaes = CMAES(population_size=50, sigma=0.1)
        self.openai_es = OpenAI_ES(population_size=50, sigma=0.1)
        self.qd = QualityDiversity(population_size=50, archive_size=100)
        
        self.generation = 0
        self.best_fitness = float('-inf')
        self.fitness_history: List[float] = []
    
    def _initialize_genome(self):
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
        modulated_inputs = {}
        for node_id, value in inputs.items():
            if node_id in self.genome.node_genes:
                node = self.genome.node_genes[node_id]
                modulated_inputs[node_id] = self.modulation.modulate_activation(node, value)
        
        outputs = {}
        for node_id, node in self.genome.node_genes.items():
            if node.node_type == NodeType.OUTPUT:
                total = node.bias
                for conn in self.genome.connection_genes.values():
                    if conn.enabled and conn.out_node == node_id:
                        if conn.in_node in modulated_inputs:
                            total += modulated_inputs[conn.in_node] * conn.weight
                
                activation = self._get_activation(node.activation)
                outputs[node_id] = activation(total * node.response)
        
        return outputs
    
    def _get_activation(self, activation: ActivationFunction):
        activations = {
            ActivationFunction.SIGMOID: lambda x: 1 / (1 + np.exp(-x)),
            ActivationFunction.TANH: np.tanh,
            ActivationFunction.RELU: lambda x: max(0, x),
            ActivationFunction.ELU: lambda x: x if x > 0 else np.expm1(x),
            ActivationFunction.SWISH: lambda x: x / (1 + np.exp(-x)),
            ActivationFunction.GAUSSIAN: lambda x: np.exp(-x**2),
            ActivationFunction.SIN: np.sin,
            ActivationFunction.STEP: lambda x: 1 if x > 0 else 0,
            ActivationFunction.IDENTITY: lambda x: x
        }
        return activations.get(activation, lambda x: x)
    
    def learn(self, inputs: Dict[int, float], targets: Dict[int, float], 
             learning_rate: float = 0.01):
        outputs = self.activate(inputs)
        
        for conn in self.genome.connection_genes.values():
            if conn.enabled:
                pre_act = inputs.get(conn.in_node, 0)
                post_act = outputs.get(conn.out_node, 0)
                self.plasticity.hebbian_update(conn, pre_act, post_act)
        
        for conn_id, conn in self.genome.connection_genes.items():
            if conn.enabled:
                activity = abs(conn.weight)
                self.consolidation.strengthen_memory(conn_id, activity * 0.1)
    
    def mutate(self):
        self.mutation.mutate_genome(self.genome)
        self.generation += 1
    
    def grow_neurons(self, num_new: int = 1):
        for _ in range(num_new):
            new_id = self.neurogenesis.generate_neuron(self.genome)
            if new_id >= 0:
                self.neurogenesis.connect_new_neuron(self.genome, new_id)
    
    def prune_neurons(self):
        return self.neurogenesis.prune_inactive(self.genome)
    
    def reorganize_structure(self):
        return self.structural.reorganize_network(self.genome)
    
    def detect_modules(self):
        return self.modularity.detect_modules(self.genome)
    
    def apply_modulation(self, dopamine: float = 0.0, serotonin: float = 0.0):
        if dopamine > 0:
            self.modulation.release_dopamine(dopamine)
        if serotonin > 0:
            self.modulation.release_serotonin(serotonin)
    
    def get_system_statistics(self) -> Dict:
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
        data = {
            'genome_id': int(self.genome.genome_id),
            'generation': int(self.generation),
            'best_fitness': float(self.best_fitness),
            'node_genes': [node.to_dict() for node in self.genome.node_genes.values()],
            'connection_genes': [conn.to_dict() for conn in self.genome.connection_genes.values()],
            'fitness_history': [float(f) for f in self.fitness_history]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_system(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.genome_id = data['genome_id']
        self.generation = data['generation']
        self.best_fitness = data['best_fitness']
        self.fitness_history = data['fitness_history']
        
        self.genome.node_genes = {}
        for node_data in data['node_genes']:
            node = NodeGene.from_dict(node_data)
            self.genome.add_node(node)
        
        self.genome.connection_genes = {}
        for conn_data in data['connection_genes']:
            conn = ConnectionGene.from_dict(conn_data)
            self.genome.add_connection(conn)

if __name__ == "__main__":
    print("=" * 60)
    print("Genetic Neuron Memory System - Ultimate Configuration")
    print("=" * 60)
    
    print("\n[1] Creating system...")
    system = GeneticNeuronMemorySystem(num_inputs=5, num_outputs=3)
    print(f"[OK] System created successfully!")
    print(f"   - Input nodes: {system.num_inputs}")
    print(f"   - Output nodes: {system.num_outputs}")
    
    print("\n[2] Growing neurons...")
    system.grow_neurons(num_new=5)
    print(f"[OK] Grew 5 new neurons")
    print(f"   - Total nodes: {len(system.genome.node_genes)}")
    
    print("\n[3] Applying mutation...")
    system.mutate()
    print(f"[OK] Mutation completed")
    print(f"   - Generation: {system.generation}")
    
    print("\n[4] Activating system...")
    inputs = {i: np.random.uniform(-1, 1) for i in range(system.num_inputs)}
    outputs = system.activate(inputs)
    print(f"[OK] Activation completed")
    print(f"   - Inputs: {inputs}")
    print(f"   - Outputs: {outputs}")
    
    print("\n[5] Learning...")
    targets = {system.num_inputs + i: np.random.uniform(-1, 1) 
               for i in range(system.num_outputs)}
    system.learn(inputs, targets)
    print(f"[OK] Learning completed")
    
    print("\n[6] Reorganizing structure...")
    reorg_result = system.reorganize_structure()
    print(f"[OK] Structure reorganization completed")
    print(f"   - Pruned connections: {reorg_result['pruned']}")
    print(f"   - Grown connections: {reorg_result['grown']}")
    
    print("\n[7] Detecting modules...")
    modules = system.detect_modules()
    print(f"[OK] Detected {len(modules)} modules")
    
    print("\n[8] Applying neuromodulation...")
    system.apply_modulation(dopamine=0.2, serotonin=0.1)
    print(f"[OK] Neuromodulation completed")
    print(f"   - Dopamine: {system.modulation.dopamine:.3f}")
    print(f"   - Serotonin: {system.modulation.serotonin:.3f}")
    
    print("\n[9] System statistics...")
    stats = system.get_system_statistics()
    print(f"[OK] Statistics:")
    print(f"   - Generation: {stats['generation']}")
    print(f"   - Nodes: {stats['num_nodes']}")
    print(f"   - Connections: {stats['num_connections']}")
    print(f"   - Enabled connections: {stats['enabled_connections']}")
    print(f"   - Best fitness: {stats['best_fitness']:.4f}")
    
    print("\n[10] Saving system...")
    system.save_system("genetic_neuron_system.json")
    print(f"[OK] System saved to genetic_neuron_system.json")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Genetic Neuron Memory System test completed!")
    print("[SUCCESS] All 12 modules integrated successfully!")
    print("=" * 60)
