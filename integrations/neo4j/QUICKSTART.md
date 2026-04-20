# Neo4j Integration Quick Start

## Installation

1. Install Neo4j database (if not already installed):
   ```bash
   # Using Docker
   docker run -d --name neo4j \
     -p 7474:7474 -p 7687:7687 \
     -e NEO4J_AUTH=neo4j/password \
     neo4j:latest
   
   # Or download from https://neo4j.com/download/
   ```

2. Install Python dependencies:
   ```bash
   pip install -r integrations/neo4j/requirements.txt
   ```

3. Set environment variables:
   ```bash
   export NEO4J_URI=bolt://localhost:7687
   export NEO4J_USER=neo4j
   export NEO4J_PASSWORD=password
   ```

## Basic Usage

### 1. Simple Connection

```python
from integrations.neo4j import Neo4jConnection

# Connect using environment variables
with Neo4jConnection() as conn:
    result = conn.execute("MATCH (n) RETURN n LIMIT 10")
    print(result)
```

### 2. Create Nodes

```python
# Create a person node
person = conn.create_node(
    label="Person",
    properties={
        "id": "p1",
        "name": "Alice",
        "age": 30
    },
    unique_key="id"
)
```

### 3. Create Relationships

```python
# Create friendship relationship
rel = conn.create_relationship(
    from_label="Person",
    from_key="id",
    from_value="p1",
    to_label="Person",
    to_key="id",
    to_value="p2",
    relationship_type="KNOWS",
    properties={"since": 2020}
)
```

### 4. Query with Cypher Builder

```python
from integrations.neo4j import CypherBuilder

builder = CypherBuilder()
query = (builder
    .match("(p:Person)")
    .where("p.age > $min_age", min_age=25)
    .return_("p.name, p.age")
    .order_by("p.age DESC")
    .limit(10)
    .build())

result = conn.execute(query, builder.get_parameters())
```

### 5. Use Graph Algorithms

```python
from integrations.neo4j import PathFinder, CentralityAnalyzer

# Find shortest path
finder = PathFinder(conn)
path = finder.shortest_path(
    from_label="Person",
    from_key="id",
    from_value="alice",
    to_label="Person",
    to_key="id",
    to_value="bob"
)

# Calculate centrality
analyzer = CentralityAnalyzer(conn)
top_users = analyzer.degree_centrality("Person", limit=10)
```

### 6. Community Detection

```python
from integrations.neo4j import CommunityDetector

detector = CommunityDetector(conn)
communities = detector.louvain("Person")

# Get community statistics
stats = detector.get_community_statistics("Person", "community")
```

## Running Tests

```bash
# Run all tests
pytest integrations/neo4j/tests/ -v

# Run specific test file
pytest integrations/neo4j/tests/test_connection.py -v

# Run with coverage
pytest integrations/neo4j/tests/ --cov=integrations/neo4j
```

## Running Examples

```bash
# Basic CRUD operations
python integrations/neo4j/examples/basic_crud.py

# Relationship examples
python integrations/neo4j/examples/relationships.py

# Algorithm demonstrations
python integrations/neo4j/examples/algorithms_demo.py
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| NEO4J_URI | Connection URI | bolt://localhost:7687 |
| NEO4J_USER | Username | neo4j |
| NEO4J_PASSWORD | Password | (required) |
| NEO4J_DATABASE | Database name | neo4j |

### YAML Configuration

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

## Integration with OpenClaw Memory

The Neo4j integration can store and query OpenClaw memory graphs:

```python
# Store memory as graph node
conn.create_node(
    label="Memory",
    properties={
        "id": memory_id,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "type": memory_type
    },
    unique_key="id"
)

# Create relationship between related memories
conn.create_relationship(
    from_label="Memory",
    from_key="id",
    from_value=memory1_id,
    to_label="Memory",
    to_key="id",
    to_value=memory2_id,
    relationship_type="RELATES_TO",
    properties={"weight": similarity_score}
)

# Find related memories
related = conn.execute("""
    MATCH (m:Memory {id: $id})-[:RELATES_TO]-(related)
    RETURN related
    ORDER BY related.timestamp DESC
    LIMIT 10
""", {"id": memory_id})
```

## Troubleshooting

### Connection Refused
- Ensure Neo4j is running: `docker ps` or check Neo4j service
- Verify URI and port: default is bolt://localhost:7687

### Authentication Failed
- Check credentials in environment variables
- For Docker: use password from NEO4J_AUTH

### Query Timeout
- Add indexes on frequently queried properties
- Use EXPLAIN to analyze query plan
- Reduce result set with LIMIT

### Memory Issues
- Adjust Neo4j heap size in neo4j.conf
- Use connection pooling appropriately
- Close connections properly

## Further Reading

- [INTEGRATION.md](./INTEGRATION.md) - Full integration documentation
- [Neo4j Docs](https://neo4j.com/docs/)
- [Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [Graph Data Science](https://neo4j.com/docs/graph-data-science-library/)
