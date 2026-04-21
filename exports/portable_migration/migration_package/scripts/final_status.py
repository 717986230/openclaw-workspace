import sqlite3
conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db')
cur = conn.cursor()
tables = ['working_memory', 'episodic_memories', 'semantic_memories', 'procedural_memories', 'evolution_log']
print('Memory DB status:')
for t in tables:
    cur.execute('SELECT COUNT(*) FROM ' + t)
    print('  {}: {} rows'.format(t, cur.fetchone()[0]))
cur.execute('SELECT COUNT(*) FROM semantic_memories WHERE source IN (?, ?, ?, ?)',
            ('NousResearch/hermes-agent', 'dwhite612/claude-code-setup', 'ivancheungckn/openclaw-workspace-template', 'TheMasterClaw/masterclaw-core'))
print('  Agent research triples: {}'.format(cur.fetchone()[0]))
conn.close()
print()
print('All systems ready.')