"""
MT5 顶配盯盘系统 - 参数优化模块 (遗传算法)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable, Optional
from dataclasses import dataclass
import random
import logging
from datetime import datetime
import pickle
import os

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """优化结果"""
    best_params: Dict[str, any]
    best_score: float
    all_scores: List[float]
    generation: int
    convergence: float  # 收敛度


class GeneticOptimizer:
    """遗传算法参数优化器"""

    def __init__(
        self,
        param_ranges: Dict[str, Tuple[float, float]],
        fitness_function: Callable,
        population_size: int = 50,
        generations: int = 100,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.8,
        elite_ratio: float = 0.1,
    ):
        """
        初始化遗传算法优化器

        Args:
            param_ranges: 参数范围字典
                {
                    'rsi_period': (7, 21),
                    'atr_period': (10, 30),
                    'bb_std': (1.5, 3.0),
                    ...
                }
            fitness_function: 适应度函数，输入参数字典，返回分数
            population_size: 种群大小
            generations: 迭代代数
            mutation_rate: 突变率
            crossover_rate: 交叉率
            elite_ratio: 精英比例
        """
        self.param_ranges = param_ranges
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_ratio = elite_ratio

        self.population = []
        self.best_individual = None
        self.best_score = float('-inf')
        self.history = []

    def optimize(self, verbose: bool = True) -> OptimizationResult:
        """执行优化"""
        # 初始化种群
        self._initialize_population()

        # 评估初始种群
        self._evaluate_population()

        # 进化迭代
        for gen in range(self.generations):
            # 选择
            parents = self._select_parents()

            # 交叉
            offspring = self._crossover(parents)

            # 突变
            offspring = self._mutate(offspring)

            # 合并种群
            self.population = offspring

            # 评估
            self._evaluate_population()

            # 记录历史
            gen_best = max(self.history[-1]['scores'])
            self.history.append({
                'generation': gen,
                'best_score': gen_best,
                'avg_score': np.mean(self.history[-1]['scores']),
            })

            if verbose and gen % 10 == 0:
                logger.info(f"Generation {gen}: Best Score = {gen_best:.4f}")

        # 返回最佳结果
        return OptimizationResult(
            best_params=self.best_individual,
            best_score=self.best_score,
            all_scores=[h['best_score'] for h in self.history],
            generation=self.generations,
            convergence=self._calculate_convergence(),
        )

    def _initialize_population(self):
        """初始化种群"""
        self.population = []
        for _ in range(self.population_size):
            individual = {}
            for param_name, (min_val, max_val) in self.param_ranges.items():
                if isinstance(min_val, int) and isinstance(max_val, int):
                    individual[param_name] = random.randint(min_val, max_val)
                else:
                    individual[param_name] = random.uniform(min_val, max_val)
            self.population.append(individual)

    def _evaluate_population(self):
        """评估种群"""
        scores = []
        for individual in self.population:
            score = self.fitness_function(individual)
            scores.append(score)

            if score > self.best_score:
                self.best_score = score
                self.best_individual = individual.copy()

        if not self.history:
            self.history.append({'scores': scores})
        else:
            self.history[-1]['scores'] = scores

    def _select_parents(self) -> List[Dict]:
        """选择父母"""
        # 锦标赛选择
        tournament_size = 3
        parents = []

        for _ in range(self.population_size):
            tournament = random.sample(range(len(self.population)), tournament_size)
            tournament_scores = [(i, self.history[-1]['scores'][i]) for i in tournament]
            winner_idx = max(tournament_scores, key=lambda x: x[1])[0]
            parents.append(self.population[winner_idx].copy())

        return parents

    def _crossover(self, parents: List[Dict]) -> List[Dict]:
        """交叉"""
        offspring = []

        # 保留精英
        elite_count = int(self.population_size * self.elite_ratio)
        elite_indices = np.argsort(self.history[-1]['scores'])[-elite_count:]
        for idx in elite_indices:
            offspring.append(self.population[idx].copy())

        # 交叉生成其余个体
        while len(offspring) < self.population_size:
            parent1, parent2 = random.sample(parents, 2)

            if random.random() < self.crossover_rate:
                child = self._single_point_crossover(parent1, parent2)
            else:
                child = parent1.copy() if random.random() < 0.5 else parent2.copy()

            offspring.append(child)

        return offspring[:self.population_size]

    def _single_point_crossover(
        self,
        parent1: Dict,
        parent2: Dict
    ) -> Dict:
        """单点交叉"""
        child = {}
        crossover_point = random.choice(list(parent1.keys()))

        in_first = True
        for key in parent1.keys():
            if key == crossover_point:
                in_first = False
            child[key] = parent1[key] if in_first else parent2[key]

        return child

    def _mutate(self, population: List[Dict]) -> List[Dict]:
        """突变"""
        mutated_population = []

        for individual in population:
            mutated = individual.copy()

            for param_name in mutated.keys():
                if random.random() < self.mutation_rate:
                    min_val, max_val = self.param_ranges[param_name]

                    # 高斯突变
                    current = mutated[param_name]
                    sigma = (max_val - min_val) * 0.1
                    mutated[param_name] = current + random.gauss(0, sigma)

                    # 限制范围
                    mutated[param_name] = max(min_val, min(max_val, mutated[param_name]))

                    # 整数参数
                    if isinstance(min_val, int):
                        mutated[param_name] = int(round(mutated[param_name]))

            mutated_population.append(mutated)

        return mutated_population

    def _calculate_convergence(self) -> float:
        """计算收敛度"""
        if len(self.history) < 10:
            return 0.0

        recent_scores = [h['best_score'] for h in self.history[-10:]]
        return 1.0 - (np.std(recent_scores) / (np.mean(recent_scores) + 1e-6))


class ParameterOptimizer:
    """参数优化器 - 封装遗传算法"""

    def __init__(self):
        """初始化"""
        self.optimizers = {}

    def optimize_indicator_params(
        self,
        df: pd.DataFrame,
        initial_params: Dict[str, float] = None
    ) -> Dict[str, any]:
        """
        优化技术指标参数

        Args:
            df: 历史数据
            initial_params: 初始参数

        Returns:
            优化后的参数
        """
        if initial_params is None:
            initial_params = {
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bb_period': 20,
                'bb_std': 2.0,
                'atr_period': 14,
                'sma_short': 20,
                'sma_long': 50,
            }

        # 定义参数范围
        param_ranges = {
            'rsi_period': (7, 21),
            'rsi_overbought': (65, 85),
            'rsi_oversold': (15, 35),
            'macd_fast': (8, 16),
            'macd_slow': (20, 32),
            'macd_signal': (6, 12),
            'bb_period': (15, 30),
            'bb_std': (1.5, 3.0),
            'atr_period': (10, 30),
            'sma_short': (10, 30),
            'sma_long': (40, 80),
        }

        # 定义适应度函数
        def fitness_function(params: Dict) -> float:
            return self._calculate_fitness(df, params)

        # 创建优化器
        optimizer = GeneticOptimizer(
            param_ranges=param_ranges,
            fitness_function=fitness_function,
            population_size=30,
            generations=50,
            mutation_rate=0.1,
            crossover_rate=0.8,
            elite_ratio=0.1,
        )

        # 执行优化
        result = optimizer.optimize(verbose=False)

        logger.info(f"优化完成: Best Score = {result.best_score:.4f}")
        logger.info(f"最佳参数: {result.best_params}")

        return {
            'best_params': result.best_params,
            'best_score': result.best_score,
            'convergence': result.convergence,
        }

    def _calculate_fitness(self, df: pd.DataFrame, params: Dict) -> float:
        """
        计算适应度 (使用简单的移动平均交叉策略)

        返回夏普比率作为适应度
        """
        close = df['close']

        # 计算策略收益
        sma_short = close.rolling(int(params['sma_short'])).mean()
        sma_long = close.rolling(int(params['sma_long'])).mean()

        # 生成信号
        position = pd.Series(0, index=close.index)
        position[sma_short > sma_long] = 1
        position[sma_short < sma_long] = -1

        # 计算收益
        returns = close.pct_change()
        strategy_returns = position.shift(1) * returns

        # 计算夏普比率
        sharpe = strategy_returns.mean() / (strategy_returns.std() + 1e-6) * np.sqrt(252)

        return sharpe if not np.isnan(sharpe) else 0.0

    def optimize_risk_params(
        self,
        df: pd.DataFrame,
        initial_params: Dict[str, float] = None
    ) -> Dict[str, any]:
        """
        优化风险管理参数

        Args:
            df: 历史数据
            initial_params: 初始参数

        Returns:
            优化后的参数
        """
        if initial_params is None:
            initial_params = {
                'max_position_size': 0.02,
                'max_positions': 5,
                'risk_reward_ratio': 2.0,
                'atr_multiplier_sl': 2.0,
                'atr_multiplier_tp': 3.0,
            }

        # 定义参数范围
        param_ranges = {
            'max_position_size': (0.01, 0.05),
            'max_positions': (1, 10),
            'risk_reward_ratio': (1.5, 3.0),
            'atr_multiplier_sl': (1.5, 3.0),
            'atr_multiplier_tp': (2.0, 5.0),
        }

        # 定义适应度函数
        def fitness_function(params: Dict) -> float:
            return self._calculate_risk_fitness(df, params)

        # 创建优化器
        optimizer = GeneticOptimizer(
            param_ranges=param_ranges,
            fitness_function=fitness_function,
            population_size=20,
            generations=30,
            mutation_rate=0.15,
            crossover_rate=0.7,
            elite_ratio=0.1,
        )

        # 执行优化
        result = optimizer.optimize(verbose=False)

        logger.info(f"风险管理参数优化完成: Best Score = {result.best_score:.4f}")
        logger.info(f"最佳参数: {result.best_params}")

        return {
            'best_params': result.best_params,
            'best_score': result.best_score,
            'convergence': result.convergence,
        }

    def _calculate_risk_fitness(self, df: pd.DataFrame, params: Dict) -> float:
        """
        计算风险管理适应度

        返回最大回撤的倒数 (负数所以取反)
        """
        close = df['close']
        high = df['high']
        low = df['low']

        # 计算 ATR
        atr = self._calculate_atr(df, int(params['atr_period']))

        # 简单的止损止盈策略
        position = pd.Series(0, index=close.index)
        entry_price = pd.Series(0.0, index=close.index)

        in_position = False
        entry_idx = 0

        for i in range(50, len(close)):
            if not in_position:
                # 入场
                position.iloc[i] = 1
                entry_price.iloc[i] = close.iloc[i]
                entry_idx = i
                in_position = True
            else:
                # 检查止损止盈
                stop_loss = entry_price.iloc[entry_idx] - params['atr_multiplier_sl'] * atr.iloc[i]
                take_profit = entry_price.iloc[entry_idx] + params['atr_multiplier_tp'] * atr.iloc[i]

                if close.iloc[i] <= stop_loss or close.iloc[i] >= take_profit:
                    in_position = False
                    position.iloc[i] = 0
                else:
                    position.iloc[i] = 1

        # 计算收益
        returns = close.pct_change()
        strategy_returns = position.shift(1) * returns

        # 计算最大回撤
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())

        # 返回得分 (最大回撤的倒数)
        score = -max_drawdown if max_drawdown > 0 else 0.0

        return score

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """计算 ATR"""
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.rolling(window=period).mean()

    def save_params(self, params: Dict, filename: str):
        """保存参数到文件"""
        os.makedirs('mt5_system/optimized_params', exist_ok=True)
        filepath = os.path.join('mt5_system/optimized_params', filename)

        with open(filepath, 'wb') as f:
            pickle.dump({
                'params': params,
                'timestamp': datetime.now().isoformat(),
            }, f)

        logger.info(f"参数已保存到 {filepath}")

    def load_params(self, filename: str) -> Optional[Dict]:
        """从文件加载参数"""
        filepath = os.path.join('mt5_system/optimized_params', filename)

        if not os.path.exists(filepath):
            logger.warning(f"参数文件不存在: {filepath}")
            return None

        with open(filepath, 'rb') as f:
            data = pickle.load(f)

        logger.info(f"参数已从 {filepath} 加载")
        return data['params']