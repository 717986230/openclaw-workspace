"""
Neo4j Configuration Management

Handles configuration loading, validation, and environment variable handling.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import yaml
import logging

logger = logging.getLogger(__name__)


@dataclass
class Neo4jConfig:
    """Neo4j connection configuration"""
    
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = ""
    database: str = "neo4j"
    
    # Connection pool settings
    max_connection_pool_size: int = 50
    connection_timeout: int = 30
    max_transaction_retry_time: int = 30
    
    # Retry settings
    max_retry_attempts: int = 3
    retry_backoff_factor: float = 2.0
    
    # Security
    encrypted: bool = True
    trust_certificates: bool = False
    
    # Custom settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Load from environment variables if not set"""
        self.uri = os.getenv("NEO4J_URI", self.uri)
        self.user = os.getenv("NEO4J_USER", self.user)
        self.password = os.getenv("NEO4J_PASSWORD", self.password)
        self.database = os.getenv("NEO4J_DATABASE", self.database)
        
        # Validate
        if not self.password:
            logger.warning("No Neo4j password provided. Set NEO4J_PASSWORD environment variable.")
    
    @classmethod
    def from_file(cls, config_path: str) -> "Neo4jConfig":
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            neo4j_config = config_data.get('neo4j', {})
            
            return cls(
                uri=neo4j_config.get('uri', 'bolt://localhost:7687'),
                user=neo4j_config.get('user', 'neo4j'),
                password=neo4j_config.get('password', ''),
                database=neo4j_config.get('database', 'neo4j'),
                max_connection_pool_size=neo4j_config.get('pool', {}).get('max_size', 50),
                connection_timeout=neo4j_config.get('pool', {}).get('timeout', 30),
                max_retry_attempts=neo4j_config.get('retry', {}).get('max_attempts', 3),
                retry_backoff_factor=neo4j_config.get('retry', {}).get('backoff_factor', 2.0),
            )
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return cls()
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return cls()
    
    def to_driver_config(self) -> Dict[str, Any]:
        """Convert to neo4j driver configuration"""
        config = {
            "max_connection_pool_size": self.max_connection_pool_size,
            "connection_timeout": self.connection_timeout,
            "max_transaction_retry_time": self.max_transaction_retry_time,
        }
        
        if self.encrypted:
            config["encrypted"] = True
        
        return config
    
    def __repr__(self) -> str:
        """Safe string representation (hides password)"""
        return (
            f"Neo4jConfig(uri={self.uri}, user={self.user}, "
            f"database={self.database}, password=***, "
            f"pool_size={self.max_connection_pool_size})"
        )


# Default configuration instance
default_config = Neo4jConfig()


def get_config(config_path: Optional[str] = None) -> Neo4jConfig:
    """
    Get Neo4j configuration.
    
    Args:
        config_path: Optional path to config file
    
    Returns:
        Neo4jConfig instance
    """
    if config_path:
        return Neo4jConfig.from_file(config_path)
    return default_config
