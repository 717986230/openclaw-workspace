import sqlite3
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

print('=== GitNexus Knowledge Summary ===')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

# 获取GitNexus知识
cursor.execute("SELECT topic, content FROM knowledge WHERE domain = 'Code Intelligence' ORDER BY topic")
gitnexus_knowledge = cursor.fetchall()

print(f'Total GitNexus Knowledge: {len(gitnexus_knowledge)} items')
print()

# 分类展示
print('=== 1. Core Concept ===')
for topic, content in gitnexus_knowledge:
    if 'Overview' in topic or 'Knowledge Graph' in topic:
        print(f'{topic}:')
        print(f'  {content}')
        print()

print('=== 2. Integration & Architecture ===')
for topic, content in gitnexus_knowledge:
    if 'MCP' in topic or 'Architecture' in topic or 'LadybugDB' in topic:
        print(f'{topic}:')
        print(f'  {content}')
        print()

print('=== 3. Tools & Features ===')
for topic, content in gitnexus_knowledge:
    if 'Tools' in topic or 'Commands' in topic or 'Resources' in topic or 'Skills' in topic:
        print(f'{topic}:')
        print(f'  {content}')
        print()

print('=== 4. Use Cases ===')
for topic, content in gitnexus_knowledge:
    if 'Enterprise' in topic or 'Web UI' in topic or 'Bridge' in topic or 'Community' in topic:
        print(f'{topic}:')
        print(f'  {content}')
        print()

print('=== 5. Safety & Documentation ===')
for topic, content in gitnexus_knowledge:
    if 'Safety' in topic:
        print(f'{topic}:')
        print(f'  {content}')
        print()

conn.close()

print()
print('=== Summary ===')
print('GitNexus is a powerful code intelligence engine that:')
print('1. Creates knowledge graphs from codebases')
print('2. Integrates with AI agents via MCP')
print('3. Provides 16 tools for code analysis')
print('4. Supports multiple editors and IDEs')
print('5. Offers both CLI and Web UI interfaces')
print()
print('Key benefits:')
print('- Deep code understanding for AI agents')
print('- Impact analysis before changes')
print('- Safe refactoring with dependency mapping')
print('- Multi-repo support for monorepos')
print('- Auto-updating documentation')
