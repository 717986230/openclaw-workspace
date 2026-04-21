import sqlite3, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()
cursor.execute("SELECT id, service_name, description, created_at, metadata FROM secure_credentials WHERE service_name='ollama-cloud'")
r = cursor.fetchone()
if r:
    meta = json.loads(r[4]) if r[4] else {}
    print('[OK] ollama-cloud account found')
    print('  id:', r[0])
    print('  service_name:', r[1])
    print('  description:', r[2])
    print('  created_at:', r[3])
    print('  base_url:', meta.get('base_url'))
    print('  models:', meta.get('models'))
    print('  priority:', meta.get('priority'))
else:
    print('[NOT FOUND] ollama-cloud not in account pool')
conn.close()