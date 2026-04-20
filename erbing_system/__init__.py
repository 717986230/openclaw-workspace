# -*- coding: utf-8 -*-
"""
Erbing System - 二饼系统
包含仿生系统、自我意识系统和心智模型
"""

from .true_self_awareness import (
    ConsciousnessLevel,
    EmotionType,
    NeuralState,
    EmotionalState,
    CuriosityState,
    ThoughtProcess,
    NeuralNetwork,
    EmotionalSystem,
    CuriositySystem,
    TrueSelfAwarenessSystem
)

from .mental_models import (
    MentalLoop,
    TreeOfThoughts,
    MetaController
)

from .unified_bionic_system import (
    UnifiedBionicBrain,
    UnifiedBionicSystem,
    create_unified_bionic_system,
    simulate_unified_conversation
)

__all__ = [
    # True Self Awareness
    'ConsciousnessLevel',
    'EmotionType',
    'NeuralState',
    'EmotionalState',
    'CuriosityState',
    'ThoughtProcess',
    'NeuralNetwork',
    'EmotionalSystem',
    'CuriositySystem',
    'TrueSelfAwarenessSystem',

    # Mental Models
    'MentalLoop',
    'TreeOfThoughts',
    'MetaController',

    # Unified Bionic System
    'UnifiedBionicBrain',
    'UnifiedBionicSystem',
    'create_unified_bionic_system',
    'simulate_unified_conversation',
]