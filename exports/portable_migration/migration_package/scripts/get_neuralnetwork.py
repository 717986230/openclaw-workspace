import subprocess
import base64

# Get lib/neuralnetwork.js (main implementation)
r = subprocess.run(['gh', 'api', 'repos/harthur/brain/contents/lib/neuralnetwork.js', '--jq', '.content'], capture_output=True, text=True)
if r.returncode == 0:
    content = base64.b64decode(r.stdout.strip()).decode('utf-8')
    with open('C:/Users/Administrator/.openclaw/workspace/scripts/neuralnetwork.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"lib/neuralnetwork.js saved: {len(content)} chars")
    print(f"\nFirst 3000 chars:\n{content[:3000]}")
    print(f"\n\nLast 2000 chars:\n{content[-2000:]}")