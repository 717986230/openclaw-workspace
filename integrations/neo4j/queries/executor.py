"""
Query Executor

High-level query execution with caching, batch processing, and streaming.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Callable, Iterator
from functools import lru_cache
import json

from ..database.connection import Neo4jConnection

logger = logging.getLogger(__name__)


class QueryExecutor:
    """
    Advanced query executor with caching and optimization.
    """
    
    def __init__(self, connection: Neo4jConnection):
        """
        Initialize executor.
        
        Args:
            connection: Neo4j connection instance
        """
        self.connection = connection
        self._query_cache: Dict[str, Any] = {}
        self._stats = {
            "queries_executed": 0,
            "cache_hits": 0,
            "total_time": 0.0,
        }
    
    def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query with timing and stats.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            database: Database name
        
        Returns:
            Query results
        """
        start_time = time.time()
        
        try:
            result = self.connection.execute(query, parameters, database)
            
            self._stats["queries_executed"] += 1
            self._stats["total_time"] += time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}\nQuery: {query}\nParams: {parameters}")
            raise
    
    def execute_batch(
        self,
        queries: List[str],
        parameters_list: Optional[List[Dict[str, Any]]] = None,
        database: Optional[str] = None,
        batch_size: int = 100
    ) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple queries in batches.
        
        Args:
            queries: List of queries
            parameters_list: Parameters for each query
            database: Database name
            batch_size: Number of queries per batch
        
        Returns:
            Results for each query
        """
        parameters_list = parameters_list or [{} for _ in queries]
        all_results = []
        
        for i in range(0, len(queries), batch_size):
            batch_queries = queries[i:i + batch_size]
            batch_params = parameters_list[i:i + batch_size]
            
            results = self.connection.execute_batch(batch_queries, batch_params, database)
            all_results.extend(results)
        
        return all_results
    
    def execute_unwind(
        self,
        query_template: str,
        data_list: List[Dict[str, Any]],
        batch_size: int = 1000,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query with UNWIND for bulk operations.
        
        Args:
            query_template: Query template with $data placeholder
            data_list: List of data items
            batch_size: Batch size for processing
            database: Database name
        
        Returns:
            Combined results
        """
        all_results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i + batch_size]
            query = query_template.replace("$data", json.dumps(batch))
            
            results = self.execute(query, {}, database)
            all_results.extend(results)
        
        return all_results
    
    def stream(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
        chunk_size: int = 100
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Stream large result sets in chunks.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            database: Database name
            chunk_size: Number of records per chunk
        
        Yields:
            Chunks of results
        """
        with self.connection.session(database) as session:
            result = session.run(query, parameters or {})
            
            chunk = []
            for record in result:
                chunk.append(record.data())
                
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            
            if chunk:
                yield chunk
    
    def execute_cached(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        cache_key: Optional[str] = None,
        ttl: int = 3600
    ) -> List[Dict[str, Any]]:
        """
        Execute query with caching.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            cache_key: Custom cache key (default: query hash)
            ttl: Time to live in seconds
        
        Returns:
            Cached or fresh results
        """
        import hashlib
        
        if not cache_key:
            cache_key = hashlib.md5(f"{query}:{json.dumps(parameters or {})}".encode()).hexdigest()
        
        # Check cache (simple implementation)
        if cache_key in self._query_cache:
            cached_time, cached_result = self._query_cache[cache_key]
            if time.time() - cached_time < ttl:
                self._stats["cache_hits"] += 1
                return cached_result
        
        # Execute and cache
        result = self.execute(query, parameters)
        self._query_cache[cache_key] = (time.time(), result)
        
        return result
    
    def execute_with_retry(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        backoff: float = 2.0,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute query with retry logic.
        
        Args:
            query: Cypher query
            parameters: Query parameters
            max_retries: Maximum retry attempts
            backoff: Exponential backoff multiplier
            database: Database name
        
        Returns:
            Query results
        """
        from neo4j.exceptions import TransientError
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return self.execute(query, parameters, database)
            except TransientError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = backoff ** attempt
                    logger.warning(f"Transient error, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
        
        raise last_exception
    
    def explain(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get query execution plan.
        
        Args:
            query: Cypher query
            parameters: Query parameters
        
        Returns:
            Execution plan information
        """
        explain_query = f"EXPLAIN {query}"
        result = self.execute(explain_query, parameters)
        return result
    
    def profile(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Profile query execution.
        
        Args:
            query: Cypher query
            parameters: Query parameters
        
        Returns:
            Profiling information
        """
        profile_query = f"PROFILE {query}"
        result = self.execute(profile_query, parameters)
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return self._stats.copy()
    
    def clear_cache(self) -> None:
        """Clear query cache"""
        self._query_cache.clear()
        logger.info("Query cache cleared")


class TransactionalExecutor:
    """Executor with transaction support"""
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
        self._operations: List[tuple] = []
    
    def add_operation(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Add an operation to the transaction"""
        self._operations.append((query, parameters or {}))
    
    def execute_all(self, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Execute all operations in a transaction"""
        if not self._operations:
            return []
        
        queries = [op[0] for op in self._operations]
        params = [op[1] for op in self._operations]
        
        results = self.connection.execute_batch(queries, params, database)
        
        self._operations.clear()
        return results
    
    def rollback(self) -> None:
        """Clear pending operations"""
        self._operations.clear()


class BulkLoader:
    """Optimized bulk data loading"""
    
    def __init__(self, connection: Neo4jConnection):
        self.connection = connection
    
    def load_nodes(
        self,
        label: str,
        nodes: List[Dict[str, Any]],
        unique_key: Optional[str] = None,
        batch_size: int = 1000
    ) -> int:
        """
        Bulk load nodes.
        
        Args:
            label: Node label
            nodes: List of node properties
            unique_key: Optional unique key for merging
            batch_size: Batch size
        
        Returns:
            Number of nodes created
        """
        if unique_key:
            query = f"""
            UNWIND $nodes AS node_data
            MERGE (n:{label} {{{unique_key}: node_data.{unique_key}}})
            SET n += node_data
            RETURN count(n) as created
            """
        else:
            query = f"""
            UNWIND $nodes AS node_data
            CREATE (n:{label})
            SET n = node_data
            RETURN count(n) as created
            """
        
        total_created = 0
        
        for i in range(0, len(nodes), batch_size):
            batch = nodes[i:i + batch_size]
            results = self.connection.execute(query, {"nodes": batch})
            
            if results:
                total_created += results[0].get("created", 0)
        
        return total_created
    
    def load_relationships(
        self,
        from_label: str,
        from_key: str,
        to_label: str,
        to_key: str,
        rel_type: str,
        relationships: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> int:
        """
        Bulk load relationships.
        
        Args:
            from_label: Source node label
            from_key: Source node key property
            to_label: Target node label
            to_key: Target node key property
            rel_type: Relationship type
            relationships: List of relationship data
            batch_size: Batch size
        
        Returns:
            Number of relationships created
        """
        query = f"""
        UNWIND $rels AS rel_data
        MATCH (a:{from_label} {{{from_key}: rel_data.from_id}})
        MATCH (b:{to_label} {{{to_key}: rel_data.to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += rel_data.properties
        RETURN count(r) as created
        """
        
        total_created = 0
        
        for i in range(0, len(relationships), batch_size):
            batch = relationships[i:i + batch_size]
            results = self.connection.execute(query, {"rels": batch})
            
            if results:
                total_created += results[0].get("created", 0)
        
        return total_created
