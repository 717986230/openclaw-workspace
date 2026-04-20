"""
Neo4j Integration for OpenClaw

Provides graph database capabilities including:
- Connection management with pooling
- Cypher query building and execution
- Graph algorithms (traversal, centrality, community detection)
- Path finding and relationship reasoning

Usage:
    from integrations.neo4j import Neo4jConnection
    
    with Neo4jConnection() as conn:
        nodes = conn.execute("MATCH (n:Person) RETURN n LIMIT 10")
        for node in nodes:
            print(node)
"""

from .database import (
    Neo4jConfig,
    Neo4jConnection,
    Neo4jConnectionPool,
    create_connection,
    get_config,
    get_pool,
)

from .queries import (
    CypherBuilder,
    NodeQueryBuilder,
    RelationshipQueryBuilder,
    QueryExecutor,
    BulkLoader,
    QueryTemplates,
)

from .algorithms import (
    GraphTraversal,
    CentralityAnalyzer,
    CommunityDetector,
    PathFinder,
)

__version__ = "1.0.0"

__all__ = [
    # Configuration
    "Neo4jConfig",
    "get_config",
    
    # Connection
    "Neo4jConnection",
    "Neo4jConnectionPool",
    "create_connection",
    "get_pool",
    
    # Queries
    "CypherBuilder",
    "NodeQueryBuilder",
    "RelationshipQueryBuilder",
    "QueryExecutor",
    "BulkLoader",
    "QueryTemplates",
    
    # Algorithms
    "GraphTraversal",
    "CentralityAnalyzer",
    "CommunityDetector",
    "PathFinder",
]
