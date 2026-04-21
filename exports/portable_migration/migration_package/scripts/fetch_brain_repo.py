import subprocess
import base64
import json

# Get repo info
result = subprocess.run(['gh', 'repo', 'view', 'harthur/brain', '--json', 'name,description,url,languages,defaultBranchRef'], capture_output=True, text=True)
if result.returncode == 0:
    info = json.loads(result.stdout)
    print("=== Repo Info ===")
    print(f"Name: {info['name']}")
    print(f"Description: {info['description']}")
    print(f"URL: {info['url']}")
    print(f"Languages: {[l['node']['name'] for l in info['languages']]}")
    print(f"Default branch: {info['defaultBranchRef']['name']}")

# Get README
result2 = subprocess.run(['gh', 'api', 'repos/harthur/brain/readme', '--jq', '.content'], capture_output=True, text=True)
if result2.returncode == 0:
    content = result2.stdout.strip()
    decoded = base64.b64decode(content).decode('utf-8')
    print("\n=== README ===")
    print(decoded[:4000])

# Get file tree
result3 = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/', '--jq', '[.[] | {name: .name, type: .type}]'], capture_output=True, text=True)
if result3.returncode == 0:
    files = json.loads(result3.stdout)
    print("\n=== Files ===")
    for f in files:
        print(f"{f['type']}: {f['name']}")