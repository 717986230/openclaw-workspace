import os

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
    ('memory-complete-restore', 'memory'),
    ('Memory Complete Restore', 'Memory'),
    ('Memory-Complete-Restore', 'Memory'),
    ('memory-system-complete', 'memory'),
    ('Memory System Complete', 'Memory'),
    ('Memory-System-Complete', 'Memory'),
]

# Update all files in memory skill
memory_path = 'skills/memory'
for root, dirs, files in os.walk(memory_path):
    for file in files:
        if file.endswith(('.md', '.py', '.json', '.txt')):
            file_path = os.path.join(root, file)
            try:
                update_file(file_path, replacements)
            except Exception as e:
                print(f'Error updating {file_path}: {e}')

print('All files updated successfully!')
