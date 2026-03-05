---
name: deep-recall
description: Recursive memory recall for persistent AI agents using RLM (Recursive Language Models). Implements the Anamnesis Architecture — "The soul stays small, the mind scales forever."
metadata: {"openclaw": {"requires": {"bins": ["deno"], "env": ["FAST_RLM_DIR"]}, "homepage": "https://github.com/Stefan27-4/DeepRecall"}}
---

# DeepRecall — OpenClaw Skill Definition

## Description
Recursive memory recall for persistent AI agents using RLM (Recursive Language Models).
Implements the Anamnesis Architecture: "The soul stays small, the mind scales forever."

## Recommended Memory Layout
- `MEMORY.md` — Compact index + orientation (~100 lines). Auto-loaded each session.
- `memory/LONG_TERM.md` — Full detailed memories. Grows forever. Searched via DeepRecall.
- `memory/YYYY-MM-DD.md` — Daily raw logs. Distill into LONG_TERM.md at end of day.

## When to Use
- Agent needs to recall information from a large/growing memory store
- Memory files exceed the context window (~128K tokens)
- Agent needs to cross-reference across many daily log files
- Deep reasoning about historical decisions, patterns, or events
- Finding specific information across weeks/months of conversation history

## Dependencies
- fast-rlm (`pip install fast-rlm`)
- Deno 2+ (`curl -fsSL https://deno.land/install.sh | sh`)
- PyYAML (`pip install pyyaml`)
- An LLM provider configured in OpenClaw

## Files
- `deep_recall.py` — Main entry point (recall, recall_quick, recall_deep)
- `provider_bridge.py` — Reads OpenClaw config to resolve API keys + models
- `model_pairs.py` — Auto-selects cheap sub-agent model
- `memory_scanner.py` — Discovers and indexes agent memory files
- `memory_indexer.py` — Generates MEMORY_INDEX.md (legacy, optional)
- `rlm_config_builder.py` — Generates fast-rlm config

## Quick Start
```python
from deep_recall import recall
result = recall("What did we discuss last week about the project?")
```

## Configuration
No additional config needed — DeepRecall reads your existing OpenClaw setup.
Override RLM settings via `config_overrides` parameter.
