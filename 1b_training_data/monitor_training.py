import json
import os
from datetime import datetime

def monitor_training(log_dir='logs'):
    print("=== Erbing Training Monitor ===")
    print()
    
    if not os.path.exists(log_dir):
        print(f"Log directory not found: {log_dir}")
        return
    
    # Find latest checkpoint
    checkpoints = [f for f in os.listdir(log_dir) if f.startswith('checkpoint_') and f.endswith('.json')]
    
    if not checkpoints:
        print("No checkpoints found.")
        return
    
    latest_checkpoint = max(checkpoints)
    checkpoint_path = os.path.join(log_dir, latest_checkpoint)
    
    print(f"Latest Checkpoint: {latest_checkpoint}")
    print()
    
    with open(checkpoint_path, 'r', encoding='utf-8') as f:
        checkpoint = json.load(f)
    
    print("=== Training Progress ===")
    print(f"  Timestamp: {checkpoint['timestamp']}")
    print(f"  Episode: {checkpoint['episode']}")
    print(f"  Total Episodes: {checkpoint['total_episodes']}")
    print(f"  Total Steps: {checkpoint['total_steps']}")
    print(f"  Total Reward: {checkpoint['total_reward']:.2f}")
    print(f"  Average Reward: {checkpoint['total_reward'] / checkpoint['total_episodes']:.2f}")
    print(f"  Best Reward: {checkpoint['best_reward']:.2f}")
    print(f"  Worst Reward: {checkpoint['worst_reward']:.2f}")
    print()
    
    stats = checkpoint['stats']
    print("=== Current Stats ===")
    print(f"  Energy: {stats['energy']}/{stats['max_energy']}")
    print(f"  Knowledge: {stats['knowledge_count']}")
    print(f"  Experiences: {stats['experience_count']}")
    print()
    
    print("=== Skills ===")
    for skill in stats['skills']:
        print(f"  {skill['name']}: Level {skill['level']}, {skill['experience']} exp")
    print()
    
    # Find latest log file
    log_files = [f for f in os.listdir(log_dir) if f.startswith('training_') and f.endswith('.log')]
    
    if log_files:
        latest_log = max(log_files)
        log_path = os.path.join(log_dir, latest_log)
        
        print(f"Latest Log: {latest_log}")
        print()
        
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print("=== Recent Activity (Last 20 lines) ===")
        for line in lines[-20:]:
            print(line.rstrip())
    else:
        print("No log files found.")

if __name__ == '__main__':
    monitor_training()
