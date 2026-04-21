---
name: knowledge-graph
description: A comprehensive knowledge graph system for tracking relationships between memories, skills, and knowledge.
version: 1.0.0
author: Erbing
triggers:
  - "knowledge graph"
  - "analyze relationships"
  - "find connections"
  - "impact analysis"
  - "discover clusters"
  - "知识图谱"
  - "关系分析"
dependencies:
  tools:
    - read
    - write
    - exec
  libraries:
    - sqlite3
    - networkx
    - json
capabilities:
  - knowledge_management
  - relationship_tracking
  - impact_analysis
  - cluster_discovery
  - context_analysis
  - graph_query
  - node_management
---

# Knowledge Graph Skill

This skill provides a comprehensive knowledge graph system for Erbing, enabling the tracking and analysis of relationships between memories, skills, and knowledge. It uses SQLite for persistence and NetworkX for graph analysis.

## How It Works

1. **Knowledge Nodes:** Stores entities (memories, skills, knowledge) as nodes in the graph.
2. **Knowledge Edges:** Defines relationships (depends_on, references, causes) between nodes.
3. **Context Analysis:** Provides a 360-degree view of any node's context.
4. **Impact Analysis:** Analyzes how changes to one node affect others.
5. **Cluster Discovery:** Identifies groups of related knowledge.

## Usage

### Basic Operations

**Add a Knowledge Node:**
```python
kg.add_node('memory_1', 'memory', 'First Memory', 'This is my first memory')
```

**Add a Relationship:**
```python
kg.add_edge('memory_1', 'knowledge_1', 'references')
```

**Query the Graph:**
```python
results = kg.query('Python')
```

### Advanced Analysis

**Get Node Context:**
```python
context = kg.get_node_context('knowledge_1', depth=2)
```

**Analyze Impact:**
```python
impact = kg.analyze_impact('knowledge_1')
```

**Discover Clusters:**
```python
clusters = kg.find_clusters()
```

## Examples

### Example 1: Tracking Learning Progress

**User:** "I just learned about Python decorators. Add this to my knowledge graph."

**Agent:** [Adds a knowledge node for 'Python Decorators' and links it to 'Python' and 'Functions']

### Example 2: Impact Analysis

**User:** "If I change my understanding of 'Python', what else is affected?"

**Agent:** [Performs impact analysis and reports all dependent skills and memories]

### Example 3: Discovering Knowledge Gaps

**User:** "Find clusters in my knowledge graph."

**Agent:** [Identifies clusters and reports areas with low cohesion]

### Example 4: Finding Connections

**User:** "How is my knowledge of Python connected to my memory of the last project?"

**Agent:** [Queries the graph and shows the relationship path between the nodes]

## Key Features

- **Persistent Storage:** Uses SQLite for durable storage.
- **Graph Analysis:** Leverages NetworkX for advanced graph algorithms.
- **Context Awareness:** Provides deep context for any knowledge node.
- **Impact Tracking:** Analyzes the ripple effects of changes.
- **Cluster Detection:** Identifies groups of related knowledge.
- **Flexible Queries:** Supports keyword and pattern-based searches.

## Dependencies

### Required Libraries
- `sqlite3` - Database storage and persistence
- `networkx` - Graph analysis algorithms and data structures
- `json` - Data serialization for metadata

### Database
- SQLite database at `memory/database/xiaozhi_memory.db`

### Storage Requirements
- Minimal disk space for database file
- Memory usage scales with graph size (typically <100MB for normal usage)
- No external services required

## Best Practices

- **Consistent IDs:** Use consistent and unique IDs for nodes.
- **Rich Metadata:** Include detailed metadata for better analysis.
- **Regular Updates:** Update the graph as new knowledge is acquired.
- **Query Optimization:** Use specific queries to improve performance.
- **Backup Regularly:** Export the database periodically to prevent data loss.

## Troubleshooting

### Common Issues

1. **"Database locked" error:**
   - Ensure only one process is writing to the database
   - Use connection pooling for concurrent reads

2. **Slow queries:**
   - Add specific keywords to narrow search scope
   - Use the `limit` parameter for large result sets

3. **Missing relationships:**
   - Verify both nodes exist before adding edges
   - Check edge type spelling (must match defined types)

## Contributing

To extend this skill:
1. Add new analysis methods to the `ErbingKnowledgeGraph` class.
2. Update the `SKILL.md` with new capabilities.
3. Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
