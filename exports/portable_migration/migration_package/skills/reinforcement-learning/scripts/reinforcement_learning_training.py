#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强化学习训练
Reinforcement Learning Training

基于Reasoning-from-Scratch项目的GRPO（Group Relative Policy Optimization）技术
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import deque
import random

class RLOptimizer(Enum):
    """RL优化器"""
    GRPO = "grpo"
    PPO = "ppo"
    A2C = "a2c"
    REINFORCE = "reinforce"

@dataclass
class RLConfig:
    """RL配置"""
    optimizer: RLOptimizer
    learning_rate: float = 1e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    entropy_coef: float = 0.01
    value_coef: float = 0.5
    max_grad_norm: float = 1.0
    batch_size: int = 32
    num_epochs: int = 10

class PolicyNetwork(nn.Module):
    """策略网络"""

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.softmax(self.fc3(x), dim=-1)
        return x


class ValueNetwork(nn.Module):
    """价值网络"""

    def __init__(self, input_size: int, hidden_size: int):
        super(ValueNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class RewardModel(nn.Module):
    """奖励模型"""

    def __init__(self, input_size: int, hidden_size: int):
        super(RewardModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.tanh(self.fc3(x))  # 输出范围[-1, 1]
        return x


class GRPOTrainer:
    """GRPO训练器"""

    def __init__(self, config: RLConfig, state_size: int, action_size: int):
        self.config = config

        # 初始化网络
        self.policy_net = PolicyNetwork(state_size, 128, action_size)
        self.value_net = ValueNetwork(state_size, 128)
        self.reward_model = RewardModel(state_size + action_size, 128)

        # 初始化优化器
        self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=config.learning_rate)
        self.value_optimizer = optim.Adam(self.value_net.parameters(), lr=config.learning_rate)
        self.reward_optimizer = optim.Adam(self.reward_model.parameters(), lr=config.learning_rate)

        # 经验回放
        self.replay_buffer = deque(maxlen=10000)

    def select_action(self, state: np.ndarray) -> Tuple[int, float]:
        """选择动作"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_probs = self.policy_net(state_tensor)

        # 采样动作
        action_dist = torch.distributions.Categorical(action_probs)
        action = action_dist.sample()
        log_prob = action_dist.log_prob(action)

        return action.item(), log_prob.item()

    def compute_advantage(self, rewards: List[float], values: List[float]) -> np.ndarray:
        """计算优势函数（GAE）"""
        advantages = []
        gae = 0

        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]

            delta = rewards[t] + self.config.gamma * next_value - values[t]
            gae = delta + self.config.gamma * self.config.gae_lambda * gae
            advantages.insert(0, gae)

        return np.array(advantages)

    def compute_returns(self, rewards: List[float]) -> np.ndarray:
        """计算回报"""
        returns = []
        R = 0

        for r in reversed(rewards):
            R = r + self.config.gamma * R
            returns.insert(0, R)

        return np.array(returns)

    def train_step(self, states: List[np.ndarray], actions: List[int],
                   old_log_probs: List[float], rewards: List[float]) -> Dict:
        """训练一步"""
        # 转换为张量
        states_tensor = torch.FloatTensor(np.array(states))
        actions_tensor = torch.LongTensor(np.array(actions))
        old_log_probs_tensor = torch.FloatTensor(np.array(old_log_probs))

        # 计算价值
        values = self.value_net(states_tensor).squeeze()

        # 计算优势
        advantages = self.compute_advantage(rewards, values.detach().numpy())
        returns = self.compute_returns(rewards)

        # 转换为张量
        advantages_tensor = torch.FloatTensor(advantages)
        returns_tensor = torch.FloatTensor(returns)

        # PPO损失
        # 1. 策略损失
        action_probs = self.policy_net(states_tensor)
        action_dist = torch.distributions.Categorical(action_probs)
        new_log_probs = action_dist.log_prob(actions_tensor)

        ratio = torch.exp(new_log_probs - old_log_probs_tensor)

        surr1 = ratio * advantages_tensor
        surr2 = torch.clamp(ratio, 1 - self.config.clip_epsilon, 1 + self.config.clip_epsilon) * advantages_tensor

        policy_loss = -torch.min(surr1, surr2).mean()

        # 2. 价值损失
        value_loss = nn.MSELoss()(self.value_net(states_tensor).squeeze(), returns_tensor)

        # 3. 熵损失
        entropy = action_dist.entropy().mean()

        # 总损失
        total_loss = policy_loss + self.config.value_coef * value_loss - self.config.entropy_coef * entropy

        # 优化策略网络
        self.policy_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.config.max_grad_norm)
        self.policy_optimizer.step()

        # 优化价值网络
        self.value_optimizer.zero_grad()
        value_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.value_net.parameters(), self.config.max_grad_norm)
        self.value_optimizer.step()

        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy': entropy.item(),
            'total_loss': total_loss.item()
        }

    def train_reward_model(self, states: List[np.ndarray], actions: List[int],
                          human_rewards: List[float]) -> Dict:
        """训练奖励模型"""
        # 转换为张量
        state_action_pairs = []
        for state, action in zip(states, actions):
            state_action = np.concatenate([state, np.eye(len(action))[action]])
            state_action_pairs.append(state_action)

        state_action_tensor = torch.FloatTensor(np.array(state_action_pairs))
        human_rewards_tensor = torch.FloatTensor(np.array(human_rewards))

        # 预测奖励
        predicted_rewards = self.reward_model(state_action_tensor).squeeze()

        # 计算损失
        reward_loss = nn.MSELoss()(predicted_rewards, human_rewards_tensor)

        # 优化
        self.reward_optimizer.zero_grad()
        reward_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.reward_model.parameters(), self.config.max_grad_norm)
        self.reward_optimizer.step()

        return {
            'reward_loss': reward_loss.item(),
            'predicted_rewards': predicted_rewards.detach().numpy(),
            'human_rewards': human_rewards
        }

    def train(self, num_episodes: int = 100) -> List[Dict]:
        """训练"""
        training_history = []

        for episode in range(num_episodes):
            episode_rewards = []
            episode_states = []
            episode_actions = []
            episode_log_probs = []

            # 模拟一个episode
            state = np.random.randn(10)  # 假设状态维度为10

            for step in range(100):  # 每个episode最多100步
                # 选择动作
                action, log_prob = self.select_action(state)

                # 模拟环境
                next_state = state + np.random.randn(10) * 0.1
                reward = np.random.randn()  # 随机奖励

                episode_rewards.append(reward)
                episode_states.append(state)
                episode_actions.append(action)
                episode_log_probs.append(log_prob)

                state = next_state

                if step == 99:  # 结束episode
                    break

            # 训练
            if len(episode_states) > 0:
                train_result = self.train_step(
                    episode_states,
                    episode_actions,
                    episode_log_probs,
                    episode_rewards
                )

                training_history.append({
                    'episode': episode,
                    'total_reward': sum(episode_rewards),
                    'steps': len(episode_states),
                    **train_result
                })

        return training_history


class ReinforcementLearningTrainer:
    """强化学习训练器"""

    def __init__(self, config: RLConfig, state_size: int, action_size: int):
        self.config = config
        self.trainer = GRPOTrainer(config, state_size, action_size)

    def train(self, num_episodes: int = 100) -> List[Dict]:
        """训练"""
        print(f"Training with {config.optimizer.value} for {num_episodes} episodes...")

        training_history = self.trainer.train(num_episodes)

        print(f"Training complete! Trained {len(training_history)} episodes")

        return training_history

    def evaluate(self, num_episodes: int = 10) -> Dict:
        """评估"""
        print(f"Evaluating for {num_episodes} episodes...")

        total_rewards = []
        total_steps = []

        for episode in range(num_episodes):
            episode_reward = 0
            episode_steps = 0

            state = np.random.randn(10)

            for step in range(100):
                action, _ = self.trainer.select_action(state)
                reward = np.random.randn()

                episode_reward += reward
                episode_steps += 1

                state = state + np.random.randn(10) * 0.1

                if step == 99:
                    break

            total_rewards.append(episode_reward)
            total_steps.append(episode_steps)

        return {
            'mean_reward': np.mean(total_rewards),
            'std_reward': np.std(total_rewards),
            'mean_steps': np.mean(total_steps),
            'std_steps': np.std(total_steps)
        }

    def save_model(self, path: str):
        """保存模型"""
        torch.save({
            'policy_net': self.trainer.policy_net.state_dict(),
            'value_net': self.trainer.value_net.state_dict(),
            'reward_model': self.trainer.reward_model.state_dict(),
            'config': self.config
        }, path)
        print(f"Model saved to {path}")

    def load_model(self, path: str):
        """加载模型"""
        checkpoint = torch.load(path)
        self.trainer.policy_net.load_state_dict(checkpoint['policy_net'])
        self.trainer.value_net.load_state_dict(checkpoint['value_net'])
        self.trainer.reward_model.load_state_dict(checkpoint['reward_model'])
        print(f"Model loaded from {path}")


if __name__ == "__main__":
    # 测试代码
    print("Testing Reinforcement Learning Training...")

    # 创建配置
    config = RLConfig(
        optimizer=RLOptimizer.GRPO,
        learning_rate=1e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_epsilon=0.2,
        entropy_coef=0.01,
        value_coef=0.5,
        max_grad_norm=1.0,
        batch_size=32,
        num_epochs=10
    )

    # 创建训练器
    trainer = ReinforcementLearningTrainer(config, state_size=10, action_size=5)

    # 训练
    training_history = trainer.train(num_episodes=10)

    # 评估
    eval_result = trainer.evaluate(num_episodes=5)

    print(f"Training history: {len(training_history)} episodes")
    print(f"Evaluation result: {eval_result}")

    # 保存模型
    trainer.save_model("rl_model.pt")

    print("Reinforcement Learning Training test complete!")
