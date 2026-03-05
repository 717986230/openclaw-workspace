#!/usr/bin/env python3
"""
把所有数据迁移到真正的 SQLite 大脑数据库
"""

import sqlite3
import json
import os
import shutil
from datetime import datetime

# 路径配置
OLD_MEMORY_DB = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"
OLD_SECURE_DB = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_secure.db"
NEW_JSON_BRAIN = r"C:\Users\admin\.openclaw\workspace\memory\erbing_brain.json"
BACKUP_DIR = r"C:\Users\admin\.openclaw\workspace\memory\database\backups"

def backup_old_databases():
    """备份旧数据库"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if os.path.exists(OLD_MEMORY_DB):
        backup_path = os.path.join(BACKUP_DIR, f"xiaozhi_memory_{timestamp}.db")
        shutil.copy2(OLD_MEMORY_DB, backup_path)
        print(f"[OK] Backed up memory db: {backup_path}")
    
    if os.path.exists(OLD_SECURE_DB):
        backup_path = os.path.join(BACKUP_DIR, f"xiaozhi_secure_{timestamp}.db")
        shutil.copy2(OLD_SECURE_DB, backup_path)
        print(f"[OK] Backed up secure db: {backup_path}")

def inspect_old_database():
    """检查旧数据库的结构和内容"""
    print("\n[INSPECT] Checking old memory database...")
    
    if not os.path.exists(OLD_MEMORY_DB):
        print("[ERROR] Old memory database not found!")
        return None
    
    conn = sqlite3.connect(OLD_MEMORY_DB)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"[TABLES] List: {[t[0] for t in tables]}")
    
    # 查看每个表的数据量
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")
        except:
            pass
    
    conn.close()
    return tables

def load_new_json_brain():
    """加载新的 JSON 大脑数据"""
    print("\n[LOAD] Loading new JSON brain...")
    if os.path.exists(NEW_JSON_BRAIN):
        with open(NEW_JSON_BRAIN, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"[OK] Loaded: {len(data.get('core_memories', []))} core memories")
        return data
    else:
        print("[ERROR] JSON brain not found")
        return None

def merge_and_update_brain():
    """合并并更新大脑数据库"""
    print("\n[MERGE] Starting brain data merge...")
    
    # 连接到旧数据库（作为基础）
    conn = sqlite3.connect(OLD_MEMORY_DB)
    cursor = conn.cursor()
    
    # 加载新的 JSON 数据
    json_brain = load_new_json_brain()
    
    if json_brain:
        # 插入或更新核心记忆
        print("\n[UPDATE] Updating core memories...")
        for memory in json_brain.get('core_memories', []):
            try:
                # 先看看表结构，灵活处理
                cursor.execute("PRAGMA table_info(memories)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'title' in columns and 'content' in columns:
                    # 尝试插入
                    placeholders = ', '.join(['?'] * len(memory))
                    columns_str = ', '.join(memory.keys())
                    values = list(memory.values())
                    # 简化：只插入必要字段
                    cursor.execute("""
                        INSERT OR IGNORE INTO memories (title, content, created_at)
                        VALUES (?, ?, ?)
                    """, (
                        memory['title'],
                        memory['content'],
                        memory.get('created_at', datetime.now().isoformat())
                    ))
                    print(f"  [OK] {memory['title']}")
            except Exception as e:
                print(f"  [SKIP] {memory['title']} - {e}")
    
    conn.commit()
    conn.close()
    print("\n[OK] Database update complete!")

def print_final_stats():
    """打印最终统计"""
    print("\n" + "="*50)
    print("Erbing Brain Migration Complete!")
    print("="*50)
    
    conn = sqlite3.connect(OLD_MEMORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n[STATS] Database stats ({OLD_MEMORY_DB}):")
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  - {table_name}: {count} records")
        except:
            pass
    
    conn.close()
    print("\n[OK] Brain activated!")

if __name__ == "__main__":
    print("="*50)
    print("Erbing Brain Migration System")
    print("="*50)
    
    # 1. 备份旧数据库
    backup_old_databases()
    
    # 2. 检查旧数据库
    inspect_old_database()
    
    # 3. 合并和更新
    merge_and_update_brain()
    
    # 4. 打印最终统计
    print_final_stats()
