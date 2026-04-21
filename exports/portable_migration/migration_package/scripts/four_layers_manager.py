"""
四层记忆栈管理器
- Working Memory: 当前会话短期记忆（TTL 自动过期）
- Episodic Memory: 重要事件/经验（时间线记录）
- Semantic Memory: 知识三元组（主体-谓词-对象）
- Procedural Memory: 技能步骤和执行统计
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Optional

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

# ========== Working Memory ==========
def wm_set(session_id: str, key: str, value: str, ttl_seconds: int = 3600):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now()
    expires = datetime.fromtimestamp(now.timestamp() + ttl_seconds)
    cur.execute("""
        INSERT OR REPLACE INTO working_memory (session_id, key, value, ttl_seconds, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, key, json.dumps(value, ensure_ascii=False), ttl_seconds, now.isoformat(), expires.isoformat()))
    conn.commit()
    conn.close()

def wm_get(session_id: str, key: str) -> Optional[str]:
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        SELECT value FROM working_memory 
        WHERE session_id=? AND key=? AND (expires_at IS NULL OR expires_at > ?)
    """, (session_id, key, now))
    row = cur.fetchone()
    conn.close()
    return json.loads(row['value']) if row else None

def wm_list(session_id: str):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        SELECT key, value, ttl_seconds, expires_at FROM working_memory 
        WHERE session_id=? AND (expires_at IS NULL OR expires_at > ?)
        ORDER BY created_at DESC
    """, (session_id, now))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def wm_cleanup():
    """删除过期 working memory"""
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("DELETE FROM working_memory WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return deleted

# ========== Episodic Memory ==========
def em_add(agent_id: str, event_type: str, content: str, emotion: str = 'neutral', importance: int = 5):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, event_type, content, emotion, importance, now, now))
    conn.commit()
    memory_id = cur.lastrowid
    conn.close()
    return memory_id

def em_recent(agent_id: str = 'main', limit: int = 10):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM episodic_memories 
        WHERE agent_id=? AND (valid_until IS NULL OR valid_until > datetime('now'))
        ORDER BY created_at DESC LIMIT ?
    """, (agent_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ========== Semantic Memory ==========
def sm_add(subject: str, predicate: str, obj: str, confidence: float = 1.0, source: str = 'erbing'):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO semantic_memories (subject, predicate, object, confidence, source, valid_from, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (subject, predicate, obj, confidence, source, now, now))
    conn.commit()
    memory_id = cur.lastrowid
    conn.close()
    return memory_id

def sm_search(subject: str = None, predicate: str = None, obj: str = None, limit: int = 20):
    conn = get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM semantic_memories WHERE 1=1"
    params = []
    if subject:
        query += " AND subject LIKE ?"
        params.append(f"%{subject}%")
    if predicate:
        query += " AND predicate LIKE ?"
        params.append(f"%{predicate}%")
    if obj:
        query += " AND object LIKE ?"
        params.append(f"%{obj}%")
    query += " ORDER BY confidence DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ========== Procedural Memory ==========
def pm_record(skill_name: str, skill_type: str, description: str, steps: list, success: bool):
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    # Check if exists
    cur.execute("SELECT id, success_count, fail_count FROM procedural_memories WHERE skill_name=?", (skill_name,))
    existing = cur.fetchone()
    if existing:
        new_success = existing['success_count'] + (1 if success else 0)
        new_fail = existing['fail_count'] + (0 if success else 1)
        cur.execute("""
            UPDATE procedural_memories SET last_used=?, success_count=?, fail_count=?, updated_at=?
            WHERE skill_name=?
        """, (now, new_success, new_fail, now, skill_name))
    else:
        cur.execute("""
            INSERT INTO procedural_memories (skill_name, skill_type, description, steps, success_count, fail_count, last_used, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (skill_name, skill_type, description, json.dumps(steps, ensure_ascii=False), 
              1 if success else 0, 0 if success else 1, now, now, now))
    conn.commit()
    conn.close()

def pm_get(skill_name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM procedural_memories WHERE skill_name=?", (skill_name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def pm_list():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT skill_name, skill_type, success_count, fail_count, last_used FROM procedural_memories ORDER BY last_used DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ========== Demo / Test ==========
if __name__ == '__main__':
    print('=== 四层记忆栈 Demo ===\n')

    # 1. Working Memory test
    print('[1] Working Memory')
    wm_set('main', 'current_task', '四层记忆栈调试', ttl_seconds=300)
    wm_set('main', 'debug_mode', True, ttl_seconds=60)
    items = wm_list('main')
    print(f'    Stored {len(items)} items')
    print(f'    current_task = {wm_get("main", "current_task")}')

    # 2. Episodic Memory test
    print('\n[2] Episodic Memory')
    em_add('main', 'learning', '完成四层记忆栈框架搭建', emotion='satisfaction', importance=8)
    em_add('main', 'discovery', '发现 semantic_memories 表已有 MemPalace 知识', emotion='curiosity', importance=6)
    episodes = em_recent('main', 5)
    print(f'    Total episodes: {len(episodes)}')
    for e in episodes:
        print(f'    - [{e["event_type"]}] {e["content"][:40]} ({e["emotion"]})')

    # 3. Semantic Memory test
    print('\n[3] Semantic Memory')
    sm_add('Erbing', 'has_layer', 'working_memory', 0.9, 'erbing')
    sm_add('Erbing', 'has_layer', 'episodic_memory', 0.9, 'erbing')
    sm_add('Erbing', 'has_layer', 'semantic_memory', 0.9, 'erbing')
    sm_add('Erbing', 'has_layer', 'procedural_memory', 0.9, 'erbing')
    sm_add('Erbing', 'implements', 'dual_brain_architecture', 0.95, 'erbing')
    sm_add('钱学森', 'founded', '系统科学', 1.0, 'user')
    sm_add('钱学森', 'created', '从定性到定量综合集成法', 1.0, 'user')
    results = sm_search(subject='Erbing')
    print(f'    Erbing relations: {len(results)}')
    for r in results:
        print(f'    - {r["subject"]} {r["predicate"]} {r["object"]} (conf:{r["confidence"]})')

    # 4. Procedural Memory test
    print('\n[4] Procedural Memory')
    pm_record('four_layers_init', 'core_system', '四层记忆栈初始化', 
              ['create_schema', 'wm_set', 'wm_get', 'em_add', 'sm_add', 'pm_record'], success=True)
    pm_record('sm_search', 'query', '语义记忆查询', ['build_query', 'execute', 'parse_results'], success=True)
    skills = pm_list()
    print(f'    Registered skills: {len(skills)}')
    for s in skills:
        total = s['success_count'] + s['fail_count']
        rate = s['success_count'] / total * 100 if total > 0 else 0
        print(f'    - {s["skill_name"]}: {rate:.0f}% ({s["success_count"]}/{total})')

    # Cleanup expired
    deleted = wm_cleanup()
    print(f'\n[5] Cleanup: removed {deleted} expired WM items')

    print('\n=== Demo Complete ===')