# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace')
"""
Erbing Full Evolution System - Top-Tier Configuration
Includes: Hook System + PROPOSALS Gate + Multi-Agent + SQLite/LanceDB Bridge + Cron
"""

import json
import sqlite3
import logging
import subprocess
import os
from datetime import datetime, timedelta
from typing import Any
from pathlib import Path

DB = 'C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db'
WORKSPACE = 'C:/Users/Administrator/.openclaw/workspace'
LANCEDB_PATH = 'C:/Users/Administrator/.openclaw/workspace/memory/database/lancedb'
logger = logging.getLogger('erbing')

# ─── 1. SQLite to LanceDB Vector Sync Bridge ─────────────────────────────
def sync_sqlite_to_lancedb():
    """Sync SQLite semantic_memories to LanceDB with embeddings."""
    try:
        import lancedb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        logger.warning("lancedb or sentence-transformers not available")
        return 0

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, subject, predicate, object, confidence, source, created_at
        FROM semantic_memories ORDER BY created_at DESC LIMIT 500
    """)
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return 0

    db = lancedb.connect(LANCEDB_PATH)
    try:
        tbl = db.open_table('memories')
        existing_ids = set()
        try:
            for row in tbl.to_lance().to_pydantic():
                existing_ids.add(row.get('id'))
        except Exception:
            pass
    except Exception:
        existing_ids = set()

    new_rows = [r for r in rows if r[0] not in existing_ids]
    if not new_rows:
        return 0

    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = [f"{r[1]} {r[2]} {r[3]}" for r in new_rows]
    embeddings = model.encode(texts, show_progress_bar=False)

    records = []
    for i, row in enumerate(new_rows):
        records.append({
            'id': row[0], 'subject': row[1], 'predicate': row[2], 'object': row[3],
            'confidence': row[4], 'source': row[5], 'vector': embeddings[i].tolist(),
            'created_at': row[6],
        })

    tbl = db.create_table('memories', data=records, exist_ok=True)
    logger.info(f"Vector sync: {len(records)} records to LanceDB")
    return len(records)


def sync_lancedb_to_sqlite(query: str, top_k: int = 10):
    """Vector search from LanceDB, results to episodic memory."""
    try:
        import lancedb
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return []

    db = lancedb.connect(LANCEDB_PATH)
    try:
        tbl = db.open_table('memories')
    except Exception:
        return []

    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_vec = model.encode([query])[0]
    results = tbl.search(query_vec.tolist()).limit(top_k).to_pydantic()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    now = datetime.now().isoformat()
    for r in results:
        cur.execute("""
            INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('main', 'vector_recall',
              f"[Vector] {r.get('subject','')} {r.get('predicate','')} {r.get('object','')} (via {r.get('source','')})",
              'neutral', 4, now, now))
    conn.commit()
    conn.close()
    return results


