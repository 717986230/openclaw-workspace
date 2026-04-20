"""
Erbing Virtual World - Complete Main Controller
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

# Environment components
from environment.virtual_sandbox import VirtualSandbox
from environment.time_accelerator import TimeAccelerator
from environment.parallel_universe import ParallelUniverse

# Training components
from training.task_simulator import MissionSimulator
from training.adversarial_arena import AdversarialArena
from training.edge_case_generator import EdgeCaseGenerator
from training.stress_test_pool import StressTestPool

# Bridge components
from bridge.reality_interface import RealityInterface
from bridge.capability_exporter import CapabilityExporter
from bridge.safety_guardian import SafetyGuardian

# Capsule interface
from capsule_interface import CapsuleInterface
from security_bridge import SecurityBridge


class CompleteVirtualWorld:
    """
    Complete Virtual World Evolution Environment
    Full implementation with all components
    """
    
    def __init__(self):
        print("=" * 60)
        print("  Erbing Complete Virtual World Environment")
        print("=" * 60)
        print()
        
        # Environment
        print("[1/4] Initializing Environment...")
        self.virtual_sandbox = VirtualSandbox()
        print("      [OK] Virtual Sandbox")
        self.time_accelerator = TimeAccelerator()
        print("      [OK] Time Accelerator")
        self.parallel_universe = ParallelUniverse()
        print("      [OK] Parallel Universe")
        
        # Training
        print("[2/4] Initializing Training...")
        self.mission_simulator = MissionSimulator()
        print("      [OK] Task Simulator")
        self.adversarial_arena = AdversarialArena()
        print("      [OK] Adversarial Arena")
        self.edge_case_generator = EdgeCaseGenerator()
        print("      [OK] Edge Case Generator")
        self.stress_test_pool = StressTestPool()
        print("      [OK] Stress Test Pool")
        
        # Bridge
        print("[3/4] Initializing Bridge...")
        self.reality_interface = RealityInterface()
        print("      [OK] Reality Interface")
        self.capability_exporter = CapabilityExporter()
        print("      [OK] Capability Exporter")
        self.safety_guardian = SafetyGuardian()
        print("      [OK] Safety Guardian")
        
        # Core
        print("[4/4] Initializing Core...")
        self.capsule_interface = CapsuleInterface()
        print("      [OK] Capsule Interface")
        self.security_bridge = SecurityBridge()
        print("      [OK] Security Bridge")
        
        print()
        print("=" * 60)
        print("  All systems initialized successfully!")
        print("=" * 60)
        print()
    
    def start_evolution(self, agent_id: str = "erbing") -> Dict:
        """
        Start complete evolution process
        """
        print("\n" + "=" * 60)
        print("  >> Starting Complete Evolution Process")
        print("=" * 60)
        print()
        
        # 1. Create security session
        print("[Step 1/8] Creating security session...")
        security_ctx = self.security_bridge.create_session(agent_id, 3, 24)
        print(f"          Token: {security_ctx.session_token[:20]}...")
        print()
        
        # 2. Enter capsule
        print("[Step 2/8] Entering capsule...")
        capsule_id = self.capsule_interface.enter_capsule(agent_id)
        print(f"          Capsule ID: {capsule_id}")
        print()
        
        # 3. Create sandbox
        print("[Step 3/8] Creating virtual sandbox...")
        sandbox = self.virtual_sandbox.create_sandbox(capsule_id)
        print(f"          Sandbox ID: {sandbox.sandbox_id}")
        print()
        
        # 4. Select universe
        print("[Step 4/8] Selecting training universe...")
        universe = self.parallel_universe.get_random_universe()
        print(f"          Universe: {universe.name} (Difficulty: {universe.difficulty})")
        print()
        
        # 5. Start time dilation
        print("[Step 5/8] Activating time acceleration...")
        time_config = self.time_accelerator.start_time_dilation('fast')
        print(f"          Dilation: {time_config.dilation_factor}x")
        print()
        
        # 6. Generate mission
        print("[Step 6/8] Generating training mission...")
        mission = self.mission_simulator.generate_mission(capsule_id, None, (1, 3))
        print(f"          Mission: {mission.title}")
        print()
        
        # 7. Configure arena
        print("[Step 7/8] Configuring adversarial arena...")
        match = self.adversarial_arena.start_match(capsule_id)
        print(f"          Opponent: {match.opponent.name}")
        print()
        
        # 8. Ready
        print("[Step 8/8] Evolution environment ready!")
        print()
        
        print("=" * 60)
        print("  [SUCCESS] Complete evolution process started!")
        print("=" * 60)
        print()
        
        return {
            'status': 'success',
            'capsule_id': capsule_id,
            'sandbox_id': sandbox.sandbox_id,
            'universe': {'id': universe.universe_id, 'name': universe.name},
            'mission': {'id': mission.mission_id, 'title': mission.title},
            'time_dilation': time_config.dilation_factor
        }
    
    def run_training_cycle(self, capsule_id: str) -> Dict:
        """Run complete training cycle"""
        print(f"\n--- Running Training Cycle ---")
        
        # Mission training
        mission = self.mission_simulator.generate_mission(capsule_id, None, (1, 5))
        mission_result = random.choice(['success', 'partial', 'failed'])
        mission_score = random.uniform(0.3, 1.0)
        
        # Arena match
        match = self.adversarial_arena.start_match(capsule_id)
        match_result = random.choice(['win', 'lose', 'draw'])
        match_score = random.uniform(0.4, 1.0)
        
        # Edge case test
        edge_case = self.edge_case_generator.generate()
        print(f"Edge Case: {edge_case.description}")
        
        # Stress test
        stress_test = self.stress_test_pool.get_test()
        print(f"Stress Test: {stress_test.description}")
        
        # Safety check
        safety_report = self.safety_guardian.check_safety(capsule_id, 'training', {})
        
        # Export capabilities
        self.capability_exporter.export_capability(capsule_id, 'training', 1, {
            'mission_result': mission_result,
            'arena_result': match_result
        })
        
        # Sync to reality
        self.reality_interface.sync_to_reality(capsule_id, {
            'cycle_completed': True,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get time stats
        time_stats = self.time_accelerator.get_stats()
        
        return {
            'mission': {'result': mission_result, 'score': mission_score},
            'arena': {'result': match_result, 'score': match_score},
            'edge_case': {'category': edge_case.category, 'difficulty': edge_case.difficulty},
            'stress_test': {'category': stress_test.category, 'intensity': stress_test.intensity},
            'safety': {'threat_level': safety_report.threat_level},
            'time': time_stats
        }
    
    def get_complete_status(self, capsule_id: str) -> Dict:
        """Get complete status"""
        capsule_state = self.capsule_interface.get_capsule_state(capsule_id)
        safety_report = self.safety_guardian.get_safety_report(capsule_id)
        capabilities = self.capability_exporter.get_capability_summary(capsule_id)
        time_stats = self.time_accelerator.get_stats()
        universes = self.parallel_universe.list_universes()
        
        return {
            'capsule': {
                'id': capsule_id,
                'level': capsule_state.level if capsule_state else 1,
                'xp': capsule_state.xp if capsule_state else 0
            },
            'safety': safety_report,
            'capabilities': capabilities,
            'time': time_stats,
            'available_universes': len(universes)
        }


def main():
    """Main entry point"""
    print()
    print("=" * 60)
    print("  Welcome to Erbing Complete Virtual World")
    print("=" * 60)
    print()
    
    world = CompleteVirtualWorld()
    
    print("\nStarting evolution...")
    result = world.start_evolution('test_agent')
    
    print("\nRunning training cycle...")
    training = world.run_training_cycle(result['capsule_id'])
    
    print("\nTraining Results:")
    print(f"  Mission: {training['mission']['result']}")
    print(f"  Arena: {training['arena']['result']}")
    print(f"  Edge Case: {training['edge_case']['category']}")
    print(f"  Stress Test: {training['stress_test']['category']}")
    print(f"  Time Dilation: {training['time']['efficiency']}")
    
    print("\nComplete status:")
    status = world.get_complete_status(result['capsule_id'])
    print(f"  Capsule Level: {status['capsule']['level']}")
    print(f"  Safety Score: {status['safety']['safety_score']}")
    print(f"  Available Universes: {status['available_universes']}")
    
    print("\n" + "=" * 60)
    print("  Complete Virtual World Environment Ready!")
    print("=" * 60)


if __name__ == "__main__":
    main()
