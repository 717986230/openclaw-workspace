import subprocess
import base64
import os

# Get README content
result = subprocess.run(['gh', 'api', 'repos/garrytan/gbrain/readme', '--jq', '.content'], capture_output=True, text=True)
if result.returncode == 0:
    content = result.stdout.strip()
    decoded = base64.b64decode(content).decode('utf-8')
    print(decoded[:5000])
else:
    print(f"Error: {result.stderr}")

# Get repo file tree
result2 = subprocess.run(['gh', 'api', 'repos/garrytan/gbrain/contents/', '--jq', '[.[] | {name: .name, type: .type}]'], capture_output=True, text=True)
if result2.returncode == 0:
    import json
    try:
        files = json.loads(result2.stdout)
        print("\n\n=== Top-level files/folders ===")
        for f in files:
            print(f"{f['type']}: {f['name']}")
    except:
        print(result2.stdout[:2000])
else:
    print(f"Error getting tree: {result2.stderr}")