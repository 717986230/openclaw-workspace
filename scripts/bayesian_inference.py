#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bayesian Inference - MCMC, Variational
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class BayesianMethod(Enum):
    MCMC = "mcmc"
    VARIATIONAL = "variational"

@dataclass
class BayesianResult:
    posterior_mean: np.ndarray
    posterior_cov: np.ndarray
    samples: np.ndarray
    log_evidence: float
    method: str

class BayesianInference:
    def __init__(self, method: BayesianMethod = BayesianMethod.MCMC):
        self.method = method
        self.posterior_mean = None
        self.posterior_cov = None
        self.samples = None
        self.log_evidence = None
    
    def infer(self, log_likelihood: Callable, prior_mean: np.ndarray,
             prior_cov: np.ndarray, n_samples: int = 1000) -> BayesianResult:
        if self.method == BayesianMethod.MCMC:
            return self._mcmc_inference(log_likelihood, prior_mean, prior_cov, n_samples)
        elif self.method == BayesianMethod.VARIATIONAL:
            return self._variational_inference(log_likelihood, prior_mean, prior_cov)
    
    def _mcmc_inference(self, log_likelihood: Callable, prior_mean: np.ndarray,
                        prior_cov: np.ndarray, n_samples: int) -> BayesianResult:
        dim = len(prior_mean)
        prior_cov_inv = np.linalg.inv(prior_cov)
        
        current = prior_mean.copy()
        current_log_prob = log_likelihood(current) + self._log_gaussian(current, prior_mean, prior_cov_inv)
        
        samples = []
        accepted = 0
        
        for i in range(n_samples):
            proposal = current + np.random.randn(dim) * 0.1
            proposal_log_prob = log_likelihood(proposal) + self._log_gaussian(proposal, prior_mean, prior_cov_inv)
            
            log_alpha = proposal_log_prob - current_log_prob
            if np.log(np.random.random()) < log_alpha:
                current = proposal
                current_log_prob = proposal_log_prob
                accepted += 1
            
            samples.append(current.copy())
        
        samples = np.array(samples)
        self.samples = samples
        self.posterior_mean = np.mean(samples, axis=0)
        self.posterior_cov = np.cov(samples.T)
        self.log_evidence = np.mean([log_likelihood(s) for s in samples])
        
        return BayesianResult(
            posterior_mean=self.posterior_mean,
            posterior_cov=self.posterior_cov,
            samples=self.samples,
            log_evidence=self.log_evidence,
            method=self.method.value
        )
    
    def _variational_inference(self, log_likelihood: Callable, prior_mean: np.ndarray,
                              prior_cov: np.ndarray) -> BayesianResult:
        dim = len(prior_mean)
        q_mean = prior_mean.copy()
        q_cov = prior_cov.copy()
        
        for _ in range(100):
            samples = np.random.multivariate_normal(q_mean, q_cov, size=100)
            
            grad_mean = np.zeros(dim)
            grad_cov = np.zeros((dim, dim))
            
            for sample in samples:
                log_prob = log_likelihood(sample)
                grad_mean += (sample - q_mean) * log_prob
                grad_cov += 0.5 * (np.outer(sample - q_mean, sample - q_mean) - q_cov) * log_prob
            
            grad_mean /= 100
            grad_cov /= 100
            
            q_mean += 0.01 * grad_mean
            q_cov += 0.01 * grad_cov
            q_cov = (q_cov + q_cov.T) / 2
            q_cov += 1e-6 * np.eye(dim)
        
        self.posterior_mean = q_mean
        self.posterior_cov = q_cov
        self.samples = np.random.multivariate_normal(q_mean, q_cov, size=1000)
        self.log_evidence = np.mean([log_likelihood(s) for s in self.samples])
        
        return BayesianResult(
            posterior_mean=self.posterior_mean,
            posterior_cov=self.posterior_cov,
            samples=self.samples,
            log_evidence=self.log_evidence,
            method=self.method.value
        )
    
    def _log_gaussian(self, x: np.ndarray, mean: np.ndarray, cov_inv: np.ndarray) -> float:
        diff = x - mean
        log_prob = -0.5 * diff @ cov_inv @ diff
        return log_prob

print("Bayesian Inference Module Loaded!")
