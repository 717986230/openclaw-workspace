import subprocess
import json
import base64
import sqlite3
from pathlib import Path

def gh(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def gh_json(cmd):
    out, err, code = gh(cmd)
    if code == 0:
        return json.loads(out)
    return None

def gh_raw(cmd):
    """Get base64 content and decode"""
    out, err, code = gh(cmd)
    if code == 0:
        try:
            return base64.b64decode(out).decode('utf-8', errors='ignore')
        except:
            return out
    return ""

print("=== Fetching PentAGI Repository Info ===\n")

# Repo metadata
repo = gh_json('gh api repos/vxcontrol/pentagi --jq "{desc: .description, stars: .stargazerCount, lang: .primaryLanguage.name, created: .createdAt, pushed: .pushedAt, url: .url}"')
if repo:
    print(f"描述: {repo['desc']}")
    print(f"Stars: {repo['stars']}")
    print(f"主语言: {repo['lang']}")
    print(f"创建: {repo['created']}")
    print(f"最新推送: {repo['pushed']}")
    print(f"URL: {repo['url']}")

# Get directory structure
print("\n=== Repository Structure ===")
dirs = gh_json('gh api "repos/vxcontrol/pentagi/contents/" --jq ".[].name"')
if dirs:
    for d in dirs:
        print(f"  {d}")

# Get README
print("\n=== README (first 200 lines) ===")
readme_b64 = gh('gh api repos/vxcontrol/pentagi/readme --jq ".content"')[0]
if readme_b64:
    decoded = base64.b64decode(readme_b64).decode('utf-8', errors='ignore')
    for i, line in enumerate(decoded.split('\n')[:200]):
        print(line)

# Check local pentagi tables
print("\n=== Local PentAGI Tables in Memory DB ===")
db_path = Path(__file__).parent.parent / 'memory' / 'database' / 'xiaozhi_memory.db'
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'pentagi%'")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}"')
        count = cur.fetchone()[0]
        # Get schema
        cur.execute(f'PRAGMA table_info("{t}")')
        cols = [col[1] for col in cur.fetchall()]
        print(f"  {t}: {count} rows | cols: {cols}")
    conn.close()
else:
    print("  Database not found")

# Check docker-compose
print("\n=== docker-compose.yml ===")
compose_b64 = gh('gh api repos/vxcontrol/pentagi/contents/docker-compose.yml --jq ".content"')[0]
if compose_b64:
    decoded = base64.b64decode(compose_b64).decode('utf-8', errors='ignore')
    print(decoded[:3000])

# Check Makefile
print("\n=== Makefile ===")
make_b64 = gh('gh api repos/vxcontrol/pentagi/contents/Makefile --jq ".content"')[0]
if make_b64:
    decoded = base64.b64decode(make_b64).decode('utf-8', errors='ignore')
    print(decoded[:2000])

# Key source files
print("\n=== Key Source Files ===")
key_files = ['cmd/server/main.go', 'internal/server/server.go', 'internal/agent/agent.go', 'internal/models/task.go']
for f in key_files:
    content_b64 = gh(f'gh api "repos/vxcontrol/pentagi/contents/{f}" --jq ".content"')[0]
    if content_b64:
        decoded = base64.b64decode(content_b64).decode('utf-8', errors='ignore')
        print(f"\n--- {f} (first 100 lines) ---")
        for i, line in enumerate(decoded.split('\n')[:100]):
            print(line)