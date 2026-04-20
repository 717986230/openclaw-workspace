---
name: graph-analysis
description: Advanced graph analysis tools for knowledge graphs, including path analysis, centrality analysis, clustering, and community detection.
version: 1.0.0
author: Erbing
triggers:
  - "graph analysis"
  - "path analysis"
  - "centrality"
  - "clustering"
  - "community detection"
  - "network analysis"
  - "图分析"
  - "路径分析"
  - "中心性分析"
  - "社区发现"
dependencies:
  tools:
    - read
    - write
    - exec
  libraries:
    - sqlite3
    - numpy
    - networkx
    - typing
    - dataclasses
    - enum
    - collections
capabilities:
  - path_analysis
  - centrality_analysis
  - clustering_analysis
  - community_detection
  - comprehensive_analysis
  - graph_statistics
  - connectivity_analysis
  - modularity_optimization
---

# Graph Analysis Skill

This skill provides advanced graph analysis tools for knowledge graphs. It includes path analysis, centrality analysis, clustering, and community detection capabilities.

## How It Works

1. **Path Analysis:** Finds shortest paths and all paths between nodes.
2. **Centrality Analysis:** Computes degree, betweenness, closeness, eigenvector centrality, and PageRank.
3. **Clustering Analysis:** Computes clustering coefficients and average clustering.
4. **Community Detection:** Detects communities using greedy modularity maximization.
5. **Comprehensive Analysis:** Performs all analyses and returns combined results.

## Usage

### Basic Operations

**Load Graph:**
```python
analysis = AdvancedGraphAnalysis(db_path)
load_result = analysis.load_graph(limit=1000)
```

**Path Analysis:**
```python
result = analysis.path_analysis(source_id, target_id)
```

**Centrality Analysis:**
```python
result = analysis.centrality_analysis()
```

### Advanced Operations

**Clustering Analysis:**
```python
result = analysis.clustering_analysis()
```

**Community Detection:**
```python
result = analysis.community_detection()
```

**Comprehensive Analysis:**
```python
results = analysis.comprehensive_analysis()
```

## Examples

### Example 1: Analyzing Centrality

**User:** "What are the most important nodes in my knowledge graph?"

**Agent:** [Performs centrality analysis and returns top nodes by degree, betweenness, and PageRank]

### Example 2: Finding Communities

**User:** "What are the main communities in my knowledge graph?"

**Agent:** [Detects communities and reports their sizes and modularity score]

### Example 3: Path Analysis

**User:** "How are these two concepts connected?"

**Agent:** [Finds shortest path and all paths between the two concepts]

### Example 4: Comprehensive Analysis

**User:** "Give me a full analysis of my knowledge graph."

**Agent:** [Runs comprehensive analysis including all metrics and returns detailed report]

## Key Features

- **Multiple Analysis Types:** Supports path, centrality, clustering, and community analysis.
- **Comprehensive Results:** Returns detailed results with explanations.
- **Graph Statistics:** Provides graph density, connectivity, and component information.
- **Flexible Loading:** Supports loading graphs with customizable limits.
- **Performance Optimized:** Uses efficient algorithms for large graphs.

## Dependencies

### Required Libraries
- `sqlite3` - Database connection for graph data
- `numpy` - Numerical computations for centrality calculations
- `networkx` - Core graph algorithms (path, centrality, clustering, communities)
- `typing` - Type hints and annotations
- `dataclasses` - Data structure definitions for results
- `enum` - Enumeration types for analysis modes
- `collections` - Counter and defaultdict utilities

### Performance Notes
- Large graphs (>10,000 nodes) may require longer processing time
- Use `limit` parameter to control graph size
- Centrality analysis on large graphs can be memory-intensive
- Community detection scales well with graph size

## Analysis Types

### Path Analysis
- **Shortest Path:** Uses Dijkstra's algorithm (unweighted) or A* (weighted)
- **All Paths:** Finds all paths up to a specified depth
- **Returns:** Path nodes, path length, and path weights

### Centrality Analysis
- **Degree Centrality:** Number of connections per node
- **Betweenness Centrality:** How often a node lies on shortest paths
- **Closeness Centrality:** Average distance to all other nodes
- **Eigenvector Centrality:** Influence based on neighbor importance
- **PageRank:** Google's algorithm for node importance

### Clustering Analysis
- **Clustering Coefficient:** How connected a node's neighbors are
- **Average Clustering:** Overall graph clustering
- **Transitivity:** Global clustering measure

### Community Detection
- **Greedy Modularity:** Fast community detection
- **Returns:** Community assignments, sizes, and modularity score

## Best Practices

- **Limit Graph Size:** Use `limit` parameter to control graph size for performance.
- **Check Connectivity:** Verify graph connectivity before path analysis.
- **Combine Analyses:** Use comprehensive analysis for a complete picture.
- **Interpret Results:** Use explanations to understand analysis results.
- **Cache Results:** Store analysis results for frequently queried graphs.

## Troubleshooting

### Common Issues

1. **"Graph is disconnected" error:**
   - Run connectivity check before path analysis
   - Use `largest_connected_component` to focus on main graph

2. **Out of memory:**
   - Reduce `limit` parameter when loading
   - Use iterative analysis instead of comprehensive
   - Free memory between large analyses

3. **Slow centrality computation:**
   - Use approximate algorithms for large graphs
   - Limit centrality to top-k nodes
   - Enable caching for repeated analyses

4. **"No path found" error:**
   - Verify both nodes exist in the graph
   - Check if nodes are in the same connected component
   - Increase depth limit for all-paths search

## Contributing

To extend this skill:
1. Add new analysis methods to the `AdvancedGraphAnalysis` class.
2. Update the `SKILL.md` with new capabilities.
3. Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
