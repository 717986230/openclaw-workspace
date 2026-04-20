"""
Neo4j Connection Manager

Manages connections to Neo4j database with connection pooling,
retry logic, and transaction handling.
"""

import logging
import time
from typing import Optional, List, Dict, Any, Callable
from contextlib import contextmanager
from functools import wraps

from neo4j import GraphDatabase, Driver, Session, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError, TransientError

from .config import Neo4jConfig, get_config

logger = logging.getLogger(__name__)


def retry_on_transient(max_attempts: int = 3, backoff_factor: float = 2.0):
    """
    Decorator for retrying on transient errors.
    
    Args:
        max_attempts: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = backoff_factor ** attempt
                        logger.warning(
                            f"Transient error on attempt {attempt + 1}/{max_attempts}. "
                            f"Retrying in {wait_time}s. Error: {e}"
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retry attempts reached for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


class Neo4jConnection:
    """
    Neo4j database connection manager.
    
    Provides connection pooling, transaction management, and query execution.
    """
    
    def __init__(self, config: Optional[Neo4jConfig] = None):
        """
        Initialize connection manager.
        
        Args:
            config: Neo4j configuration. Uses default if not provided.
        """
        self.config = config or get_config()
        self._driver: Optional[Driver] = None
        self._is_connected = False
        
    def connect(self) -> None:
        """Establish connection to Neo4j database"""
        if self._is_connected:
            logger.warning("Already connected to Neo4j")
            return
        
        try:
            self._driver = GraphDatabase.driver(
                self.config.uri,
                auth=(self.config.user, self.config.password),
                **self.config.to_driver_config()
            )
            
            # Verify connection
            self._driver.verify_connectivity()
            self._is_connected = True
            logger.info(f"Connected to Neo4j at {self.config.uri}")
            
        except AuthError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable: {e}")
            raise
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close connection to Neo4j database"""
        if self._driver:
            self._driver.close()
            self._driver = None
            self._is_connected = False
            logger.info("Disconnected from Neo4j")
    
    @property
    def driver(self) -> Driver:
        """Get the driver instance"""
        if not self._driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        return self._driver
    
    @contextmanager
    def session(self, database: Optional[str] = None):
        """
        Context manager for database session.
        
        Args:
            database: Database name. Uses config default if not provided.
        
        Yields:
            Neo4j session
        """
        database = database or self.config.database
        session = self.driver.session(database=database)
        try:
            yield session
        finally:
            session.close()
    
    @contextmanager
    def transaction(self, database: Optional[str] = None):
        """
        Context manager for database transaction.
        
        Args:
            database: Database name
        
        Yields:
            Neo4j transaction
        """
        with self.session(database) as session:
            tx = session.begin_transaction()
            try:
                yield tx
                tx.commit()
            except Exception:
                tx.rollback()
                raise
    
    @retry_on_transient()
    def execute(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            database: Database name
        
        Returns:
            List of result records
        """
        parameters = parameters or {}
        
        with self.session(database) as session:
            result = session.run(query, parameters)
            records = [record.data() for record in result]
            return records
    
    def execute_batch(
        self,
        queries: List[str],
        parameters_list: Optional[List[Dict[str, Any]]] = None,
        database: Optional[str] = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Execute multiple queries in a single transaction.
        
        Args:
            queries: List of Cypher query strings
            parameters_list: List of parameter dicts for each query
            database: Database name
        
        Returns:
            List of results for each query
        """
        parameters_list = parameters_list or [{} for _ in queries]
        
        with self.transaction(database) as tx:
            results = []
            for query, params in zip(queries, parameters_list):
                result = tx.run(query, params)
                results.append([record.data() for record in result])
            return results
    
    def create_node(
        self,
        label: str,
        properties: Dict[str, Any],
        unique_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a node in the graph.
        
        Args:
            label: Node label
            properties: Node properties
            unique_key: Property name for uniqueness constraint
        
        Returns:
            Created node properties
        """
        if unique_key:
            query = f"""
            MERGE (n:{label} {{{unique_key}: $value}})
            SET n += $properties
            RETURN n
            """
            params = {
                "value": properties.get(unique_key),
                "properties": properties
            }
        else:
            query = f"CREATE (n:{label} $properties) RETURN n"
            params = {"properties": properties}
        
        result = self.execute(query, params)
        return result[0]["n"] if result else {}
    
    def create_relationship(
        self,
        from_label: str,
        from_key: str,
        from_value: Any,
        to_label: str,
        to_key: str,
        to_value: Any,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a relationship between two nodes.
        
        Args:
            from_label: Source node label
            from_key: Source node property key
            from_value: Source node property value
            to_label: Target node label
            to_key: Target node property key
            to_value: Target node property value
            relationship_type: Relationship type
            properties: Relationship properties
        
        Returns:
            Created relationship properties
        """
        query = f"""
        MATCH (a:{from_label} {{{from_key}: $from_value}})
        MATCH (b:{to_label} {{{to_key}: $to_value}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r += $properties
        RETURN r
        """
        
        result = self.execute(query, {
            "from_value": from_value,
            "to_value": to_value,
            "properties": properties or {}
        })
        
        return result[0]["r"] if result else {}
    
    def find_node(
        self,
        label: str,
        properties: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a node by label and properties.
        
        Args:
            label: Node label
            properties: Node properties to match
        
        Returns:
            Node properties or None if not found
        """
        conditions = " AND ".join([f"n.{k} = ${k}" for k in properties.keys()])
        query = f"MATCH (n:{label}) WHERE {conditions} RETURN n"
        
        result = self.execute(query, properties)
        return result[0]["n"] if result else None
    
    def delete_node(
        self,
        label: str,
        key: str,
        value: Any,
        force: bool = False
    ) -> bool:
        """
        Delete a node from the graph.
        
        Args:
            label: Node label
            key: Property key
            value: Property value
            force: If True, also delete connected relationships
        
        Returns:
            True if node was deleted
        """
        if force:
            query = f"""
            MATCH (n:{label} {{{key}: $value}})
            DETACH DELETE n
            RETURN count(n) as deleted
            """
        else:
            query = f"""
            MATCH (n:{label} {{{key}: $value}})
            DELETE n
            RETURN count(n) as deleted
            """
        
        result = self.execute(query, {"value": value})
        return result[0]["deleted"] > 0 if result else False
    
    def health_check(self) -> bool:
        """Check if connection is healthy"""
        try:
            self.execute("RETURN 1 as test")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def __repr__(self) -> str:
        return f"Neo4jConnection(connected={self._is_connected}, config={self.config})"


# Convenience function for creating a connection
def create_connection(config_path: Optional[str] = None) -> Neo4jConnection:
    """
    Create a Neo4j connection.
    
    Args:
        config_path: Optional path to config file
    
    Returns:
        Neo4jConnection instance
    """
    config = get_config(config_path) if config_path else None
    return Neo4jConnection(config)
