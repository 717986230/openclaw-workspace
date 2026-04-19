import subprocess
import json
import base64
import os

base = 'C:/Users/Administrator/.openclaw/workspace/ai-agent-research'

repos_info = {
    'claude-code': 'dwhite612/claude-code-setup',
    'masterclaw': 'TheMasterClaw/masterclaw-core',
    'omnethdb': 'ubcent/omnethdb',
    'openclaw-template': 'ivancheungckn/openclaw-workspace-template',
    'modularintellect': 'LuckCow/ModularIntellect',
    'hermes-agent': 'NousResearch/hermes-agent',
}

for name, repo in repos_info.items():
    r = subprocess.run(['gh', 'repo', 'view', repo, '--json', 
                       'name,description,stargazerCount,primaryLanguage,url,pushedAt'],
                      capture_output=True, text=True, encoding='utf-8')
    if r.returncode == 0:
        d = json.loads(r.stdout)
        stars = d.get('stargazerCount', 0)
        lang = d.get('primaryLanguage', {})
        lang_name = lang.get('name', '?') if lang else '?'
        desc = (d.get('description') or '')[:120]
        pushed = d.get('pushedAt', '')[:10]
        print('=== {} ==='.format(name))
        print('  Stars: {} | Lang: {}'.format(stars, lang_name))
        print('  Desc: {}'.format(desc))
        print('  Pushed: {}'.format(pushed))
        print()