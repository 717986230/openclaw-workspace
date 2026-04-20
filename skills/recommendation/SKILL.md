---
name: recommendation
description: Intelligent recommendation system with content-based, collaborative, graph-based, and hybrid recommendation methods.
triggers:
  - "recommendation"
  - "recommend"
  - "content-based"
  - "collaborative filtering"
  - "graph-based"
dependencies:
  - tool: read
  - tool: write
  - tool: exec
  - library: sqlite3
  - library: numpy
  - library: networkx
  - library: typing
  - library: dataclasses
  - library: enum
  - library: collections
  - library: random
capabilities:
  - content_based_recommendation
  - collaborative_recommendation
  - graph_based_recommendation
  - hybrid_recommendation
  - user_history_tracking
  - similarity_computation
---

# Recommendation Skill

This skill provides an intelligent recommendation system with content-based, collaborative, graph-based, and hybrid recommendation methods.

## How It Works

1.  **Content-Based Recommendation:** Recommends items based on content similarity.
2.  **Collaborative Recommendation:** Recommends items based on user history and collaborative filtering.
3.  **Graph-Based Recommendation:** Recommends items based on graph structure and relationships.
4.  **Hybrid Recommendation:** Combines multiple recommendation methods for better results.
5.  **User History Tracking:** Tracks user history for personalized recommendations.

## Usage

### Basic Operations

**Content-Based Recommendation:**
```python
recommendation = IntelligentRecommendation(db_path)
recommendation.load_graph(limit=1000)
results = recommendation.content_based_recommendation(memory_id, max_results=10)
```

**Collaborative Recommendation:**
```python
results = recommendation.collaborative_recommendation(user_id, max_results=10)
```

**Graph-Based Recommendation:**
```python
results = recommendation.graph_based_recommendation(memory_id, max_results=10)
```

### Advanced Operations

**Hybrid Recommendation:**
```python
results = recommendation.hybrid_recommendation(memory_id, user_id, max_results=10)
```

**Update User History:**
```python
recommendation.update_user_history(user_id, memory_id)
```

## Examples

### Example 1: Content-Based Recommendation
**User:** "Recommend items similar to this memory."
**Agent:** [Finds similar memories based on content and recommends them]

### Example 2: Collaborative Recommendation
**User:** "Recommend items based on my history."
**Agent:** [Uses collaborative filtering to recommend items based on user history]

### Example 3: Hybrid Recommendation
**User:** "Give me the best recommendations using all methods."
**Agent:** [Combines content-based, graph-based, and collaborative methods for hybrid recommendations]

## Key Features

- **Multiple Methods:** Supports content-based, collaborative, graph-based, and hybrid recommendations.
- **User History:** Tracks user history for personalized recommendations.
- **Graph Integration:** Uses graph structure for relationship-based recommendations.
- **Hybrid Approach:** Combines multiple methods for better recommendations.
- **Flexible Scoring:** Provides flexible scoring and explanation for recommendations.

## Dependencies

- **Python Libraries:** `sqlite3`, `numpy`, `networkx`, `typing`, `dataclasses`, `enum`, `collections`, `random`

## Best Practices

- **Load Graph:** Always load the graph before making recommendations.
- **Update History:** Regularly update user history for better collaborative recommendations.
- **Method Selection:** Choose the appropriate method based on your use case.
- **Hybrid Approach:** Use hybrid recommendations for the best results.
- **Tune Thresholds:** Adjust similarity thresholds based on your data.

## Contributing

To extend this skill:
1.  Add new recommendation methods to the `IntelligentRecommendation` class.
2.  Update the `SKILL.md` with new capabilities.
3.  Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
