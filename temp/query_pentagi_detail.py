import sqlite3, os

db = r'C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    
    # Check all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [r[0] for r in cur.fetchall()]
    print('ALL tables:', all_tables)
    
    # pentagi tables
    pentagi_tables = [t for t in all_tables if t.startswith('pentagi_')]
    for t in pentagi_tables:
        print('\n=== ' + t + ' ===')
        cur.execute('SELECT * FROM ' + t)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        print('Count:', len(rows))
        print('Columns:', cols)
        if rows:
            print('Sample (first 3):')
            for row in rows[:3]:
                print(' ', dict(zip(cols, row)))
    conn.close()
else:
    print('DB not found')