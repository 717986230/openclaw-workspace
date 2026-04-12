import sqlite3
import random
from datetime import datetime, timedelta

class ErbingVirtualWorld:
    def __init__(self, db_path='erbing_virtual_world.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
    def get_world_state(self):
        self.cursor.execute('SELECT * FROM world_state WHERE id = 1')
        return self.cursor.fetchone()
    
    def get_skills(self):
        self.cursor.execute('SELECT * FROM skills')
        return self.cursor.fetchall()
    
    def get_skill(self, name):
        self.cursor.execute('SELECT * FROM skills WHERE name = ?', (name,))
        return self.cursor.fetchone()
    
    def update_skill(self, name, experience):
        self.cursor.execute('UPDATE skills SET experience = experience + ? WHERE name = ?', (experience, name))
        self.conn.commit()
    
    def add_experience(self, action, description, outcome, reward, learned=None):
        learned_json = str(learned) if learned else '[]'
        self.cursor.execute('INSERT INTO experiences (action, description, outcome, reward, learned, timestamp) VALUES (?, ?, ?, ?, ?, ?)', 
                          (action, description, outcome, reward, learned_json, datetime.now()))
        self.conn.commit()
    
    def add_knowledge(self, domain, topic, content, confidence=0.3):
        self.cursor.execute('INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at) VALUES (?, ?, ?, ?, 0, NULL, ?)', 
                          (domain, topic, content, confidence, datetime.now()))
        self.conn.commit()
    
    def update_energy(self, energy):
        self.cursor.execute('UPDATE world_state SET energy = ? WHERE id = 1', (energy,))
        self.conn.commit()
    
    def explore(self, domain, topic):
        world_state = self.get_world_state()
        energy = world_state[3]
        
        if energy < 20:
            self.add_experience('explore', f'Explore {domain} - {topic}', 'Not enough energy', -5.0)
            return {'success': False, 'reason': 'Not enough energy'}
        
        self.update_energy(energy - 20)
        
        success = random.random() > 0.3
        
        if success:
            self.add_knowledge(domain, topic, f'New knowledge about {domain} - {topic}')
            reward = 10.0 + random.random() * 10.0
            
            if domain == 'Coding':
                self.update_skill('Coding', 5)
            elif domain == 'AI Tech':
                self.update_skill('AI Tech', 5)
            
            self.add_experience('explore', f'Explore {domain} - {topic}', 'Success', reward, [f'Learned {domain} - {topic}'])
            return {'success': True, 'reward': reward, 'learned': f'{domain} - {topic}'}
        else:
            self.add_experience('explore', f'Explore {domain} - {topic}', 'Failed', -2.0)
            return {'success': False, 'reason': 'Exploration failed'}
    
    def learn(self, skill_name, difficulty=0.5):
        skill = self.get_skill(skill_name)
        if not skill:
            self.add_experience('learn', f'Learn {skill_name}', 'Skill not found', -1.0)
            return {'success': False, 'reason': 'Skill not found'}
        
        world_state = self.get_world_state()
        energy = world_state[3]
        
        if energy < 30:
            self.add_experience('learn', f'Learn {skill_name}', 'Not enough energy', -5.0)
            return {'success': False, 'reason': 'Not enough energy'}
        
        self.update_energy(energy - 30)
        
        success_rate = 1.0 - difficulty * 0.5
        success = random.random() < success_rate
        
        if success:
            exp_gain = int(20 * (1.0 - difficulty * 0.5))
            self.update_skill(skill_name, exp_gain)
            
            reward = 15.0 + random.random() * 10.0
            self.add_experience('learn', f'Learn {skill_name} (difficulty: {difficulty})', 'Success', reward, [f'{skill_name} +{exp_gain} exp'])
            return {'success': True, 'reward': reward, 'exp_gain': exp_gain}
        else:
            self.add_experience('learn', f'Learn {skill_name} (difficulty: {difficulty})', 'Failed', -3.0)
            return {'success': False, 'reason': 'Learning failed'}
    
    def practice(self, skill_name, task):
        skill = self.get_skill(skill_name)
        if not skill:
            self.add_experience('practice', f'Practice {skill_name} - {task}', 'Skill not found', -1.0)
            return {'success': False, 'reason': 'Skill not found'}
        
        world_state = self.get_world_state()
        energy = world_state[3]
        
        if energy < 15:
            self.add_experience('practice', f'Practice {skill_name} - {task}', 'Not enough energy', -5.0)
            return {'success': False, 'reason': 'Not enough energy'}
        
        self.update_energy(energy - 15)
        
        skill_level = skill[2]
        success_rate = 0.5 + skill_level * 0.01
        success = random.random() < success_rate
        
        if success:
            exp_gain = int(10 * (1.0 + skill_level * 0.02))
            self.update_skill(skill_name, exp_gain)
            
            reward = 10.0 + random.random() * 5.0
            self.add_experience('practice', f'Practice {skill_name} - {task}', 'Success', reward, [f'{skill_name} +{exp_gain} exp'])
            return {'success': True, 'reward': reward, 'exp_gain': exp_gain}
        else:
            self.add_experience('practice', f'Practice {skill_name} - {task}', 'Failed', -2.0)
            return {'success': False, 'reason': 'Practice failed'}
    
    def rest(self):
        world_state = self.get_world_state()
        energy = world_state[3]
        max_energy = world_state[4]
        
        recovery = min(20.0, max_energy - energy)
        self.update_energy(energy + recovery)
        
        self.add_experience('rest', 'Rest', f'Recovered {recovery} energy', 2.0)
        return {'success': True, 'recovered': recovery}
    
    def get_stats(self):
        world_state = self.get_world_state()
        skills = self.get_skills()
        
        self.cursor.execute('SELECT COUNT(*) FROM knowledge')
        knowledge_count = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT COUNT(*) FROM experiences')
        experience_count = self.cursor.fetchone()[0]
        
        return {
            'energy': world_state[3],
            'max_energy': world_state[4],
            'skills': [{'name': s[0], 'level': s[2], 'experience': s[3]} for s in skills],
            'knowledge_count': knowledge_count,
            'experience_count': experience_count
        }

if __name__ == '__main__':
    world = ErbingVirtualWorld()
    
    print('=== Erbing Virtual World ===')
    print()
    
    stats = world.get_stats()
    print(f'Energy: {stats["energy"]}/{stats["max_energy"]}')
    print(f'Skills: {len(stats["skills"])}')
    print(f'Knowledge: {stats["knowledge_count"]}')
    print(f'Experiences: {stats["experience_count"]}')
    print()
    
    print('Skills:')
    for skill in stats['skills']:
        print(f'  {skill["name"]}: Level {skill["level"]}, {skill["experience"]} exp')
    print()
    
    print('=== Testing Actions ===')
    print()
    
    result = world.explore('Coding', 'Python')
    print(f'Explore: {result}')
    
    result = world.learn('Coding', difficulty=0.3)
    print(f'Learn: {result}')
    
    result = world.practice('Coding', 'Write a function')
    print(f'Practice: {result}')
    
    result = world.rest()
    print(f'Rest: {result}')
    
    print()
    print('=== Updated Stats ===')
    print()
    
    stats = world.get_stats()
    print(f'Energy: {stats["energy"]}/{stats["max_energy"]}')
    print(f'Skills: {len(stats["skills"])}')
    print(f'Knowledge: {stats["knowledge_count"]}')
    print(f'Experiences: {stats["experience_count"]}')
    print()
    
    print('Skills:')
    for skill in stats['skills']:
        print(f'  {skill["name"]}: Level {skill["level"]}, {skill["experience"]} exp')
