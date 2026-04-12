#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建脱敏数据库副本给 Erbing-1B 训练
复制所有数据，过滤敏感字段
"""

import sqlite3
import shutil
import os
import re
from datetime import datetime

SOURCE_DB = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
OUTPUT_DB = "C:/Users/Administrator/.openclaw/workspace/1b_training_data/erbing_1b_training.db"

# 敏感词模式
SENSITIVE_PATTERNS = [
    r'api[_\-]?key',
    r'token',
    r'secret',
    r'password',
    r'credential',
    r'auth[_\-]',
    r'private[_\-]',
    r'密钥',
    r'密码',
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI keys
    r'ghp_[a-zA-Z0-9]{36}',   # GitHub tokens
]

# 完全跳过的表
SKIP_TABLES = [
    'config',
    'sqlite_sequence',
    'sqlite_stat1',
]

# 跳过的列
SKIP_COLUMNS = [
    'metadata',  # 可能包含敏感信息
]

def is_sensitive(text):
    """检查文本是否包含敏感信息"""
    if text is None:
        return False
    text_str = str(text)
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text_str, re.IGNORECASE):
            return True
    return False

def sanitize_value(value):
    """清理单个值"""
    if value is None:
        return None
    if isinstance(value, str):
        if is_sensitive(value):
            return '[REDACTED]'
        return value
    return value

def create_sanitized_database():
    print("开始创建脱敏数据库...")
    
    # 删除旧文件
    if os.path.exists(OUTPUT_DB):
        os.remove(OUTPUT_DB)
    
    # 连接源数据库
    src_conn = sqlite3.connect(SOURCE_DB)
    src_cursor = src_conn.cursor()
    
    # 创建目标数据库
    dst_conn = sqlite3.connect(OUTPUT_DB)
    dst_cursor = dst_conn.cursor()
    
    # 获取所有表
    src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [t[0] for t in src_cursor.fetchall()]
    
    total_rows = 0
    skipped_rows = 0
    table_stats = {}
    
    for table in all_tables:
        if table in SKIP_TABLES:
            print(f"跳过表: {table}")
            continue
        
        # 获取表结构
        src_cursor.execute(f"PRAGMA table_info({table})")
        columns_info = src_cursor.fetchall()
        columns = [col[1] for col in columns_info]
        column_types = {col[1]: col[2] for col in columns_info}
        
        # 过滤敏感列
        safe_columns = [col for col in columns if col.lower() not in [c.lower() for c in SKIP_COLUMNS]]
        
        if not safe_columns:
            print(f"  表 {table} 没有安全列，跳过")
            continue
        
        # 创建表结构
        create_cols = []
        for col in columns_info:
            if col[1] in safe_columns:
                create_cols.append(f'"{col[1]}" {col[2]}')
        
        create_sql = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(create_cols)})'
        try:
            dst_cursor.execute(create_sql)
        except Exception as e:
            print(f"  创建表 {table} 失败: {e}")
            continue
        
        # 复制数据
        try:
            cols_str = ', '.join(f'"{c}"' for c in safe_columns)
            src_cursor.execute(f'SELECT {cols_str} FROM "{table}"')
            rows = src_cursor.fetchall()
        except Exception as e:
            print(f"  读取表 {table} 失败: {e}")
            continue
        
        safe_rows = []
        for row in rows:
            # 检查是否有敏感内容
            has_sensitive = False
            for val in row:
                if isinstance(val, str) and is_sensitive(val):
                    has_sensitive = True
                    break
            
            if not has_sensitive:
                # 清理值
                safe_row = tuple(sanitize_value(v) for v in row)
                safe_rows.append(safe_row)
        
        # 插入数据
        if safe_rows:
            placeholders = ', '.join(['?' for _ in safe_columns])
            insert_sql = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders})'
            try:
                dst_cursor.executemany(insert_sql, safe_rows)
            except Exception as e:
                # 逐条插入
                for row in safe_rows:
                    try:
                        dst_cursor.execute(insert_sql, row)
                    except:
                        pass
        
        table_stats[table] = {
            'total': len(rows),
            'kept': len(safe_rows),
            'filtered': len(rows) - len(safe_rows)
        }
        total_rows += len(rows)
        skipped_rows += len(rows) - len(safe_rows)
        
        print(f"  {table}: {len(safe_rows)}/{len(rows)} 行保留")
    
    # 创建索引
    print("\n创建索引...")
    dst_cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type)")
    dst_cursor.execute("CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category)")
    dst_cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_relations_type ON knowledge_relations(relation_type)")
    
    # 提交并关闭
    dst_conn.commit()
    src_conn.close()
    dst_conn.close()
    
    # 输出统计
    print(f"\n{'='*60}")
    print("脱敏数据库创建完成!")
    print(f"总行数: {total_rows}")
    print(f"保留行数: {total_rows - skipped_rows}")
    print(f"过滤行数: {skipped_rows}")
    print(f"输出文件: {OUTPUT_DB}")
    print(f"文件大小: {os.path.getsize(OUTPUT_DB) / 1024 / 1024:.2f} MB")
    
    # 保存统计
    stats = {
        'created_at': datetime.now().isoformat(),
        'source_db': SOURCE_DB,
        'output_db': OUTPUT_DB,
        'total_rows': total_rows,
        'kept_rows': total_rows - skipped_rows,
        'filtered_rows': skipped_rows,
        'tables': table_stats
    }
    
    import json
    stats_file = OUTPUT_DB.replace('.db', '_stats.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"统计文件: {stats_file}")
    
    return OUTPUT_DB

if __name__ == "__main__":
    create_sanitized_database()
