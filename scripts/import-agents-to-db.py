#!/usr/bin/env python3
"""
导入 agency-agents 到数据库
"""
import os
import re
import sqlite3
import json
from pathlib import Path
from datetime import datetime

# 数据库路径
DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
AGENTS_PATH = "C:/Users/Administrator/.openclaw/workspace/agency-agents"

def parse_yaml_frontmatter(content):
    """解析 YAML frontmatter"""
    if not content.startswith('---'):
        return {}, content
    
    # 查找第二个 ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return {}, content
    
    yaml_content = content[3:end_idx].strip()
    body_content = content[end_idx+3:].strip()
    
    # 简单解析 YAML
    metadata = {}
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip().strip('"\'')
    
    return metadata, body_content

def extract_agent_info(filepath, content):
    """提取 Agent 信息"""
    metadata, body = parse_yaml_frontmatter(content)
    
    # 从文件路径提取类别
    rel_path = os.path.relpath(filepath, AGENTS_PATH)
    parts = rel_path.split(os.sep)
    category = parts[0] if len(parts) > 1 else "uncategorized"
    
    # 从文件名提取 agent 名称
    filename = os.path.basename(filepath)
    agent_name = os.path.splitext(filename)[0]
    
    # 从 body 提取描述（第一行）
    lines = body.split('\n')
    description = ""
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            description = line[:500]  # 取前500字符作为描述
            break
    
    return {
        'name': metadata.get('name', agent_name),
        'category': category,
        'description': metadata.get('description', description),
        'emoji': metadata.get('emoji', '🤖'),
        'color': metadata.get('color', 'blue'),
        'tools': metadata.get('tools', ''),
        'vibe': metadata.get('vibe', ''),
        'filepath': rel_path,
        'full_content': content,
        'metadata': json.dumps(metadata)
    }

def main():
    print("开始导入 agency-agents 到数据库...")
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建表（如果不存在）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            emoji TEXT,
            color TEXT,
            tools TEXT,
            vibe TEXT,
            filepath TEXT UNIQUE,
            full_content TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 扫描所有 agent 文件
    agents_dir = Path(AGENTS_PATH)
    md_files = list(agents_dir.rglob("*.md"))
    
    # 过滤掉非 agent 文件
    exclude_patterns = ['README', 'CONTRIBUTING', 'LICENSE', '.github', 'examples']
    agent_files = [
        f for f in md_files 
        if not any(pattern in str(f) for pattern in exclude_patterns)
    ]
    
    print(f"发现 {len(agent_files)} 个 agent 文件")
    
    # 导入每个 agent
    imported = 0
    errors = []
    
    for filepath in agent_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            agent_info = extract_agent_info(str(filepath), content)
            
            # 插入或更新
            cursor.execute('''
                INSERT INTO agent_prompts 
                (name, category, description, emoji, color, tools, vibe, filepath, full_content, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(filepath) DO UPDATE SET
                    name=excluded.name,
                    category=excluded.category,
                    description=excluded.description,
                    emoji=excluded.emoji,
                    color=excluded.color,
                    tools=excluded.tools,
                    vibe=excluded.vibe,
                    full_content=excluded.full_content,
                    metadata=excluded.metadata,
                    updated_at=excluded.updated_at
            ''', (
                agent_info['name'],
                agent_info['category'],
                agent_info['description'],
                agent_info['emoji'],
                agent_info['color'],
                agent_info['tools'],
                agent_info['vibe'],
                agent_info['filepath'],
                agent_info['full_content'],
                agent_info['metadata'],
                datetime.now().isoformat()
            ))
            
            imported += 1
            if imported % 20 == 0:
                print(f"已导入 {imported}/{len(agent_files)} 个 agent")
                
        except Exception as e:
            errors.append(f"{filepath}: {str(e)}")
    
    # 提交事务
    conn.commit()
    
    # 统计
    cursor.execute("SELECT category, COUNT(*) FROM agent_prompts GROUP BY category")
    stats = cursor.fetchall()
    
    print("\n导入统计:")
    print(f"成功导入: {imported} 个 agent")
    print(f"失败: {len(errors)} 个")
    
    print("\n分类统计:")
    for category, count in stats:
        print(f"  {category}: {count}")
    
    if errors:
        print("\n错误详情:")
        for error in errors[:5]:
            print(f"  {error}")
    
    # 关闭连接
    conn.close()
    
    print("\n导入完成！")

if __name__ == "__main__":
    main()
