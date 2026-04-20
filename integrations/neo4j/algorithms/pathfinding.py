"""
Path Finding Algorithms

Dijkstra, A*, shortest paths, and related algorithms.
"""

from typing import List, Dict, Any, Optional, Tuple
import logging

from ..database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


class PathFinder:
    """
    Path finding algorithms for graphs.
    """
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    def shortest_path(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10
    ) -> Optional[Dict[str, Any]]:
        """
        Find shortest path between two nodes.
        
        Args:
            from_label: Source node label
            from_key: Source node key property
            from_value: Source node key value
            to_label: Target node label
            to_key: Target node key property
            to_value: Target node key value
            relationship_type: Relationship type filter
            max_depth: Maximum path length
        
        Returns:
            Path information or None
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = shortestPath(
            (a:{from_label} {{{from_key}: $from_value}})
            -[*{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        WHERE length(path) <= {max_depth}
        RETURN 
            [node in nodes(path) | {{id: node.id, labels: labels(node), properties: properties(node)}}] as nodes,
            [rel in relationships(path) | {{type: type(rel), properties: properties(rel)}}] as relationships,
            length(path) as path_length
        """
        
        result = self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
        
        if result:
            return result[0]
        return None
    
    def all_shortest_paths(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find all shortest paths between two nodes.
        
        Args:
            from_label: Source node label
            from_key: Source node key property
            from_value: Source node key value
            to_label: Target node label
            to_key: Target node key property
            to_value: Target node key value
            relationship_type: Relationship type filter
            max_depth: Maximum path length
            limit: Maximum number of paths
        
        Returns:
            List of path information
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = allShortestPaths(
            (a:{from_label} {{{from_key}: $from_value}})
            -[*{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        WHERE length(path) <= {max_depth}
        RETURN 
            [node in nodes(path) | {{id: node.id, labels: labels(node)}}] as nodes,
            [rel in relationships(path) | {{type: type(rel)}}] as relationships,
            length(path) as path_length
        LIMIT {limit}
        """
        
        return self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
    
    def dijkstra(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        weight_property: str = "weight",
        relationship_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find shortest path using Dijkstra's algorithm with weights.
        
        Args:
            from_label: Source node label
            from_key: Source node key property
            from_value: Source node key value
            to_label: Target node label
            to_key: Target node key property
            to_value: Target node key value
            weight_property: Property to use as weight
            relationship_type: Relationship type filter
        
        Returns:
            Path with total cost or None
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH (source:{from_label} {{{from_key}: $from_value}}), (target:{to_label} {{{to_key}: $to_value}})
        CALL gds.shortestPath.dijkstra.stream({{
            sourceNode: source,
            targetNode: target,
            relationshipWeightProperty: '{weight_property}',
            relationshipTypes: ['{relationship_type or "ALL"}']
        }})
        YIELD index, node, totalCost
        RETURN 
            gds.util.asNode(node).id as node_id,
            totalCost
        ORDER BY index
        """
        
        try:
            result = self.connection.execute(query, {
                "from_value": from_value,
                "to_value": to_value
            })
            
            if result:
                nodes = [r["node_id"] for r in result]
                total_cost = result[-1]["totalCost"] if result else 0
                return {
                    "nodes": nodes,
                    "total_cost": total_cost
                }
        except Exception as e:
            logger.warning(f"Dijkstra via GDS failed: {e}, using Cypher fallback")
            return self._dijkstra_cypher(
                from_label, from_key, from_value,
                to_label, to_key, to_value,
                weight_property, relationship_type
            )
        
        return None
    
    def _dijkstra_cypher(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        weight_property: str,
        relationship_type: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Cypher-based Dijkstra fallback"""
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = (
            (a:{from_label} {{{from_key}: $from_value}})
            -[r{rel_pattern}*]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        WITH path, reduce(cost = 0.0, rel in relationships(path) | cost + coalesce(rel.{weight_property}, 1.0)) as total_cost
        ORDER BY total_cost ASC
        LIMIT 1
        RETURN 
            [node in nodes(path) | node.id] as nodes,
            total_cost
        """
        
        result = self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
        
        if result:
            return result[0]
        return None
    
    def a_star(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        weight_property: str = "weight",
        relationship_type: Optional[str] = None,
        latitude_property: str = "latitude",
        longitude_property: str = "longitude"
    ) -> Optional[Dict[str, Any]]:
        """
        Find path using A* algorithm (requires geographic coordinates).
        
        Args:
            from_label: Source node label
            from_key: Source node key property
            from_value: Source node key value
            to_label: Target node label
            to_key: Target node key property
            to_value: Target node key value
            weight_property: Property to use as weight
            relationship_type: Relationship type filter
            latitude_property: Latitude property name
            longitude_property: Longitude property name
        
        Returns:
            Path with total cost or None
        """
        query = f"""
        MATCH (source:{from_label} {{{from_key}: $from_value}}), (target:{to_label} {{{to_key}: $to_value}})
        CALL gds.shortestPath.astar.stream({{
            sourceNode: source,
            targetNode: target,
            relationshipWeightProperty: '{weight_property}',
            relationshipTypes: ['{relationship_type or "ALL"}'],
            latitudeProperty: '{latitude_property}',
            longitudeProperty: '{longitude_property}'
        }})
        YIELD index, node, totalCost
        RETURN 
            gds.util.asNode(node).id as node_id,
            totalCost
        ORDER BY index
        """
        
        try:
            result = self.connection.execute(query, {
                "from_value": from_value,
                "to_value": to_value
            })
            
            if result:
                nodes = [r["node_id"] for r in result]
                total_cost = result[-1]["totalCost"] if result else 0
                return {
                    "nodes": nodes,
                    "total_cost": total_cost
                }
        except Exception as e:
            logger.error(f"A* algorithm failed: {e}")
        
        return None
    
    def path_exists(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 10
    ) -> bool:
        """
        Check if a path exists between two nodes.
        
        Returns:
            True if path exists
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = (
            (a:{from_label} {{{from_key}: $from_value}})
            -[*1..{max_depth}{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        RETURN count(path) > 0 as exists
        """
        
        result = self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
        
        return result[0]["exists"] if result else False
    
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
    ) -> List[Dict[str, Any]]:
        """
        Get all paths between two nodes up to a maximum depth.
        
        Returns:
            List of path information
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH path = (
            (a:{from_label} {{{from_key}: $from_value}})
            -[*1..{max_depth}{rel_pattern}]-
            (b:{to_label} {{{to_key}: $to_value}})
        )
        RETURN 
            [node in nodes(path) | node.id] as nodes,
            [rel in relationships(path) | type(rel)] as relationship_types,
            length(path) as path_length
        ORDER BY path_length
        LIMIT {limit}
        """
        
        return self.connection.execute(query, {
            "from_value": from_value,
            "to_value": to_value
        })
    
    def get_reachable_nodes(
        self,
        label: str,
        key: str,
        value: Any,
        relationship_type: Optional[str] = None,
        max_depth: int = 3,
        direction: str = "outgoing",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get all nodes reachable from a starting node.
        
        Args:
            label: Start node label
            key: Start node key property
            value: Start node key value
            relationship_type: Relationship type filter
            max_depth: Maximum traversal depth
            direction: Direction - 'outgoing', 'incoming', or 'both'
            limit: Maximum results
        
        Returns:
            List of reachable nodes with distances
        """
        if direction == "outgoing":
            rel_pattern = f"-[:{relationship_type}]->" if relationship_type else "->"
        elif direction == "incoming":
            rel_pattern = f"<-[:{relationship_type}]-" if relationship_type else "<-"
        else:
            rel_pattern = f"-[:{relationship_type}]-" if relationship_type else "-"
        
        query = f"""
        MATCH path = (start:{label} {{{key}: $value}}){rel_pattern}*1..{max_depth}(node)
        WITH DISTINCT node, min(length(path)) as distance
        RETURN node.id as id, node.name as name, distance
        ORDER BY distance
        LIMIT {limit}
        """
        
        return self.connection.execute(query, {"value": value})
