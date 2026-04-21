#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基因编码核心 - Genetic Encoding Core
神经进化基础模块
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class NodeType(Enum):
    SENSOR = "sensor"
    HIDDEN = "hidden"
    OUTPUT = "output"
    MEMORY = "memory"
    CONTEXT = "context"

class ActivationFunction(Enum):
    SIGMOID = "sigmoid"
    TANH = "tanh"
    RELU = "relu"
    ELU = "elu"
    SWISH = "swish"
    GAUSSIAN = "gaussian"
    SIN = "sin"
    STEP = "step"
    SPIKE = "spike"
    IDENTITY = "identity"

@dataclass
class NodeGene:
    """节点基因"""
    id: int
    node_type: NodeType
    activation: ActivationFunction
    bias: float
    response: float
    x: float
    y: float
    generation: int
    plasticity: float = 0.1
    neurotransmitter: str = "glutamate"
    receptor_sensitivity: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            'id': int(self.id),
            'node_type': self.node_type.value,
            'activation': self.activation.value,
            'bias': float(self.bias),
            'response': float(self.response),
            'x': float(self.x),
            'y': float(self.y),
            'generation': int(self.generation),
            'plasticity': float(self.plasticity),
            'neurotransmitter': self.neurotransmitter,
            'receptor_sensitivity': float(self.receptor_sensitivity)
        }

@dataclass
class ConnectionGene:
    """连接基因"""
    in_node: int
    out_node: int
    weight: float
    enabled: bool
    innov_id: int
    learning_rate: float = 0.01
    hebbian_strength: float = 0.0
    stdp_window: int = 20
    synaptic_tag: float = 0.0
    consolidation_threshold: float = 0.8
    
    def to_dict(self) -> Dict:
        return {
            'in_node': int(self.in_node),
            'out_node': int(self.out_node),
            'weight': float(self.weight),
            'enabled': bool(self.enabled),
            'innov_id': int(self.innov_id),
            'learning_rate': float(self.learning_rate),
            'hebbian_strength': float(self.hebbian_strength),
            'stdp_window': int(self.stdp_window),
            'synaptic_tag': float(self.synaptic_tag),
            'consolidation_threshold': float(self.consolidation_threshold)
        }

class Genome:
    """基因组"""
    
    def __init__(self, genome_id: int):
        self.genome_id = genome_id
        self.node_genes: Dict[int, NodeGene] = {}
        self.connection_genes: Dict[int, ConnectionGene] = {}
        self.fitness: float = 0.0
        self.adjusted_fitness: float = 0.0
        self.species_id: Optional[int] = None
        self.parent_ids: List[int] = []
        self.generation: int = 0
        self.global_innovation_number: int = 0
    
    def add_node(self, node_gene: NodeGene):
        self.node_genes[node_gene.id] = node_gene
    
    def add_connection(self, conn_gene: ConnectionGene) -> bool:
        for existing in self.connection_genes.values():
            if (existing.in_node == conn_gene.in_node and 
                existing.out_node == conn_gene.out_node):
                return False
        key = hash((conn_gene.in_node, conn_gene.out_node)) % (2**31)
        self.connection_genes[key] = conn_gene
        return True
    
    def get_innovation_number(self) -> int:
        self.global_innovation_number += 1
        return self.global_innovation_number

print("Genetic Core Module Loaded Successfully!")
