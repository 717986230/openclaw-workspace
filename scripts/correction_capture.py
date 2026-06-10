#!/usr/bin/env python3
"""
Correction Capture System for Erbing
Stores structured human corrections as memory, mines patterns, and reminds on session start.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = "/Users/xinglong/openclaw-workspace/memory/database/xiaozhi_memory.db"


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            original_mistake TEXT,
            correction TEXT,
            lesson TEXT,
            action_plan TEXT,
            severity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'open',
            resolved_at TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def add_correction(
    original_mistake: str,
    correction: str,
    lesson: str = "",
    action_plan: str = "",
    severity: int = 1,
    session_id: str = ""
) -> int:
    """Add a new correction record. Returns the new row id."""
    conn = _get_conn()
    try:
        cur = conn.execute(
            """
            INSERT INTO corrections
                (original_mistake, correction, lesson, action_plan, severity, session_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (original_mistake, correction, lesson, action_plan, severity, session_id)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def resolve_correction(correction_id: int) -> bool:
    """Mark a correction as resolved. Returns True if a row was updated."""
    conn = _get_conn()
    try:
        cur = conn.execute(
            """
            UPDATE corrections
            SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status != 'resolved'
            """,
            (correction_id,)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def get_open_corrections(min_severity: int = 1, limit: int = 20) -> list:
    """Return un-resolved corrections at or above min_severity."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, timestamp, session_id, original_mistake, correction,
                   lesson, action_plan, severity, status, resolved_at
            FROM corrections
            WHERE status IN ('open', 'in_progress') AND severity >= ?
            ORDER BY
                CASE status WHEN 'open' THEN 0 ELSE 1 END,
                severity DESC,
                timestamp DESC
            LIMIT ?
            """,
            (min_severity, limit)
        ).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


def get_recent_corrections(n: int = 5) -> list:
    """Return the n most recent corrections (including resolved)."""
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT id, timestamp, session_id, original_mistake, correction,
                   lesson, action_plan, severity, status, resolved_at
            FROM corrections
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (n,)
        ).fetchall()
        return _rows_to_dicts(rows)
    finally:
        conn.close()


def mine_patterns(min_count: int = 2) -> list:
    """
    Group corrections by original_mistake (fuzzy keyword bucket)
    and return frequency stats for high-frequency error types.
    Returns list of dicts with mistake_bucket, count, avg_severity.
    """
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT original_mistake, COUNT(*) as cnt, AVG(severity) as avg_sev,
                   MAX(severity) as max_sev
            FROM corrections
            GROUP BY original_mistake
            HAVING cnt >= ?
            ORDER BY cnt DESC, max_sev DESC
            """
        , (min_count,)).fetchall()
        return [
            {
                "mistake_bucket": r[0],
                "count": r[1],
                "avg_severity": round(r[2], 2) if r[2] else 0,
                "max_severity": r[3],
            }
            for r in rows
        ]
    finally:
        conn.close()


def get_high_freq_mistakes(days: int = 30, top_n: int = 5) -> list:
    """Return most frequent mistakes in the last N days."""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    conn = _get_conn()
    try:
        rows = conn.execute(
            """
            SELECT original_mistake, COUNT(*) as cnt
            FROM corrections
            WHERE timestamp >= ?
            GROUP BY original_mistake
            ORDER BY cnt DESC
            LIMIT ?
            """,
            (cutoff, top_n)
        ).fetchall()
        return [{"mistake": r[0], "count": r[1]} for r in rows]
    finally:
        conn.close()


def remind_me(
    min_severity: int = 2,
    max_age_days: int = 7,
    include_resolved_recent: bool = False
) -> str:
    """
    Build a session-start reminder string showing unresolved high-severity
    corrections (and recently resolved ones if include_resolved_recent).
    """
    lines = []
    severity_label = {1: "⚠️", 2: "🔴", 3: "🚨"}
    label_map = {
        1: "轻微",
        2: "中等",
        3: "严重",
    }

    cutoff = (datetime.now() - timedelta(days=max_age_days)).isoformat()
    conn = _get_conn()
    try:
        open_rows = conn.execute(
            """
            SELECT id, timestamp, session_id, original_mistake, correction,
                   lesson, action_plan, severity
            FROM corrections
            WHERE status IN ('open', 'in_progress')
              AND severity >= ?
              AND timestamp >= ?
            ORDER BY severity DESC, timestamp DESC
            """,
            (min_severity, cutoff)
        ).fetchall()

        if open_rows:
            lines.append("📌 **Erbing 待处理纠正提醒**\n")
            for r in open_rows:
                sev = r[7]
                ts  = r[1][:16] if r[1] else ""
                lines.append(
                    f"{severity_label.get(sev,'⚠️')} "
                    f"[{label_map.get(sev,'?')}] {ts}  |  ID:{r[0]}\n"
                    f"   错误: {r[3]}\n"
                    f"   纠正: {r[4]}\n"
                    f"   教训: {r[6]}\n"
                    f"   计划: {r[7]}\n"
                )

        # recently resolved
        if include_resolved_recent:
            res_rows = conn.execute(
                """
                SELECT id, timestamp, resolved_at, original_mistake, correction, severity
                FROM corrections
                WHERE status = 'resolved' AND resolved_at >= ?
                ORDER BY resolved_at DESC
                LIMIT 5
                """,
                (cutoff,)
            ).fetchall()
            if res_rows:
                lines.append("\n✅ **最近已解决的纠正**\n")
                for r in res_rows:
                    lines.append(
                        f"  ✓ [{r[0]}] {r[3][:60]} → {r[4][:60]}\n"
                    )

        if not lines:
            return "✅ 暂无未解决的严重纠正。"
        return "\n".join(lines)
    finally:
        conn.close()


def _rows_to_dicts(rows):
    keys = [
        "id", "timestamp", "session_id", "original_mistake", "correction",
        "lesson", "action_plan", "severity", "status", "resolved_at"
    ]
    return [dict(zip(keys, r)) for r in rows]


# ── CLI demo / quick-test entry point ──────────────────────────────────────
if __name__ == "__main__":
    import json

    print("=== add_correction ===")
    cid = add_correction(
        original_mistake="忘记确认用户意图就执行",
        correction="先复述用户需求，再执行",
        lesson="执行前必须确认理解一致",
        action_plan="加入 check-back 环节",
        severity=2,
        session_id="cli-test-001"
    )
    print(f"Created correction id={cid}")

    print("\n=== get_open_corrections ===")
    print(json.dumps(get_open_corrections(min_severity=1), ensure_ascii=False, indent=2))

    print("\n=== get_recent_corrections(3) ===")
    print(json.dumps(get_recent_corrections(3), ensure_ascii=False, indent=2))

    print("\n=== mine_patterns ===")
    print(json.dumps(mine_patterns(min_count=1), ensure_ascii=False, indent=2))

    print("\n=== remind_me ===")
    print(remind_me(min_severity=2))

    print("\n=== resolve_correction ===")
    print(f"Updated: {resolve_correction(cid)}")
    print(f"Updated again: {resolve_correction(cid)}")

    print("\nDone.")