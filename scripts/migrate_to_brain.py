#!/usr/bin/env python3
"""
鎶婃墍鏈夋暟鎹縼绉诲埌鐪熸鐨?SQLite 澶ц剳鏁版嵁搴?"""

import sqlite3
import json
import os
import shutil
from datetime import datetime

# 璺緞閰嶇疆
OLD_MEMORY_DB = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db"
OLD_SECURE_DB = r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_secure.db"
NEW_JSON_BRAIN = r"C:\Users\Administrator\.openclaw\workspace\memory\erbing_brain.json"
BACKUP_DIR = r"C:\Users\Administrator\.openclaw\workspace\memory\database\backups"

def backup_old_databases():
    """澶囦唤鏃ф暟鎹簱"""
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
    """妫€鏌ユ棫鏁版嵁搴撶殑缁撴瀯鍜屽唴瀹?""
    print("\n[INSPECT] Checking old memory database...")
    
    if not os.path.exists(OLD_MEMORY_DB):
        print("[ERROR] Old memory database not found!")
        return None
    
    conn = sqlite3.connect(OLD_MEMORY_DB)
    cursor = conn.cursor()
    
    # 鑾峰彇鎵€鏈夎〃
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"[TABLES] List: {[t[0] for t in tables]}")
    
    # 鏌ョ湅姣忎釜琛ㄧ殑鏁版嵁閲?    for table in tables:
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
    """鍔犺浇鏂扮殑 JSON 澶ц剳鏁版嵁"""
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
    """鍚堝苟骞舵洿鏂板ぇ鑴戞暟鎹簱"""
    print("\n[MERGE] Starting brain data merge...")
    
    # 杩炴帴鍒版棫鏁版嵁搴擄紙浣滀负鍩虹锛?    conn = sqlite3.connect(OLD_MEMORY_DB)
    cursor = conn.cursor()
    
    # 鍔犺浇鏂扮殑 JSON 鏁版嵁
    json_brain = load_new_json_brain()
    
    if json_brain:
        # 鎻掑叆鎴栨洿鏂版牳蹇冭蹇?        print("\n[UPDATE] Updating core memories...")
        for memory in json_brain.get('core_memories', []):
            try:
                # 鍏堢湅鐪嬭〃缁撴瀯锛岀伒娲诲鐞?                cursor.execute("PRAGMA table_info(memories)")
                columns = [col[1] for col in cursor.fetchall()]
                
                if 'title' in columns and 'content' in columns:
                    # 灏濊瘯鎻掑叆
                    placeholders = ', '.join(['?'] * len(memory))
                    columns_str = ', '.join(memory.keys())
                    values = list(memory.values())
                    # 绠€鍖栵細鍙彃鍏ュ繀瑕佸瓧娈?                    cursor.execute("""
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
    """鎵撳嵃鏈€缁堢粺璁?""
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
    
    # 1. 澶囦唤鏃ф暟鎹簱
    backup_old_databases()
    
    # 2. 妫€鏌ユ棫鏁版嵁搴?    inspect_old_database()
    
    # 3. 鍚堝苟鍜屾洿鏂?    merge_and_update_brain()
    
    # 4. 鎵撳嵃鏈€缁堢粺璁?    print_final_stats()
