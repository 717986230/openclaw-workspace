#!/usr/bin/env python3
"""
扫描碎片记忆 - 找出所有未整合、碎片化的记忆
"""
import sys
import os
import io
import json
import sqlite3
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace"
DB = os.path.join(WORKSPACE, 'memory', 'database', 'xiaozhi_memory.db')


def scan_fragmented_memories() -> dict:
    """扫描碎片记忆"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    result = {
        "timestamp": datetime.now().isoformat(),
        "fragments": [],
        "categories": {},
        "recent": [],
        "high_importance": [],
        "unintegrated": []
    }

    try:
        # 1. 按分类统计
        cur.execute("""
            SELECT category, COUNT(*), AVG(importance)
            FROM memories
            WHERE category IS NOT NULL AND category != ''
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        for cat, cnt, avg_imp in cur.fetchall():
            result["categories"][cat] = {"count": cnt, "avg_importance": round(avg_imp, 2)}

        # 2. 最近 7 天的记忆
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cur.execute("""
            SELECT id, title, type, category, importance, created_at
            FROM memories
            WHERE created_at > ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (week_ago,))
        for r in cur.fetchall():
            result["recent"].append({
                "id": r[0], "title": r[1], "type": r[2],
                "category": r[3], "importance": r[4], "created": r[5]
            })

        # 3. 高重要性记忆（>= 8）
        cur.execute("""
            SELECT id, title, type, category, importance, updated_at
            FROM memories
            WHERE importance >= 8
            ORDER BY importance DESC, updated_at DESC
            LIMIT 30
        """)
        for r in cur.fetchall():
            result["high_importance"].append({
                "id": r[0], "title": r[1], "type": r[2],
                "category": r[3], "importance": r[4], "updated": r[5]
            })

        # 4. 未整合的记忆（没有明确分类或重要性低的）
        cur.execute("""
            SELECT id, title, type, category, importance, content, created_at
            FROM memories
            WHERE (category IS NULL OR category = '' OR category = 'None')
            ORDER BY created_at DESC
            LIMIT 50
        """)
        for r in cur.fetchall():
            result["unintegrated"].append({
                "id": r[0], "title": r[1], "type": r[2],
                "category": r[3], "importance": r[4],
                "content_preview": r[5][:100] if r[5] else "",
                "created": r[6]
            })

        # 5. 情景记忆碎片
        cur.execute("""
            SELECT id, event_type, content, emotion, importance, created_at
            FROM episodic_memories
            ORDER BY created_at DESC
            LIMIT 30
        """)
        for r in cur.fetchall():
            result["fragments"].append({
                "type": "episodic", "id": r[0], "event_type": r[1],
                "content": r[2][:80], "emotion": r[3], "importance": r[4], "created": r[5]
            })

        # 6. 语义记忆碎片
        cur.execute("""
            SELECT id, subject, predicate, object, confidence, created_at
            FROM semantic_memories
            ORDER BY created_at DESC
            LIMIT 30
        """)
        for r in cur.fetchall():
            result["fragments"].append({
                "type": "semantic", "id": r[0],
                "triple": f"{r[1]} {r[2]} {r[3]}",
                "confidence": r[4], "created": r[5]
            })

        # 7. 程序记忆碎片
        cur.execute("""
            SELECT id, skill_name, skill_type, description, success_count, fail_count, last_used
            FROM procedural_memories
            ORDER BY last_used DESC
            LIMIT 20
        """)
        for r in cur.fetchall():
            result["fragments"].append({
                "type": "procedural", "id": r[0],
                "skill": r[1], "type": r[2],
                "success": r[4], "fail": r[5], "last_used": r[6]
            })

        # 8. ToM 信念碎片
        try:
            cur.execute("""
                SELECT entity, belief_type, content, confidence, created_at
                FROM tom_beliefs
                ORDER BY created_at DESC
                LIMIT 20
            """)
            for r in cur.fetchall():
                result["fragments"].append({
                    "type": "tom_belief", "entity": r[0],
                    "belief_type": r[1], "content": r[2][:60],
                    "confidence": r[3], "created": r[4]
                })
        except:
            pass

        # 9. 情感状态碎片
        try:
            cur.execute("""
                SELECT user_id, emotion, intensity, trigger, created_at
                FROM emotional_state
                ORDER BY created_at DESC
                LIMIT 20
            """)
            for r in cur.fetchall():
                result["fragments"].append({
                    "type": "emotion", "user": r[0],
                    "emotion": r[1], "intensity": r[2],
                    "trigger": r[3][:50], "created": r[4]
                })
        except:
            pass

        # 10. 统计
        result["stats"] = {
            "total_memories": len(result["categories"]),
            "recent_count": len(result["recent"]),
            "high_importance_count": len(result["high_importance"]),
            "unintegrated_count": len(result["unintegrated"]),
            "fragment_count": len(result["fragments"])
        }

    except Exception as e:
        result["error"] = str(e)
    finally:
        conn.close()

    return result


if __name__ == "__main__":
    result = scan_fragmented_memories()
    print(json.dumps(result, ensure_ascii=False, indent=2))