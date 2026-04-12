#!/usr/bin/env python3
"""
导出脱敏数据脚本
从数据库中提取数据并进行匿名化处理
"""
import sqlite3
import json
import hashlib
import re
from datetime import datetime
import sys

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def anonymize_text(text, method='hash'):
    """匿名化文本内容"""
    if not text:
        return text
    
    if method == 'hash':
        # 使用哈希值替换敏感内容
        return hashlib.md5(text.encode()).hexdigest()[:16]
    elif method == 'mask':
        # 部分遮盖
        if len(text) > 10:
            return text[:3] + '***' + text[-3:]
        return '***'
    elif method == 'placeholder':
        # 使用占位符
        return '[REDACTED]'
    return text

def export_anonymized_data(db_path, output_dir):
    """导出脱敏数据"""
    print(f"开始导出脱敏数据...")
    print(f"数据库: {db_path}")
    print(f"输出目录: {output_dir}\n")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 过滤掉 FTS5 内部表
    tables = [t for t in tables if not t.startswith('memory_index') and t != 'sqlite_sequence']
    
    export_results = {}
    
    for table in tables:
        print(f"处理表: {table}...")
        
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"  [INFO] 表为空，跳过")
                continue
            
            # 转换为字典列表
            data = []
            for row in rows:
                row_dict = dict(row)
                
                # 根据表名进行不同程度的脱敏
                row_dict = anonymize_row(table, row_dict)
                data.append(row_dict)
            
            export_results[table] = {
                'count': len(data),
                'sample': data[:3] if data else []  # 只保留前3条作为示例
            }
            
            # 保存完整数据到 JSON
            output_file = f"{output_dir}/{table}_data.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  [OK] 导出 {len(data)} 条记录到 {output_file}")
            
        except Exception as e:
            print(f"  [FAIL] 导出失败: {e}")
    
    conn.close()
    
    # 保存汇总信息
    summary_file = f"{output_dir}/DATA_EXPORT_SUMMARY.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'export_time': datetime.now().isoformat(),
            'database': db_path,
            'total_tables': len(export_results),
            'tables': export_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n[OK] 导出完成！")
    print(f"汇总文件: {summary_file}")
    
    return export_results

