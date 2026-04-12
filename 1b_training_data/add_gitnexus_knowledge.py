import sqlite3
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

# GitNexus知识
gitnexus_knowledge = [
    ('Code Intelligence', 'GitNexus Overview', 'GitNexus is a zero-server code intelligence engine that indexes any codebase into a knowledge graph. Tracks every dependency, call chain, cluster, and execution flow. Exposes smart tools via MCP so AI agents never miss code. Competes with DeepWiki but goes deeper with knowledge graph analysis'),
    ('Code Intelligence', 'Knowledge Graph for Code', 'Creates a knowledge graph from codebase - every dependency, call chain, cluster, and execution flow tracked. Uses Leiden community detection for functional areas. Provides 360-degree symbol view with categorized refs and process participation'),
    ('Code Intelligence', 'MCP Integration', 'Model Context Protocol (MCP) integration for AI agents. Exposes 16 tools (11 per-repo + 5 group). Supports Claude Code, Cursor, Codex, Windsurf, OpenCode. Auto-installs agent skills and hooks for Claude Code'),
    ('Code Intelligence', 'CLI Commands', 'gitnexus analyze: Index repository. gitnexus mcp: Start MCP server. gitnexus serve: Start local HTTP server. gitnexus wiki: Generate repository wiki. gitnexus group: Multi-repo management. gitnexus clean: Delete indexes'),
    ('Code Intelligence', '16 MCP Tools', 'list_repos, query (BM25 + semantic + RRF), context (360 symbol view), impact (blast radius analysis), detect_changes (git-diff impact), rename (multi-file coordinated), cypher (raw graph queries), group_list, group_sync, group_contracts, group_query, group_status'),
    ('Code Intelligence', 'Resources', 'gitnexus://repos (list repos), gitnexus://repo/{name}/context (stats), gitnexus://repo/{name}/clusters (functional areas), gitnexus://repo/{name}/processes (execution flows), gitnexus://repo/{name}/schema (graph schema)'),
    ('Code Intelligence', 'Agent Skills', '4 skills auto-installed: Exploring (navigate code), Debugging (trace bugs), Impact Analysis (blast radius), Refactoring (safe refactors). Repo-specific skills generated via Leiden community detection'),
    ('Code Intelligence', 'Multi-Repo Architecture', 'Global registry at ~/.gitnexus/registry.json. One MCP server serves multiple repos. Connection pool for LadybugDB. No per-project MCP config needed. Works for monorepos and microservices'),
    ('Code Intelligence', 'LadybugDB', 'Native storage for CLI (fast, persistent). WASM version for web UI (in-memory, per session). Tree-sitter for parsing (native bindings for CLI, WASM for web). PolyForm Noncommercial license'),
    ('Code Intelligence', 'Enterprise Features', 'PR review with blast radius analysis. Auto-updating Code Wiki. Auto-reindexing. Multi-repo support with unified graph. OCaml support. Priority feature/language support. SaaS or self-hosted deployment'),
    ('Code Intelligence', 'Web UI', 'Visual graph explorer + AI chat in browser. Quick exploration and demos. Limited by browser memory (~5k files). No install required at gitnexus.vercel.app. Bridge mode connects to CLI-indexed repos'),
    ('Code Intelligence', 'Bridge Mode', 'gitnexus serve connects web UI to CLI. Web UI auto-detects local server. Can browse all CLI-indexed repos without re-uploading. No re-indexing needed. Combines CLI power with web convenience'),
    ('Code Intelligence', 'Community Integrations', 'pi-gitnexus: Plugin for pi.dev coding agent. gitnexus-stable-ops: Stable ops and deployment workflows. Community-built projects. Not officially maintained but worth exploring'),
    ('Code Intelligence', 'Safety Features', 'GUARDRAILS.md for safety rules. ARCHITECTURE.md for system design. RUNBOOK.md for operations. TESTING.md for test commands. CONTRIBUTING.md for guidelines. Clear documentation structure'),
]

# 添加知识到数据库
print('Adding GitNexus knowledge...')
for domain, topic, content in gitnexus_knowledge:
    cursor.execute('''
        INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at)
        VALUES (?, ?, ?, 0.8, 0, NULL, ?)
    ''', (domain, topic, content, datetime.now()))

conn.commit()

# 统计
cursor.execute('SELECT COUNT(*) FROM knowledge')
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM knowledge WHERE domain = 'Code Intelligence'")
code_intel_count = cursor.fetchone()[0]

print(f'Total knowledge: {total}')
print(f'Code Intelligence knowledge: {code_intel_count}')
print('GitNexus knowledge added successfully!')

# 展示添加的知识
print()
print('=== GitNexus Knowledge Added ===')
cursor.execute("SELECT topic, content FROM knowledge WHERE domain = 'Code Intelligence'")
for topic, content in cursor.fetchall():
    print(f'{topic}:')
    print(f'  {content[:100]}...' if len(content) > 100 else f'  {content}')
    print()

conn.close()
