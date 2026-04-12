#!/usr/bin/env python3
"""
数据库表结构优化脚本
执行数据库清理、合并和优化操作
"""
import sqlite3
import os
import shutil
import sys
from datetime import datetime

# 设置输出编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def backup_database(db_path):
    """备份数据库文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"[OK] 数据库已备份到: {backup_path}")
    return backup_path

def get_table_info(conn, table_name):
    """获取表结构信息"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    return cursor.fetchall()

def get_table_count(conn, table_name):
    """获取表的记录数"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]
    except:
        return -1

def optimize_database(db_path):
    """优化数据库"""
    print(f"开始优化数据库: {db_path}\n")

    # 备份数据库
    backup_path = backup_database(db_path)

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = [row[0] for row in cursor.fetchall()]

    print(f"当前数据库中有 {len(all_tables)} 个表\n")

    # 分类表
    tables_with_data = []
    tables_without_data = []
    fts_tables = []

    for table in all_tables:
        if table.startswith('memory_index'):
            fts_tables.append(table)
            continue

        count = get_table_count(conn, table)
        if count > 0:
            tables_with_data.append((table, count))
        else:
            tables_without_data.append(table)

    print("=== 有数据的表 ===")
    for table, count in sorted(tables_with_data, key=lambda x: x[1], reverse=True):
        print(f"  {table}: {count} 条记录")

    print(f"\n=== 无数据的表 ({len(tables_without_data)} 个) ===")
    for table in tables_without_data:
        print(f"  {table}")

    print(f"\n=== FTS5 内部表 ({len(fts_tables)} 个) ===")
    for table in fts_tables:
        print(f"  {table}")

    # 保留历史/扩展表，避免再次误删
    print("\n=== 跳过删除空表 ===")
    unused_tables = []
    deleted_count = 0
    print("  [SKIP] 保留历史/扩展表结构，不再按空表条件删除")
    print(f"\n共删除 {deleted_count} 个未使用的表")

    # 合并重复的表
    print("\n=== 开始合并重复的表 ===")

    # 合并 config 和 system_config
    if 'system_config' in all_tables and 'config' in all_tables:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO config (key, value, updated_at)
                SELECT key, value, updated_at FROM system_config
            """)
            cursor.execute("DROP TABLE IF EXISTS system_config")
            print("  [OK] 合并 system_config 到 config")
        except Exception as e:
            print(f"  [FAIL] 合并 system_config 失败: {e}")

    # 合并 memory_links 和 memory_associations
    if 'memory_associations' in all_tables and 'memory_links' in all_tables:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO memory_links (memory_a_id, memory_b_id, link_type, strength, created_at)
                SELECT memory_a_id, memory_b_id, association_type, relevance_score, created_at
                FROM memory_associations
            """)
            print("  [OK] 合并 memory_associations 到 memory_links（保留原表）")
        except Exception as e:
            print(f"  [FAIL] 合并 memory_associations 失败: {e}")

    # 重建索引
    print("\n=== 开始重建索引 ===")

    # 删除旧索引
    indexes_to_drop = [
        'idx_memories_type',
        'idx_memories_category',
        'idx_memories_created_at',
        'idx_memories_importance',
        'idx_memory_links_a',
        'idx_memory_links_b',
        'idx_memory_links_type',
        'idx_causal_cause',
        'idx_causal_effect',
        'idx_knowledge_source',
        'idx_knowledge_target',
        'idx_agent_diary_date',
        'idx_agent_diary_agent',
        'idx_user_beliefs_user',
        'idx_user_beliefs_confidence',
        'idx_intent_session',
        'idx_intent_confidence',
        'idx_emotional_user',
        'idx_emotional_created'
    ]

    for index in indexes_to_drop:
        try:
            cursor.execute(f"DROP INDEX IF EXISTS {index}")
        except:
            pass

    # 创建新索引
    indexes_to_create = [
        ("idx_memories_type", "memories", "type"),
        ("idx_memories_category", "memories", "category"),
        ("idx_memories_created_at", "memories", "created_at"),
        ("idx_memories_importance", "memories", "importance"),
        ("idx_memory_links_a", "memory_links", "memory_a_id"),
        ("idx_memory_links_b", "memory_links", "memory_b_id"),
        ("idx_memory_links_type", "memory_links", "link_type"),
        ("idx_causal_cause", "causal_relations", "cause_memory_id"),
        ("idx_causal_effect", "causal_relations", "effect_memory_id"),
        ("idx_knowledge_source", "knowledge_relations", "source_memory_id"),
        ("idx_knowledge_target", "knowledge_relations", "target_memory_id"),
        ("idx_agent_diary_date", "agent_diary", "date"),
        ("idx_agent_diary_agent", "agent_diary", "agent_id"),
        ("idx_user_beliefs_user", "user_beliefs", "user_id"),
        ("idx_user_beliefs_confidence", "user_beliefs", "confidence"),
        ("idx_intent_session", "intent_tracking", "session_id"),
        ("idx_intent_confidence", "intent_tracking", "confidence"),
        ("idx_emotional_user", "emotional_state", "user_id"),
        ("idx_emotional_created", "emotional_state", "created_at")
    ]

    created_count = 0
    for index_name, table, column in indexes_to_create:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})")
            print(f"  [OK] 创建索引: {index_name}")
            created_count += 1
        except Exception as e:
            print(f"  [FAIL] 创建索引失败 {index_name}: {e}")

    print(f"\n共创建 {created_count} 个索引")

    # 优化数据库
    print("\n=== 优化数据库 ===")
    try:
        cursor.execute("VACUUM")
        print("  [OK] 数据库优化完成 (VACUUM)")
    except Exception as e:
        print(f"  [FAIL] 数据库优化失败: {e}")

    try:
        cursor.execute("ANALYZE")
        print("  [OK] 数据库分析完成 (ANALYZE)")
    except Exception as e:
        print(f"  [FAIL] 数据库分析失败: {e}")

    # 提交更改
    conn.commit()

    # 获取优化后的表信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    final_tables = [row[0] for row in cursor.fetchall()]

    print(f"\n=== 优化完成 ===")
    print(f"优化前表数量: {len(all_tables)}")
    print(f"优化后表数量: {len(final_tables)}")
    print(f"删除表数量: {deleted_count}")
    print(f"备份位置: {backup_path}")

    # 获取数据库大小
    db_size = os.path.getsize(db_path) / 1024 / 1024
    print(f"数据库大小: {db_size:.2f} MB")

    conn.close()

    return backup_path

def generate_schema_documentation(db_path, output_path):
    """生成表结构文档"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 数据库表结构文档\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"数据库路径: {db_path}\n\n")
        f.write(f"表数量: {len(tables)}\n\n")

        for table in tables:
            if table.startswith('memory_index'):
                continue

            f.write(f"## {table}\n\n")

            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            f.write("### 列信息\n\n")
            f.write("| 列名 | 类型 | 主键 | 非空 | 默认值 |\n")
            f.write("|------|------|------|------|--------|\n")

            for col in columns:
                col_id, name, col_type, not_null, default_val, pk = col
                pk_str = "✓" if pk else ""
                not_null_str = "✓" if not_null else ""
                default_str = str(default_val) if default_val is not None else ""

                f.write(f"| {name} | {col_type} | {pk_str} | {not_null_str} | {default_str} |\n")

            f.write("\n")

            # 获取记录数
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                f.write(f"### 记录数\n\n")
                f.write(f"{count} 条记录\n\n")
            except:
                pass

            # 获取索引
            cursor.execute(f"PRAGMA index_list({table})")
            indexes = cursor.fetchall()

            if indexes:
                f.write("### 索引\n\n")
                for idx in indexes:
                    idx_name = idx[1]
                    f.write(f"- {idx_name}\n")
                f.write("\n")

            f.write("---\n\n")

    conn.close()

    print(f"[OK] 表结构文档已生成: {output_path}")

if __name__ == "__main__":
    db_path = "memory/database/xiaozhi_memory.db"

    if not os.path.exists(db_path):
        print(f"[FAIL] 数据库文件不存在: {db_path}")
        exit(1)

    print("=" * 60)
    print("数据库表结构优化工具")
    print("=" * 60)
    print()

    # 优化数据库
    backup_path = optimize_database(db_path)

    # 生成表结构文档
    schema_doc_path = "memory/database/DATABASE_SCHEMA.md"
    generate_schema_documentation(db_path, schema_doc_path)

    print()
    print("=" * 60)
    print("优化完成!")
    print("=" * 60)
