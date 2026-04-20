# Neuroevolution Skill

神经进化技能 - 支持拓扑和权重同时进化的神经进化系统，灵感来源于NEAT。

## Description

提供多种进化策略（NEAT、HyperNEAT、CMA-ES、OpenAI-ES、NSGA2等），支持物种形成、创新号追踪、多种激活函数，以及完整的神经进化训练流程。

## Triggers

- 用户请求神经进化训练
- 用户提到"NEAT"、"神经进化"、"进化神经网络"
- 需要同时优化网络拓扑和权重
- 需要多目标进化或质量多样性搜索

## Capabilities

1. **拓扑进化** - 自动发现网络结构
2. **权重进化** - 同时优化连接权重
3. **物种形成** - 维护种群多样性
4. **多种策略** - NEAT/HyperNEAT/CMA-ES/OpenAI-ES/NSGA2/QD
5. **多种激活函数** - Sigmoid/Tanh/ReLU/Swish/Gaussian等
6. **并行计算** - 支持多进程评估

## Dependencies

- Python 3.8+
- PyTorch >= 1.9
- NumPy

## Components

- `EvolutionStrategy` - 进化策略枚举
- `Species` - 物种数据类
- `NeuralNetwork` - 表现型神经网络
- `NeuroevolutionTrainer` - 主训练器

## Usage Example

```python
from neuroevolution import NeuroevolutionTrainer, EvolutionStrategy

trainer = NeuroevolutionTrainer(
    num_inputs=10,
    num_outputs=5,
    population_size=150,
    strategy=EvolutionStrategy.NEAT
)
trainer.create_initial_population()
# 运行进化...
```
