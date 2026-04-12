#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出数据库内容供 1B 模型学习
排除敏感信息（密钥、token等）
"""

import sqlite3
import json
import os

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
OUTPUT_DIR = "C:/Users/Administrator/.openclaw/workspace/1b_training_data"

# 敏感词列表 - 包含这些的字段会被跳过
SENSITIVE_KEYWORDS = [
    'key', 'token', 'secret', 'password', 'credential', 'api_key',
    'auth', 'private', '密钥', '密码', 'token', 'api_token'
]

# 敏感表 - 这些表完全跳过
SENSITIVE_TABLES = [
    'config',  # 可能包含配置密钥
]

# 需要导出的核心表
EXPORT_TABLES = [
    'memories',
    'knowledge_relations',
    'causal_relations',
    'episodic_memories',
    'semantic_memories',
    'agent_diary',
    'evolution_log',
    'user_beliefs',
    'intent_tracking',
    'emotional_state',
    'meta_cognition',
    'social_context',
    'session_summaries',
    'procedural_memories',
    'working_memory',
    'memory_links',
    'memory_associations',
    'graph_insights',
    'deep_research',
]

def is_sensitive(text):
    """检查文本是否包含敏感信息"""
    if text is None:
        return False
    text_lower = str(text).lower()
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def export_table(cursor, table_name):
    """导出单个表"""
    print(f"\n导出表: {table_name}")
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 过滤敏感列
    safe_columns = [col for col in columns if not is_sensitive(col)]
    
    # 获取数据
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
    except Exception as e:
        print(f"  跳过 {table_name}: {e}")
        return None
    
    # 转换数据，过滤敏感内容
    safe_rows = []
    for row in rows:
        safe_row = {}
        skip_row = False
        for i, col in enumerate(columns):
            if col in safe_columns:
                value = row[i]
                # 检查值是否包含敏感信息
                if is_sensitive(value):
                    skip_row = True
                    break
                safe_row[col] = value
        if not skip_row:
            safe_rows.append(safe_row)
    
    print(f"  导出 {len(safe_rows)} 条记录 ({len(rows)} 总记录, 过滤 {len(rows) - len(safe_rows)} 条敏感)")
    
    return {
        'table': table_name,
        'columns': safe_columns,
        'count': len(safe_rows),
        'data': safe_rows
    }

def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [t[0] for t in cursor.fetchall()]
    
    print(f"数据库共有 {len(all_tables)} 个表")
    print(f"计划导出 {len(EXPORT_TABLES)} 个核心表")
    
    # 导出数据
    exported_data = {}
    total_records = 0
    
    for table in EXPORT_TABLES:
        if table in SENSITIVE_TABLES:
            print(f"跳过敏感表: {table}")
            continue
        if table not in all_tables:
            print(f"表不存在: {table}")
            continue
        
        result = export_table(cursor, table)
        if result:
            exported_data[table] = result
            total_records += result['count']
    
    conn.close()
    
    # 保存为JSON
    output_file = os.path.join(OUTPUT_DIR, "knowledge_base.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(exported_data, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n{'='*60}")
    print(f"导出完成!")
    print(f"总表数: {len(exported_data)}")
    print(f"总记录数: {total_records}")
    print(f"输出文件: {output_file}")
    
    # 生成统计摘要
    summary = {
        'export_time': '2026-04-12',
        'total_tables': len(exported_data),
        'total_records': total_records,
        'tables': {name: data['count'] for name, data in exported_data.items()}
    }
    
    summary_file = os.path.join(OUTPUT_DIR, "export_summary.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"摘要文件: {summary_file}")
    
    # 生成训练格式的文本文件
    text_file = os.path.join(OUTPUT_DIR, "knowledge_base.txt")
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write("# 二饼知识库导出\n")
        f.write(f"# 导出时间: 2026-04-12\n")
        f.write(f"# 总记录数: {total_records}\n\n")
        
        for table_name, table_data in exported_data.items():
            f.write(f"\n## 表: {table_name} ({table_data['count']} 条)\n\n")
            for row in table_data['data'][:100]:  # 每个表最多100条示例
                f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")
    
    print(f"文本文件: {text_file}")
    
    return output_file

if __name__ == "__main__":
    main()
