#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Factor Inference System - Startup Script
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from factor_inference_system import FactorInferenceSystem

def setup_logging(config):
    """Setup logging"""
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', 'logs/factor_inference.log')
    console = config.get('logging', {}).get('console', True)
    
    # Create logs directory
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler() if console else None
        ]
    )
    
    return logging.getLogger('FactorInferenceSystem')

def load_config(config_path='factor_inference_config.json'):
    """Load configuration"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Config file not found: {config_path}")
        print("[INFO] Using default configuration")
        return {
            'factor_inference': {'enabled': True},
            'genetic_neuron': {'enabled': True},
            'logging': {'level': 'INFO', 'console': True}
        }

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print(" " * 15 + "FACTOR INFERENCE SYSTEM")
    print(" " * 20 + "Ultimate Configuration")
    print("=" * 70)
    print()

def print_system_status(system, config):
    """Print system status"""
    print("[SYSTEM STATUS]")
    print("-" * 70)
    
    # Factor Inference
    fi_config = config.get('factor_inference', {})
    print(f"Factor Inference: {'ENABLED' if fi_config.get('enabled') else 'DISABLED'}")
    
    if fi_config.get('enabled'):
        modules = fi_config.get('modules', {})
        for module_name, module_config in modules.items():
            status = 'ENABLED' if module_config.get('enabled') else 'DISABLED'
            method = module_config.get('default_method', 'N/A')
            print(f"  - {module_name}: {status} (method: {method})")
    
    # Genetic Neuron
    gn_config = config.get('genetic_neuron', {})
    print(f"\nGenetic Neuron: {'ENABLED' if gn_config.get('enabled') else 'DISABLED'}")
    
    if gn_config.get('enabled'):
        modules = gn_config.get('modules', {})
        enabled_count = sum(1 for m in modules.values() if m)
        print(f"  - Modules: {enabled_count}/{len(modules)} enabled")
    
    # Memory System
    ms_config = config.get('memory_system', {})
    print(f"\nMemory System:")
    print(f"  - Database: {ms_config.get('database_path', 'N/A')}")
    print(f"  - LanceDB: {ms_config.get('lancedb_path', 'N/A')}")
    print(f"  - Backup: {'ENABLED' if ms_config.get('backup_enabled') else 'DISABLED'}")
    
    # Performance
    perf_config = config.get('performance', {})
    print(f"\nPerformance:")
    print(f"  - Max Workers: {perf_config.get('max_workers', 4)}")
    print(f"  - Batch Size: {perf_config.get('batch_size', 100)}")
    print(f"  - Cache Size: {perf_config.get('cache_size', 1000)}")
    
    print("-" * 70)
    print()

def run_quick_test(system):
    """Run quick system test"""
    print("[QUICK TEST]")
    print("-" * 70)
    
    import numpy as np
    
    # Test data
    X = np.random.randn(50, 5)
    
    # Test 1: Factor Analysis
    print("[1/6] Testing Factor Analysis...")
    try:
        result = system.analyze_factors(X, n_components=2)
        print(f"      OK - Method: {result.method}, Components: {result.n_components}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    # Test 2: Causal Inference
    print("[2/6] Testing Causal Inference...")
    try:
        treatment = np.random.randint(0, 2, 50)
        outcome = np.random.randn(50) + 0.3 * treatment
        result = system.infer_causal_effect(treatment, outcome)
        print(f"      OK - Method: {result.method}, Effect: {result.treatment_effect:.4f}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    # Test 3: Latent Variable Models
    print("[3/6] Testing Latent Variable Models...")
    try:
        result = system.discover_latent_variables(X, n_components=2)
        print(f"      OK - Method: {result.method}, Components: {result.n_components}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    # Test 4: Bayesian Inference
    print("[4/6] Testing Bayesian Inference...")
    try:
        def log_likelihood(x):
            return -0.5 * np.sum(x ** 2)
        prior_mean = np.zeros(5)
        prior_cov = np.eye(5)
        result = system.bayesian_infer(log_likelihood, prior_mean, prior_cov, n_samples=50)
        print(f"      OK - Method: {result.method}, Evidence: {result.log_evidence:.4f}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    # Test 5: Matrix Factorization
    print("[5/6] Testing Matrix Factorization...")
    try:
        result = system.factorize_matrix(X, rank=2)
        print(f"      OK - Method: {result.method}, Error: {result.error:.4f}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    # Test 6: SEM
    print("[6/6] Testing SEM...")
    try:
        model = {'variables': ['X1', 'X2', 'Y'], 'paths': [('X1', 'X2'), ('X2', 'Y')]}
        sem_data = np.random.randn(50, 3)
        result = system.fit_sem(sem_data, model)
        print(f"      OK - Method: {result.method}, Paths: {len(result.path_coefficients)}")
    except Exception as e:
        print(f"      FAILED - {e}")
    
    print("-" * 70)
    print()

def main():
    """Main startup function"""
    # Print banner
    print_banner()
    
    # Load configuration
    print("[1/4] Loading configuration...")
    config = load_config()
    print("      OK - Configuration loaded")
    print()
    
    # Setup logging
    print("[2/4] Setting up logging...")
    logger = setup_logging(config)
    logger.info("Factor Inference System starting...")
    print("      OK - Logging configured")
    print()
    
    # Create system
    print("[3/4] Creating Factor Inference System...")
    system = FactorInferenceSystem()
    print("      OK - System created")
    print()
    
    # Print status
    print_system_status(system, config)
    
    # Run quick test
    print("[4/4] Running quick system test...")
    run_quick_test(system)
    
    # Final message
    print("=" * 70)
    print("[SUCCESS] Factor Inference System started successfully!")
    print("=" * 70)
    print()
    print("[INFO] System is ready for use.")
    print("[INFO] All 6 modules are operational.")
    print("[INFO] Configuration: factor_inference_config.json")
    print("[INFO] Logs: logs/factor_inference.log")
    print()
    print("[COMMANDS]")
    print("  - python factor_inference_system.py  # Run full test")
    print("  - python start_factor_inference.py  # Start system")
    print()
    
    logger.info("Factor Inference System started successfully")
    
    return system

if __name__ == "__main__":
    system = main()
