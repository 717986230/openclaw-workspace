"""
Vector Database Integration Module.

Provides unified interface for multiple vector databases.
"""

from .base import (
    VectorDBBase,
    DistanceMetric,
    IndexType,
    SearchResult,
    CollectionInfo
)
from .exceptions import (
    VectorDBError,
    ConnectionError,
    CollectionNotFoundError,
    InsertError
)


# Database registry
_registry = {}


def register_vector_db(name: str, client_class):
    """Register a vector database implementation."""
    _registry[name.lower()] = client_class


def get_vector_db(name: str, **kwargs) -> VectorDBBase:
    """
    Get a vector database client by name.
    
    Args:
        name: Database name (milvus, pinecone, weaviate, chromadb, faiss)
        **kwargs: Client configuration
        
    Returns:
        Vector database client instance
        
    Raises:
        ValueError: If database not registered
    """
    name_lower = name.lower()
    
    if name_lower not in _registry:
        available = ", ".join(_registry.keys())
        raise ValueError(f"Unknown vector database: {name}. Available: {available}")
    
    return _registry[name_lower](**kwargs)


def list_vector_dbs() -> list:
    """List registered vector databases."""
    return list(_registry.keys())


# Register built-in implementations
def _register_builtins():
    """Register built-in vector database implementations."""
    try:
        from .milvus import MilvusClient
        register_vector_db("milvus", MilvusClient)
    except ImportError:
        pass
    
    try:
        from .chromadb import ChromaClient
        register_vector_db("chromadb", ChromaClient)
    except ImportError:
        pass
    
    # Additional implementations can be added:
    # from .pinecone import PineconeClient
    # register_vector_db("pinecone", PineconeClient)
    
    # from .weaviate import WeaviateClient
    # register_vector_db("weaviate", WeaviateClient)
    
    # from .faiss import FAISSClient
    # register_vector_db("faiss", FAISSClient)


_register_builtins()


__all__ = [
    "VectorDBBase",
    "DistanceMetric",
    "IndexType",
    "SearchResult",
    "CollectionInfo",
    "VectorDBError",
    "ConnectionError",
    "CollectionNotFoundError",
    "InsertError",
    "register_vector_db",
    "get_vector_db",
    "list_vector_dbs"
]
