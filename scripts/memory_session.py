#!/usr/bin/env python3
"""
Session Context Loader - 每 Session 开始时运行
读取最近的 episodic + 重要记忆，写入 working_memory 供当前 session 使用
"""
import sys
import os
import io
import json
import sqlite3
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace"
SKILL_SCRIPTS = os.path.join(WORKSPACE, 'skills', 'memory-complete', 'scripts')
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

DB = os.path.join(WORKSPACE, 'memory', 'database', 'xiaozhi_memory.db')


def load_session_context(session_id: str, limit: int = 20) -> dict:
    """加载当前 session 需要的上下文记忆"""
    result = {"session_id": session_id, "loaded": [], "stats": {}}

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.now()

    try:
        # 1. 今天的情景记忆 (最近消息)
        cur.execute("""SELECT id, event_type, content, emotion, importance, created_at
            FROM episodic_memories ORDER BY created_at DESC LIMIT ?""", (limit,))
        episodes = cur.fetchall()
        result["loaded"].append({"type": "episodes_today", "count": len(episodes)})
        for ep in episodes:
            try:
                cur.execute("""INSERT INTO working_memory (session_id, key, value, ttl_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    (session_id, f"episode:{ep[0]}", json.dumps({
                        "id": ep[0], "type": ep[1], "content": ep[2][:200],
                        "emotion": ep[3], "importance": ep[4], "created": ep[5]
                    }, ensure_ascii=False), 7200, now.isoformat()))
            except:
                pass

        # 2. 高重要性记忆 (importance >= 8)
        cur.execute("""SELECT id, title, content, importance FROM memories
            WHERE importance >= 8 ORDER BY updated_at DESC LIMIT 10""")
        important = cur.fetchall()
        result["loaded"].append({"type": "high_importance", "count": len(important)})
        for mem in important:
            try:
                cur.execute("""INSERT INTO working_memory (session_id, key, value, ttl_seconds, created_at)
                    VALUES (?, ?, ?, ?, ?)""",
                    (session_id, f"important:{mem[0]}", json.dumps({
                        "id": mem[0], "title": mem[1], "content": mem[2][:200], "importance": mem[3]
                    }, ensure_ascii=False), 3600, now.isoformat()))
            except:
                pass

        # 3. ToM 信念 (tom_beliefs 表, 列: entity, content)
        try:
            cur.execute("""SELECT entity, content, confidence FROM tom_beliefs
                ORDER BY created_at DESC LIMIT 5""")
            tom_beliefs = cur.fetchall()
            result["loaded"].append({"type": "tom_beliefs", "count": len(tom_beliefs)})
        except Exception as e:
            result["loaded"].append({"type": "tom_beliefs", "count": 0, "error": str(e)})

        # 4. 情感状态 (emotional_state 表)
        try:
            cur.execute("""SELECT emotion, intensity, trigger FROM emotional_state
                ORDER BY created_at DESC LIMIT 3""")
            emotions = cur.fetchall()
            result["loaded"].append({"type": "emotions", "count": len(emotions)})
        except:
            result["loaded"].append({"type": "emotions", "count": 0})

        # 5. 用户偏好 (user_beliefs)
        try:
            cur.execute("""SELECT belief_content, confidence FROM user_beliefs
                ORDER BY updated_at DESC LIMIT 5""")
            beliefs = cur.fetchall()
            result["loaded"].append({"type": "user_beliefs", "count": len(beliefs)})
        except:
            result["loaded"].append({"type": "user_beliefs", "count": 0})

        conn.commit()
        result["stats"]["status"] = "ok"

    except Exception as e:
        result["stats"]["error"] = str(e)
    finally:
        conn.close()

    return result


def get_current_context(session_id: str = "current") -> dict:
    """获取当前 session 的上下文记忆供 Agent 使用"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    context = {"session_id": session_id, "context": {}}

    try:
        # 获取工作记忆
        cur.execute("""SELECT key, value FROM working_memory
            WHERE session_id = ? AND (expires_at IS NULL OR expires_at > ?)
            ORDER BY created_at DESC LIMIT 30""",
            (session_id, datetime.now().isoformat()))
        working = cur.fetchall()
        context["context"]["working_memory"] = [
            {"key": k, "value": json.loads(v)} for k, v in working
        ]

        # 获取最近的 episodic
        cur.execute("""SELECT content, emotion, importance, created_at
            FROM episodic_memories ORDER BY created_at DESC LIMIT 10""")
        episodes = cur.fetchall()
        context["context"]["recent_episodes"] = [
            {"content": e[0][:100], "emotion": e[1], "importance": e[2], "time": e[3]}
            for e in episodes
        ]

        # 获取当前情感
        cur.execute("""SELECT emotion, intensity FROM emotional_state
            ORDER BY created_at DESC LIMIT 1""")
        em = cur.fetchone()
        context["context"]["current_emotion"] = {"emotion": em[0], "intensity": em[1]} if em else None

        # 获取用户意图
        cur.execute("""SELECT user_intent, inferred_goal FROM intent_tracking
            ORDER BY created_at DESC LIMIT 3""")
        intents = cur.fetchall()
        context["context"]["recent_intents"] = [
            {"intent": i[0], "goal": i[1]} for i in intents
        ]

    except Exception as e:
        context["error"] = str(e)
    finally:
        conn.close()

    return context


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Session Context Loader")
        print("  python memory_session.py load [session_id] [limit]")
        print("  python memory_session.py get [session_id]")
        sys.exit(1)

    cmd = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else "current"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    if cmd == "load":
        result = load_session_context(session_id, limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif cmd == "get":
        result = get_current_context(session_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown: {cmd}")