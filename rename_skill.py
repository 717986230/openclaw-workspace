import os
import re

def update_file(file_path, replacements):
    """Update file with multiple replacements"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Updated: {file_path}')

# Define replacements
replacements = [
    ('agency-agents-caller', 'agent-caller'),
    ('Agency Agents Caller', 'Agent Caller'),
    ('Agency-Agents-Caller', 'Agent-Caller'),
]

# Update README.md
readme_path = 'skills/agent-caller/README.md'
if os.path.exists(readme_path):
    update_file(readme_path, replacements)

# Update SKILL.md
skill_path = 'skills/agent-caller/SKILL.md'
if os.path.exists(skill_path):
    update_file(skill_path, replacements)

print('All files updated successfully!')
