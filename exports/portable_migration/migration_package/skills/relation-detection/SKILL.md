---
name: relation-detection
description: Automatic detection of causal relations and knowledge relations between memories using keyword matching, similarity analysis, and category-based detection.
triggers:
  - "relation detection"
  - "causal relations"
  - "knowledge relations"
  - "auto detect"
  - "similarity analysis"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: sqlite3
  - library: json
  - library: datetime
  - library: typing
  - library: re
capabilities:
  - causal_relation_detection
  - knowledge_relation_detection
  - similarity_based_detection
  - category_based_detection
  - batch_relation_detection
---

# Relation Detection Skill

This skill provides automatic detection of causal relations and knowledge relations between memories. It uses keyword matching, similarity analysis, and category-based detection to identify relationships.

## How It Works

1.  **Causal Relation Detection:** Detects cause-effect relationships using causal keywords.
2.  **Knowledge Relation Detection:** Detects various knowledge relations (is_a, part_of, related_to, etc.) using relation keywords.
3.  **Similarity-Based Detection:** Detects relations based on content similarity using Jaccard similarity.
4.  **Category-Based Detection:** Detects relations between memories in the same category.
5.  **Batch Detection:** Processes multiple memories in batch for efficient relation detection.

## Usage

### Basic Operations

**Detect Causal Relations:**
```python
detector = RelationDetector(db_path)
causal_relations = detector.detect_causal_relations(memory_id)
```

**Detect Knowledge Relations:**
```python
knowledge_relations = detector.detect_knowledge_relations(memory_id)
```

### Advanced Operations

**Detect Relations by Similarity:**
```python
similarity_relations = detector.detect_relations_by_similarity(memory_id, threshold=0.3)
```

**Detect Relations by Category:**
```python
category_relations = detector.detect_relations_by_category(memory_id)
```

**Auto Detect and Add Relations:**
```python
manager = AutoRelationManager(db_path)
result = manager.auto_detect_and_add_relations(memory_id)
```

**Batch Detect Relations:**
```python
results = manager.batch_detect_relations(limit=100)
```

## Examples

### Example 1: Detecting Causal Relations
**User:** "What causes this memory?"
**Agent:** [Analyzes the memory and detects causal relationships with other memories]

### Example 2: Detecting Knowledge Relations
**User:** "How is this memory related to others?"
**Agent:** [Detects various knowledge relations (is_a, part_of, related_to, etc.)]

### Example 3: Batch Detection
**User:** "Detect relations for the last 100 memories."
**Agent:** [Processes all memories and detects relations automatically]

## Key Features

- **Multiple Detection Methods:** Supports keyword matching, similarity analysis, and category-based detection.
- **Automatic Relation Addition:** Automatically adds detected relations to the database.
- **Batch Processing:** Efficiently processes multiple memories in batch.
- **Flexible Thresholds:** Configurable similarity thresholds for detection.

## Dependencies

- **Python Libraries:** `sqlite3`, `json`, `datetime`, `typing`, `re`

## Best Practices

- **Use Appropriate Thresholds:** Adjust similarity thresholds based on your data.
- **Batch Process:** Use batch detection for large datasets to improve performance.
- **Review Results:** Review detected relations before relying on them.
- **Combine Methods:** Use multiple detection methods for better coverage.

## Contributing

To extend this skill:
1.  Add new detection methods to the `RelationDetector` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
