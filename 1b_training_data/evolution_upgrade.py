import sqlite3
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

print('=== Erbing Evolution Upgrade ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# 1. 添加进化里程碑表
print('1. Adding evolution milestones table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS evolution_milestones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        milestone_name TEXT NOT NULL,
        description TEXT NOT NULL,
        requirement_type TEXT NOT NULL,
        requirement_value INTEGER NOT NULL,
        reward_bonus REAL NOT NULL,
        unlocked_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 2. 添加进化成就表
print('2. Adding evolution achievements table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS evolution_achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        achievement_name TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 3. 添加进化统计表
print('3. Adding evolution stats table...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS evolution_stats (
        id INTEGER PRIMARY KEY,
        total_episodes INTEGER DEFAULT 0,
        total_knowledge INTEGER DEFAULT 0,
        total_experiences INTEGER DEFAULT 0,
        best_reward REAL DEFAULT 0.0,
        evolution_level INTEGER DEFAULT 1,
        evolution_points INTEGER DEFAULT 0,
        last_evolution TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 4. 插入进化里程碑
print('4. Adding evolution milestones...')
milestones = [
    ('First Steps', 'Complete first 10 episodes', 'episodes', 10, 100.0),
    ('Knowledge Seeker', 'Learn 100 knowledge items', 'knowledge', 100, 200.0),
    ('Experience Hunter', 'Accumulate 1000 experiences', 'experiences', 1000, 300.0),
    ('Skill Master', 'Reach level 5 in any skill', 'skill_level', 5, 500.0),
    ('Knowledge Expert', 'Learn 500 knowledge items', 'knowledge', 500, 800.0),
    ('Experience Master', 'Accumulate 10000 experiences', 'experiences', 10000, 1000.0),
    ('Evolution Novice', 'Reach evolution level 2', 'evolution_level', 2, 1500.0),
    ('Evolution Apprentice', 'Reach evolution level 3', 'evolution_level', 3, 2000.0),
    ('Evolution Expert', 'Reach evolution level 5', 'evolution_level', 5, 5000.0),
    ('Evolution Master', 'Reach evolution level 10', 'evolution_level', 10, 10000.0),
]

for name, desc, req_type, req_value, reward in milestones:
    cursor.execute('''
        INSERT OR REPLACE INTO evolution_milestones 
        (milestone_name, description, requirement_type, requirement_value, reward_bonus)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, desc, req_type, req_value, reward))

# 5. 初始化进化统计
print('5. Initializing evolution stats...')
cursor.execute('SELECT COUNT(*) FROM evolution_stats')
if cursor.fetchone()[0] == 0:
    cursor.execute('''
        INSERT INTO evolution_stats 
        (id, total_episodes, total_knowledge, total_experiences, best_reward, evolution_level, evolution_points)
        VALUES (1, 0, 0, 0, 0.0, 1, 0)
    ''')

# 6. 添加更多高级知识领域
print('6. Adding advanced knowledge domains...')
advanced_knowledge = [
    # AI Agent进阶知识
    ('AI Agent', 'Prompt Engineering', 'Advanced prompt engineering techniques: Few-shot learning, Chain-of-Thought, Tree-of-Thought, Self-Consistency, Program-of-Thoughts. Structured prompts, role-based prompts, multi-turn conversation design'),
    ('AI Agent', 'Agent Architecture', 'Multi-agent systems, hierarchical agents, collaborative agents, competitive agents. Agent communication protocols, shared memory, distributed decision making. Orchestration patterns'),
    ('AI Agent', 'Tool Use Mastery', 'Advanced tool use: function calling, API integration, code execution, web scraping, database queries. Tool composition, error handling, retry logic, rate limiting'),
    ('AI Agent', 'Memory Systems', 'Short-term memory, long-term memory, episodic memory, semantic memory. Memory consolidation, forgetting mechanisms, memory retrieval strategies. Vector databases, knowledge graphs'),
    
    # 高级编程知识
    ('Advanced Coding', 'Design Patterns', 'Creational patterns: Singleton, Factory, Builder, Prototype. Structural patterns: Adapter, Bridge, Composite, Decorator, Facade. Behavioral patterns: Observer, Strategy, Command, State, Mediator'),
    ('Advanced Coding', 'Architecture Patterns', 'Microservices, monolithic, serverless, event-driven. CQRS, Event Sourcing, Saga pattern. Domain-Driven Design (DDD), hexagonal architecture, clean architecture'),
    ('Advanced Coding', 'Performance Optimization', 'Algorithm complexity, Big O notation, time-space tradeoffs. Caching strategies, lazy loading, precomputation. Profiling, benchmarking, optimization techniques'),
    ('Advanced Coding', 'Security Best Practices', 'OWASP Top 10 mitigation, input validation, output encoding. Authentication patterns, authorization strategies, session management. Cryptography basics, secure communication'),
    
    # 高级AI技术
    ('Advanced AI', 'Model Training', 'Data preprocessing, feature engineering, model selection. Hyperparameter tuning, cross-validation, ensemble methods. Transfer learning, fine-tuning, domain adaptation'),
    ('Advanced AI', 'MLOps', 'Model versioning, experiment tracking, model registry. CI/CD for ML, automated testing, model monitoring. A/B testing, canary deployment, rollback strategies'),
    ('Advanced AI', 'Edge AI', 'Model quantization, pruning, distillation. On-device inference, model optimization for mobile. Edge deployment, federated learning, privacy-preserving ML'),
    ('Advanced AI', 'Generative AI', 'Text generation, image generation, music generation. GANs, VAEs, diffusion models. Prompt engineering for generative models, style transfer, content creation'),
    
    # 高级安全知识
    ('Advanced Security', 'Red Team Operations', 'Adversary simulation, full-scope attacks, physical security. Social engineering, technical attacks, operational security. Reporting, lessons learned, remediation'),
    ('Advanced Security', 'Blue Team Defense', 'Security monitoring, threat hunting, incident response. SIEM optimization, detection rules, playbooks. Forensic analysis, malware analysis, threat intelligence'),
    ('Advanced Security', 'Threat Modeling', 'STRIDE, DREAD, PASTA, OCTAVE. Attack surface analysis, threat actors, risk assessment. Secure design principles, defense in depth'),
    ('Advanced Security', 'Cloud Security', 'AWS security, Azure security, GCP security. IAM, encryption, network security. Compliance, auditing, incident response in cloud'),
    
    # 高级数据知识
    ('Advanced Data', 'Database Design', 'Normalization, denormalization, schema design. Indexing strategies, query optimization, performance tuning. Distributed databases, sharding, replication'),
    ('Advanced Data', 'Data Pipelines', 'ETL/ELT, data ingestion, data transformation. Stream processing, batch processing, real-time analytics. Data quality, data lineage, metadata management'),
    ('Advanced Data', 'Big Data Technologies', 'Hadoop, Spark, Kafka, Flink. Data lakes, data warehouses, data mesh. Distributed computing, MapReduce, RDDs, DataFrames'),
    ('Advanced Data', 'Data Visualization', 'Chart types, interactive dashboards, storytelling with data. D3.js, Plotly, Tableau, PowerBI. Accessibility, color theory, best practices'),
]

for domain, topic, content in advanced_knowledge:
    cursor.execute('''
        INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at)
        VALUES (?, ?, ?, 0.9, 0, NULL, ?)
    ''', (domain, topic, content, datetime.now()))

conn.commit()

# 统计
cursor.execute('SELECT COUNT(*) FROM knowledge')
total_knowledge = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM evolution_milestones')
total_milestones = cursor.fetchone()[0]

print()
print('=== Evolution Upgrade Complete ===')
print(f'Total knowledge: {total_knowledge}')
print(f'Evolution milestones: {total_milestones}')
print()
print('New features added:')
print('1. Evolution milestones system (10 milestones)')
print('2. Evolution achievements system')
print('3. Evolution stats tracking')
print('4. Advanced knowledge domains (20 items)')
print()
print('Evolution system upgraded successfully!')

conn.close()
