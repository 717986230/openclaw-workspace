"""
Neo4j Connection Pool

Advanced connection pooling with health checks and automatic recovery.
"""

import logging
import threading
import time
from typing import Optional, List, Dict, Any
from queue import Queue, Empty
from dataclasses import dataclass

from neo4j import Driver

from .connection import Neo4jConnection
from .config import Neo4jConfig

logger = logging.getLogger(__name__)


@dataclass
class PooledConnection:
    """Wrapper for a pooled connection"""
    connection: Neo4jConnection
    created_at: float
    last_used: float
    in_use: bool = False
    error_count: int = 0


class Neo4jConnectionPool:
    """
    Thread-safe connection pool for Neo4j.
    
    Features:
    - Pre-warming connections
    - Connection health checks
    - Automatic recovery
    - Timeout handling
    """
    
    def __init__(
        self,
        config: Optional[Neo4jConfig] = None,
        min_connections: int = 2,
        max_connections: int = 10,
        connection_timeout: int = 30,
        idle_timeout: int = 300,
        health_check_interval: int = 60
    ):
        """
        Initialize connection pool.
        
        Args:
            config: Neo4j configuration
            min_connections: Minimum number of connections to maintain
            max_connections: Maximum number of connections allowed
            connection_timeout: Timeout for acquiring a connection
            idle_timeout: Time before idle connections are closed
            health_check_interval: Interval between health checks
        """
        self.config = config or Neo4jConfig()
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.health_check_interval = health_check_interval
        
        self._pool: Queue[PooledConnection] = Queue()
        self._connections: Dict[int, PooledConnection] = {}
        self._lock = threading.Lock()
        self._initialized = False
        self._closed = False
        
    def initialize(self) -> None:
        """Initialize the pool with minimum connections"""
        with self._lock:
            if self._initialized:
                return
            
            logger.info(f"Initializing connection pool with {self.min_connections} connections")
            
            for _ in range(self.min_connections):
                conn = self._create_connection()
                if conn:
                    self._pool.put(conn)
            
            self._initialized = True
            
            # Start health check thread
            self._start_health_check()
    
    def _create_connection(self) -> Optional[PooledConnection]:
        """Create a new connection"""
        try:
            connection = Neo4jConnection(self.config)
            connection.connect()
            
            pooled_conn = PooledConnection(
                connection=connection,
                created_at=time.time(),
                last_used=time.time()
            )
            
            return pooled_conn
            
        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            return None
    
    def acquire(self, timeout: Optional[int] = None) -> Neo4jConnection:
        """
        Acquire a connection from the pool.
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Neo4jConnection instance
        
        Raises:
            RuntimeError: If pool is exhausted
        """
        timeout = timeout or self.connection_timeout
        
        if not self._initialized:
            self.initialize()
        
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            try:
                pooled_conn = self._pool.get(block=True, timeout=1)
                
                # Check if connection is still healthy
                if not pooled_conn.connection.health_check():
                    logger.warning("Acquired connection failed health check, creating new one")
                    pooled_conn = self._create_connection()
                    if not pooled_conn:
                        continue
                
                with self._lock:
                    pooled_conn.in_use = True
                    pooled_conn.last_used = time.time()
                
                return pooled_conn.connection
                
            except Empty:
                # Try to create a new connection if under max
                with self._lock:
                    if len(self._connections) < self.max_connections:
                        logger.info("Pool exhausted, creating new connection")
                        conn = self._create_connection()
                        if conn:
                            conn.in_use = True
                            return conn.connection
                
                continue
        
        raise RuntimeError(f"Failed to acquire connection within {timeout} seconds")
    
    def release(self, connection: Neo4jConnection) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            connection: Connection to release
        """
        with self._lock:
            for conn_id, pooled_conn in self._connections.items():
                if pooled_conn.connection == connection:
                    pooled_conn.in_use = False
                    pooled_conn.last_used = time.time()
                    self._pool.put(pooled_conn)
                    return
        
        # If not found in tracked connections, just close it
        logger.warning("Released connection not found in pool, closing")
        connection.disconnect()
    
    def _start_health_check(self) -> None:
        """Start background health check thread"""
        def health_check_loop():
            while not self._closed:
                time.sleep(self.health_check_interval)
                self._check_connections()
        
        thread = threading.Thread(target=health_check_loop, daemon=True)
        thread.start()
    
    def _check_connections(self) -> None:
        """Check health of pooled connections"""
        with self._lock:
            to_remove = []
            
            for conn_id, pooled_conn in self._connections.items():
                if pooled_conn.in_use:
                    continue
                
                # Check if connection is idle too long
                if time.time() - pooled_conn.last_used > self.idle_timeout:
                    if len(self._connections) > self.min_connections:
                        logger.info("Closing idle connection")
                        to_remove.append(conn_id)
                        continue
                
                # Health check
                if not pooled_conn.connection.health_check():
                    logger.warning("Connection failed health check, removing")
                    to_remove.append(conn_id)
            
            # Remove bad connections
            for conn_id in to_remove:
                pooled_conn = self._connections.pop(conn_id, None)
                if pooled_conn:
                    pooled_conn.connection.disconnect()
            
            # Ensure minimum connections
            while len(self._connections) < self.min_connections:
                conn = self._create_connection()
                if conn:
                    self._pool.put(conn)
    
    def close(self) -> None:
        """Close all connections in the pool"""
        with self._lock:
            self._closed = True
            
            for conn_id, pooled_conn in self._connections.items():
                try:
                    pooled_conn.connection.disconnect()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
            
            self._connections.clear()
            
            # Clear the queue
            while not self._pool.empty():
                try:
                    self._pool.get_nowait()
                except Empty:
                    break
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        with self._lock:
            total = len(self._connections)
            in_use = sum(1 for c in self._connections.values() if c.in_use)
            
            return {
                "total_connections": total,
                "in_use": in_use,
                "available": total - in_use,
                "min_connections": self.min_connections,
                "max_connections": self.max_connections,
            }
    
    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Context manager for acquiring connections
class ConnectionAcquire:
    """Context manager for acquiring and releasing connections"""
    
    def __init__(self, pool: Neo4jConnectionPool, timeout: Optional[int] = None):
        self.pool = pool
        self.timeout = timeout
        self.connection: Optional[Neo4jConnection] = None
    
    def __enter__(self) -> Neo4jConnection:
        self.connection = self.pool.acquire(self.timeout)
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.pool.release(self.connection)


def get_pool(config_path: Optional[str] = None) -> Neo4jConnectionPool:
    """
    Get a connection pool instance.
    
    Args:
        config_path: Optional config file path
    
    Returns:
        Neo4jConnectionPool instance
    """
    config = Neo4jConfig.from_file(config_path) if config_path else None
    return Neo4jConnectionPool(config)
