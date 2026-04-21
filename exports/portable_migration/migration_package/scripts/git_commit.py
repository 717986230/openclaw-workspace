import subprocess
import os

os.chdir('C:/Users/Administrator/.openclaw/workspace')

# Git add
subprocess.run(['git', 'add', 'hermes/', 'scripts/four_layers_manager.py', 'scripts/store_hermes.py'], check=True)
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print('Status:', result.stdout)

# Git commit
result = subprocess.run([
    'git', 'commit', '-m',
    'feat: Hermes-style four-layer memory stack + checkpoint system\n\n'
    '- FourLayersManager: Working/Episodic/Semantic/Procedural memory\n'
    '- ErbingMemoryManager: Hermes MemoryManager pattern (prefetch/sync/nudge)\n'
    '- Checkpoint save/restore via evolution_log\n'
    '- 37 semantic triples: Hermes Agent architecture knowledge base\n'
    '- Periodic nudge + skill self-improvement loop'
], capture_output=True, text=True)
print('Commit result:', result.returncode)
print(result.stdout)
if result.stderr:
    print(result.stderr[:500])