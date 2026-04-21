import sqlite3
from datetime import datetime
import sys

conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db')
cur = conn.cursor()

# Check existing Hermes entries
cur.execute("SELECT COUNT(*) FROM semantic_memories WHERE subject='Hermes Agent'")
existing = cur.fetchone()[0]
print(f'Existing Hermes entries: {existing}')

now = datetime.now().isoformat()

# Hermes Agent core facts
hermes_facts = [
    ("Hermes Agent", "implements", "self_improving_loop", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "MemoryManager", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "BuiltinMemoryProvider", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "skill_utils", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "context_compressor", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "checkpoint_manager", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_component", "skill_manager_tool", 1.0, "NousResearch/hermes-agent"),
    ("Hermes Agent", "implements", "memory_context_fencing", 0.95, "NousResearch/hermes-agent"),
    ("Hermes Agent", "implements", "skill_autonomous_creation", 0.95, "NousResearch/hermes-agent"),
    ("Hermes Agent", "implements", "periodic_nudge_system", 0.9, "NousResearch/hermes-agent"),
    ("Hermes Agent", "supports", "FTS5_session_search", 0.9, "NousResearch/hermes-agent"),
    ("Hermes Agent", "supports", "cron_scheduling", 0.9, "NousResearch/hermes-agent"),
    ("Hermes Agent", "supports", "subagent_delegation", 0.9, "NousResearch/hermes-agent"),
    ("Hermes Agent", "has_stars", "99675", 1.0, "GitHub"),
    ("MemoryManager", "pattern", "provider_orchestrator", 1.0, "hermes_memory_manager.py"),
    ("MemoryManager", "enforces", "one_external_provider_limit", 1.0, "hermes_memory_manager.py"),
    ("MemoryManager", "has_method", "prefetch_all", 1.0, "hermes_memory_manager.py"),
    ("MemoryManager", "has_method", "sync_all", 1.0, "hermes_memory_manager.py"),
    ("MemoryManager", "has_method", "queue_prefetch_all", 1.0, "hermes_memory_manager.py"),
    ("MemoryProvider", "interface", "prefetch_sync_pattern", 1.0, "hermes_memory_provider.py"),
    ("Hermes ecosystem", "has_member", "Hermes Atlas (ksimback)", 0.9, "hermes-ecosystem README"),
    ("Hermes ecosystem", "has_member", "Hermes-Wiki (cclank)", 0.9, "hermes-wiki README"),
    ("Hermes ecosystem", "has_member", "hermes-hud (joeynyc)", 0.9, "hermes-hud README"),
    ("Hermes ecosystem", "has_member", "hermes-control-interface (xaspx)", 0.9, "hermes-control-interface README"),
    ("Hermes Atlas", "does", "web_scraping_for_security_review", 0.9, "hermes-ecosystem README"),
    ("Hermes Atlas", "generates", "State_of_Hermes_reports", 0.9, "hermes-ecosystem README"),
    ("Hermes-Wiki", "does", "auto_generate_wiki_from_source", 0.9, "hermes-wiki README"),
    ("hermes-hud", "does", "TUI_to_browser_HUD", 0.9, "hermes-hud README"),
    ("hermes-hud", "monitors", "agent_consciousness_state", 0.9, "hermes-hud README"),
    ("hermes-control-interface", "does", "multi_agent_dashboard", 0.9, "hermes-control-interface README"),
    ("hermes-control-interface", "manages", "processes_and_scheduling", 0.9, "hermes-control-interface README"),
    ("Erbing", "can_learn_from", "Hermes Agent", 0.8, "xl instruction"),
    ("钱学森", "founded", "系统科学体系", 1.0, "user"),
    ("钱学森", "created", "从定性到定量综合集成法", 1.0, "user"),
    ("从定性到定量综合集成法", "has_pattern", "closed_learning_loop", 0.7, "comparison"),
    ("Hermes Agent", "implements", "closed_learning_loop", 0.95, "NousResearch"),
    ("closed_learning_loop", "is_similar_to", "从定性到定量综合集成法", 0.7, "analysis"),
]

if existing == 0:
    for subject, predicate, obj, confidence, source in hermes_facts:
        cur.execute("""
            INSERT INTO semantic_memories (subject, predicate, object, confidence, source, valid_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject, predicate, obj, confidence, source, now, now))
    conn.commit()
    print(f'Inserted {len(hermes_facts)} Hermes facts + knowledge links')
else:
    print('Hermes facts already exist, skipping insert')

# Record this research as an episodic memory
cur.execute("""
    INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('main', 'learning', 
      'Researched Hermes Agent self-evolution architecture: MemoryManager provider orchestrator, skill autonomous creation, checkpoint manager, 80+ ecosystem forks. Key insight: closed learning loop matches 钱学森综合集成法 philosophy.',
      'curiosity', 9, now, now))
conn.commit()
print(f'Episodic memory recorded')

conn.close()
print('Done')