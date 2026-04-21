#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factorization - Matrix, Tensor, NMF
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FactorizationMethod(Enum):
    MATRIX = "matrix"
    TENSOR = "tensor"
    NMF = "nmf"
    SVD = "svd"

@dataclass
class FactorizationResult:
    """因子分解结果"""
    factors: List[np.ndarray]
    reconstruction: np.ndarray
    error: float
    method: str
    ranks: List[int]

class MatrixFactorization:
    """矩阵分解系统"""
    
    def __init__(self, method: FactorizationMethod = FactorizationMethod.MATRIX):
        self.method = method
        self.factors = None
        self.reconstruction = None
        self.error = None
    
    def factorize(self, X: np.ndarray, ranks: List[int] = None) -> FactorizationResult:
        """因子分解"""
        X = np.array(X)
        
        if ranks is None:
            ranks = [min(X.shape) // 2]
        
        if self.method == FactorizationMethod.MATRIX:
            return self._matrix_factorization(X, ranks[0])
        elif self.method == FactorizationMethod.NMF:
            return self._nmf_factorization(X, ranks[0])
        elif self.method == FactorizationMethod.SVD:
            return self._svd_factorization(X, ranks[0])
        elif self.method == FactorizationMethod.TENSOR:
            return self._tensor_factorization(X, ranks)
    
    def _matrix_factorization(self, X: np.ndarray, rank: int) -> FactorizationResult:
        """矩阵分解（ALS）"""
        n, m = X.shape
        
        # 初始化因子
        U = np.random.randn(n, rank)
        V = np.random.randn(rank, m)
        
        # 交替最小二乘
        for _ in range(100):
            # 更新U
            VVt = V @ V.T
            XVt = X @ V.T
            U = XVt @ np.linalg.inv(VVt + 1e-6 * np.eye(rank))
            
            # 更新V
            UtU = U.T @ U
            UtX = U.T @ X
            V = np.linalg.inv(UtU + 1e-6 * np.eye(rank)) @ UtX
        
        # 重建
        reconstruction = U @ V
        
        # 计算误差
        error = np.sum((X - reconstruction) ** 2)
        
        self.factors = [U, V]
        self.reconstruction = reconstruction
        self.error = error
        
        return FactorizationResult(
            factors=self.factors,
            reconstruction=self.reconstruction,
            error=self.error,
            method=self.method.value,
            ranks=[rank]
        )
    
    def _nmf_factorization(self, X: np.ndarray, rank: int) -> FactorizationResult:
        """非负矩阵分解"""
        X = np.maximum(X, 0)
        n, m = X.shape
        
        W = np.random.rand(n, rank)
        H = np.random.rand(rank, m)
        
        for _ in range(100):
            H = H * (W.T @ X) / (W.T @ W @ H + 1e-10)
            W = W * (X @ H.T) / (W @ H @ H.T + 1e-10)
        
        reconstruction = W @ H
        error = np.sum((X - reconstruction) ** 2)
        
        self.factors = [W, H]
        self.reconstruction = reconstruction
        self.error = error
        
        return FactorizationResult(
            factors=self.factors,
            reconstruction=self.reconstruction,
            error=self.error,
            method=self.method.value,
            ranks=[rank]
        )
    
    def _svd_factorization(self, X: np.ndarray, rank: int) -> FactorizationResult:
        """奇异值分解"""
        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        
        # 截断
        U = U[:, :rank]
        S = S[:rank]
        Vt = Vt[:rank, :]
        
        # 重建
        reconstruction = U @ np.diag(S) @ Vt
        
        # 计算误差
        error = np.sum((X - reconstruction) ** 2)
        
        self.factors = [U, np.diag(S), Vt]
        self.reconstruction = reconstruction
        self.error = error
        
        return FactorizationResult(
            factors=self.factors,
            reconstruction=self.reconstruction,
            error=self.error,
            method=self.method.value,
            ranks=[rank]
        )
    
    def _tensor_factorization(self, X: np.ndarray, ranks: List[int]) -> FactorizationResult:
        """张量分解（CP分解简化版）"""
        # 简化版：将张量reshape为矩阵
        if len(X.shape) == 3:
            n1, n2, n3 = X.shape
            X_matrix = X.reshape(n1, n2 * n3)
            rank = ranks[0]
            
            # 矩阵分解
            result = self._matrix_factorization(X_matrix, rank)
            
            # 重建张量
            reconstruction = result.reconstruction.reshape(n1, n2, n3)
            
            self.factors = result.factors
            self.reconstruction = reconstruction
            self.error = np.sum((X - reconstruction) ** 2)
            
            return FactorizationResult(
                factors=self.factors,
                reconstruction=self.reconstruction,
                error=self.error,
                method=self.method.value,
                ranks=ranks
            )
        else:
            raise ValueError("Only 3D tensors supported")
    
    def get_factor_importance(self) -> List[float]:
        """获取因子重要性"""
        if self.factors is None:
            return []
        
        if self.method == FactorizationMethod.SVD:
            S = self.factors[1]
            return [float(s) for s in np.diag(S)]
        else:
            # 简化：使用因子范数
            importances = []
            for factor in self.factors:
                importances.append(float(np.linalg.norm(factor)))
            return importances

print("Matrix Factorization Module Loaded!")
