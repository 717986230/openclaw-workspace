"""
基因神经元记忆系统 - Genetic Neural Memory System

基于 Synaptic Memory, Moss, Synaptic Memory Bank 等顶级项目的借鉴实现
实现 Hebbian Learning, Memory Consolidation, Spreading Activation 等核心算法

作者: Erbing
创建时间: 2026-04-12
"""

__version__ = "1.0.0"
__author__ = "Erbing"

from .core import (
    GeneticMemorySystem,
    MemoryGene,
    Synapse,
    MemoryNeuron,
    HebbianEngine,
    ConsolidationEngine,
    SpreadingActivationEngine,
    SynapticWeightCalculator,
    GeneticEvolutionEngine,
)

from .database import (
    GeneticMemoryDatabase,
    setup_genetic_tables,
)

from .api import (
    GeneticMemoryAPI,
)

__all__ = [
    "GeneticMemorySystem",
    "MemoryGene",
    "Synapse",
    "MemoryNeuron",
    "HebbianEngine",
    "ConsolidationEngine",
    "SpreadingActivationEngine",
    "SynapticWeightCalculator",
    "GeneticEvolutionEngine",
    "GeneticMemoryDatabase",
    "setup_genetic_tables",
    "GeneticMemoryAPI",
]
