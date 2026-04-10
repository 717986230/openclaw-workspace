#!/usr/bin/env python3
"""
蚁群策略进化引擎 - 动态调整采集策略、优化信息素算法
"""
import json
import random
import math
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

class AntColonyStrategyEvolver:
    """蚁群策略进化器 - 智能采集策略"""
    
    def __init__(self):
        self.config_dir = Path("skills/swarm-orchestration/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 信息素系统
        self.pheromones = {
            "quality": {"strength": 1.0, "decay": 0.1, "boost": 0.3},
            "trail": {"strength": 0.7, "decay": 0.2, "boost": 0.2},
            "alarm": {"strength": 0.5, "decay": 0.5, "boost": 0.1}
        }
        
        # 采集策略
        self.strategies = {
            "exploration": {
                "name": "探索策略",
                "weight": 0.3,
                "actions": ["random_walk", "breadth_first", "diversify_sources"]
            },
            "exploitation": {
                "name": "开发策略",
                "weight": 0.5,
                "actions": ["follow_pheromone", "deep_dive", "quality_focus"]
            },
            "balanced": {
                "name": "平衡策略",
                "weight": 0.2,
                "actions": ["hybrid_search", "adaptive_routing", "dynamic_priority"]
            }
        }
        
        # 学习历史
        self.learning_history = []
        self.strategy_performance = defaultdict(list)
    
    def evolve_strategies(self):
        """进化策略"""
        timestamp = datetime.now().isoformat()
        
        print(f"\n[蚁群策略进化] {timestamp}")
        
        # 1. 分析历史性能
        performance = self._analyze_performance()
        
        # 2. 调整策略权重
        self._adjust_weights(performance)
        
        # 3. 优化信息素算法
        self._optimize_pheromones()
        
        # 4. 添加新策略
        new_strategies = self._discover_new_strategies()
        
        # 5. 保存配置
        self._save_evolved_config()
        
        evolution_result = {
            "timestamp": timestamp,
            "performance": performance,
            "adjustments": {
                "weight_changes": self._get_weight_changes(),
                "pheromone_tuning": self._get_pheromone_changes(),
                "new_strategies": new_strategies
            }
        }
        
        self.learning_history.append(evolution_result)
        
        return evolution_result
    
    def _analyze_performance(self):
        """分析历史性能"""
        # 模拟性能分析
        performance = {
            "exploration": {
                "success_rate": random.uniform(0.6, 0.9),
                "novelty_score": random.uniform(0.5, 0.8),
                "efficiency": random.uniform(0.4, 0.7)
            },
            "exploitation": {
                "success_rate": random.uniform(0.7, 0.95),
                "quality_score": random.uniform(0.7, 0.95),
                "efficiency": random.uniform(0.6, 0.9)
            },
            "balanced": {
                "success_rate": random.uniform(0.65, 0.88),
                "balance_score": random.uniform(0.6, 0.85),
                "efficiency": random.uniform(0.5, 0.8)
            }
        }
        
        for strategy, metrics in performance.items():
            self.strategy_performance[strategy].append(metrics)
        
        return performance
    
    def _adjust_weights(self, performance):
        """基于性能调整权重"""
        total_score = 0
        scores = {}
        
        for strategy, metrics in performance.items():
            # 综合评分
            score = (
                metrics["success_rate"] * 0.4 +
                metrics.get("quality_score", metrics.get("novelty_score", 0.5)) * 0.35 +
                metrics["efficiency"] * 0.25
            )
            scores[strategy] = score
            total_score += score
        
        # 归一化权重
        if total_score > 0:
            for strategy in self.strategies:
                old_weight = self.strategies[strategy]["weight"]
                new_weight = scores.get(strategy, 0.33) / total_score
                
                # 平滑调整（避免剧烈变化）
                smoothed_weight = old_weight * 0.7 + new_weight * 0.3
                self.strategies[strategy]["weight"] = smoothed_weight
    
    def _optimize_pheromones(self):
        """优化信息素参数"""
        for ptype, params in self.pheromones.items():
            # 动态调整衰减率
            if ptype == "quality":
                # 高质量信息素衰减更慢
                params["decay"] = max(0.05, params["decay"] * 0.95)
            elif ptype == "alarm":
                # 警报信息素衰减更快
                params["decay"] = min(0.7, params["decay"] * 1.05)
            
            # 调整增强因子
            params["boost"] = params["boost"] * (1 + random.uniform(-0.05, 0.05))
    
    def _discover_new_strategies(self):
        """发现新策略"""
        new_strategies = []
        
        # 基于历史发现新模式
        if len(self.learning_history) > 5:
            # 添加协同策略
            new_strategies.append({
                "name": "collaborative_filtering",
                "description": "基于社区协作的过滤策略",
                "weight": 0.1,
                "priority": "medium"
            })
        
        if len(self.learning_history) > 10:
            # 添加预测策略
            new_strategies.append({
                "name": "predictive_routing",
                "description": "预测性路由策略",
                "weight": 0.15,
                "priority": "high"
            })
        
        return new_strategies
    
    def _get_weight_changes(self):
        """获取权重变化"""
        changes = {}
        for strategy, params in self.strategies.items():
            changes[strategy] = {
                "weight": params["weight"],
                "actions": params["actions"]
            }
        return changes
    
    def _get_pheromone_changes(self):
        """获取信息素变化"""
        return dict(self.pheromones)
    
    def _save_evolved_config(self):
        """保存进化后的配置"""
        config = {
            "timestamp": datetime.now().isoformat(),
            "strategies": self.strategies,
            "pheromones": self.pheromones,
            "performance_history": list(self.strategy_performance.values())[-5:]  # 最近5次
        }
        
        config_file = self.config_dir / "ant_strategy_evolved.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        print(f"[配置已保存] {config_file}")
    
    def get_optimal_strategy(self):
        """获取最优策略"""
        best_strategy = max(
            self.strategies.items(),
            key=lambda x: x[1]["weight"]
        )
        
        return {
            "strategy": best_strategy[0],
            "config": best_strategy[1],
            "pheromone_params": self.pheromones
        }

def main():
    evolver = AntColonyStrategyEvolver()
    
    print("\n" + "="*60)
    print("[蚁群策略进化引擎]")
    print("="*60)
    
    result = evolver.evolve_strategies()
    
    print("\n[进化结果]")
    print(f"  策略调整: {len(result['adjustments']['weight_changes'])} 个")
    print(f"  信息素优化: {len(result['adjustments']['pheromone_tuning'])} 类")
    print(f"  新策略: {len(result['adjustments']['new_strategies'])} 个")
    
    optimal = evolver.get_optimal_strategy()
    print(f"\n[当前最优策略] {optimal['strategy']}")

if __name__ == "__main__":
    main()
