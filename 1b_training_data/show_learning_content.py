import sqlite3
import random

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

# 获取总知识点数
cursor.execute('SELECT COUNT(*) FROM knowledge')
total_knowledge = cursor.fetchone()[0]

# 获取各个领域的知识点数
cursor.execute('SELECT domain, COUNT(*) FROM knowledge GROUP BY domain ORDER BY COUNT(*) DESC')
domains = cursor.fetchall()

print(f'=== Knowledge Overview ===')
print(f'Total Knowledge: {total_knowledge}')
print()

print('Knowledge by Domain:')
for domain, count in domains:
    print(f'  {domain}: {count}')
print()

# 随机展示一些知识点
print('=== Sample Knowledge (Random 10) ===')
cursor.execute('SELECT domain, topic, content FROM knowledge ORDER BY RANDOM() LIMIT 10')
samples = cursor.fetchall()

for i, (domain, topic, content) in enumerate(samples, 1):
    print(f'{i}. [{domain}] {topic}')
    print(f'   {content[:100]}...' if len(content) > 100 else f'   {content}')
    print()

# 展示LLM知识
print('=== LLM Knowledge ===')
cursor.execute("SELECT domain, topic, content FROM knowledge WHERE domain LIKE '%LLM%' OR topic LIKE '%LLM%' OR topic LIKE '%GPT%' OR topic LIKE '%Claude%' OR topic LIKE '%Gemini%' LIMIT 5")
llm_knowledge = cursor.fetchall()

for domain, topic, content in llm_knowledge:
    print(f'[{domain}] {topic}')
    print(f'{content}')
    print()

# 展示黑客知识
print('=== Hacker Knowledge ===')
cursor.execute("SELECT domain, topic, content FROM knowledge WHERE domain LIKE '%Hacking%' OR domain LIKE '%Web%' OR domain LIKE '%Network%' OR domain LIKE '%System%' OR domain LIKE '%Crypto%' LIMIT 5")
hacker_knowledge = cursor.fetchall()

for domain, topic, content in hacker_knowledge:
    print(f'[{domain}] {topic}')
    print(f'{content}')
    print()

conn.close()
