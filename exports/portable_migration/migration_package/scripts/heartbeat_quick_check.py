import os
import glob

workspace = r'C:\Users\Administrator\.openclaw\workspace'

# Check session files
session_files = glob.glob(os.path.join(workspace, 'sessions', '*.json'))
print(f'Session files: {len(session_files)}')

if len(session_files) > 100:
    print('Need cleanup: Yes')
else:
    print('Need cleanup: No')

# Check memory database
memory_db = os.path.join(workspace, 'memory', 'database', 'xiaozhi_memory.db')
if os.path.exists(memory_db):
    size = os.path.getsize(memory_db)
    print(f'Memory DB: Exists ({size} bytes)')
else:
    print('Memory DB: Not found')

# Check LanceDB
lancedb_dir = os.path.join(workspace, 'memory', 'database', 'lancedb')
if os.path.exists(lancedb_dir):
    files = os.listdir(lancedb_dir)
    print(f'LanceDB: Exists ({len(files)} files)')
else:
    print('LanceDB: Not found')
