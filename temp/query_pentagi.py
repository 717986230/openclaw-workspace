import sqlite3, os, sys

db = r'C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db'
if os.path.exists(db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'pentagi%'")
    tables = [r[0] for r in cur.fetchall()]
    print('Tables:', tables)
    for t in tables:
        print('\n=== ' + t + ' ===')
        cur.execute('PRAGMA table_info(' + t + ')')
        print('Columns:', cur.fetchall())
        cur.execute('SELECT * FROM ' + t + ' LIMIT 5')
        rows = cur.fetchall()
        print('Sample rows:')
        for row in rows:
            print(' ', row)
    conn.close()
else:
    print('DB not found at', db)