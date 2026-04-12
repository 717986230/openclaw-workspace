#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Latent Variable Models - GMM, LDA
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class LatentMethod(Enum):
    GMM = "gmm"
    LDA = "lda"

@dataclass
class LatentResult:
    latent_variables: np.ndarray
    reconstruction: np.ndarray
    log_likelihood: float
    method: str
    n_components: int

class LatentVariableModels:
    def __init__(self, method: LatentMethod = LatentMethod.GMM):
        self.method = method
        self.latent_variables = None
        self.reconstruction = None
        self.log_likelihood = None
        self.parameters = None
    
    def fit(self, X: np.ndarray, n_components: int = 2) -> LatentResult:
        X = np.array(X)
        if self.method == LatentMethod.GMM:
            return self._fit_gmm(X, n_components)
        elif self.method == LatentMethod.LDA:
            return self._fit_lda(X, n_components)
    
    def _fit_gmm(self, X: np.ndarray, n_components: int) -> LatentResult:
        n_samples, n_features = X.shape
        means = X[np.random.choice(n_samples, n_components, replace=False)]
        covariances = [np.eye(n_features) for _ in range(n_components)]
        weights = np.ones(n_components) / n_components
        
        for _ in range(100):
            responsibilities = np.zeros((n_samples, n_components))
            for k in range(n_components):
                diff = X - means[k]
                inv_cov = np.linalg.inv(covariances[k] + 1e-6 * np.eye(n_features))
                exp_term = np.exp(-0.5 * np.sum(diff @ inv_cov * diff, axis=1))
                responsibilities[:, k] = weights[k] * exp_term
            responsibilities = responsibilities / np.sum(responsibilities, axis=1, keepdims=True)
            
            Nk = np.sum(responsibilities, axis=0)
            weights = Nk / n_samples
            for k in range(n_components):
                means[k] = np.sum(responsibilities[:, k:k+1] * X, axis=0) / Nk[k]
                diff = X - means[k]
                covariances[k] = (responsibilities[:, k:k+1] * diff).T @ diff / Nk[k]
                covariances[k] += 1e-6 * np.eye(n_features)
        
        self.latent_variables = responsibilities
        self.parameters = {'means': means, 'covariances': covariances, 'weights': weights}
        
        reconstruction = np.zeros_like(X)
        for k in range(n_components):
            reconstruction += responsibilities[:, k:k+1] @ means[k:k+1, :]
        self.reconstruction = reconstruction
        
        log_likelihood = 0.0
        for k in range(n_components):
            diff = X - means[k]
            inv_cov = np.linalg.inv(covariances[k] + 1e-6 * np.eye(n_features))
            log_det = np.log(np.linalg.det(covariances[k] + 1e-6 * np.eye(n_features)))
            exp_term = np.exp(-0.5 * np.sum(diff @ inv_cov * diff, axis=1))
            log_likelihood += np.sum(np.log(weights[k] * exp_term / np.sqrt((2 * np.pi) ** n_features * np.exp(log_det))))
        self.log_likelihood = log_likelihood
        
        return LatentResult(
            latent_variables=self.latent_variables,
            reconstruction=self.reconstruction,
            log_likelihood=self.log_likelihood,
            method=self.method.value,
            n_components=n_components
        )
    
    def _fit_lda(self, X: np.ndarray, n_components: int) -> LatentResult:
        n_samples, n_features = X.shape
        topic_word_dist = np.random.dirichlet(np.ones(n_features), n_components)
        doc_topic_dist = np.random.dirichlet(np.ones(n_components), n_samples)
        
        for _ in range(50):
            for d in range(n_samples):
                doc_topic_dist[d] = np.random.dirichlet(np.ones(n_components) + np.sum(X[d:d+1, :] * topic_word_dist.T, axis=1))
        
        self.latent_variables = doc_topic_dist
        self.parameters = {'topic_word_dist': topic_word_dist, 'doc_topic_dist': doc_topic_dist}
        reconstruction = doc_topic_dist @ topic_word_dist
        self.reconstruction = reconstruction
        log_likelihood = np.sum(X * np.log(reconstruction + 1e-10))
        self.log_likelihood = log_likelihood
        
        return LatentResult(
            latent_variables=self.latent_variables,
            reconstruction=self.reconstruction,
            log_likelihood=self.log_likelihood,
            method=self.method.value,
            n_components=n_components
        )
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.parameters is None:
            raise ValueError("Model not fitted")
        if self.method == LatentMethod.GMM:
            responsibilities = np.zeros((X.shape[0], len(self.parameters['means'])))
            for k, mean in enumerate(self.parameters['means']):
                diff = X - mean
                inv_cov = np.linalg.inv(self.parameters['covariances'][k] + 1e-6 * np.eye(X.shape[1]))
                exp_term = np.exp(-0.5 * np.sum(diff @ inv_cov * diff, axis=1))
                responsibilities[:, k] = self.parameters['weights'][k] * exp_term
            return responsibilities / np.sum(responsibilities, axis=1, keepdims=True)
        return self.latent_variables

print("Latent Variable Models Module Loaded!")