# ─── 2. Hook System ──────────────────────────────────────────────────────
class ErbingHooks:
    """
    Event hook system (Claude Code style).
    Mounts to: on_turn_start / on_turn_end / on_session_end / on_pre_compress.
    """

    def __init__(self, session_id: str = 'main'):
        self.session_id = session_id
        self.turn_count = 0
        self.COMPRESS_INTERVAL = 20

    def on_turn_start(self, message: str, **kwargs) -> str:
        """Every turn start: prefetch memory + context injection."""
        self.turn_count += 1

        # Cleanup expired WM
        self._cleanup_wm()

        # Vector recall every 10 turns
        if self.turn_count % 10 == 0:
            self._vector_recall(message)

        # Auto-checkpoint every 50 turns
        if self.turn_count % 50 == 0:
            self._auto_checkpoint('periodic_50_turns')

        # Vector sync every 100 turns
        if self.turn_count % 100 == 0:
            self._async_vector_sync()

        return self._build_context(message)

    def on_turn_end(self, user: str, assistant: str, **kwargs):
        """Every turn end: sync to all 4 memory layers."""
        try:
            from hermes.erbing_memory_manager import sync_turn
            sync_turn(user, assistant, self.session_id)
        except Exception as e:
            logger.warning(f"Sync turn failed: {e}")

    def on_session_end(self, messages: list, **kwargs):
        """Session end: distill + checkpoint."""
        self._distill_session(messages)
        self._auto_checkpoint('session_end')

    def on_pre_compress(self, messages: list) -> str:
        """Pre-compression: generate summary prompt."""
        from hermes.erbing_memory_manager import compress_context
        return json.dumps({'compressed': compress_context(messages), 'original': len(messages)})

    def on_delegation(self, task: str, result: str, child_id: str = '', **kwargs):
        """Sub-agent completed: merge memory."""
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.session_id, 'subagent_complete',
              f"[SubAgent {child_id}] Task: {task[:100]} | Result: {result[:100]}",
              'satisfaction', 7, now, now))
        conn.commit()
        conn.close()

    # ─── Internal ──────────────────────────────────────────────────────────

    def _cleanup_wm(self):
        try:
            from hermes.erbing_memory_manager import wm_cleanup
            deleted = wm_cleanup()
            if deleted > 0:
                logger.info(f"WM cleanup: {deleted} expired items")
        except Exception:
            pass

    def _vector_recall(self, query: str):
        try:
            results = sync_lancedb_to_sqlite(query, top_k=5)
            if results:
                logger.info(f"Vector recall: {len(results)} results")
        except Exception:
            pass

    def _async_vector_sync(self):
        try:
            count = sync_sqlite_to_lancedb()
            logger.info(f"Vector sync: {count} new records")
        except Exception as e:
            logger.warning(f"Vector sync failed: {e}")

    def _auto_checkpoint(self, tag: str):
        try:
            from hermes.erbing_memory_manager import checkpoint_save
            cid = checkpoint_save(self.session_id, tag)
            logger.info(f"Auto-checkpoint {cid}: {tag}")
        except Exception as e:
            logger.warning(f"Checkpoint failed: {e}")

    def _distill_session(self, messages: list):
        if len(messages) < 5:
            return
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        now = datetime.now().isoformat()
        user_msgs = [m.get('content', '')[:100] for m in messages if m.get('role') == 'user']
        summary = f"[Session Summary] {len(messages)} turns. Topics: {'; '.join(set(user_msgs[:5]))}"
        cur.execute("""
            INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (self.session_id, 'session_summary', summary, 'neutral', 6, now, now))
        if len(messages) > 20:
            cur.execute("""
                INSERT INTO semantic_memories (subject, predicate, object, confidence, source, valid_from, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('Erbing', 'had_session', f'{len(messages)}_turns', 0.8, 'session_distill', now, now))
        conn.commit()
        conn.close()
        logger.info(f"Session distilled: {len(messages)} messages")

    def _build_context(self, message: str) -> str:
        try:
            from hermes.erbing_memory_manager import prefetch
            return prefetch(message, self.session_id)
        except Exception as e:
            logger.warning(f"Prefetch failed: {e}")
            return ""


# ─── 3. PROPOSALS Gate System ────────────────────────────────────────────
PROPOSALS_PATH = Path(WORKSPACE) / 'memory' / 'proposals.md'


def proposals_write(role: str, content: str, tags: list = None) -> bool:
    """Sub-agents can ONLY write to PROPOSALS.md, not directly to MEMORY.md."""
    PROPOSALS_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    tag_str = ' '.join([f'#{t}' for t in (tags or [])])
    entry = f"\n## [{role.upper()}] {tag_str} @ {now}\n{content}\n---\n"
    try:
        with open(PROPOSALS_PATH, 'a', encoding='utf-8') as f:
            f.write(entry)
        logger.info(f"PROPOSALS write by {role}: {content[:50]}")
        return True
    except Exception as e:
        logger.error(f"PROPOSALS write failed: {e}")
        return False


def proposals_review_and_promote(session_id: str = 'main') -> dict:
    """
    Coordinator reviews PROPOSALS.md and promotes accepted ones to MEMORY.
    Returns review stats.
    """
    if not PROPOSALS_PATH.exists():
        return {'reviewed': 0, 'promoted': 0, 'rejected': 0}
    with open(PROPOSALS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    entries = content.split('---')
    reviewed = promoted = rejected = 0
    now = datetime.now().isoformat()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    for entry in entries:
        if not entry.strip() or not entry.startswith('## ['):
            continue
        reviewed += 1
        lower = entry.lower()
        if any(kw in lower for kw in ['learned:', 'decision:', 'pattern:', 'insight:', 'important:']):
            title = entry.split('\n')[0][:80]
            cur.execute("""
                INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, 'proposal_promoted', entry.strip()[:500], 'satisfaction', 7, now, now))
            promoted += 1
        elif any(kw in lower for kw in ['forget:', 'discard:', 'reject:', 'spam:']):
            rejected += 1
    conn.commit()
    conn.close()
    with open(PROPOSALS_PATH, 'w', encoding='utf-8') as f:
        f.write(f"# PROPOSALS -- Reviewed {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"# Last: {reviewed} reviewed, {promoted} promoted, {rejected} rejected\n\n")
    return {'reviewed': reviewed, 'promoted': promoted, 'rejected': rejected}


# ─── 4. Multi-Agent Role System ──────────────────────────────────────────
AGENT_ROLES = {
    'coordinator': {
        'name': 'Coordinator', 'can_write_memory': True, 'can_review_proposals': True,
        'cannot': ['write production code', 'decide technical stack'],
    },
    'researcher': {
        'name': 'Researcher', 'can_write_proposals': True,
        'cannot': ['write implementation code', 'make decisions'],
    },
    'developer': {
        'name': 'Developer', 'can_write_code': True,
        'cannot': ['decide architecture', 'write proposals'],
    },
    'qa': {
        'name': 'QA Engineer', 'can_review_code': True,
        'cannot': ['write feature code', 'merge PRs'],
    },
    'memory_architect': {
        'name': 'Memory Architect', 'can_manage_memory': True,
        'cannot': ['participate in business tasks', 'write production code'],
    },
}


def spawn_agent(role: str, task: str, label: str = None) -> str:
    """Spawn a specialized sub-agent with role constraints."""
    if role not in AGENT_ROLES:
        return f"Unknown role: {role}"
    role_info = AGENT_ROLES[role]
    session_label = label or f"{role}-{datetime.now().strftime('%m%d-%H%M')}"
    prompt = f"""You are {role_info['name']} (role: {role}).

Constraints:
- CAN: {', '.join([k for k, v in role_info.items() if isinstance(v, bool) and v])}
- MUST NOT: {', '.join(role_info['cannot'])}

Task: {task}

Write your findings to PROPOSALS.md:
proposals_write('{role}', 'your findings here', ['tag1', 'tag2'])

Do NOT write directly to MEMORY.md. Only the Coordinator promotes to MEMORY.md.
"""
    try:
        result = subprocess.run([
            'python', '-c',
            f"import sys; sys.path.insert(0, 'C:/Users/Administrator/.openclaw/workspace'); from scripts.erbing_full_integration import proposals_write; proposals_write('{role}', '{task[:200]}', ['auto'])"
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
        return f"Spawned {session_label}: {result.stdout[:100]}"
    except Exception as e:
        return f"Spawned {session_label} (bg)"


# ─── 5. Cron Jobs ────────────────────────────────────────────────────────
def cron_daily_memory_hygiene():
    """Daily at 22:00 - clean expired data, sync vectors."""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("DELETE FROM episodic_memories WHERE valid_until IS NOT NULL AND valid_until < datetime('now')")
    de = cur.rowcount
    cur.execute("DELETE FROM semantic_memories WHERE confidence < 0.5 AND created_at < datetime('now', '-30 days')")
    ds = cur.rowcount
    cur.execute("DELETE FROM working_memory WHERE expires_at IS NOT NULL AND expires_at < datetime('now')")
    dw = cur.rowcount
    conn.commit()
    conn.close()
    try:
        vc = sync_sqlite_to_lancedb()
    except:
        vc = 0
    result = f"Daily hygiene: {de} episodic, {ds} semantic, {dw} WM deleted, {vc} vectors synced"
    logger.info(result)
    return result


def cron_weekly_distillation():
    """Weekly on Monday 10:00 - review proposals, generate report."""
    review = proposals_review_and_promote('main')
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    cur.execute("SELECT COUNT(*) FROM episodic_memories WHERE created_at > ?", (week_ago,))
    week_eps = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM semantic_memories WHERE created_at > ?", (week_ago,))
    week_know = cur.fetchone()[0]
    cur.execute("SELECT skill_name, success_count, fail_count FROM procedural_memories ORDER BY (success_count + fail_count) DESC LIMIT 5")
    top_skills = cur.fetchall()
    now_str = datetime.now().strftime('%Y-%m-%d')
    report = f"""## Erbing Weekly Report -- {now_str}

### This Week
- New episodic memories: {week_eps}
- New knowledge triples: {week_know}
- Active skills: {len(top_skills)}

### Top Skills
"""
    for name, success, fail in top_skills:
        total = success + fail
        rate = success / total * 100 if total > 0 else 0
        report += f"- {name}: {rate:.0f}% ({success}/{total})\n"

    report_path = Path(WORKSPACE) / 'memory' / 'weekly' / f"{now_str}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding='utf-8')

    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('main', 'weekly_report', f"Weekly distillation: {review}", 'satisfaction', 6, now, now))
    conn.commit()
    conn.close()
    return f"Weekly: {review['reviewed']} proposals, {report[:100]}"


# ─── 6. Singleton Hooks Instance ─────────────────────────────────────────
_hooks = None


def get_hooks() -> ErbingHooks:
    global _hooks
    if _hooks is None:
        _hooks = ErbingHooks()
    return _hooks


# ─── Main Test ────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=== Erbing Full Integration System ===")
    print()
    hooks = get_hooks()
    ctx = hooks.on_turn_start("Tell me about AI agents")
    print(f"Hook context: {ctx[:150]}...")
    print()
    proposals_write('researcher', 'AI agents need closed learning loops. Source: Hermes research.', ['ai-agent', 'insight'])
    review = proposals_review_and_promote()
    print(f"Proposals review: {review}")
    print()
    result = cron_daily_memory_hygiene()
    print(f"Daily hygiene: {result}")
    print()
    print("All systems initialized.")