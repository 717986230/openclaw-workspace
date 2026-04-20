"""
Graph Algorithms Demonstration

Shows centrality, community detection, and path finding algorithms.
"""

from integrations.neo4j.database import Neo4jConnection
from integrations.neo4j.algorithms import (
    CentralityAnalyzer,
    CommunityDetector,
    PathFinder,
    GraphTraversal
)


def setup_sample_graph(conn: Neo4jConnection) -> None:
    """Create a sample social network graph"""
    
    # Create users
    users = [
        {"id": "u1", "name": "Alice"},
        {"id": "u2", "name": "Bob"},
        {"id": "u3", "name": "Charlie"},
        {"id": "u4", "name": "Diana"},
        {"id": "u5", "name": "Eve"},
        {"id": "u6", "name": "Frank"},
        {"id": "u7", "name": "Grace"},
        {"id": "u8", "name": "Henry"},
    ]
    
    for user in users:
        conn.create_node("User", user, "id")
    
    # Create friendships (KNOWS relationships)
    friendships = [
        ("u1", "u2"), ("u1", "u3"), ("u1", "u4"),
        ("u2", "u3"), ("u2", "u5"),
        ("u3", "u4"), ("u3", "u6"),
        ("u4", "u7"),
        ("u5", "u6"), ("u5", "u8"),
        ("u6", "u7"), ("u6", "u8"),
        ("u7", "u8"),
    ]
    
    for from_id, to_id in friendships:
        conn.create_relationship(
            "User", "id", from_id,
            "User", "id", to_id,
            "KNOWS",
            {"weight": 1.0}
        )
    
    print(f"Created {len(users)} users and {len(friendships)} friendships")


def main():
    """Run algorithm demonstrations"""
    
    with Neo4jConnection() as conn:
        
        # Setup
        print("=" * 60)
        print("Setting up sample graph...")
        print("=" * 60)
        setup_sample_graph(conn)
        
        # ============================================
        # Centrality Analysis
        # ============================================
        print("\n" + "=" * 60)
        print("CENTRALITY ANALYSIS")
        print("=" * 60)
        
        centrality = CentralityAnalyzer(conn)
        
        # Degree Centrality
        print("\n1. Degree Centrality (top users by connections)")
        print("-" * 40)
        degree_results = centrality.degree_centrality("User", "KNOWS", limit=5)
        for r in degree_results:
            print(f"  {r['name']}: {r['degree']} connections")
        
        # PageRank
        print("\n2. PageRank (influence scores)")
        print("-" * 40)
        pagerank_results = centrality.pagerank("User", "KNOWS", limit=5)
        for r in pagerank_results:
            print(f"  {r['name']}: {r['score']:.4f}")
        
        # ============================================
        # Community Detection
        # ============================================
        print("\n" + "=" * 60)
        print("COMMUNITY DETECTION")
        print("=" * 60)
        
        community = CommunityDetector(conn)
        
        # Connected Components
        print("\n1. Connected Components")
        print("-" * 40)
        components = community.connected_components("User", "KNOWS")
        component_groups = {}
        for c in components:
            comp_id = c['componentId']
            if comp_id not in component_groups:
                component_groups[comp_id] = []
            component_groups[comp_id].append(c['name'])
        
        for comp_id, members in component_groups.items():
            print(f"  Component {comp_id}: {', '.join(members)}")
        
        # Triangle Count
        print("\n2. Triangle Count")
        print("-" * 40)
        triangles = community.triangle_count("User", "KNOWS")
        for t in triangles[:5]:
            print(f"  {t['name']}: {t['triangleCount']} triangles")
        
        # ============================================
        # Path Finding
        # ============================================
        print("\n" + "=" * 60)
        print("PATH FINDING")
        print("=" * 60)
        
        pathfinder = PathFinder(conn)
        
        # Shortest Path
        print("\n1. Shortest Path (Alice to Henry)")
        print("-" * 40)
        path = pathfinder.shortest_path(
            "User", "id", "u1",
            "User", "id", "u8"
        )
        
        if path:
            node_names = [n.get('properties', {}).get('name', n.get('id')) for n in path['nodes']]
            print(f"  Path: {' -> '.join(node_names)}")
            print(f"  Length: {path['path_length']}")
        
        # All Shortest Paths
        print("\n2. All Shortest Paths (Alice to Eve)")
        print("-" * 40)
        all_paths = pathfinder.all_shortest_paths(
            "User", "id", "u1",
            "User", "id", "u5",
            limit=5
        )
        
        for i, p in enumerate(all_paths, 1):
            names = [n.get('properties', {}).get('name', n.get('id')) for n in p['nodes']]
            print(f"  Path {i}: {' -> '.join(names)}")
        
        # Reachable Nodes
        print("\n3. Reachable Nodes from Alice (within 2 hops)")
        print("-" * 40)
        reachable = pathfinder.get_reachable_nodes(
            "User", "id", "u1",
            relationship_type="KNOWS",
            max_depth=2
        )
        
        for r in reachable:
            print(f"  {r['name']}: distance {r['distance']}")
        
        # ============================================
        # Graph Traversal
        # ============================================
        print("\n" + "=" * 60)
        print("GRAPH TRAVERSAL")
        print("=" * 60)
        
        traversal = GraphTraversal(conn)
        
        # BFS
        print("\n1. Breadth-First Search from Alice")
        print("-" * 40)
        bfs_result = traversal.breadth_first_search(
            "User", "id", "u1",
            relationship_type="KNOWS",
            max_depth=3
        )
        print(f"  Visited: {[v.get('name') for v in bfs_result]}")
        
        # DFS
        print("\n2. Depth-First Search from Alice")
        print("-" * 40)
        dfs_result = traversal.depth_first_search(
            "User", "id", "u1",
            relationship_type="KNOWS",
            max_depth=3
        )
        print(f"  Visited: {[v.get('name') for v in dfs_result]}")
        
        # Neighbors
        print("\n3. Direct Neighbors of Charlie")
        print("-" * 40)
        neighbors = traversal.get_neighbors("User", "id", "u3")
        print(f"  Neighbors: {[n.get('name') for n in neighbors]}")
        
        # ============================================
        # Cleanup
        # ============================================
        print("\n" + "=" * 60)
        print("Cleaning up...")
        print("=" * 60)
        conn.execute("MATCH (n:User) DETACH DELETE n")
        print("Done.")


if __name__ == "__main__":
    main()
