---
name: mcp-integration
description: A comprehensive MCP (Model Context Protocol) toolset for standardized knowledge operations.
version: 1.0.0
author: Erbing
triggers:
  - "mcp tools"
  - "knowledge operations"
  - "graph query"
  - "context management"
  - "impact analysis"
  - "MCP工具"
  - "知识操作"
  - "上下文管理"
dependencies:
  tools:
    - read
    - write
    - exec
  libraries:
    - json
    - typing
    - datetime
  modules:
    - erbing_knowledge_graph
capabilities:
  - context_management
  - knowledge_query
  - impact_analysis
  - graph_operations
  - resource_system
  - safe_rename
  - multi_context_support
  - uri_based_resources
---

# MCP Integration Skill

This skill provides a comprehensive MCP (Model Context Protocol) toolset for Erbing, enabling standardized knowledge operations. It offers 16 core tools plus a resource system for managing knowledge graphs.

## How It Works

1. **Single Context Tools (11):** Tools for managing individual contexts (list, query, get context, analyze impact, detect changes, safe rename, add/update/delete nodes, query graph).
2. **Multi Context Tools (5):** Tools for managing groups of contexts (group list, sync, query, status, contracts).
3. **Resource System:** A URI-based resource system for accessing different types of knowledge.

## Usage

### Basic Operations

**List Contexts:**
```python
tools.call_tool('list_contexts')
```

**Query Knowledge:**
```python
tools.call_tool('query', query='Python', limit=10)
```

**Get Node Context:**
```python
tools.call_tool('get_context', node_id='memory_1', depth=2)
```

### Advanced Operations

**Analyze Impact:**
```python
tools.call_tool('analyze_impact', node_id='knowledge_1')
```

**Safe Rename:**
```python
tools.call_tool('safe_rename', old_name='old_name', new_name='new_name', dry_run=False)
```

**Query Graph:**
```python
tools.call_tool('query_graph', cypher_query='MATCH (n:memory) RETURN n')
```

## Examples

### Example 1: Managing Knowledge

**User:** "Add a new memory about Python decorators."

**Agent:** [Adds a new node to the knowledge graph with the specified content and metadata]

### Example 2: Analyzing Impact

**User:** "What happens if I change my understanding of 'Python'?"

**Agent:** [Performs impact analysis and reports all dependent nodes]

### Example 3: Querying Resources

**User:** "Get all memories in the system."

**Agent:** [Queries the resource system and returns all memory nodes]

### Example 4: Multi-Context Operations

**User:** "Sync all contexts related to my current project."

**Agent:** [Uses multi-context tools to synchronize related knowledge groups]

## Key Features

- **Standardized Interface:** Provides a consistent API for all knowledge operations.
- **Graph Operations:** Supports complex graph queries and operations.
- **Impact Analysis:** Analyzes the ripple effects of changes.
- **Resource System:** URI-based access to different knowledge types.
- **Multi Context Support:** Manages groups of contexts efficiently.
- **Safe Operations:** Includes dry-run modes for destructive operations.

## Dependencies

### Required Libraries
- `json` - Data serialization for tool inputs/outputs
- `typing` - Type hints and annotations for type safety
- `datetime` - Timestamp handling for metadata

### Internal Modules
- `erbing_knowledge_graph` - Core knowledge graph implementation
  - Must be importable from Python path
  - Provides graph storage and query capabilities

### Tool Count
- **Single Context Tools:** 11 tools for individual context management
- **Multi Context Tools:** 5 tools for group context operations
- **Total:** 16 core tools + resource system

## Tool Reference

### Single Context Tools

| Tool | Description |
|------|-------------|
| `list_contexts` | List all available contexts |
| `query` | Query knowledge by keyword |
| `get_context` | Get node context with depth control |
| `analyze_impact` | Analyze change impact on dependencies |
| `detect_changes` | Detect recent changes in context |
| `safe_rename` | Safely rename nodes with validation |
| `add_node` | Add a new knowledge node |
| `update_node` | Update existing node metadata |
| `delete_node` | Delete a node (with safety checks) |
| `query_graph` | Execute graph query (Cypher-like) |
| `get_node` | Get single node by ID |

### Multi Context Tools

| Tool | Description |
|------|-------------|
| `group_list` | List all context groups |
| `sync` | Synchronize context groups |
| `multi_query` | Query across multiple contexts |
| `status` | Get status of context groups |
| `contracts` | Manage context contracts |

## Best Practices

- **Use Safe Rename:** Always use `safe_rename` with `dry_run=True` first.
- **Query Efficiently:** Use specific queries to improve performance.
- **Analyze Impact:** Check impact before making significant changes.
- **Resource URIs:** Use the resource system for standardized access.
- **Batch Operations:** Group related operations when possible.

## Troubleshooting

### Common Issues

1. **"Module not found" error:**
   - Ensure `erbing_knowledge_graph` is in Python path
   - Check installation of required modules

2. **"Invalid URI" error:**
   - Verify URI format: `knowledge://type/id`
   - Check that the node type is valid

3. **Slow queries:**
   - Use the `limit` parameter
   - Add specific keywords to narrow scope
   - Check graph size and indexing

4. **"Node not found" error:**
   - Verify node ID exists
   - Check for typos in node names
   - Use `list_contexts` to see available nodes

## Contributing

To extend this skill:
1. Add new tools to the `ErbingMCPTools` class.
2. Update the `SKILL.md` with new capabilities.
3. Test thoroughly before committing.

---

**Last Updated:** 2026-04-16
**Maintained By:** Erbing (Main OpenClaw Agent)
