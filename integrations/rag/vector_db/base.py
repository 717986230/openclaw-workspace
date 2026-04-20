"""
Base class for all vector database implementations.
Provides unified interface for RAG operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime


class DistanceMetric(Enum):
    """Supported distance metrics."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"


class IndexType(Enum):
    """Supported index types."""
    FLAT = "flat"
    IVF = "ivf"
    HNSW = "hnsw"
    ANNOY = "annoy"
    AUTO = "auto"


@dataclass
class SearchResult:
    """Represents a single search result."""
    id: str
    score: float
    vector: Optional[np.ndarray] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "score": self.score,
            "vector": self.vector.tolist() if self.vector is not None else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class CollectionInfo:
    """Information about a collection."""
    name: str
    dimension: int
    metric: DistanceMetric
    count: int
    index_type: IndexType
    created_at: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "dimension": self.dimension,
            "metric": self.metric.value,
            "count": self.count,
            "index_type": self.index_type.value,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class VectorDBBase(ABC):
    """
    Abstract base class for vector database implementations.
    
    All vector database clients must implement this interface to ensure
    consistent behavior across different backends.
    """
    
    def __init__(self, name: str):
        """Initialize the vector database client."""
        self.name = name
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the vector database.
        
        Returns:
            True if connection successful, False otherwise
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the vector database.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """
        Check if connected to the database.
        
        Returns:
            True if connected
        """
        pass
    
    @abstractmethod
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        index_type: IndexType = IndexType.AUTO,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """
        Create a new collection/index.
        
        Args:
            name: Collection name
            dimension: Vector dimension
            metric: Distance metric
            index_type: Type of index to use
            metadata: Optional collection metadata
            **kwargs: Additional database-specific options
            
        Returns:
            True if created successfully
            
        Raises:
            ValueError: If collection already exists
        """
        pass
    
    @abstractmethod
    async def collection_exists(self, name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection exists
        """
        pass
    
    @abstractmethod
    async def get_collection_info(self, name: str) -> CollectionInfo:
        """
        Get information about a collection.
        
        Args:
            name: Collection name
            
        Returns:
            Collection information
            
        Raises:
            ValueError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def insert(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """
        Insert vectors into collection.
        
        Args:
            collection: Collection name
            vectors: List of vectors to insert
            metadatas: Optional metadata for each vector
            ids: Optional IDs for each vector (auto-generated if not provided)
            batch_size: Batch size for bulk insert
            
        Returns:
            List of inserted IDs
            
        Raises:
            ValueError: If collection doesn't exist or invalid dimensions
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        include_vectors: bool = False,
        include_metadata: bool = True,
        **kwargs
    ) -> List[SearchResult]:
        """
        Search for similar vectors.
        
        Args:
            collection: Collection name
            query_vector: Query vector
            top_k: Number of results to return
            filter: Optional metadata filter
            include_vectors: Whether to include vectors in results
            include_metadata: Whether to include metadata in results
            **kwargs: Additional search parameters
            
        Returns:
            List of search results sorted by similarity
            
        Raises:
            ValueError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Delete vectors from collection.
        
        Args:
            collection: Collection name
            ids: Optional list of IDs to delete
            filter: Optional metadata filter for deletion
            
        Returns:
            Number of vectors deleted
            
        Raises:
            ValueError: If collection doesn't exist or no criteria provided
        """
        pass
    
    @abstractmethod
    async def get(
        self,
        collection: str,
        ids: List[str],
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """
        Retrieve vectors by IDs.
        
        Args:
            collection: Collection name
            ids: List of IDs to retrieve
            include_vectors: Whether to include vectors
            include_metadata: Whether to include metadata
            
        Returns:
            List of search results
            
        Raises:
            ValueError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
        upsert: bool = False
    ) -> bool:
        """
        Update a vector or its metadata.
        
        Args:
            collection: Collection name
            id: Vector ID
            vector: Optional new vector
            metadata: Optional new metadata (will be merged with existing)
            upsert: If True, insert if doesn't exist
            
        Returns:
            True if updated successfully
            
        Raises:
            ValueError: If collection doesn't exist or vector not found
        """
        pass
    
    @abstractmethod
    async def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """
        Count vectors in collection.
        
        Args:
            collection: Collection name
            filter: Optional metadata filter
            
        Returns:
            Number of vectors
            
        Raises:
            ValueError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def drop_collection(self, name: str) -> bool:
        """
        Drop a collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if dropped successfully
            
        Raises:
            ValueError: If collection doesn't exist
        """
        pass
    
    @abstractmethod
    async def list_collections(self) -> List[str]:
        """
        List all collections.
        
        Returns:
            List of collection names
        """
        pass
    
    # Batch operations
    
    async def batch_insert(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """
        Insert vectors in batches (default implementation).
        
        Subclasses can override for optimized batch insert.
        """
        all_ids = []
        for i in range(0, len(vectors), batch_size):
            batch_vectors = vectors[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size] if metadatas else None
            batch_ids = ids[i:i + batch_size] if ids else None
            
            inserted_ids = await self.insert(
                collection,
                batch_vectors,
                batch_metadatas,
                batch_ids
            )
            all_ids.extend(inserted_ids)
        
        return all_ids
    
    # Utility methods
    
    def _validate_vectors(self, vectors: List[np.ndarray], dimension: int) -> bool:
        """Validate vectors have correct dimension."""
        for vec in vectors:
            if len(vec.shape) != 1:
                raise ValueError(f"Vector must be 1D, got shape {vec.shape}")
            if vec.shape[0] != dimension:
                raise ValueError(f"Vector dimension {vec.shape[0]} != expected {dimension}")
        return True
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
