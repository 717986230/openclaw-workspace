#!/usr/bin/env python3
"""
验证数据库功能脚本
检查优化后的数据库表是否正常工作
"""
import sqlite3
import sys

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def test_table_operations(conn, table_name):
    """测试表的基本操作"""
    cursor = conn.cursor()
    
    try:
        # 测试 SELECT
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        result = cursor.fetchone()
        
        # 获取列数
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        return True, len(columns), len(result) if result else 0
    except Exception as e:
        return False, 0, str(e)

def verify_database(db_path):
    """验证数据库"""
    print(f"验证数据库: {db_path}\n")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    # 过滤掉内部表
    tables = [t for t in tables if not t.startswith('memory_index') and t != 'sqlite_sequence']
    
    print(f"共有 {len(tables)} 个表需要验证\n")
    
    # 核心表列表（必须正常工作的表）
    core_tables = [
        'memories',
        'episodic_memories',
        'semantic_memories',
        'knowledge_relations',
        'causal_relations',
        'agent_diary',
        'agent_prompts',
        'registered_tools',
        'platform_messages',
        'user_beliefs',
        'intent_tracking',
        'emotional_state',
        'meta_cognition',
        'social_context',
        'evolution_log',
        'layered_context',
        'clawvard_students',
        'clawvard_courses',
        'clawvard_exam_results',
        'config'
    ]
    
    results = {
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    print("=" * 60)
    print("开始验证表功能")
    print("=" * 60)
    
    for table in tables:
        is_core = table in core_tables
        status, col_count, record_count = test_table_operations(conn, table)
        
        if status:
            print(f"[OK] {table:<30} ({col_count} 列, {record_count} 条记录)")
            if is_core:
                results['passed'].append(table)
        else:
            print(f"[FAIL] {table:<30} - {record_count}")
            if is_core:
                results['failed'].append(table)
            else:
                results['warnings'].append(table)
    
    # 测试核心功能
    print("\n" + "=" * 60)
    print("测试核心功能")
    print("=" * 60)
    
    # 测试 memories 表的核心操作
    try:
        cursor.execute("INSERT INTO memories (type, title, content, category, importance) VALUES (?, ?, ?, ?, ?)",
                      ('test', 'Test Memory', 'Test content', 'test', 5))
        test_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (test_id,))
        result = cursor.fetchone()
        
        cursor.execute("DELETE FROM memories WHERE id = ?", (test_id,))
        
        if result:
            print("[OK] memories 表 CRUD 测试通过")
            results['passed'].append('memories_CRUD')
        else:
            print("[FAIL] memories 表 CRUD 测试失败")
            results['failed'].append('memories_CRUD')
    except Exception as e:
        print(f"[FAIL] memories 表 CRUD 测试失败: {e}")
        results['failed'].append('memories_CRUD')
    
    # 测试全文搜索
    try:
        cursor.execute("SELECT * FROM memory_index LIMIT 1")
        result = cursor.fetchone()
        if result:
            print("[OK] 全文搜索 (FTS5) 正常工作")
            results['passed'].append('FTS5')
        else:
            print("[WARN] 全文搜索表为空，但结构正常")
            results['warnings'].append('FTS5_empty')
    except Exception as e:
        print(f"[FAIL] 全文搜索测试失败: {e}")
        results['failed'].append('FTS5')
    
    # 测试索引
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()
        print(f"[OK] 数据库有 {len(indexes)} 个索引")
        results['passed'].append('indexes')
    except Exception as e:
        print(f"[FAIL] 索引测试失败: {e}")
        results['failed'].append('indexes')
    
    # 测试事务
    try:
        conn.execute("BEGIN")
        conn.execute("ROLLBACK")
        print("[OK] 事务功能正常")
        results['passed'].append('transaction')
    except Exception as e:
        print(f"[FAIL] 事务测试失败: {e}")
        results['failed'].append('transaction')
    
    conn.close()
    
    # 汇总
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    print(f"通过: {len(results['passed'])} 项")
    print(f"失败: {len(results['failed'])} 项")
    print(f"警告: {len(results['warnings'])} 项")
    
    if results['failed']:
        print("\n失败的项:")
        for item in results['failed']:
            print(f"  - {item}")
    
    if results['warnings']:
        print("\n警告项:")
        for item in results['warnings']:
            print(f"  - {item}")
    
    print("\n" + "=" * 60)
    if len(results['failed']) == 0:
        print("数据库功能验证通过！")
        print("=" * 60)
        return True
    else:
        print(f"数据库功能验证失败 ({len(results['failed'])} 项)")
        print("=" * 60)
        return False

if __name__ == '__main__':
    db_path = 'memory/database/xiaozhi_memory.db'
    
    success = verify_database(db_path)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
