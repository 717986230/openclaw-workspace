"""
Relationship Examples

Demonstrates relationship creation, querying, and traversal.
"""

from integrations.neo4j.database import Neo4jConnection
from integrations.neo4j.queries import CypherBuilder, RelationshipQueryBuilder
from integrations.neo4j.algorithms import GraphTraversal


def main():
    """Run relationship examples"""
    
    with Neo4jConnection() as conn:
        
        # Setup: Create sample data
        print("Setting up sample data...")
        
        # Create person nodes
        for i, name in enumerate(["Alice", "Bob", "Charlie", "Diana", "Eve"], 1):
            conn.create_node("Person", {"id": f"p{i}", "name": name}, "id")
        
        # Create relationships
        relationships = [
            ("p1", "p2", "KNOWS"),
            ("p2", "p3", "KNOWS"),
            ("p3", "p4", "KNOWS"),
            ("p4", "p5", "KNOWS"),
            ("p1", "p3", "FRIEND"),
            ("p2", "p4", "FRIEND"),
        ]
        
        for from_id, to_id, rel_type in relationships:
            conn.create_relationship(
                "Person", "id", from_id,
                "Person", "id", to_id,
                rel_type
            )
        
        print("Sample data created.\n")
        
        # Example 1: Find direct relationships
        print("Example 1: Find direct relationships")
        print("-" * 40)
        
        query = """
        MATCH (a:Person {id: $id})-[r]-(b:Person)
        RETURN a.name, type(r) as relationship, b.name
        """
        results = conn.execute(query, {"id": "p1"})
        for r in results:
            print(f"{r['a.name']} --[{r['relationship']}]--> {r['b.name']}")
        
        # Example 2: Using CypherBuilder
        print("\nExample 2: Using CypherBuilder")
        print("-" * 40)
        
        builder = CypherBuilder()
        query = (builder
            .match("(a:Person)-[r:KNOWS]-(b:Person)")
            .where("a.id = $id OR b.id = $id", id="p2")
            .return_("a.name, b.name, r")
            .build())
        
        results = conn.execute(query, builder.get_parameters())
        for r in results:
            print(f"{r['a.name']} KNOWS {r['b.name']}")
        
        # Example 3: Find paths
        print("\nExample 3: Find paths between nodes")
        print("-" * 40)
        
        traversal = GraphTraversal(conn)
        path = traversal.get_path(
            "Person", "id", "p1",
            "Person", "id", "p5"
        )
        
        if path:
            path_names = [n.get("name") for n in path]
            print(f"Path: {' -> '.join(path_names)}")
        
        # Example 4: Find all paths
        print("\nExample 4: Find all paths")
        print("-" * 40)
        
        all_paths = traversal.get_all_paths(
            "Person", "id", "p1",
            "Person", "id", "p4",
            max_depth=4
        )
        
        for i, path in enumerate(all_paths, 1):
            path_names = [n.get("name") for n in path]
            print(f"Path {i}: {' -> '.join(path_names)}")
        
        # Example 5: Traverse from a node
        print("\nExample 5: BFS Traversal")
        print("-" * 40)
        
        visited = traversal.breadth_first_search(
            "Person", "id", "p1",
            max_depth=3
        )
        
        print(f"Visited nodes: {[v.get('name') for v in visited]}")
        
        # Example 6: Find common neighbors
        print("\nExample 6: Find common neighbors")
        print("-" * 40)
        
        query = """
        MATCH (a:Person {id: 'p1'})-[:KNOWS]-(common)-[:KNOWS]-(b:Person {id: 'p3'})
        WHERE a <> b
        RETURN DISTINCT common.name as common_friend
        """
        results = conn.execute(query)
        print(f"Common friends: {[r['common_friend'] for r in results]}")
        
        # Example 7: Relationship patterns
        print("\nExample 7: Complex relationship patterns")
        print("-" * 40)
        
        query = """
        MATCH path = (a:Person)-[:KNOWS*1..3]-(b:Person)
        WHERE a.id = 'p1' AND a <> b
        RETURN DISTINCT b.name as reachable, length(path) as distance
        ORDER BY distance
        """
        results = conn.execute(query)
        for r in results:
            print(f"{r['reachable']} (distance: {r['distance']})")
        
        # Cleanup
        print("\nCleaning up...")
        conn.execute("MATCH (n:Person) DETACH DELETE n")
        print("Done.")


if __name__ == "__main__":
    main()
