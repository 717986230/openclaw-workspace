import urllib.request
import json

repos_readmes = {
    'hermes-agent': 'NousResearch/hermes-agent',
    'hermes-ecosystem': 'ksimback/hermes-ecosystem',
    'hermes-hud': 'joeynyc/hermes-hud',
    'hermes-control-interface': 'xaspx/hermes-control-interface',
}

import subprocess

for name, repo in repos_readmes.items():
    print(f'\n=== {name} README ===')
    try:
        result = subprocess.run(
            ['gh', 'api', f'repos/{repo}/readme'],
            capture_output=True, text=True, encoding='utf-8'
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            import base64
            content = base64.b64decode(data['content']).decode('utf-8', errors='ignore')
            print(content[:4000])
    except Exception as e:
        print(f'Error: {e}')