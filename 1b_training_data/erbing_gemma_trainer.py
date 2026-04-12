import sqlite3
import json
from datetime import datetime
from erbing_auto_evolution import ErbingAutoEvolution

class ErbingGemmaTrainer:
    def __init__(self, db_path='erbing_virtual_world.db'):
        self.world = ErbingAutoEvolution(db_path)
        self.training_data = []
        self.virtual_world = self.world.world
    
    def collect_training_data(self, episodes=10, max_steps=100):
        print(f'=== Collecting Training Data ({episodes} episodes) ===')
        print()
        
        for episode in range(episodes):
            print(f'--- Episode {episode + 1}/{episodes} ---')
            
            for step in range(max_steps):
                action, param1, param2 = self.world.decide_action()
                
                state = self.world.world.get_stats()
                
                if action == 'explore':
                    result = self.world.world.explore(param1, param2)
                elif action == 'learn':
                    result = self.world.world.learn(param1, param2)
                elif action == 'practice':
                    result = self.world.world.practice(param1, param2)
                elif action == 'rest':
                    result = self.world.world.rest()
                
                next_state = self.world.world.get_stats()
                
                training_sample = {
                    'state': state,
                    'action': action,
                    'params': [param1, param2],
                    'reward': result.get('reward', 0.0) or result.get('recovered', 0.0),
                    'next_state': next_state,
                    'done': False
                }
                
                self.training_data.append(training_sample)
            
            print(f'  Collected {max_steps} samples')
            print()
        
        print(f'=== Training Data Collection Complete ===')
        print(f'Total samples: {len(self.training_data)}')
        
        return self.training_data
    
    def save_training_data(self, filepath='erbing_training_data.jsonl'):
        print(f'=== Saving Training Data to {filepath} ===')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for sample in self.training_data:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f'Saved {len(self.training_data)} samples to {filepath}')
    
    def generate_training_prompts(self, filepath='erbing_training_prompts.jsonl'):
        print(f'=== Generating Training Prompts to {filepath} ===')
        
        prompts = []
        
        for sample in self.training_data:
            state = sample['state']
            action = sample['action']
            params = sample['params']
            reward = sample['reward']
            
            skills_str = ', '.join([f"{s['name']}: Level {s['level']}, {s['experience']} exp" for s in state['skills']])
            
            prompt = f"""You are Erbing, an AI assistant with the following state:

Energy: {state['energy']}/{state['max_energy']}
Skills: {skills_str}
Knowledge: {state['knowledge_count']} items
Experiences: {state['experience_count']} items

You decided to: {action} {params[0] if params[0] else ''} {params[1] if params[1] else ''}

This action resulted in a reward of {reward:.2f}

What would you do next?"""

            response = f"""Based on my current state and the reward I received, I should:

1. Analyze the reward: {reward:.2f} is {'good' if reward > 0 else 'bad'}
2. Consider my energy: {state['energy']}/{state['max_energy']}
3. Evaluate my skills: {skills_str}
4. Choose the best action: {'rest' if state['energy'] < 30 else 'learn or practice'}

My next action would be: {'rest' if state['energy'] < 30 else 'learn a skill'}"""

            prompts.append({
                'prompt': prompt,
                'response': response
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for prompt_data in prompts:
                f.write(json.dumps(prompt_data, ensure_ascii=False) + '\n')
        
        print(f'Generated {len(prompts)} prompts to {filepath}')

if __name__ == '__main__':
    trainer = ErbingGemmaTrainer()
    
    print('=== Erbing Gemma Trainer ===')
    print()
    
    data = trainer.collect_training_data(episodes=3, max_steps=30)
    
    trainer.save_training_data('erbing_training_data.jsonl')
    
    trainer.generate_training_prompts('erbing_training_prompts.jsonl')
    
    print()
    print('=== Training Complete ===')
    print(f'Total samples: {len(data)}')
    print('Training data saved to: erbing_training_data.jsonl')
    print('Training prompts saved to: erbing_training_prompts.jsonl')
