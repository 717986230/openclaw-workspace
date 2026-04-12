import sqlite3
import random
from datetime import datetime
from erbing_virtual_world import ErbingVirtualWorld

class ErbingAutoEvolution:
    def __init__(self, db_path='erbing_virtual_world.db'):
        self.world = ErbingVirtualWorld(db_path)
        self.actions = ['explore', 'learn', 'practice', 'rest']
        self.domains = ['Coding', 'AI Tech', 'Security', 'Deployment', 'Tool Use', 'Problem Solving', 'Communication', 'Collaboration', 'Dark Web', 'Code Intelligence', 'AI Agent', 'Advanced Coding', 'Advanced AI', 'Advanced Security', 'Advanced Data']
        self.topics = ['Python', 'JavaScript', 'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Web Development', 'API Design', 'Database', 'Cloud Computing', 'DevOps', 'Testing', 'Security', 'Optimization', 'Architecture',
                       # LLM Knowledge
                       'Transformer Architecture', 'GPT Series', 'Claude Series', 'Gemini Series', 'Llama Series', 'Mistral Series', 'Qwen Series', 'DeepSeek Series',
                       'Pre-training', 'Fine-tuning', 'Constitutional AI', 'Efficient Training',
                       'Quantization', 'Speculative Decoding', 'KV Cache Optimization',
                       'Chain-of-Thought', 'Tool Use', 'RAG', 'Multimodal',
                       'Coding Assistants', 'Research Assistants', 'Creative Writing',
                       # Hacker Knowledge
                       'Reconnaissance', 'Vulnerability Assessment', 'Exploitation', 'Post-Exploitation',
                       'OWASP Top 10', 'Advanced Web Attacks', 'API Security',
                       'Network Attacks', 'Wireless Security', 'Firewall Evasion',
                       'Privilege Escalation', 'Malware Analysis', 'Rootkits',
                       'Cryptographic Attacks', 'SSL/TLS Attacks', 'Password Cracking',
                       'Phishing', 'Psychological Manipulation',
                       'Zero-Day Exploits', 'APT', 'Red Teaming',
                       'SIEM', 'Endpoint Detection', 'Incident Response', 'Threat Intelligence',
                       # Dark Web Knowledge
                       'Tor Network', 'Onion Routing', 'Hidden Services', 'Darknet Markets',
                       'Cryptocurrency', 'Threat Actor Communities', 'Data Leaks',
                       'OSINT Techniques', 'Security Risks', 'Legal Considerations',
                       # Code Intelligence Knowledge
                       'GitNexus Overview', 'Knowledge Graph for Code', 'MCP Integration',
                       'CLI Commands', '16 MCP Tools', 'Resources',
                       'Agent Skills', 'Multi-Repo Architecture', 'LadybugDB',
                       'Enterprise Features', 'Web UI', 'Bridge Mode',
                       'Community Integrations', 'Safety Features',
                       # AI Agent Knowledge
                       'Prompt Engineering', 'Agent Architecture', 'Tool Use Mastery', 'Memory Systems',
                       # Advanced Coding Knowledge
                       'Design Patterns', 'Architecture Patterns', 'Performance Optimization', 'Security Best Practices',
                       # Advanced AI Knowledge
                       'Model Training', 'MLOps', 'Edge AI', 'Generative AI',
                       # Advanced Security Knowledge
                       'Red Team Operations', 'Blue Team Defense', 'Threat Modeling', 'Cloud Security',
                       # Advanced Data Knowledge
                       'Database Design', 'Data Pipelines', 'Big Data Technologies', 'Data Visualization']
    
    def decide_action(self):
        stats = self.world.get_stats()
        energy = stats['energy']
        
        if energy < 20:
            return 'rest', None, None
        
        if energy < 40:
            if random.random() < 0.7:
                return 'rest', None, None
            else:
                action = random.choice(['learn', 'practice'])
                skill = random.choice(self.domains)
                if action == 'learn':
                    difficulty = random.uniform(0.3, 0.7)
                    return action, skill, difficulty
                else:
                    task = random.choice(self.topics)
                    return action, skill, task
        
        if random.random() < 0.3:
            domain = random.choice(self.domains)
            topic = random.choice(self.topics)
            return 'explore', domain, topic
        
        if random.random() < 0.5:
            action = random.choice(['learn', 'practice'])
            skill = random.choice(self.domains)
            if action == 'learn':
                difficulty = random.uniform(0.3, 0.7)
                return action, skill, difficulty
            else:
                task = random.choice(self.topics)
                return action, skill, task
        
        return 'rest', None, None
    
    def run_episode(self, max_steps=100):
        print(f'=== Starting Episode (max {max_steps} steps) ===')
        print()
        
        total_reward = 0.0
        step = 0
        
        for step in range(max_steps):
            action, param1, param2 = self.decide_action()
            
            if action == 'explore':
                result = self.world.explore(param1, param2)
                print(f'Step {step + 1}: Explore {param1} - {param2} -> {result}')
                if result['success']:
                    total_reward += result['reward']
            
            elif action == 'learn':
                result = self.world.learn(param1, param2)
                print(f'Step {step + 1}: Learn {param1} (difficulty: {param2:.2f}) -> {result}')
                if result['success']:
                    total_reward += result['reward']
            
            elif action == 'practice':
                result = self.world.practice(param1, param2)
                print(f'Step {step + 1}: Practice {param1} - {param2} -> {result}')
                if result['success']:
                    total_reward += result['reward']
            
            elif action == 'rest':
                result = self.world.rest()
                print(f'Step {step + 1}: Rest -> {result}')
                if result['success']:
                    total_reward += result.get('recovered', 0.0)
            
            if step % 10 == 9:
                stats = self.world.get_stats()
                print(f'  -> Energy: {stats["energy"]}/{stats["max_energy"]}, Total Reward: {total_reward:.2f}')
                print()
        
        print(f'=== Episode Complete ===')
        print(f'Total Steps: {step + 1}')
        print(f'Total Reward: {total_reward:.2f}')
        print()
        
        stats = self.world.get_stats()
        print('Final Stats:')
        print(f'  Energy: {stats["energy"]}/{stats["max_energy"]}')
        print(f'  Knowledge: {stats["knowledge_count"]}')
        print(f'  Experiences: {stats["experience_count"]}')
        print()
        print('Skills:')
        for skill in stats['skills']:
            print(f'  {skill["name"]}: Level {skill["level"]}, {skill["experience"]} exp')
        
        return total_reward
    
    def run_training(self, episodes=10, max_steps=100):
        print(f'=== Starting Training ({episodes} episodes) ===')
        print()
        
        all_rewards = []
        
        for episode in range(episodes):
            print(f'\n--- Episode {episode + 1}/{episodes} ---')
            reward = self.run_episode(max_steps)
            all_rewards.append(reward)
        
        print(f'\n=== Training Complete ===')
        print(f'Average Reward: {sum(all_rewards) / len(all_rewards):.2f}')
        print(f'Best Episode: {max(all_rewards):.2f}')
        print(f'Worst Episode: {min(all_rewards):.2f}')
        
        return all_rewards

if __name__ == '__main__':
    evolution = ErbingAutoEvolution()
    
    print('=== Erbing Auto Evolution System ===')
    print()
    
    rewards = evolution.run_training(episodes=5, max_steps=50)
    
    print()
    print('=== Training Summary ===')
    print(f'Episodes: {len(rewards)}')
    print(f'Average Reward: {sum(rewards) / len(rewards):.2f}')
    print(f'Best Episode: {max(rewards):.2f}')
    print(f'Worst Episode: {min(rewards):.2f}')
