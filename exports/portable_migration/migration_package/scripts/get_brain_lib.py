import subprocess
import base64
import json

# Get lib/brain.js (main file)
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/lib/brain.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/brain_lib.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"lib/brain.js saved: {len(content)} chars")
    print(f"\nFirst 2000 chars:\n{content[:2000]}")

# Get lib/lookup.js
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/lib/lookup.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/lookup.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nlib/lookup.js saved: {len(content)} chars")
    print(f"First 1000 chars:\n{content[:1000]}")

# Get lib/train.js
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/lib/train.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/train.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nlib/train.js saved: {len(content)} chars")
    print(f"First 1000 chars:\n{content[:1000]}")