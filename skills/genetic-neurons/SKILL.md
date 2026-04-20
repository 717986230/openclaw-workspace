# Genetic Neurons Skill

基因神经元记忆系统 - 整合12个神经科学模块的完整记忆和学习系统。

## Description

完美顶配配置的基因神经元记忆系统，整合了基因突变、突触可塑性、神经发生、记忆巩固、注意力机制、神经调制、脉冲神经网络、结构可塑性、异构神经元、模块化、以及多种进化策略（CMA-ES、OpenAI-ES、质量多样性）。

## Triggers

- 用户请求基因神经元系统
- 用户提到"遗传算法"、"神经进化"、"记忆系统"
- 需要构建具有学习能力的神经网络
- 需要模拟生物神经系统的可塑性和记忆

## Capabilities

1. **基因表达** - 支持节点基因和连接基因
2. **突触可塑性** - Hebbian学习、STDP等
3. **神经发生** - 生长和修剪神经元
4. **记忆巩固** - 长期记忆增强
5. **注意力机制** - 选择性注意
6. **神经调制** - 多巴胺、血清素调节
7. **脉冲网络** - 时间编码的脉冲神经元
8. **结构可塑性** - 动态网络重组
9. **异构神经元** - 多种神经元类型
10. **模块化** - 功能模块检测
11. **进化优化** - CMA-ES/OpenAI-ES/QD

## Dependencies

- Python 3.8+
- NumPy
- 依赖模块：genetic_core, genetic_mutation, synaptic_plasticity, neurogenesis, memory_consolidation, attention_mechanism, neuromodulation, spiking_neural_networks, structural_plasticity, heterogeneous_neurons, modularity, evolution_strategies

## Components

- `GeneticNeuronMemorySystem` - 主系统类
- 整合12个独立模块

## Usage Example

```python
from genetic_neuron_memory_system import GeneticNeuronMemorySystem

system = GeneticNeuronMemorySystem(num_inputs=10, num_outputs=5)

# 激活系统
inputs = {i: 0.5 for i in range(10)}
outputs = system.activate(inputs)

# 学习
targets = {10: 1.0, 11: 0.5, 12: -0.5}
system.learn(inputs, targets)

# 进化
system.grow_neurons(3)
system.mutate()
system.reorganize_structure()

# 保存/加载
system.save_system("system.json")
system.load_system("system.json")
```
