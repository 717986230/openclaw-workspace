import subprocess
import json

for dir_path in ['agent', 'skills', 'memory', 'tools']:
    r = subprocess.run(['gh', 'api', 'repos/NousResearch/hermes-agent/contents/' + dir_path],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        data = json.loads(r.stdout)
        print(f'=== {dir_path}/ ===')
        for f in data:
            print(f'  {f["type"]} {f["name"]}')