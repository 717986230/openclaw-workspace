import subprocess
import base64
import json

# Get lib folder contents
result = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/lib', '--jq', '[.[] | {name: .name, type: .type, download_url}]'], capture_output=True, text=True)
if result.returncode == 0:
    files = json.loads(result.stdout)
    print("=== lib/ files ===")
    for f in files:
        print(f"{f['type']}: {f['name']}")
        if f['type'] == 'file' and f['name'].endswith('.js'):
            # Get content
            r = subprocess.run(['gh', 'api', f"repos/harthur/brain/contents/lib/{f['name']}", '--jq', '.content'], capture_output=True, text=True)
            if r.returncode == 0:
                content = base64.b64decode(r.stdout.strip()).decode('utf-8')
                print(f"\n--- {f['name']} ---")
                print(content[:3000])

# Get browser.js content
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/browser.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    print("\n\n=== browser.js (first 4000 chars) ===")
    print(content[:4000])