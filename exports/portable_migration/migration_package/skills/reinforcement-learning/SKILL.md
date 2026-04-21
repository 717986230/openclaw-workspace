# Reinforcement Learning Skill

强化学习训练技能 - 基于GRPO（Group Relative Policy Optimization）技术的强化学习训练系统。

## Description

提供完整的强化学习训练框架，支持GRPO、PPO等优化器，包含策略网络、价值网络和奖励模型，支持训练、评估和模型保存/加载。

## Triggers

- 用户请求强化学习训练
- 用户提到"RL"、"GRPO"、"PPO"、"策略梯度"
- 需要训练agent或进行策略优化
- 需要实现奖励模型学习

## Capabilities

1. **策略优化** - 支持GRPO/PPO等优化算法
2. **策略网络** - 可配置的策略网络实现
3. **价值网络** - 用于优势函数估计的价值网络
4. **奖励模型** - 可训练的奖励模型
5. **GAE优势估计** - 广义优势估计计算
6. **模型持久化** - 支持模型保存和加载

## Dependencies

- Python 3.8+
- PyTorch >= 1.9
- NumPy

## Components

- `RLOptimizer` - 优化器类型枚举
- `RLConfig` - 训练配置数据类
- `PolicyNetwork` - 策略网络
- `ValueNetwork` - 价值网络
- `RewardModel` - 奖励模型
- `GRPOTrainer` - GRPO训练器
- `ReinforcementLearningTrainer` - 主训练器

## Usage Example

```python
from reinforcement_learning_training import ReinforcementLearningTrainer, RLConfig, RLOptimizer

config = RLConfig(
    optimizer=RLOptimizer.GRPO,
    learning_rate=1e-4,
    gamma=0.99
)
trainer = ReinforcementLearningTrainer(config, state_size=10, action_size=5)
history = trainer.train(num_episodes=100)
trainer.save_model("model.pt")
```
