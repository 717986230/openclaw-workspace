#!/usr/bin/env python3
"""
Erbing Evolution Part 1: Mental Loop + Tree of Thoughts
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import random

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingMentalLoop:
    """心智循环 - 执行前先模拟"""
    
    def __init__(self):
        self.memory = get_memory()
        self.risk_threshold = 0.3

    def act_with_simulation(self, action: str) -> Dict:
        """带模拟的行动"""
        
        # 1. 模拟
        simulation = self._simulate(action)
        
        # 2. 预测后果
        consequences = self._predict_consequences(action)
        
        # 3. 评估风险
        risk = self._assess_risk(consequences)
        
        # 4. 决策
        if risk < self.risk_threshold:
            decision = "execute"
        elif risk < 0.7:
            decision = "adjust"
        else:
            decision = "abort"
        
        return {
            "action": action,
            "risk": risk,
            "decision": decision,
            "consequences": consequences
        }

    def _simulate(self, action: str) -> Dict:
        results = self.memory.search(action, limit=3)
        return {"similar_cases": len(results)}

    def _predict_consequences(self, action: str) -> List[str]:
        consequences = []
        if "删除" in action or "delete" in action.lower():
            consequences.append("数据丢失风险")
        if "发送" in action or "send" in action.lower():
            consequences.append("信息泄露风险")
        if not consequences:
            consequences.append("正常执行")
        return consequences

    def _assess_risk(self, consequences: List[str]) -> float:
        for c in consequences:
            if "风险" in c or "丢失" in c or "泄露" in c:
                return 0.7
        return 0.2


class ErbingTreeOfThoughts:
    """思维树 - 多路径探索"""
    
    def __init__(self):
        self.memory = get_memory()

    def solve(self, problem: str) -> Dict:
        """解决复杂问题"""
        
        # 1. 生成多个思路
        thoughts = [
            {"id": 1, "approach": "分解问题", "score": random.uniform(0.5, 1.0)},
            {"id": 2, "approach": "类比推理", "score": random.uniform(0.5, 1.0)},
            {"id": 3, "approach": "逆向思考", "score": random.uniform(0.5, 1.0)}
        ]
        
        # 2. 选择最优
        best = max(thoughts, key=lambda x: x["score"])
        
        return {
            "problem": problem,
            "thoughts": thoughts,
            "best_path": best
        }
