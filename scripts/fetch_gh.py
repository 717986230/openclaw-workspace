import urllib.request
import json
import sqlite3
from pathlib import Path

GITHUB_API = "https://api.github.com"

def gh_api(path):
    req = urllib.request.Request(f"{GITHUB_API}{path}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

def gh_raw_b64(path):
    req = urllib.request.Request(f"{GITHUB_API}{path}")
    req.add_header("Accept", "application/vnd.github.v3.raw")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return f"Error: {e}"

print("=" * 60)
print("PentAGI 项目深度研究报告")
print("=" * 60)

# 1. Repo info
repo = gh_api("/repos/vxcontrol/pentagi")
print(f"\n## 项目基本信息")
print(f"  名称: {repo.get('full_name', 'N/A')}")
stars = repo.get('stargazers_count', 0)
print(f"  Stars: {stars:,}")
print(f"  描述: {repo.get('description', 'N/A')}")
print(f"  主语言: {repo.get('language', 'N/A')}")
print(f"  创建: {repo.get('created_at', 'N/A')}")
print(f"  最新推送: {repo.get('pushed_at', 'N/A')}")
print(f"  Fork数: {repo.get('forks_count', 'N/A')}")
print(f"  License: {repo.get('license', {}).get('spdx_id', 'N/A')}")
print(f"  Issues: {repo.get('open_issues_count', 'N/A')}")
print(f"  URL: {repo.get('html_url', 'N/A')}")

# 2. Topics
topics = gh_api("/repos/vxcontrol/pentagi/topics")
if isinstance(topics, dict):
    print(f"\n## 主题标签")
    for t in topics.get('names', [])[:20]:
        print(f"  - {t}")

# 3. README
print(f"\n## README (前300行)")
readme = gh_raw_b64("/repos/vxcontrol/pentagi/readme")
lines = readme.split('\n')[:300]
for line in lines:
    print(line)

# 4. Repository structure
print(f"\n## 仓库结构")
contents = gh_api("/repos/vxcontrol/pentagi/contents/")
if isinstance(contents, list):
    for item in contents:
        print(f"  [{item.get('type', '?')}] {item.get('name', '?')}")

# 5. docker-compose
print(f"\n## docker-compose.yml")
compose = gh_raw_b64("/repos/vxcontrol/pentagi/contents/docker-compose.yml")
print(compose[:4000])

# 6. Local pentagi tables
print(f"\n## 本地 PentAGI 数据库表分析")
db_path = Path(__file__).parent.parent / 'memory' / 'database' / 'xiaozhi_memory.db'
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'pentagi%'")
    tables = [r[0] for r in cur.fetchall()]
    for t in tables:
        cur.execute(f'SELECT count(*) FROM "{t}"')
        count = cur.fetchone()[0]
        cur.execute(f'PRAGMA table_info("{t}")')
        cols = [(col[1], col[2]) for col in cur.fetchall()]
        print(f"\n  ### {t} ({count} rows)")
        for cn, ct in cols:
            print(f"    {cn}: {ct}")
    conn.close()
else:
    print("  数据库不存在")

# 7. Key source files
print(f"\n## 核心源码文件分析")
key_files = [
    ("/repos/vxcontrol/pentagi/contents/cmd/server/main.go", "cmd/server/main.go"),
    ("/repos/vxcontrol/pentagi/contents/internal/agent/agent.go", "internal/agent/agent.go"),
    ("/repos/vxcontrol/pentagi/contents/internal/models/task.go", "internal/models/task.go"),
    ("/repos/vxcontrol/pentagi/contents/Makefile", "Makefile"),
]
for api_path, label in key_files:
    content = gh_raw_b64(api_path)
    print(f"\n--- {label} ---")
    lines = content.split('\n')[:80]
    for l in lines:
        print(l)

# 8. Recent commits / releases
print(f"\n## 最近 Releases")
releases = gh_api("/repos/vxcontrol/pentagi/releases?per_page=5")
if isinstance(releases, list):
    for rel in releases:
        print(f"  {rel.get('tag_name', 'N/A')} - {rel.get('name', 'N/A')}")
        print(f"    {rel.get('published_at', 'N/A')}")
        print(f"    {rel.get('body', '')[:200]}")
        print()

print("\n" + "=" * 60)
print("报告生成完成")
print("=" * 60)