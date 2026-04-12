#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factor Inference System - Complete Integration
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import json

from factor_analysis import FactorAnalysis, FactorMethod, FactorResult
from causal_inference import CausalInference, CausalMethod, CausalEffect
from latent_variable_models import LatentVariableModels, LatentMethod, LatentResult
from bayesian_inference import BayesianInference, BayesianMethod, BayesianResult
from matrix_factorization import MatrixFactorization, FactorizationMethod, FactorizationResult
from structural_equation_modeling import StructuralEquationModeling, SEMMethod, SEMResult

class FactorInferenceSystem:
    def __init__(self):
        self.factor_analysis = FactorAnalysis(FactorMethod.PCA)
        self.causal_inference = CausalInference(CausalMethod.POTENTIAL_OUTCOMES)
        self.latent_models = LatentVariableModels(LatentMethod.GMM)
        self.bayesian_inference = BayesianInference(BayesianMethod.MCMC)
        self.matrix_factorization = MatrixFactorization(FactorizationMethod.MATRIX)
        self.sem = StructuralEquationModeling(SEMMethod.PATH_ANALYSIS)
        
        self.factor_result = None
        self.causal_result = None
        self.latent_result = None
        self.bayesian_result = None
        self.factorization_result = None
        self.sem_result = None
    
    def analyze_factors(self, X: np.ndarray, n_components: int = 2) -> FactorResult:
        self.factor_result = self.factor_analysis.fit(X, n_components)
        return self.factor_result
    
    def infer_causal_effect(self, treatment: np.ndarray, outcome: np.ndarray,
                           covariates: Optional[np.ndarray] = None) -> CausalEffect:
        self.causal_result = self.causal_inference.estimate_ate(treatment, outcome, covariates)
        return self.causal_result
    
    def discover_latent_variables(self, X: np.ndarray, n_components: int = 2) -> LatentResult:
        self.latent_result = self.latent_models.fit(X, n_components)
        return self.latent_result
    
    def bayesian_infer(self, log_likelihood, prior_mean: np.ndarray,
                     prior_cov: np.ndarray, n_samples: int = 1000) -> BayesianResult:
        self.bayesian_result = self.bayesian_inference.infer(log_likelihood, prior_mean, prior_cov, n_samples)
        return self.bayesian_result
    
    def factorize_matrix(self, X: np.ndarray, rank: int = 2) -> FactorizationResult:
        self.factorization_result = self.matrix_factorization.factorize(X, [rank])
        return self.factorization_result
    
    def fit_sem(self, data: np.ndarray, model: Dict) -> SEMResult:
        self.sem_result = self.sem.fit(data, model)
        return self.sem_result
    
    def get_system_statistics(self) -> Dict:
        stats = {
            'factor_analysis': {
                'method': self.factor_analysis.method.value,
                'n_components': self.factor_result.n_components if self.factor_result else 0
            },
            'causal_inference': {
                'method': self.causal_inference.method.value,
                'treatment_effect': self.causal_result.treatment_effect if self.causal_result else 0.0
            },
            'latent_models': {
                'method': self.latent_models.method.value,
                'n_components': self.latent_result.n_components if self.latent_result else 0
            },
            'bayesian_inference': {
                'method': self.bayesian_inference.method.value,
                'log_evidence': self.bayesian_result.log_evidence if self.bayesian_result else 0.0
            },
            'matrix_factorization': {
                'method': self.matrix_factorization.method.value,
                'error': self.factorization_result.error if self.factorization_result else 0.0
            },
            'sem': {
                'method': self.sem.method.value,
                'fit_indices': self.sem_result.fit_indices if self.sem_result else {}
            }
        }
        return stats

if __name__ == "__main__":
    print("=" * 60)
    print("Factor Inference System - Ultimate Configuration")
    print("=" * 60)
    
    print("\n[1] Creating system...")
    system = FactorInferenceSystem()
    print("[OK] System created!")
    
    print("\n[2] Testing factor analysis...")
    X = np.random.randn(100, 10)
    factor_result = system.analyze_factors(X, n_components=3)
    print(f"[OK] Method: {factor_result.method}, Components: {factor_result.n_components}")
    
    print("\n[3] Testing causal inference...")
    treatment = np.random.randint(0, 2, 100)
    outcome = np.random.randn(100) + 0.5 * treatment
    covariates = np.random.randn(100, 5)
    causal_result = system.infer_causal_effect(treatment, outcome, covariates)
    print(f"[OK] Method: {causal_result.method}, Effect: {causal_result.treatment_effect:.4f}")
    
    print("\n[4] Testing latent variable models...")
    latent_result = system.discover_latent_variables(X, n_components=3)
    print(f"[OK] Method: {latent_result.method}, Components: {latent_result.n_components}")
    
    print("\n[5] Testing Bayesian inference...")
    def log_likelihood(x):
        return -0.5 * np.sum(x ** 2)
    prior_mean = np.zeros(10)
    prior_cov = np.eye(10)
    bayesian_result = system.bayesian_infer(log_likelihood, prior_mean, prior_cov, n_samples=100)
    print(f"[OK] Method: {bayesian_result.method}, Evidence: {bayesian_result.log_evidence:.4f}")
    
    print("\n[6] Testing matrix factorization...")
    factorization_result = system.factorize_matrix(X, rank=3)
    print(f"[OK] Method: {factorization_result.method}, Error: {factorization_result.error:.4f}")
    
    print("\n[7] Testing SEM...")
    model = {'variables': ['X1', 'X2', 'X3', 'Y'], 'paths': [('X1', 'X2'), ('X2', 'X3'), ('X3', 'Y')]}
    sem_data = np.random.randn(100, 4)
    sem_result = system.fit_sem(sem_data, model)
    print(f"[OK] Method: {sem_result.method}, Paths: {len(sem_result.path_coefficients)}")
    
    print("\n[8] System statistics...")
    stats = system.get_system_statistics()
    print(f"[OK] All 6 modules integrated successfully!")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Factor Inference System test completed!")
    print("=" * 60)
