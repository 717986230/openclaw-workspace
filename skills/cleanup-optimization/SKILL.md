---
name: cleanup-optimization
description: Automatic cleanup and optimization system for databases, including expired memory cleanup, duplicate merging, isolated memory detection, and index optimization.
triggers:
  - "cleanup"
  - "optimization"
  - "database cleanup"
  - "performance optimization"
  - "duplicate detection"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: sqlite3
  - library: numpy
  - library: typing
  - library: dataclasses
  - library: enum
  - library: datetime
capabilities:
  - expired_cleanup
  - duplicate_merging
  - isolated_detection
  - index_optimization
  - comprehensive_cleanup
  - cleanup_statistics
---

# Cleanup Optimization Skill

This skill provides an automatic cleanup and optimization system for databases. It includes expired memory cleanup, duplicate merging, isolated memory detection, and index optimization.

## How It Works

1.  **Expired Cleanup:** Removes expired memories based on age and importance.
2.  **Duplicate Merging:** Merges duplicate memories based on similarity.
3.  **Isolated Detection:** Detects isolated memories with no relations.
4.  **Index Optimization:** Optimizes database indexes for better performance.
5.  **Comprehensive Cleanup:** Performs all cleanup operations in one go.

## Usage

### Basic Operations

**Cleanup Expired Memories:**
```python
cleanup = AutoCleanupOptimization(db_path)
result = cleanup.cleanup_expired_memories(days_threshold=365)
```

**Merge Duplicate Memories:**
```python
result = cleanup.merge_duplicate_memories(similarity_threshold=0.9)
```

**Detect Isolated Memories:**
```python
result = cleanup.detect_isolated_memories()
```

### Advanced Operations

**Optimize Indexes:**
```python
result = cleanup.optimize_indexes()
```

**Comprehensive Cleanup:**
```python
results = cleanup.comprehensive_cleanup()
```

**Get Cleanup Statistics:**
```python
stats = cleanup.get_cleanup_statistics()
```

## Examples

### Example 1: Cleaning Expired Memories
**User:** "Clean up memories older than 1 year."
**Agent:** [Removes expired memories and reports the number of items cleaned]

### Example 2: Merging Duplicates
**User:** "Merge duplicate memories."
**Agent:** [Finds and merges duplicate memories based on similarity]

### Example 3: Comprehensive Cleanup
**User:** "Perform a comprehensive cleanup of my database."
**Agent:** [Performs all cleanup operations and reports the results]

## Key Features

- **Multiple Cleanup Types:** Supports expired, duplicate, and isolated cleanup.
- **Similarity-Based Merging:** Uses similarity thresholds to identify duplicates.
- **Index Optimization:** Optimizes database indexes for better performance.
- **Comprehensive Cleanup:** Performs all cleanup operations in one go.
- **Statistics:** Provides cleanup statistics and information.

## Dependencies

- **Python Libraries:** `sqlite3`, `numpy`, `typing`, `dataclasses`, `enum`, `datetime`

## Best Practices

- **Regular Cleanup:** Schedule regular cleanup to maintain database health.
- **Threshold Tuning:** Adjust thresholds based on your data and requirements.
- **Backup First:** Always backup before performing cleanup operations.
- **Monitor Statistics:** Monitor cleanup statistics to ensure effectiveness.
- **Test Thoroughly:** Test cleanup operations on a copy of the database first.

## Contributing

To extend this skill:
1.  Add new cleanup or optimization methods to the `AutoCleanupOptimization` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
