"""
Erbing Virtual World - Main Controller
Complete Virtual World Evolution Environment
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any

from capsule_interface import CapsuleInterface
from mission_simulator import MissionSimulator
from adversarial_arena import AdversarialArena
from security_bridge import SecurityBridge


class VirtualWorldEvolution:
    """
    Complete Virtual World Evolution Environment
    Integrates mission simulator, adversarial arena, security bridge, and capsule interface
    """
    
    def __init__(self):
        print("=" * 60)
        print("  Erbing Virtual World Evolution Environment")
        print("=" * 60)
        print()
        
        # Initialize components
        print("[1/4] Initializing Capsule Interface...")
        self.capsule_interface = CapsuleInterface()
        print("      [OK] Capsule Interface ready")
        
        print("[2/4] Initializing Mission Simulator...")
        self.mission_simulator = MissionSimulator()
        print("      [OK] Mission Simulator ready")
        
        print("[3/4] Initializing Adversarial Arena...")
        self.adversarial_arena = AdversarialArena()
        print("      [OK] Adversarial Arena ready")
        
        print("[4/4] Initializing Security Bridge...")
        self.security_bridge = SecurityBridge()
        print("      [OK] Security Bridge ready")
        
        print()
        print("=" * 60)
        print("  All systems initialized successfully!")
        print("=" * 60)
        print()
    
    def start_evolution(self, agent_id: str = "erbing_default") -> Dict:
        """
        Start evolution process
        """
        print("\n" + "=" * 60)
        print("  >> Starting Evolution Process")
        print("=" * 60)
        print()
        
        # Step 1: Create security session
        print("[Step 1/5] Creating security session...")
        security_context = self.security_bridge.create_session(
            capsule_id=agent_id,
            security_level=3,
            duration_hours=24
        )
        print(f"          Session Token: {security_context.session_token[:20]}...")
        print(f"          Security Level: {security_context.security_level}")
        print(f"          Expires At: {security_context.expires_at}")
        print()
        
        # Step 2: Enter capsule
        print("[Step 2/5] Entering capsule...")
        capsule_id = self.capsule_interface.enter_capsule(agent_id)
        print(f"          Capsule ID: {capsule_id}")
        print(f"          Status: Active")
        print()
        
        # Step 3: Generate initial mission
        print("[Step 3/5] Generating initial mission...")
        mission = self.mission_simulator.generate_mission(
            capsule_id=capsule_id,
            difficulty_range=(1, 3)
        )
        print(f"          Mission ID: {mission.mission_id}")
        print(f"          Type: {mission.mission_type}")
        print(f"          Difficulty: {mission.difficulty}")
        print(f"          Title: {mission.title}")
        print()
        
        # Step 4: Configure training environment
        print("[Step 4/5] Configuring training environment...")
        match = self.adversarial_arena.start_match(
            capsule_id=capsule_id,
            match_type='pve'
        )
        print(f"          Match ID: {match.match_id}")
        print(f"          Opponent: {match.opponent.name} (Lvl {match.opponent.level})")
        print()
        
        # Step 5: Initialization complete
        print("[Step 5/5] Evolution environment ready!")
        print()
        
        print("=" * 60)
        print("  [SUCCESS] Evolution process started!")
        print("=" * 60)
        print()
        
        return {
            'status': 'success',
            'capsule_id': capsule_id,
            'session_token': security_context.session_token,
            'initial_mission': {
                'mission_id': mission.mission_id,
                'type': mission.mission_type,
                'difficulty': mission.difficulty,
                'title': mission.title
            },
            'training_match': {
                'match_id': match.match_id,
                'opponent': match.opponent.name,
                'opponent_level': match.opponent.level
            }
        }
    
    def run_training_cycle(self, capsule_id: str) -> Dict:
        """
        Run training cycle
        """
        print(f"\n--- Training Cycle for {capsule_id} ---")
        
        # 1. Execute mission
        print("[Training] Executing mission...")
        mission = self.mission_simulator.generate_mission(
            capsule_id=capsule_id,
            difficulty_range=(1, 5)
        )
        
        # Simulate mission execution
        mission_result = random.choice(['success', 'partial', 'failed'])
        score = random.uniform(0.3, 1.0) if mission_result != 'failed' else random.uniform(0, 0.3)
        
        result = self.mission_simulator.complete_mission(
            mission.mission_id,
            mission_result,
            score,
            mission.objectives[:int(len(mission.objectives) * score)]
        )
        
        print(f"          Mission: {mission.title}")
        print(f"          Result: {mission_result} (Score: {score:.2f})")
        print(f"          XP Gained: {result.get('xp_earned', 0)}")
        
        # 2. Arena training
        print("[Training] Running arena match...")
        match = self.adversarial_arena.start_match(capsule_id=capsule_id)
        
        # Simulate match
        match_result = random.choice(['win', 'lose', 'draw'])
        match_score = random.uniform(0.4, 1.0) if match_result == 'win' else random.uniform(0.2, 0.6)
        
        arena_result = self.adversarial_arena.end_match(
            match.match_id,
            match_result,
            match_score
        )
        
        print(f"          Opponent: {match.opponent.name}")
        print(f"          Result: {match_result} (Score: {match_score:.2f})")
        print(f"          XP Gained: {arena_result['xp_gained']}")
        
        # 3. Update status
        capsule_state = self.capsule_interface.get_capsule_state(capsule_id)
        
        return {
            'mission': {
                'id': mission.mission_id,
                'result': mission_result,
                'score': score,
                'xp': result.get('xp_earned', 0)
            },
            'arena': {
                'id': match.match_id,
                'result': match_result,
                'score': match_score,
                'xp': arena_result['xp_gained']
            },
            'capsule_state': {
                'level': capsule_state.level if capsule_state else 1,
                'xp': capsule_state.xp if capsule_state else 0,
                'energy': capsule_state.energy if capsule_state else 100
            }
        }
    
    def get_status(self, capsule_id: str) -> Dict:
        """
        Get evolution status
        """
        capsule_state = self.capsule_interface.get_capsule_state(capsule_id)
        mission_stats = self.mission_simulator.get_mission_stats(capsule_id)
        security_report = self.security_bridge.get_security_report(capsule_id)
        
        return {
            'capsule': {
                'id': capsule_id,
                'level': capsule_state.level if capsule_state else 1,
                'xp': capsule_state.xp if capsule_state else 0,
                'energy': capsule_state.energy if capsule_state else 100,
                'status': capsule_state.status if capsule_state else 'unknown'
            },
            'missions': mission_stats,
            'security': security_report
        }
    
    def stop_evolution(self, capsule_id: str) -> Dict:
        """
        Stop evolution process
        """
        print(f"\n=== Stopping Evolution for {capsule_id} ===")
        
        # Exit capsule
        result = self.capsule_interface.exit_capsule(capsule_id)
        
        # Get final report
        final_report = self.get_status(capsule_id)
        
        print("\n" + "=" * 60)
        print("  Evolution Process Completed!")
        print("=" * 60)
        print()
        
        return {
            'status': 'completed',
            'exit_result': result,
            'final_report': final_report
        }


def interactive_menu():
    """
    Interactive menu
    """
    world = VirtualWorldEvolution()
    
    current_capsule_id = None
    
    while True:
        print("\n" + "-" * 60)
        print("  Virtual World Evolution Environment")
        print("-" * 60)
        print()
        print("  [1] Start Evolution Process")
        print("  [2] Run Training Cycle")
        print("  [3] Check Status")
        print("  [4] Stop Evolution")
        print("  [5] View Mission List")
        print("  [6] View Opponents")
        print("  [0] Exit")
        print()
        
        choice = input("  Select option > ").strip()
        
        if choice == '1':
            agent_id = input("  Enter agent ID (default: erbing_default) > ").strip()
            if not agent_id:
                agent_id = "erbing_default"
            result = world.start_evolution(agent_id)
            current_capsule_id = result.get('capsule_id')
            
        elif choice == '2':
            if not current_capsule_id:
                print("  [ERROR] Please start evolution first")
            else:
                result = world.run_training_cycle(current_capsule_id)
                print(f"\n  Training Result:")
                print(f"  Mission: {result['mission']['result']} (XP: {result['mission']['xp']})")
                print(f"  Arena: {result['arena']['result']} (XP: {result['arena']['xp']})")
                print(f"  Capsule Level: {result['capsule_state']['level']}")
                print(f"  Capsule XP: {result['capsule_state']['xp']}")
                
        elif choice == '3':
            if not current_capsule_id:
                print("  [ERROR] Please start evolution first")
            else:
                status = world.get_status(current_capsule_id)
                print(f"\n  Capsule Status:")
                print(f"  ID: {status['capsule']['id']}")
                print(f"  Level: {status['capsule']['level']}")
                print(f"  XP: {status['capsule']['xp']}")
                print(f"  Energy: {status['capsule']['energy']}")
                print(f"  Status: {status['capsule']['status']}")
                print(f"\n  Mission Stats:")
                print(f"  Total: {status['missions']['total_missions']}")
                print(f"  Completed: {status['missions']['completed_missions']}")
                print(f"  Success Rate: {status['missions']['success_rate']:.1%}")
                print(f"  Avg Score: {status['missions']['avg_score']:.2f}")
                print(f"\n  Security Score: {status['security']['security_score']:.1f}/100")
                
        elif choice == '4':
            if not current_capsule_id:
                print("  [ERROR] Please start evolution first")
            else:
                result = world.stop_evolution(current_capsule_id)
                current_capsule_id = None
                
        elif choice == '5':
            missions = world.mission_simulator.get_available_missions(current_capsule_id or 'default')
            print(f"\n  Available Missions ({len(missions)}):")
            for m in missions[:10]:
                print(f"  [{m['difficulty']}] {m['title']} ({m['mission_type']}) - XP: {m['xp_reward']}")
                
        elif choice == '6':
            print(f"\n  Sample Opponents:")
            for i in range(5):
                opp = world.adversarial_arena.get_random_opponent()
                print(f"  {opp.name} (Lvl {opp.level}) - Style: {opp.style}")
                
        elif choice == '0':
            print("\n  Exiting Virtual World...")
            break
            
        else:
            print("  [ERROR] Invalid option, please try again")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  Welcome to Erbing Virtual World Evolution Environment")
    print("=" * 60)
    print()
    
    interactive_menu()
