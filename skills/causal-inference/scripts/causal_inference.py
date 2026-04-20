#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Causal Inference - Do-calculus, Potential Outcomes
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

class CausalMethod(Enum):
    DO_CALCULUS = "do_calculus"
    POTENTIAL_OUTCOMES = "potential_outcomes"
    STRUCTURAL_CAUSAL = "structural_causal"
    INSTRUMENTAL_VARIABLE = "instrumental_variable"
    PROPENSITY_SCORE = "propensity_score"

@dataclass
class CausalEffect:
    """因果效应估计"""
    treatment_effect: float
    confidence_interval: Tuple[float, float]
    p_value: float
    method: str
    assumptions: List[str]

class CausalInference:
    """因果推断系统"""
    
    def __init__(self, method: CausalMethod = CausalMethod.POTENTIAL_OUTCOMES):
        self.method = method
        self.causal_graph: Optional[Dict] = None
        self.treatment_effect: Optional[float] = None
        self.confidence_interval: Optional[Tuple[float, float]] = None
    
    def estimate_ate(self, treatment: np.ndarray, outcome: np.ndarray, 
                    covariates: Optional[np.ndarray] = None) -> CausalEffect:
        """估计平均处理效应（ATE）"""
        if self.method == CausalMethod.POTENTIAL_OUTCOMES:
            return self._estimate_ate_potential_outcomes(treatment, outcome, covariates)
        elif self.method == CausalMethod.PROPENSITY_SCORE:
            return self._estimate_ate_propensity_score(treatment, outcome, covariates)
        elif self.method == CausalMethod.INSTRUMENTAL_VARIABLE:
            return self._estimate_ate_iv(treatment, outcome, covariates)
        else:
            raise ValueError(f"Unknown method: {self.method}")
    
    def _estimate_ate_potential_outcomes(self, treatment: np.ndarray, 
                                        outcome: np.ndarray,
                                        covariates: Optional[np.ndarray] = None) -> CausalEffect:
        """潜在结果框架估计ATE"""
        # 简单差分估计
        treated_outcome = outcome[treatment == 1]
        control_outcome = outcome[treatment == 0]
        
        ate = np.mean(treated_outcome) - np.mean(control_outcome)
        
        # 计算标准误差
        n_treated = len(treated_outcome)
        n_control = len(control_outcome)
        se = np.sqrt(np.var(treated_outcome) / n_treated + np.var(control_outcome) / n_control)
        
        # 95%置信区间
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        
        # p值
        z_score = ate / se
        p_value = 2 * (1 - 0.5 * (1 + np.abs(z_score)))
        
        self.treatment_effect = ate
        self.confidence_interval = ci
        
        return CausalEffect(
            treatment_effect=ate,
            confidence_interval=ci,
            p_value=p_value,
            method=self.method.value,
            assumptions=["SUTVA", "Consistency", "Positivity"]
        )
    
    def _estimate_ate_propensity_score(self, treatment: np.ndarray,
                                       outcome: np.ndarray,
                                       covariates: np.ndarray) -> CausalEffect:
        """倾向得分匹配估计ATE"""
        # 简化版：使用逻辑回归估计倾向得分
        n_samples = covariates.shape[0]
        n_features = covariates.shape[1]
        
        # 初始化权重
        weights = np.random.randn(n_features + 1)
        
        # 梯度下降
        for _ in range(100):
            logits = covariates @ weights[1:] + weights[0]
            probs = 1 / (1 + np.exp(-logits))
            gradient = covariates.T @ (treatment - probs) / n_samples
            weights[1:] += 0.01 * gradient
            weights[0] += 0.01 * np.mean(treatment - probs)
        
        # 计算倾向得分
        propensity_scores = 1 / (1 + np.exp(-(covariates @ weights[1:] + weights[0])))
        
        # 逆概率加权（IPW）
        ipw_treated = outcome[treatment == 1] / propensity_scores[treatment == 1]
        ipw_control = outcome[treatment == 0] / (1 - propensity_scores[treatment == 0])
        
        ate = np.mean(ipw_treated) - np.mean(ipw_control)
        
        # 简化置信区间
        se = np.sqrt(np.var(ipw_treated) / len(ipw_treated) + np.var(ipw_control) / len(ipw_control))
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        p_value = 2 * (1 - 0.5 * (1 + np.abs(ate / se)))
        
        return CausalEffect(
            treatment_effect=ate,
            confidence_interval=ci,
            p_value=p_value,
            method=self.method.value,
            assumptions=["Unconfoundedness", "Positivity"]
        )
    
    def _estimate_ate_iv(self, treatment: np.ndarray, outcome: np.ndarray,
                        covariates: np.ndarray) -> CausalEffect:
        """工具变量估计ATE"""
        # 简化版：两阶段最小二乘法（2SLS）
        instrument = covariates[:, 0]  # 使用第一个协变量作为工具变量
        
        # 第一阶段：回归treatment on instrument
        n = len(treatment)
        X = np.column_stack([np.ones(n), instrument])
        beta1 = np.linalg.inv(X.T @ X) @ X.T @ treatment
        
        # 预测treatment
        treatment_pred = X @ beta1
        
        # 第二阶段：回归outcome on predicted treatment
        X2 = np.column_stack([np.ones(n), treatment_pred])
        beta2 = np.linalg.inv(X2.T @ X2) @ X2.T @ outcome
        
        ate = beta2[1]
        
        # 简化标准误差
        residuals = outcome - X2 @ beta2
        se = np.sqrt(np.sum(residuals ** 2) / (n - 2)) / np.sqrt(np.sum((treatment_pred - np.mean(treatment_pred)) ** 2))
        ci = (ate - 1.96 * se, ate + 1.96 * se)
        p_value = 2 * (1 - 0.5 * (1 + np.abs(ate / se)))
        
        return CausalEffect(
            treatment_effect=ate,
            confidence_interval=ci,
            p_value=p_value,
            method=self.method.value,
            assumptions=["Relevance", "Exclusion", "Exogeneity"]
        )
    
    def do_calculus(self, intervention: str, target: str, 
                   graph: Dict) -> float:
        """Do-calculus计算干预效应"""
        # 简化版：基于d-separation
        if self._is_d_separated(graph, intervention, target):
            return 0.0
        else:
            return 1.0
    
    def _is_d_separated(self, graph: Dict, x: str, y: str) -> bool:
        """检查d-separation"""
        # 简化版：检查是否有路径
        if x not in graph or y not in graph:
            return True
        
        # BFS检查路径
        visited = set()
        queue = [x]
        
        while queue:
            current = queue.pop(0)
            if current == y:
                return False
            if current in visited:
                continue
            visited.add(current)
            
            if current in graph:
                for neighbor in graph[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return True
    
    def backdoor_adjustment(self, treatment: str, outcome: str,
                           confounders: List[str], data: np.ndarray) -> float:
        """后门准则调整"""
        # 简化版：分层分析
        treated = data[data[:, 0] == 1]
        control = data[data[:, 0] == 0]
        
        effect = np.mean(treated[:, 1]) - np.mean(control[:, 1])
        
        return effect
    
    def frontdoor_adjustment(self, treatment: str, outcome: str,
                           mediator: str, data: np.ndarray) -> float:
        """前门准则调整"""
        # 简化版：中介分析
        n = data.shape[0]
        
        # 计算mediator对treatment的效应
        effect_tm = np.cov(data[:, 0], data[:, 2])[0, 1] / np.var(data[:, 0])
        
        # 计算outcome对mediator的效应
        effect_mo = np.cov(data[:, 2], data[:, 1])[0, 1] / np.var(data[:, 2])
        
        # 总效应
        total_effect = effect_tm * effect_mo
        
        return total_effect

print("Causal Inference Module Loaded!")
