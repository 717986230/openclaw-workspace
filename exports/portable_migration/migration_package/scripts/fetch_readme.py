import urllib.request
import sys

# Fix console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

req = urllib.request.Request('https://raw.githubusercontent.com/vxcontrol/pentagi/main/README.md')
with urllib.request.urlopen(req, timeout=20) as r:
    content = r.read().decode('utf-8', errors='replace')
    with open(r'C:\Users\Administrator\.openclaw\workspace\scripts\pentagi_readme.md', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Downloaded {len(content)} chars")
    print(content[:6000])