# Neo4j Integration for OpenClaw

## Overview

This integration provides Neo4j graph database capabilities to OpenClaw, enabling advanced graph operations, relationship reasoning, and Cypher query support.

## Architecture

```
integrations/neo4j/
├── INTEGRATION.md          # This file
├── database/               # Database connection and management
│   ├── connection.py       # Connection manager
│   ├── config.py          # Configuration handling
│   └── pool.py            # Connection pooling
├── queries/                # Query management
│   ├── cypher.py          # Cypher query builder
│   ├── templates.py       # Pre-defined query templates
│   └── executor.py        # Query execution engine
├── algorithms/             # Graph algorithms
│   ├── traversal.py       # Graph traversal algorithms
│   ├── centrality.py      # Centrality measures
│   ├── community.py       # Community detection
│   └── pathfinding.py     # Path finding algorithms
├── examples/               # Usage examples
│   ├── basic_crud.py      # Basic CRUD operations
│   ├── relationships.py   # Relationship examples
│   └── algorithms_demo.py # Algorithm demonstrations
└── tests/                  # Test suite
    ├── test_connection.py  # Connection tests
    ├── test_queries.py    # Query tests
    └── test_algorithms.py # Algorithm tests
```

## Features

### 1. Graph Database Integration
- Connection management with connection pooling
- Automatic reconnection and error handling
- Transaction support
- Batch operations

### 2. Cypher Query Support
- Query builder for programmatic query construction
- Parameterized queries for security
- Query templates for common operations
- Query execution with retry logic

### 3. Graph Algorithms
- **Traversal**: BFS, DFS, shortest path
- **Centrality**: PageRank, betweenness, closeness
- **Community Detection**: Louvain, label propagation
- **Path Finding**: Dijkstra, A*, all paths

### 4. Relationship Reasoning
- Inference engine for deriving new relationships
- Pattern matching for complex queries
- Temporal relationship tracking
- Weighted relationship analysis

## Configuration

### Environment Variables

```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
NEO4J_MAX_CONNECTION_POOL_SIZE=50
NEO4J_CONNECTION_TIMEOUT=30
```

### Config File (config.yaml)

```yaml
neo4j:
  uri: bolt://localhost:7687
  user: neo4j
  password: ${NEO4J_PASSWORD}
  database: neo4j
  pool:
    max_size: 50
    timeout: 30
  retry:
    max_attempts: 3
    backoff_factor: 2
```

## Usage Examples

### Basic Connection

```python
from integrations.neo4j.database.connection import Neo4jConnection

# Create connection
conn = Neo4jConnection(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Execute query
result = conn.execute("MATCH (n) RETURN n LIMIT 10")
```

### Query Builder

```python
from integrations.neo4j.queries.cypher import CypherBuilder

# Build query
builder = CypherBuilder()
query = (builder
    .match("(p:Person)")
    .where("p.age > ?", 25)
    .return_("p.name, p.age")
    .order_by("p.age DESC")
    .limit(10)
    .build()
)
```

### Graph Algorithms

```python
from integrations.neo4j.algorithms.pathfinding import PathFinder

# Find shortest path
finder = PathFinder(conn)
path = finder.shortest_path(
    start_node="Alice",
    end_node="Bob",
    relationship_type="KNOWS"
)
```

## Integration with OpenClaw

### Memory Graph Integration

Neo4j can be used to store and query the knowledge graph:

```python
# Store memory as graph node
memory_node = neo4j_client.create_node(
    label="Memory",
    properties={
        "id": memory_id,
        "content": content,
        "timestamp": datetime.now()
    }
)

# Create relationships between related memories
neo4j_client.create_relationship(
    from_node=memory1_id,
    to_node=memory2_id,
    type="RELATES_TO",
    properties={"weight": similarity_score}
)
```

### Skill Graph Integration

Skills can be organized as a graph:

```python
# Create skill node
skill_node = neo4j_client.create_node(
    label="Skill",
    properties={
        "name": "web-crawler",
        "category": "automation",
        "version": "1.0.0"
    }
)

# Link related skills
neo4j_client.create_relationship(
    from_node="web-crawler",
    to_node="summarize",
    type="DEPENDS_ON"
)
```

## Security Considerations

1. **Authentication**: Always use environment variables for credentials
2. **Query Injection**: Use parameterized queries only
3. **Connection Encryption**: Use bolt+s or bolt+ssc URIs for TLS
4. **Access Control**: Implement proper role-based access

## Performance Optimization

1. **Indexes**: Create indexes on frequently queried properties
2. **Constraints**: Use uniqueness constraints for unique identifiers
3. **Batch Operations**: Use batch inserts for bulk data
4. **Connection Pooling**: Configure appropriate pool size

## Monitoring

- Connection pool status
- Query execution times
- Transaction success/failure rates
- Node/relationship counts

## Troubleshooting

### Common Issues

1. **Connection Refused**: Check Neo4j service status
2. **Authentication Failed**: Verify credentials
3. **Query Timeout**: Optimize query or add indexes
4. **Memory Issues**: Adjust heap size in Neo4j config

## Dependencies

```
neo4j>=5.0.0
neo4j-driver>=5.0.0
py2neo>=2021.0.0
```

## License

MIT License - Part of OpenClaw Integration Framework

## References

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/)
- [Graph Algorithms Library](https://neo4j.com/docs/graph-data-science-library/)
