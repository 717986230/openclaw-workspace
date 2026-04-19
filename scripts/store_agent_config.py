import sqlite3
from datetime import datetime

conn = sqlite3.connect('C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db')
cur = conn.cursor()
now = datetime.now().isoformat()

# Check if already added
cur.execute("SELECT COUNT(*) FROM semantic_memories WHERE subject='Claude Code Production'")
existing = cur.fetchone()[0]

knowledge = [
    # Claude Code Production System
    ("Claude Code Production", "implements", "88_plus_skills_architecture", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "has_layer", "Tier1_claudemd_memory", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "has_layer", "Tier2_supabase_memory", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "has_layer", "Tier3_session_handoff", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "runs", "11_specialized_agents", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "implements", "security_hardened_permissions", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "implements", "always_on_execution", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "has", "150_plus_allow_patterns", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "manages", "~50_properties_and_trading_bots", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "principle", "memory_is_everything", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "principle", "specialization_scales_better_than_generalist", 1.0, "dwhite612/claude-code-setup"),
    ("Claude Code Production", "principle", "always_on_beats_on_demand", 1.0, "dwhite612/claude-code-setup"),

    # OpenClaw 4-layer Template
    ("OpenClaw 4-layer Template", "implements", "4_layer_context_memory", 1.0, "ivancheungckn/openclaw-workspace-template"),
    ("OpenClaw 4-layer Template", "rule", "data_flows_up_never_down", 1.0, "ivancheungckn/openclaw-workspace-template"),
    ("OpenClaw 4-layer Template", "enforces", "subagent_proposals_only_no_direct_memory_write", 1.0, "ivancheungckn/openclaw-workspace-template"),
    ("OpenClaw 4-layer Template", "has", "coordinator_researcher_developer_qa_memory_architect_roles", 1.0, "ivancheungckn/openclaw-workspace-template"),
    ("OpenClaw 4-layer Template", "process", "daily_log_to_proposals_to_memory", 1.0, "ivancheungckn/openclaw-workspace-template"),
    ("OpenClaw 4-layer Template", "distills", "every_10_to_20_turns", 1.0, "ivancheungckn/openclaw-workspace-template"),

    # MasterClaw Core
    ("MasterClaw Core", "has_api", "chat_memory_sessions_maintenance", 1.0, "TheMasterClaw/masterclaw-core"),
    ("MasterClaw Core", "has", "prometheus_metrics_endpoint", 1.0, "TheMasterClaw/masterclaw-core"),
    ("MasterClaw Core", "has", "security_health_check", 1.0, "TheMasterClaw/masterclaw-core"),
    ("MasterClaw Core", "supports", "chroma_and_json_memory_backend", 1.0, "TheMasterClaw/masterclaw-core"),
    ("MasterClaw Core", "has", "cache_api_with_redis_support", 1.0, "TheMasterClaw/masterclaw-core"),
    ("MasterClaw Core", "provides", "maintenance_api_dry_run_mode", 1.0, "TheMasterClaw/masterclaw-core"),

    # Erbing integration
    ("Erbing", "implements", "hermes_memory_manager_pattern", 1.0, "erbing_memory_manager.py"),
    ("Erbing", "implements", "4_layer_memory_stack", 1.0, "erbing_memory_manager.py"),
    ("Erbing", "implements", "closed_learning_loop_prefetch_sync_checkpoint", 1.0, "erbing_memory_manager.py"),
    ("Erbing", "implements", "skill_self_improvement", 1.0, "erbing_memory_manager.py"),
    ("Erbing", "implements", "periodic_nudge_system", 1.0, "erbing_memory_manager.py"),
    ("Erbing", "can_evolve_to", "multi_agent_coordinator", 0.8, "ai-agent-configuration"),
    ("Erbing", "can_evolve_to", "specialized_researcher_agent", 0.8, "ai-agent-configuration"),
    ("Erbing", "can_evolve_to", "memory_architect_agent", 0.9, "ai-agent-configuration"),

    # Cross-cutting insights
    ("closed_learning_loop", "is_core_pattern_in", "Hermes_Agent", 1.0, "analysis"),
    ("data_flows_up", "is_core_pattern_in", "OpenClaw_Template", 1.0, "analysis"),
    ("security_by_default", "is_core_pattern_in", "Claude_Code_Production", 1.0, "analysis"),
    ("specialization", "beats", "generalist_approach", 0.9, "analysis"),
]

if existing == 0:
    for subject, predicate, obj, confidence, source in knowledge:
        cur.execute("""
            INSERT INTO semantic_memories (subject, predicate, object, confidence, source, valid_from, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (subject, predicate, obj, confidence, source, now, now))
    conn.commit()
    print('Inserted {} knowledge triples'.format(len(knowledge)))
else:
    print('Already exists, skipping')

# Record episodic event
cur.execute("""
    INSERT INTO episodic_memories (agent_id, event_type, content, emotion, importance, valid_from, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", ('main', 'learning',
      'Integrated AI Agent research from Claude Code Production (88+ skills, 11 agents), OpenClaw 4-layer Template, MasterClaw Core (API, memory backend), ModularIntellect. Core patterns: closed learning loop, data-flows-up memory, specialization scales.',
      'curiosity', 9, now, now))
conn.commit()

# Record config update
cur.execute("""
    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", ('evolution_config', 'Erbings AI Agent Configuration v1',
      'Full configuration document created at memory/Erbings-AI-Agent-Configuration.md. Covers: Hermes memory pattern, Claude Code production system, MasterClaw API, OpenClaw 4-layer template, 5-role multi-agent design, hook system, skill self-evolution.',
      'evolution', '["ai-agent","memory-system","multi-agent","hermes","claude-code","masterclaw"]',
      9, now, now))
conn.commit()
print('Config memory recorded')

conn.close()