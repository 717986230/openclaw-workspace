import sqlite3
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

print('=== Erbing Learning Report ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# Statistics
cursor.execute('SELECT COUNT(*) FROM knowledge')
knowledge_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM experiences')
experience_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM skills')
skill_count = cursor.fetchone()[0]

print('Statistics:')
print(f'  Knowledge: {knowledge_count}')
print(f'  Experiences: {experience_count}')
print(f'  Skills: {skill_count}')
print()

# Skills status
print('Skills Status:')
cursor.execute('SELECT name, type, level, experience FROM skills')
skills = cursor.fetchall()
for name, skill_type, level, exp in skills:
    print(f'  {name}: Level {level}, {exp} exp')
print()

# Recent knowledge
print('Recently Learned Knowledge (Last 10):')
cursor.execute('SELECT domain, topic, content, created_at FROM knowledge ORDER BY created_at DESC LIMIT 10')
recent_knowledge = cursor.fetchall()

for i, (domain, topic, content, created_at) in enumerate(recent_knowledge, 1):
    print(f'{i}. [{domain}] {topic}')
    print(f'   {content[:80]}...' if len(content) > 80 else f'   {content}')
    print(f'   Learned at: {created_at}')
print()

# Recent experiences
print('Recent Experiences (Last 5):')
cursor.execute('SELECT action, description, outcome, reward, timestamp FROM experiences ORDER BY timestamp DESC LIMIT 5')
recent_experiences = cursor.fetchall()

for i, (action, description, outcome, reward, timestamp) in enumerate(recent_experiences, 1):
    print(f'{i}. Action: {action}')
    print(f'   Description: {description}')
    print(f'   Outcome: {outcome}')
    print(f'   Reward: {reward:.2f}')
    print(f'   Time: {timestamp}')
print()

# Knowledge by domain
print('Knowledge by Domain:')
cursor.execute('SELECT domain, COUNT(*) as count FROM knowledge GROUP BY domain ORDER BY count DESC')
domains = cursor.fetchall()
for domain, count in domains:
    print(f'  {domain}: {count} items')

conn.close()