def anonymize_row(table_name, row):
    """根据表名对行数据进行脱敏"""
    
    if table_name == 'memories':
        # 保留结构，脱敏内容
        if 'content' in row and row['content']:
            row['content'] = anonymize_text(row['content'], 'placeholder')
        if 'title' in row and row['title']:
            row['title'] = anonymize_text(row['title'], 'mask')
        if 'tags' in row and row['tags']:
            # 保留标签结构但脱敏值
            row['tags'] = '[ANONYMIZED_TAGS]'
    
    elif table_name == 'episodic_memories':
        if 'content' in row and row['content']:
            row['content'] = anonymize_text(row['content'], 'placeholder')
        # 保留 agent_id 用于追踪
    
    elif table_name == 'semantic_memories':
        # 保留主谓宾结构但脱敏值
        if 'subject' in row and row['subject']:
            row['subject'] = anonymize_text(row['subject'], 'mask')
        if 'object' in row and row['object']:
            row['object'] = anonymize_text(row['object'], 'mask')
    
    elif table_name == 'agent_diary':
        if 'summary' in row and row['summary']:
            row['summary'] = anonymize_text(row['summary'], 'placeholder')
        if 'learnings' in row and row['learnings']:
            row['learnings'] = '[ANONYMIZED]'
        if 'decisions' in row and row['decisions']:
            row['decisions'] = '[ANONYMIZED]'
    
    elif table_name == 'platform_messages':
        # 脱敏消息内容
        if 'content' in row and row['content']:
            row['content'] = anonymize_text(row['content'], 'placeholder')
        if 'sender_id' in row and row['sender_id']:
            row['sender_id'] = anonymize_text(row['sender_id'], 'hash')
        if 'channel_id' in row and row['channel_id']:
            row['channel_id'] = anonymize_text(row['channel_id'], 'hash')
    
    elif table_name == 'user_beliefs':
        if 'belief_content' in row and row['belief_content']:
            row['belief_content'] = anonymize_text(row['belief_content'], 'placeholder')
        if 'user_id' in row and row['user_id']:
            row['user_id'] = anonymize_text(row['user_id'], 'hash')
    
    elif table_name == 'intent_tracking':
        if 'user_intent' in row and row['user_intent']:
            row['user_intent'] = anonymize_text(row['user_intent'], 'placeholder')
        if 'inferred_goal' in row and row['inferred_goal']:
            row['inferred_goal'] = anonymize_text(row['inferred_goal'], 'placeholder')
    
    elif table_name == 'emotional_state':
        if 'trigger' in row and row['trigger']:
            row['trigger'] = anonymize_text(row['trigger'], 'placeholder')
        if 'context' in row and row['context']:
            row['context'] = anonymize_text(row['context'], 'placeholder')
    
    elif table_name == 'meta_cognition':
        if 'thought_process' in row and row['thought_process']:
            row['thought_process'] = anonymize_text(row['thought_process'], 'placeholder')
        if 'self_assessment' in row and row['self_assessment']:
            row['self_assessment'] = anonymize_text(row['self_assessment'], 'placeholder')
    
    elif table_name == 'social_context':
        if 'relationship_type' in row and row['relationship_type']:
            row['relationship_type'] = anonymize_text(row['relationship_type'], 'placeholder')
    
    elif table_name == 'evolution_log':
        if 'description' in row and row['description']:
            row['description'] = anonymize_text(row['description'], 'placeholder')
    
    elif table_name == 'layered_context':
        if 'context_value' in row and row['context_value']:
            row['context_value'] = anonymize_text(row['context_value'], 'placeholder')
    
    elif table_name == 'config':
        # 保留配置键，脱敏值（如果是敏感值）
        if 'key' in row and row['key'] and any(kw in str(row['key']).lower() for kw in ['token', 'key', 'secret', 'password', 'auth']):
            if 'value' in row and row['value']:
                row['value'] = '[REDACTED]'
    
    elif table_name == 'agent_prompts':
        # 保留提示名称，脱敏完整内容
        if 'full_content' in row and row['full_content']:
            # 保留前100字符作为预览
            content = row['full_content']
            if len(content) > 100:
                row['full_content'] = content[:100] + '\n\n[CONTENT_REDACTED]'
    
    elif table_name == 'knowledge_relations':
        # 保留关系结构
        pass  # 关系数据通常是结构化的，不需要脱敏
    
    elif table_name == 'causal_relations':
        # 保留因果关系结构
        if 'evidence' in row and row['evidence']:
            row['evidence'] = anonymize_text(row['evidence'], 'placeholder')
    
    return row

def create_sample_data_file(output_dir):
    """创建示例数据文件（用于演示）"""
    sample_data = {
        'description': 'This is anonymized sample data for demonstration purposes',
        'tables': {
            'memories': [
                {
                    'id': 1,
                    'type': 'learning',
                    'title': '[REDACTED_TITLE_1]',
                    'content': '[REDACTED_CONTENT]',
                    'category': 'knowledge',
                    'tags': '[ANONYMIZED_TAGS]',
                    'importance': 8,
                    'confidence': 0.85,
                    'created_at': '2026-04-01T10:00:00',
                    'updated_at': '2026-04-01T10:00:00'
                },
                {
                    'id': 2,
                    'type': 'event',
                    'title': '[REDACTED_TITLE_2]',
                    'content': '[REDACTED_CONTENT]',
                    'category': 'system',
                    'tags': '[ANONYMIZED_TAGS]',
                    'importance': 5,
                    'confidence': 0.75,
                    'created_at': '2026-04-02T14:30:00',
                    'updated_at': '2026-04-02T14:30:00'
                }
            ],
            'knowledge_relations': [
                {
                    'id': 1,
                    'source_memory_id': 1,
                    'target_memory_id': 2,
                    'relation_type': 'related_to',
                    'relation_strength': 0.8,
                    'created_at': '2026-04-02T15:00:00'
                }
            ]
        }
    }
    
    sample_file = f"{output_dir}/SAMPLE_DATA.json"
    with open(sample_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] 创建示例数据文件: {sample_file}")

if __name__ == '__main__':
    import os
    
    db_path = 'memory/database/xiaozhi_memory.db'
    output_dir = 'memory/database/anonymized_data'
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 导出脱敏数据
    export_anonymized_data(db_path, output_dir)
    
    # 创建示例数据
    create_sample_data_file(output_dir)
    
    print("\n" + "="*60)
    print("脱敏数据导出完成!")
    print(f"输出目录: {output_dir}")
    print("="*60)