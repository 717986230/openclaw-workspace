"""
Community Detection Algorithms

Louvain, label propagation, and connected components.
"""

from typing import List, Dict, Any, Optional
import logging

from ..database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


class CommunityDetector:
    """
    Community detection algorithms for graphs.
    """
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    def louvain(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        max_iterations: int = 10,
        intermediate_communities: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Detect communities using Louvain algorithm.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            max_iterations: Maximum iterations
            intermediate_communities: Include intermediate results
        
        Returns:
            List of nodes with community assignments
        """
        query = f"""
        CALL gds.louvain.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}',
            maxIterations: {max_iterations},
            includeIntermediateCommunities: {str(intermediate_communities).lower()}
        }})
        YIELD nodeId, communityId, intermediateCommunityIds
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               communityId,
               intermediateCommunityIds
        ORDER BY communityId
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Louvain algorithm failed: {e}")
            return []
    
    def louvain_write(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        community_property: str = "community",
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Run Louvain and write community IDs to nodes.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            community_property: Property name for community ID
            max_iterations: Maximum iterations
        
        Returns:
            Statistics about the operation
        """
        query = f"""
        CALL gds.louvain.write({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}',
            maxIterations: {max_iterations},
            writeProperty: '{community_property}'
        }})
        YIELD nodePropertiesWritten, communityCount, ranIterations, didConverge
        RETURN nodePropertiesWritten, communityCount, ranIterations, didConverge
        """
        
        try:
            result = self.connection.execute(query)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Louvain write failed: {e}")
            return {}
    
    def label_propagation(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        max_iterations: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect communities using Label Propagation algorithm.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            max_iterations: Maximum iterations
        
        Returns:
            List of nodes with community assignments
        """
        query = f"""
        CALL gds.labelPropagation.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}',
            maxIterations: {max_iterations}
        }})
        YIELD nodeId, communityId
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               communityId
        ORDER BY communityId
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Label Propagation failed: {e}")
            return []
    
    def connected_components(
        self,
        label: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find connected components in the graph.
        
        Args:
            label: Node label
            relationship_type: Relationship type
        
        Returns:
            List of nodes with component assignments
        """
        query = f"""
        CALL gds.wcc.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, componentId
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               componentId
        ORDER BY componentId
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Connected components failed: {e}")
            return []
    
    def strongly_connected_components(
        self,
        label: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find strongly connected components.
        
        Args:
            label: Node label
            relationship_type: Relationship type
        
        Returns:
            List of nodes with SCC assignments
        """
        query = f"""
        CALL gds.alpha.scc.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, componentId
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               componentId
        ORDER BY componentId
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Strongly connected components failed: {e}")
            return []
    
    def triangle_count(
        self,
        label: str,
        relationship_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Count triangles for each node.
        
        Args:
            label: Node label
            relationship_type: Relationship type
        
        Returns:
            List of nodes with triangle counts
        """
        query = f"""
        CALL gds.triangleCount.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, triangleCount
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               triangleCount
        ORDER BY triangleCount DESC
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Triangle count failed: {e}")
            return []
    
    def local_clustering_coefficient(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate local clustering coefficient for nodes.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            limit: Maximum results
        
        Returns:
            List of nodes with clustering coefficients
        """
        query = f"""
        CALL gds.localClusteringCoefficient.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}'
        }})
        YIELD nodeId, localClusteringCoefficient
        RETURN gds.util.asNode(nodeId).id as id,
               gds.util.asNode(nodeId).name as name,
               localClusteringCoefficient
        ORDER BY localClusteringCoefficient DESC
        LIMIT {limit}
        """
        
        try:
            return self.connection.execute(query)
        except Exception as e:
            logger.error(f"Local clustering coefficient failed: {e}")
            return []
    
    def get_community_members(
        self,
        label: str,
        community_property: str,
        community_id: Any
    ) -> List[Dict[str, Any]]:
        """
        Get all members of a specific community.
        
        Args:
            label: Node label
            community_property: Property containing community ID
            community_id: Community ID to match
        
        Returns:
            List of nodes in the community
        """
        query = f"""
        MATCH (n:{label})
        WHERE n.{community_property} = $community_id
        RETURN n
        """
        
        result = self.connection.execute(query, {"community_id": community_id})
        return [r["n"] for r in result]
    
    def get_community_statistics(
        self,
        label: str,
        community_property: str
    ) -> List[Dict[str, Any]]:
        """
        Get statistics about each community.
        
        Args:
            label: Node label
            community_property: Property containing community ID
        
        Returns:
            List of community statistics
        """
        query = f"""
        MATCH (n:{label})
        WITH n.{community_property} as community, count(n) as size
        RETURN community, size
        ORDER BY size DESC
        """
        
        return self.connection.execute(query)
    
    def modularity_optimization(
        self,
        label: str,
        relationship_type: Optional[str] = None,
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Optimize modularity for community detection.
        
        Args:
            label: Node label
            relationship_type: Relationship type
            max_iterations: Maximum iterations
        
        Returns:
            Modularity statistics
        """
        query = f"""
        CALL gds.louvain.stats({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type or "ALL"}',
            maxIterations: {max_iterations}
        }})
        YIELD communityCount, modularity, ranIterations, didConverge
        RETURN communityCount, modularity, ranIterations, didConverge
        """
        
        try:
            result = self.connection.execute(query)
            return result[0] if result else {}
        except Exception as e:
            logger.error(f"Modularity optimization failed: {e}")
            return {}
