import sqlite3
import json
import time
import os
from datetime import datetime
from erbing_auto_evolution import ErbingAutoEvolution

class ErbingContinuousTrainer:
    def __init__(self, db_path='erbing_virtual_world.db', log_dir='logs'):
        import os
        
        self.db_path = db_path
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Use absolute path for database
        abs_db_path = os.path.abspath(db_path)
        print(f'Using database: {abs_db_path}')
        
        self.world = ErbingAutoEvolution(abs_db_path)
        
        self.start_time = datetime.now()
        self.total_episodes = 0
        self.total_steps = 0
        self.total_reward = 0.0
        self.best_reward = float('-inf')
        self.worst_reward = float('inf')
        
        self.log_file = os.path.join(log_dir, f'training_{self.start_time.strftime("%Y%m%d_%H%M%S")}.log')
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def save_checkpoint(self, episode, reward):
        checkpoint_file = os.path.join(self.log_dir, f'checkpoint_{episode}.json')
        
        stats = self.world.world.get_stats()
        
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'episode': episode,
            'total_episodes': self.total_episodes,
            'total_steps': self.total_steps,
            'total_reward': self.total_reward,
            'best_reward': self.best_reward,
            'worst_reward': self.worst_reward,
            'stats': stats
        }
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        
        self.log(f"Checkpoint saved: {checkpoint_file}")
    
    def run_episode(self, episode_num, max_steps=100):
        self.log(f"=== Starting Episode {episode_num} ===")
        
        episode_reward = 0.0
        step = 0
        
        for step in range(max_steps):
            action, param1, param2 = self.world.decide_action()
            
            if action == 'explore':
                result = self.world.world.explore(param1, param2)
                if result['success']:
                    episode_reward += result['reward']
            
            elif action == 'learn':
                result = self.world.world.learn(param1, param2)
                if result['success']:
                    episode_reward += result['reward']
            
            elif action == 'practice':
                result = self.world.world.practice(param1, param2)
                if result['success']:
                    episode_reward += result['reward']
            
            elif action == 'rest':
                result = self.world.world.rest()
                if result['success']:
                    episode_reward += result.get('recovered', 0.0)
            
            if step % 10 == 9:
                stats = self.world.world.get_stats()
                self.log(f"  Step {step + 1}: Energy {stats['energy']}/{stats['max_energy']}, Reward {episode_reward:.2f}")
        
        self.total_episodes += 1
        self.total_steps += step + 1
        self.total_reward += episode_reward
        
        if episode_reward > self.best_reward:
            self.best_reward = episode_reward
            self.log(f"  New best reward: {episode_reward:.2f}")
        
        if episode_reward < self.worst_reward:
            self.worst_reward = episode_reward
            self.log(f"  New worst reward: {episode_reward:.2f}")
        
        stats = self.world.world.get_stats()
        self.log(f"=== Episode {episode_num} Complete ===")
        self.log(f"  Steps: {step + 1}")
        self.log(f"  Reward: {episode_reward:.2f}")
        self.log(f"  Energy: {stats['energy']}/{stats['max_energy']}")
        self.log(f"  Knowledge: {stats['knowledge_count']}")
        self.log(f"  Experiences: {stats['experience_count']}")
        
        for skill in stats['skills']:
            self.log(f"  {skill['name']}: Level {skill['level']}, {skill['experience']} exp")
        
        self.log(f"  Total Episodes: {self.total_episodes}")
        self.log(f"  Total Steps: {self.total_steps}")
        self.log(f"  Total Reward: {self.total_reward:.2f}")
        self.log(f"  Average Reward: {self.total_reward / self.total_episodes:.2f}")
        self.log(f"  Best Reward: {self.best_reward:.2f}")
        self.log(f"  Worst Reward: {self.worst_reward:.2f}")
        
        return episode_reward
    
    def run_continuous(self, save_interval=10, max_steps=100):
        self.log("=== Starting Continuous Training ===")
        self.log(f"  Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"  Save Interval: Every {save_interval} episodes")
        self.log(f"  Max Steps per Episode: {max_steps}")
        self.log("")
        
        episode_num = 1
        
        try:
            while True:
                reward = self.run_episode(episode_num, max_steps)
                
                if episode_num % save_interval == 0:
                    self.save_checkpoint(episode_num, reward)
                    
                    stats = self.world.world.get_stats()
                    self.log("")
                    self.log("=== Training Summary ===")
                    self.log(f"  Episodes: {self.total_episodes}")
                    self.log(f"  Total Steps: {self.total_steps}")
                    self.log(f"  Total Reward: {self.total_reward:.2f}")
                    self.log(f"  Average Reward: {self.total_reward / self.total_episodes:.2f}")
                    self.log(f"  Best Reward: {self.best_reward:.2f}")
                    self.log(f"  Worst Reward: {self.worst_reward:.2f}")
                    self.log(f"  Knowledge: {stats['knowledge_count']}")
                    self.log(f"  Experiences: {stats['experience_count']}")
                    self.log("")
                
                episode_num += 1
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.log("")
            self.log("=== Training Interrupted ===")
            self.save_checkpoint(episode_num - 1, reward)
            
            elapsed = datetime.now() - self.start_time
            self.log(f"  Elapsed Time: {elapsed}")
            self.log(f"  Total Episodes: {self.total_episodes}")
            self.log(f"  Total Steps: {self.total_steps}")
            self.log(f"  Total Reward: {self.total_reward:.2f}")
            self.log(f"  Average Reward: {self.total_reward / self.total_episodes:.2f}")
            self.log(f"  Best Reward: {self.best_reward:.2f}")
            self.log(f"  Worst Reward: {self.worst_reward:.2f}")
            
            stats = self.world.world.get_stats()
            self.log(f"  Final Energy: {stats['energy']}/{stats['max_energy']}")
            self.log(f"  Final Knowledge: {stats['knowledge_count']}")
            self.log(f"  Final Experiences: {stats['experience_count']}")
            
            self.log("")
            self.log("=== Final Skills ===")
            for skill in stats['skills']:
                self.log(f"  {skill['name']}: Level {skill['level']}, {skill['experience']} exp")
            
            self.log("")
            self.log("Training stopped. Checkpoint saved.")

if __name__ == '__main__':
    trainer = ErbingContinuousTrainer()
    
    print("=== Erbing Continuous Training System ===")
    print()
    print("This will run 24/7 continuous training.")
    print("Press Ctrl+C to stop and save checkpoint.")
    print()
    
    trainer.run_continuous(save_interval=10, max_steps=100)
