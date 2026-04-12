import sqlite3

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS skills (name TEXT PRIMARY KEY, type TEXT NOT NULL, level INTEGER DEFAULT 1, experience INTEGER DEFAULT 0, max_level INTEGER DEFAULT 100, abilities TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, topic TEXT NOT NULL, content TEXT NOT NULL, confidence REAL DEFAULT 0.5, usage_count INTEGER DEFAULT 0, last_used TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS experiences (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, description TEXT NOT NULL, outcome TEXT NOT NULL, reward REAL NOT NULL, learned TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS achievements (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS world_state (id INTEGER PRIMARY KEY, world_time TIMESTAMP NOT NULL, day_count INTEGER DEFAULT 0, energy REAL DEFAULT 100.0, max_energy REAL DEFAULT 100.0)''')

skills = [
    ('Coding', 'coding', 1, 0, 100, '[]'),
    ('AI Tech', 'ai_tech', 1, 0, 100, '[]'),
    ('Security', 'security', 1, 0, 100, '[]'),
    ('Deployment', 'deployment', 1, 0, 100, '[]'),
    ('Tool Use', 'tool_use', 1, 0, 100, '[]'),
    ('Problem Solving', 'problem_solving', 1, 0, 100, '[]'),
    ('Communication', 'communication', 1, 0, 100, '[]'),
    ('Collaboration', 'collaboration', 1, 0, 100, '[]')
]

cursor.executemany('INSERT OR REPLACE INTO skills (name, type, level, experience, max_level, abilities) VALUES (?, ?, ?, ?, ?, ?)', skills)
cursor.execute('INSERT OR REPLACE INTO world_state (id, world_time, day_count, energy, max_energy) VALUES (1, datetime("now"), 0, 100.0, 100.0)')

conn.commit()
print('Virtual world initialized successfully')
