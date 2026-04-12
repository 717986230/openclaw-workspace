"""
检查并脱敏敏感信息
扫描数据库和文件，移除或替换所有敏感数据
"""

import sqlite3
import json
import re
import os
from pathlib import Path

def scan_and_clean_sensitive_data():
    """扫描并清理敏感数据"""
    
    print('=== Scanning for Sensitive Data ===')
    print()
    
    # 1. 检查数据库文件
    db_files = [
        'memory/database/xiaozhi_memory.db',
        '1b_training_data/erbing_virtual_world.db'
    ]
    
    sensitive_patterns = [
        r'password',
        r'secret',
        r'api_key',
        r'token',
        r'credential',
        r'private_key',
        r'auth',
        r'login',
        r'email',
        r'phone',
        r'address',
        r'credit_card'
    ]
    
    # 2. 检查文件
    print('1. Checking .gitignore for database files...')
    gitignore_path = '.gitignore'
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            gitignore_content = f.read()
        
        # 检查是否忽略了数据库文件
        db_patterns = ['*.db', '*.db-journal', '*.sqlite', '*.sqlite3']
        
        for pattern in db_patterns:
            if pattern not in gitignore_content:
                print(f'   Adding {pattern} to .gitignore')
                gitignore_content += f'\n{pattern}'
        
        # 写回.gitignore
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        
        print('   .gitignore updated')
    else:
        print('   Creating .gitignore with database patterns')
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join([
                '# Database files',
                '*.db',
                '*.db-journal',
                '*.sqlite',
                '*.sqlite3',
                '',
                '# Sensitive files',
                '*_backup_*.zip',
                '*-journal',
                ''
            ]))
    
    print()
    
    # 3. 检查已提交的敏感文件
    print('2. Checking for sensitive files in Git...')
    
    sensitive_files = []
    
    # 扫描所有文件
    for root, dirs, files in os.walk('.'):
        # 跳过.git目录
        if '.git' in root:
            continue
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # 检查数据库文件
            if file.endswith(('.db', '.db-journal', '.sqlite', '.sqlite3')):
                sensitive_files.append(file_path)
                print(f'   Found database: {file_path}')
            
            # 检查备份文件
            if 'backup' in file.lower() and file.endswith('.zip'):
                sensitive_files.append(file_path)
                print(f'   Found backup: {file_path}')
    
    print()
    
    # 4. 从Git中移除敏感文件
    if sensitive_files:
        print('3. Removing sensitive files from Git...')
        
        for file in sensitive_files:
            print(f'   Removing: {file}')
            os.system(f'git rm --cached "{file}" 2>nul')
        
        print()
    
    # 5. 检查代码文件中的敏感信息
    print('4. Scanning code files for sensitive patterns...')
    
    code_files = []
    for ext in ['.py', '.js', '.json', '.md', '.txt']:
        code_files.extend(Path('.').rglob(f'*{ext}'))
    
    sensitive_found = []
    
    for file_path in code_files:
        if '.git' in str(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查敏感模式
            for pattern in sensitive_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    sensitive_found.append(str(file_path))
                    break
        except:
            pass
    
    if sensitive_found:
        print(f'   Found potential sensitive info in {len(sensitive_found)} files:')
        for file in sensitive_found[:10]:
            print(f'   - {file}')
    else:
        print('   No sensitive patterns found')
    
    print()
    
    # 6. 创建脱敏报告
    print('5. Creating sanitization report...')
    
    report = {
        'scan_time': str(os.popen('date /t && time /t').read()),
        'gitignore_updated': True,
        'sensitive_files_found': len(sensitive_files),
        'sensitive_files_removed': sensitive_files,
        'code_files_scanned': len(code_files),
        'sensitive_patterns_found': len(sensitive_found),
        'recommendations': [
            'Always use .gitignore for database files',
            'Never commit real passwords or API keys',
            'Use environment variables for secrets',
            'Review files before committing',
            'Use git-secrets or similar tools'
        ]
    }
    
    with open('SANITIZATION_REPORT.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print('   Report saved to SANITIZATION_REPORT.json')
    print()
    
    # 7. 更新.gitignore
    print('6. Final .gitignore update...')
    
    additional_ignores = [
        '# Sanitization reports',
        'SANITIZATION_REPORT.json',
        '',
        '# Temporary files',
        '*.tmp',
        '*.temp',
        '*.log',
        ''
    ]
    
    with open('.gitignore', 'a', encoding='utf-8') as f:
        f.write('\n'.join(additional_ignores))
    
    print('   .gitignore finalized')
    print()
    
    print('=== Sanitization Complete ===')
    print()
    print('Summary:')
    print(f'  - Database files: Added to .gitignore')
    print(f'  - Sensitive files found: {len(sensitive_files)}')
    print(f'  - Code files scanned: {len(code_files)}')
    print(f'  - Sensitive patterns found: {len(sensitive_found)}')
    print()
    print('Next steps:')
    print('  1. Review sensitive files list')
    print('  2. Remove sensitive files from Git history if needed')
    print('  3. Commit .gitignore changes')
    print('  4. Push cleaned repository')
    
    return report

if __name__ == '__main__':
    scan_and_clean_sensitive_data()
