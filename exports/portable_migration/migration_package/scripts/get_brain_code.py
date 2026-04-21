import subprocess
import base64
import json
import os

# Get brain.js (main file) content
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/brain.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/brain.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"brain.js saved: {len(content)} chars")

# Get browser.js
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/browser.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/browser_brain.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"browser_brain.js saved: {len(content)} chars")

# Get package.json for dependencies
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/package.json', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    print(f"\npackage.json:\n{content}")