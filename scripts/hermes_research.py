import subprocess
import json

repos = [
    'ksimback/hermes-ecosystem',
    'cclank/Hermes-Wiki',
    'joeynyc/hermes-hud',
    'xaspx/hermes-control-interface',
    'NousResearch/hermes-agent',
]

for repo in repos:
    try:
        result = subprocess.run(
            ['gh', 'repo', 'view', repo, '--json', 'name,description,stargazerCount,primaryLanguage,url'],
            capture_output=True, text=True, encoding='utf-8'
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            print(f"=== {repo} ===")
            print(f"  Stars: {data.get('stargazerCount', 'N/A')}")
            print(f"  Lang: {data.get('primaryLanguage', 'N/A')}")
            print(f"  Desc: {data.get('description', 'N/A')}")
            print(f"  URL: {data.get('url', 'N/A')}")
            print()
    except Exception as e:
        print(f"Error {repo}: {e}")