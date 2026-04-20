---
name: memory-optimization
description: A memory consolidation system for long-term potentiation and memory stabilization.
version: 1.0.0
author: Erbing
triggers:
  - "memory consolidation"
  - "optimize memory"
  - "strengthen memory"
  - "sleep consolidation"
  - "memory decay"
  - "记忆优化"
  - "记忆巩固"
  - "记忆衰减"
dependencies:
  tools:
    - read
    - write
    - exec
  libraries:
    - numpy
    - genetic_core
capabilities:
  - memory_strengthening
  - memory_decay
  - replay_consolidation
  - sleep_consolidation
  - memory_statistics
  - replay_buffer_management
  - adaptive_decay
---

# Memory Optimization Skill

This skill provides a memory consolidation system for Erbing, enabling long-term potentiation and memory stabilization. It simulates biological memory processes like strengthening, decay, and sleep consolidation.

## How It Works

1. **Memory Strengthening:** Increases the strength of specific memories based on activity.
2. **Memory Decay:** Gradually weakens unused memories over time.
3. **Replay Consolidation:** Replays important memories to reinforce them.
4. **Sleep Consolidation:** Simulates sleep-based memory consolidation cycles.
5. **Memory Statistics:** Provides insights into memory health.

## Usage

### Basic Operations

**Strengthen a Memory:**
```python
consolidation.strengthen_memory(conn_id, amount=0.1)
```

**Weaken a Memory:**
```python
consolidation.weaken_memory(conn_id, amount=0.05)
```

**Add Replay Sample:**
```python
consolidation.add_replay(in_node, out_node, activity)
```

### Advanced Operations

**Replay Memory:**
```python
consolidation.replay_memory(connections)
```

**Sleep Consolidation:**
```python
consolidation.sleep_consolidation(connections, sleep_cycles=5)
```

**Get Memory Statistics:**
```python
stats = consolidation.get_memory_statistics()
```

## Examples

### Example 1: Strengthening Important Memories

**User:** "I just learned something important. Strengthen this memory."

**Agent:** [Identifies the memory and increases its strength by the specified amount]

### Example 2: Sleep Consolidation

**User:** "I'm going to sleep. Consolidate my memories."

**Agent:** [Runs sleep consolidation cycles to reinforce important memories and apply decay]

### Example 3: Memory Health Check

**User:** "Check my memory health."

**Agent:** [Provides statistics on memory strength, consolidation, and decay levels]

### Example 4: Manual Replay

**User:** "Replay my most important memories from today."

**Agent:** [Selects high-activity memories and runs replay consolidation]

## Key Features

- **Biological Simulation:** Mimics real memory processes including LTP (Long-Term Potentiation).
- **Replay Buffer:** Stores and replays important memories for reinforcement.
- **Sleep Cycles:** Simulates sleep-based consolidation for memory stabilization.
- **Adaptive Decay:** Weakens unused memories over time to prevent clutter.
- **Statistics Dashboard:** Provides insights into memory health and distribution.

## Dependencies

### Required Libraries
- `numpy` - Numerical computations for memory strength calculations
- `genetic_core` - Core genetic/evolutionary algorithms for memory selection

### System Requirements
- No external services required
- Memory usage scales with replay buffer size
- Works with local memory database

## Best Practices

- **Regular Consolidation:** Run consolidation regularly to maintain memory health.
- **Sleep Cycles:** Use sleep consolidation for long-term memory stability.
- **Monitor Decay:** Keep an eye on memory decay to prevent loss of important memories.
- **Replay Important Memories:** Prioritize replay for high-value memories.
- **Balance Strength and Decay:** Adjust parameters based on memory importance.

## Parameters

### Memory Strengthening
- Default amount: `0.1` (10% increase)
- Maximum strength: `1.0`
- Recommended range: `0.05 - 0.2`

### Memory Decay
- Default decay rate: `0.05` (5% decrease)
- Minimum strength threshold: `0.01`
- Decay applies to inactive memories only

### Sleep Consolidation
- Default cycles: `5`
- Each cycle processes replay buffer
- Recommended: Run before/after sleep periods

## Troubleshooting

### Common Issues

1. **Memories decaying too fast:**
   - Reduce decay rate parameter
   - Run replay consolidation more frequently
   - Strengthen important memories explicitly

2. **Replay buffer overflow:**
   - Clear old replay samples
   - Reduce buffer size in configuration
   - Process replay buffer before adding new samples

3. **Statistics showing unexpected values:**
   - Verify memory IDs are correct
   - Check that consolidation has been run recently
   - Ensure database is not corrupted

## Contributing

To extend this skill:
1. Add new consolidation methods to the `MemoryConsolidation` class.
2. Update the `SKILL.md` with new capabilities.
3. Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
