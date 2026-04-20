"""
Graph Traversal Algorithms

BFS, DFS, and custom traversal strategies.
"""

from typing import List, Dict, Any, Optional, Set, Callable, Iterator
from collections import deque
import logging

from ..database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


class GraphTraversal:
    """
    Graph traversal algorithms for Neo4j.
    """
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    def breadth_first_search(
        self,
        start_label: str,
        start_key: str,
        start_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10,
        direction: str = "outgoing"
    ) -> List[Dict[str, Any]]:
        """
        Breadth-First Search traversal.
        
        Args:
            start_label: Start node label
            start_key: Start node key property
            start_value: Start node key value
            relationship_type: Relationship type to traverse (optional)
            max_depth: Maximum traversal depth
            direction: Direction - 'outgoing', 'incoming', or 'both'
        
        Returns:
            List of visited nodes in BFS order
        """
        if direction == "outgoing":
            rel_pattern = f"-[:{relationship_type}]->" if relationship_type else "->"
        elif direction == "incoming":
            rel_pattern = f"<-[:{relationship_type}]-" if relationship_type else "<-"
        else:
            rel_pattern = f"-[:{relationship_type}]-" if relationship_type else "-"
        
        # Use Cypher for BFS
        query = f"""
        MATCH path = (start:{start_label} {{{start_key}: $start_value}}){rel_pattern}*1..{max_depth}(node)
        RETURN DISTINCT node, length(path) as depth
        ORDER BY depth, node.id
        """
        
        result = self.connection.execute(query, {"start_value": start_value})
        return [r["node"] for r in result]
    
    def depth_first_search(
        self,
        start_label: str,
        start_key: str,
        start_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10,
        direction: str = "outgoing"
    ) -> List[Dict[str, Any]]:
        """
        Depth-First Search traversal.
        
        Args:
            start_label: Start node label
            start_key: Start node key property
            start_value: Start node key value
            relationship_type: Relationship type to traverse
            max_depth: Maximum traversal depth
            direction: Direction of traversal
        
        Returns:
            List of visited nodes in DFS order
        """
        if direction == "outgoing":
            rel_pattern = f"-[:{relationship_type}]->" if relationship_type else "->"
        elif direction == "incoming":
            rel_pattern = f"<-[:{relationship_type}]-" if relationship_type else "<-"
        else:
            rel_pattern = f"-[:{relationship_type}]-" if relationship_type else "-"
        
        query = f"""
        MATCH path = (start:{start_label} {{{start_key}: $start_value}}){rel_pattern}*1..{max_depth}(node)
        WITH DISTINCT node, path
        ORDER BY size(path) DESC, node.id
        RETURN node
        """
        
        result = self.connection.execute(query, {"start_value": start_value})
        return [r["node"] for r in result]
    
    def get_neighbors(
        self,
        label: str,
        key: str,
        value: Any,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get direct neighbors of a node.
        
        Args:
            label: Node label
            key: Node key property
            value: Node key value
            relationship_type: Relationship type filter
            direction: Direction filter
            limit: Maximum neighbors to return
        
        Returns:
            List of neighbor nodes
        """
        if direction == "outgoing":
            rel_pattern = f"-[:{relationship_type}]->" if relationship_type else "->"
        elif direction == "incoming":
            rel_pattern = f"<-[:{relationship_type}]-" if relationship_type else "<-"
        else:
            rel_pattern = f"-[:{relationship_type}]-" if relationship_type else "-"
        
        query = f"""
        MATCH (n:{label} {{{key}: $value}}){rel_pattern}(neighbor)
        RETURN DISTINCT neighbor
        LIMIT {limit}
        """
        
        result = self.connection.execute(query, {"value": value})
        return [r["neighbor"] for r in result]
    
    def get_path(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get a path between two nodes.
        
        Returns:
            List of nodes in the path, or None if no path exists
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = shortestPath(
            (a:{from_label} {{{from_key}: $from_value}})
            -[*{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        WHERE length(path) <= {max_depth}
        RETURN [node in nodes(path) | node] as path_nodes
        """
        
        result = self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
        
        if result:
            return result[0].get("path_nodes", [])
        return None
    
    def get_all_paths(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 5,
        limit: int = 10
    ) -> List[List[Dict[str, Any]]]:
        """
        Get all paths between two nodes.
        
        Returns:
            List of paths (each path is a list of nodes)
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = (
            (a:{from_label} {{{from_key}: $from_value}})
            -[*1..{max_depth}{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        RETURN [node in nodes(path) | node] as path_nodes
        ORDER BY length(path)
        LIMIT {limit}
        """
        
        result = self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
        
        return [r.get("path_nodes", []) for r in result]
    
    def walk_with_callback(
        self,
        start_label: str,
        start_key: str,
        start_value: Any,
        callback: Callable[[Dict[str, Any], int], bool],
        relationship_type: Optional[str] = None,
        max_depth: int = 10,
        direction: str = "outgoing"
    ) -> int:
        """
        Walk the graph with a callback function.
        
        Args:
            start_label: Start node label
            start_key: Start node key property
            start_value: Start node key value
            callback: Function(node, depth) -> should_continue
            relationship_type: Relationship type to traverse
            max_depth: Maximum traversal depth
            direction: Direction of traversal
        
        Returns:
            Number of nodes visited
        """
        visited: Set[Any] = set()
        queue = deque([(start_label, start_key, start_value, 0)])
        count = 0
        
        while queue:
            label, key, value, depth = queue.popleft()
            
            if depth > max_depth:
                continue
            
            # Get the node
            node = self.connection.find_node(label, {key: value})
            if not node:
                continue
            
            # Get unique identifier
            node_id = node.get("id") or node.get(key)
            if node_id in visited:
                continue
            
            visited.add(node_id)
            count += 1
            
            # Call callback
            if not callback(node, depth):
                break
            
            # Get neighbors
            neighbors = self.get_neighbors(label, key, value, relationship_type, direction)
            
            for neighbor in neighbors:
                neighbor_id = neighbor.get("id") or neighbor.get(key)
                if neighbor_id not in visited:
                    queue.append((label, key, neighbor_id, depth + 1))
        
        return count
