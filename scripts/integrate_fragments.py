#!/usr/bin/env python3
"""
碎片记忆整合 - 将所有碎片记忆整合到统一架构
"""
import sys
import os
import io
import json
import sqlite3
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WORKSPACE = r"C:\Users\Administrator\.openclaw\workspace"
DB = os.path.join(WORKSPACE, 'memory', 'database', 'xiaozhi_memory.db')


def integrate_fragments() -> dict:
    """整合碎片记忆"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    result = {
        "timestamp": datetime.now().isoformat(),
        "actions": [],
        "stats": {}
    }

    try:
        # 1. 整合未分类记忆
        cur.execute("""
            SELECT id, title, type, content, importance, created_at
            FROM memories
            WHERE (category IS NULL OR category = '' OR category = 'None')
            AND importance >= 7
        """)
        unintegrated = cur.fetchall()
        result["stats"]["unintegrated_high_importance"] = len(unintegrated)

        for mem in unintegrated:
            mem_id, title, mtype, content, importance, created = mem
            # 根据内容推断分类
            if "学习" in title or "learning" in mtype:
                category = "learnings"
            elif "知识" in title or "knowledge" in mtype:
                category = "knowledge"
            elif "进化" in title or "evolution" in mtype:
                category = "evolution"
            elif "原创" in title or "original" in mtype:
                category = "original"
            else:
                category = "knowledge"

            cur.execute("""
                UPDATE memories
                SET category = ?, updated_at = ?
                WHERE id = ?
            """, (category, datetime.now().isoformat(), mem_id))
            result["actions"].append({
                "action": "categorize",
                "id": mem_id,
                "title": title,
                "category": category
            })

        # 2. 压缩 report 记忆
        cur.execute("""
            SELECT id, title, content, created_at
            FROM memories
            WHERE category = 'report'
            ORDER BY created_at DESC
            LIMIT 74
        """)
        reports = cur.fetchall()
        result["stats"]["reports_before"] = len(reports)

        # 保留最近 10 条，其余归档
        for i, (rep_id, title, content, created) in enumerate(reports[10:]):
            cur.execute("""
                UPDATE memories
                SET category = 'report_archived', updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), rep_id))
            result["actions"].append({
                "action": "archive_report",
                "id": rep_id,
                "title": title
            })

        result["stats"]["reports_after"] = 10

        # 3. 归档 test 记忆
        cur.execute("""
            SELECT id, title, created_at
            FROM memories
            WHERE category = 'test'
            ORDER BY created_at DESC
        """)
        tests = cur.fetchall()
        result["stats"]["tests_before"] = len(tests)

        for test_id, title, created in tests:
            cur.execute("""
                UPDATE memories
                SET category = 'test_history', updated_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), test_id))
            result["actions"].append({
                "action": "archive_test",
                "id": test_id,
                "title": title
            })

        result["stats"]["tests_after"] = 0

        # 4. 扩展 ToM 信念
        # 从高重要性记忆中提取用户偏好
        cur.execute("""
            SELECT title, content, importance
            FROM memories
            WHERE importance >= 9
            AND (category = 'knowledge' OR category = 'learnings' OR category = 'original')
            LIMIT 10
        """)
        high_importance = cur.fetchall()
        result["stats"]["high_importance_for_tom"] = len(high_importance)

        for title, content, importance in high_importance:
            try:
                cur.execute("""
                    INSERT INTO tom_beliefs (entity, belief_type, content, confidence, evidence, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, ("user", "preference", title[:100], 0.8, content[:200], datetime.now().isoformat(), datetime.now().isoformat()))
                result["actions"].append({
                    "action": "add_tom_belief",
                    "title": title,
                    "belief_type": "preference"
                })
            except Exception as e:
                result["actions"].append({
                    "action": "add_tom_belief_error",
                    "title": title,
                    "error": str(e)
                })

        # 5. 统计整合后状态
        cur.execute("""
            SELECT category, COUNT(*)
            FROM memories
            GROUP BY category
            ORDER BY COUNT(*) DESC
        """)
        result["stats"]["categories_after"] = {cat: cnt for cat, cnt in cur.fetchall()}

        cur.execute("SELECT COUNT(*) FROM tom_beliefs")
        result["stats"]["tom_beliefs_after"] = cur.fetchone()[0]

        conn.commit()

    except Exception as e:
        result["error"] = str(e)
        conn.rollback()
    finally:
        conn.close()

    return result


if __name__ == "__main__":
    result = integrate_fragments()
    print(json.dumps(result, ensure_ascii=False, indent=2))