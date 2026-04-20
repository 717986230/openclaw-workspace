"""
Centrality Algorithms

PageRank, betweenness, closeness, and degree centrality measures.
"""

from typing import List, Dict, Any, Optional
import logging

from ..database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


class CentralityAnalyzer:
    """
    Centrality analysis algorithms for graphs.
    """
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    def degree_centrality(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate degree centrality for nodes.
        
        Args:
            label: Node label
            relationship_type: Relationship type filter
            direction: 'incoming', 'outgoing', or 'both'
            limit: Maximum results
        
        Returns:
            List of nodes with degree scores
        """
        if direction == "incoming":
            rel_pattern = f"<-[:{relationship_type}]-" if relationship_type else "<-"
        elif direction == "outgoing":
            rel_pattern = f"-[:{relationship_type}]->" if relationship_type else "->"
        else:
            rel_pattern = f"-[:{relationship_type}]-" if relationship_type else "-"
        
        query = f"""
        MATCH (n:{label})
        OPTIONAL MATCH (n){rel_pattern}(neighbor)
        WITH n, count(neighbor) as degree
        ORDER BY degree DESC
        LIMIT {limit}
        RETURN n.id as id, n.name as name, degree
        """
        
        return self.connection.execute(query)
    
    def weighted_degree_centrality(
        self,
        label: str,
        relationship_type: str,
        weight_property: str = "weight",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate weighted degree centrality.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            weight_property: Property to use as weight
            limit: Maximum results
        
        Returns:
            List of nodes with weighted degree scores
        """
        query = f"""
        MATCH (n:{label})-[r:{relationship_type}]-(neighbor)
        WITH n, sum(coalesce(r.{weight_property}, 1.0)) as weighted_degree
        ORDER BY weighted_degree DESC
        LIMIT {limit}
        RETURN n.id as id, n.name as name, weighted_degree
        """
        
        return self.connection.execute(query)
    
    def pagerank(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        iterations: int = 20,
        damping_factor: float = 0.85,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate PageRank scores using GDS or custom implementation.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            iterations: Number of iterations
            damping_factor: Damping factor (default 0.85)
            limit: Maximum results
        
        Returns:
            List of nodes with PageRank scores
        """
        # Try using GDS library if available
        try:
            query = f"""
            CALL gds.pageRank.stream({{
                nodeProjection: '{label}',
                relationshipProjection: '{relationship_type or "ALL"}',
                maxIterations: {iterations},
                dampingFactor: {damping_factor}
            }})
            YIELD nodeId, score
            RETURN gds.util.asNode(nodeId).id as id, 
                   gds.util.asNode(nodeId).name as name, 
                   score
            ORDER BY score DESC
            LIMIT {limit}
            """
            
            return self.connection.execute(query)
            
        except Exception:
            # Fallback to custom implementation
            logger.info("GDS not available, using custom PageRank")
            return self._custom_pagerank(label, relationship_type, iterations, damping_factor, limit)
    
    def _custom_pagerank(
        self,
        label: str,
        relationship_type: Optional[str],
        iterations: int,
        damping_factor: float,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Custom PageRank implementation"""
        # Get all nodes and their outgoing relationships
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        query = f"""
        MATCH (n:{label})
        OPTIONAL MATCH (n)-[{rel_pattern}]->(out)
        WITH n, count(out) as out_degree, collect(out) as outgoing
        RETURN n.id as id, n.name as name, out_degree, 
               [node in outgoing | node.id] as outgoing_ids
        """
        
        nodes_data = self.connection.execute(query)
        
        # Initialize scores
        nodes = {n["id"]: n for n in nodes_data if n["id"]}
        scores = {nid: 1.0 / len(nodes) for nid in nodes.keys()}
        
        # Iterate
        for _ in range(iterations):
            new_scores = {}
            for nid in nodes.keys():
                new_scores[nid] = (1 - damping_factor) / len(nodes)
            
            # Distribute scores
            for nid, node_data in nodes.items():
                out_degree = node_data["out_degree"]
                if out_degree > 0:
                    contribution = damping_factor * scores[nid] / out_degree
                    for out_id in node_data["outgoing_ids"]:
                        if out_id in new_scores:
                            new_scores[out_id] += contribution
            
            scores = new_scores
        
        # Sort and return
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            {
                "id": nid,
                "name": nodes.get(nid, {}).get("name"),
                "score": score
            }
            for nid, score in sorted_scores
        ]
    
    def betweenness_centrality(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate betweenness centrality using GDS.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            limit: Maximum results
        
        Returns:
            List of nodes with betweenness scores
        """
        query = f"""
        CALL gds.betweenness.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               score
        ORDER BY score DESC
        LIMIT {limit}
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.warning(f"Betweenness centrality requires GDS: {e}")
            return []
    
    def closeness_centrality(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate closeness centrality using GDS.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            limit: Maximum results
        
        Returns:
            List of nodes with closeness scores
        """
        query = f"""
        CALL gds.closeness.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               score
        ORDER BY score DESC
        LIMIT {limit}
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.warning(f"Closeness centrality requires GDS: {e}")
            return []
    
    def eigenvector_centrality(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        iterations: int = 20,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate eigenvector centrality using GDS.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            iterations: Number of iterations
            limit: Maximum results
        
        Returns:
            List of nodes with eigenvector scores
        """
        query = f"""
        CALL gds.eigenvector.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}',
            maxIterations: {iterations}
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               score
        ORDER BY score DESC
        LIMIT {limit}
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.warning(f"Eigenvector centrality requires GDS: {e}")
            return []
    
    def harmonic_centrality(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate harmonic centrality using GDS.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            limit: Maximum results
        
        Returns:
            List of nodes with harmonic scores
        """
        query = f"""
        CALL gds.alpha.closeness.harmonic.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               score
        ORDER BY score DESC
        LIMIT {limit}
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.warning(f"Harmonic centrality requires GDS: {e}")
            return []
