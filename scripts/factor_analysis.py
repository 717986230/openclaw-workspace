#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factor Analysis - PCA, ICA, FA
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FactorMethod(Enum):
    PCA = "pca"
    ICA = "ica"
    FA = "fa"

@dataclass
class FactorResult:
    factors: np.ndarray
    loadings: np.ndarray
    explained_variance: np.ndarray
    explained_variance_ratio: np.ndarray
    method: str
    n_components: int

class FactorAnalysis:
    def __init__(self, method: FactorMethod = FactorMethod.PCA):
        self.method = method
        self.factors = None
        self.loadings = None
        self.explained_variance = None
        self.explained_variance_ratio = None
        self.mean = None
        self.components = None
    
    def fit(self, X: np.ndarray, n_components: int = None) -> FactorResult:
        X = np.array(X)
        if n_components is None:
            n_components = min(X.shape[0], X.shape[1])
        n_components = min(n_components, X.shape[1])
        
        self.mean = np.mean(X, axis=0)
        X_centered = X - self.mean
        
        if self.method == FactorMethod.PCA:
            return self._fit_pca(X_centered, n_components)
        elif self.method == FactorMethod.ICA:
            return self._fit_ica(X_centered, n_components)
        elif self.method == FactorMethod.FA:
            return self._fit_fa(X_centered, n_components)
    
    def _fit_pca(self, X: np.ndarray, n_components: int) -> FactorResult:
        cov_matrix = np.cov(X, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
        idx = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        eigenvalues = eigenvalues[:n_components]
        eigenvectors = eigenvectors[:, :n_components]
        
        self.factors = X @ eigenvectors
        self.loadings = eigenvectors
        self.components = eigenvectors
        
        total_variance = np.sum(eigenvalues)
        self.explained_variance = eigenvalues
        self.explained_variance_ratio = eigenvalues / total_variance
        
        return FactorResult(
            factors=self.factors,
            loadings=self.loadings,
            explained_variance=self.explained_variance,
            explained_variance_ratio=self.explained_variance_ratio,
            method=self.method.value,
            n_components=n_components
        )
    
    def _fit_ica(self, X: np.ndarray, n_components: int) -> FactorResult:
        cov = np.cov(X, rowvar=False)
        D, E = np.linalg.eigh(cov)
        D = np.diag(1.0 / np.sqrt(D + 1e-10))
        X_whitened = (E @ D @ E.T @ X.T).T
        
        W = np.random.randn(n_components, X.shape[1])
        W = W / np.linalg.norm(W, axis=1, keepdims=True)
        
        for _ in range(100):
            Y = X_whitened @ W.T
            gY = np.tanh(Y)
            g_prime = 1 - gY ** 2
            W_new = (gY.T @ X_whitened) / X.shape[0] - np.diag(g_prime.mean(axis=0)) @ W
            W_new = W_new @ np.linalg.inv(np.sqrt(W_new @ W_new.T))
            if np.max(np.abs(W - W_new)) < 1e-6:
                break
            W = W_new
        
        self.factors = X_whitened @ W.T
        self.loadings = W.T
        self.components = W
        
        explained_var = np.var(self.factors, axis=0)
        total_var = np.sum(explained_var)
        self.explained_variance = explained_var
        self.explained_variance_ratio = explained_var / total_var
        
        return FactorResult(
            factors=self.factors,
            loadings=self.loadings,
            explained_variance=self.explained_variance,
            explained_variance_ratio=self.explained_variance_ratio,
            method=self.method.value,
            n_components=n_components
        )
    
    def _fit_fa(self, X: np.ndarray, n_components: int) -> FactorResult:
        corr_matrix = np.corrcoef(X, rowvar=False)
        loadings = np.random.randn(X.shape[1], n_components)
        
        for _ in range(100):
            inv_loadings = np.linalg.inv(loadings.T @ loadings + np.eye(n_components) * 0.01)
            factor_scores = X @ loadings @ inv_loadings
            loadings = (X.T @ factor_scores) @ np.linalg.inv(factor_scores.T @ factor_scores)
            loadings = loadings / np.linalg.norm(loadings, axis=0)
        
        self.factors = X @ loadings
        self.loadings = loadings
        self.components = loadings
        
        explained_var = np.var(self.factors, axis=0)
        total_var = np.sum(np.var(X, axis=0))
        self.explained_variance = explained_var
        self.explained_variance_ratio = explained_var / total_var
        
        return FactorResult(
            factors=self.factors,
            loadings=self.loadings,
            explained_variance=self.explained_variance,
            explained_variance_ratio=self.explained_variance_ratio,
            method=self.method.value,
            n_components=n_components
        )
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.components is None:
            raise ValueError("Model not fitted")
        X = np.array(X)
        X_centered = X - self.mean
        return X_centered @ self.components
    
    def inverse_transform(self, factors: np.ndarray) -> np.ndarray:
        if self.components is None:
            raise ValueError("Model not fitted")
        return factors @ self.components.T + self.mean

print("Factor Analysis Module Loaded!")
