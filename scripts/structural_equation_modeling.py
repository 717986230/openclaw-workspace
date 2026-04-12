#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structural Equation Modeling - Path Analysis
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class SEMMethod(Enum):
    PATH_ANALYSIS = "path_analysis"

@dataclass
class SEMResult:
    path_coefficients: Dict[str, float]
    fit_indices: Dict[str, float]
    standardized_coefficients: Dict[str, float]
    method: str

class StructuralEquationModeling:
    def __init__(self, method: SEMMethod = SEMMethod.PATH_ANALYSIS):
        self.method = method
        self.path_coefficients = None
        self.fit_indices = None
        self.standardized_coefficients = None
    
    def fit(self, data: np.ndarray, model: Dict) -> SEMResult:
        data = np.array(data)
        if self.method == SEMMethod.PATH_ANALYSIS:
            return self._fit_path_analysis(data, model)
    
    def _fit_path_analysis(self, data: np.ndarray, model: Dict) -> SEMResult:
        paths = model.get('paths', [])
        path_coefficients = {}
        standardized_coefficients = {}
        
        for path in paths:
            from_var, to_var = path
            from_idx = model['variables'].index(from_var)
            to_idx = model['variables'].index(to_var)
            
            X = data[:, from_idx:from_idx+1]
            y = data[:, to_idx]
            
            beta = np.linalg.inv(X.T @ X) @ X.T @ y
            path_coefficients[f"{from_var}->{to_var}"] = float(beta[0])
            
            std_x = np.std(X)
            std_y = np.std(y)
            standardized_coefficients[f"{from_var}->{to_var}"] = float(beta[0] * std_x / std_y)
        
        self.path_coefficients = path_coefficients
        self.standardized_coefficients = standardized_coefficients
        
        fit_indices = self._calculate_fit_indices(data, model, path_coefficients)
        self.fit_indices = fit_indices
        
        return SEMResult(
            path_coefficients=self.path_coefficients,
            fit_indices=self.fit_indices,
            standardized_coefficients=self.standardized_coefficients,
            method=self.method.value
        )
    
    def _calculate_fit_indices(self, data: np.ndarray, model: Dict,
                              path_coefficients: Dict) -> Dict:
        n = data.shape[0]
        chi_square = 0.0
        for coeff in path_coefficients.values():
            chi_square += coeff ** 2
        
        df = len(path_coefficients)
        rmsea = np.sqrt(max(0, (chi_square - df) / (df * (n - 1))))
        cfi = 1.0 - chi_square / (chi_square + df)
        tli = cfi
        srmr = np.sqrt(chi_square / df)
        
        return {
            'chi_square': chi_square,
            'df': df,
            'rmsea': rmsea,
            'cfi': cfi,
            'tli': tli,
            'srmr': srmr
        }
    
    def get_direct_effects(self) -> Dict[str, float]:
        if self.path_coefficients is None:
            return {}
        return self.path_coefficients
    
    def get_indirect_effects(self, model: Dict) -> Dict[str, float]:
        if self.path_coefficients is None:
            return {}
        
        indirect_effects = {}
        paths = model.get('paths', [])
        
        for i, path1 in enumerate(paths):
            for path2 in paths[i+1:]:
                if path1[1] == path2[0]:
                    key = f"{path1[0]}->{path2[1]}"
                    coeff1 = self.path_coefficients.get(f"{path1[0]}->{path1[1]}", 0)
                    coeff2 = self.path_coefficients.get(f"{path2[0]}->{path2[1]}", 0)
                    indirect_effects[key] = coeff1 * coeff2
        
        return indirect_effects
    
    def get_total_effects(self, model: Dict) -> Dict[str, float]:
        direct = self.get_direct_effects()
        indirect = self.get_indirect_effects(model)
        
        total = direct.copy()
        for path, effect in indirect.items():
            if path in total:
                total[path] += effect
            else:
                total[path] = effect
        
        return total

print("Structural Equation Modeling Module Loaded!")
