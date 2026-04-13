import os

def fix_unicode_in_file(file_path):
    """Fix Unicode characters in file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Unicode characters with ASCII
    replacements = [
        ('✓', '[OK]'),
        ('✗', '[ERROR]'),
        ('✅', '[OK]'),
        ('❌', '[ERROR]'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {file_path}')

# Fix all Python files in memory skill
memory_path = 'skills/memory'
for root, dirs, files in os.walk(memory_path):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            try:
                fix_unicode_in_file(file_path)
            except Exception as e:
                print(f'Error fixing {file_path}: {e}')

print('All Python files fixed!')
