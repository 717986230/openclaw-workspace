import sqlite3

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

cursor.execute('INSERT OR REPLACE INTO world_state (id, world_time, day_count, energy, max_energy) VALUES (1, datetime("now"), 0, 100.0, 100.0)')
conn.commit()

print('World state initialized')

cursor.execute('SELECT * FROM world_state')
print('World state:', cursor.fetchone())
