"""
ChromaDB vector database implementation (local-first).
"""

from typing import List, Dict, Optional, Any
import numpy as np
from datetime import datetime
import json

from ..base import (
    VectorDBBase,
    DistanceMetric,
    IndexType,
    SearchResult,
    CollectionInfo
)
from ..exceptions import ConnectionError, CollectionNotFoundError, InsertError


class ChromaClient(VectorDBBase):
    """
    ChromaDB client implementation.
    
    ChromaDB is lightweight, local-first vector database ideal for
    development and smaller-scale applications.
    """
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: int = 8000,
        anonymized_telemetry: bool = False,
        **kwargs
    ):
        """
        Initialize ChromaDB client.
        
        Args:
            persist_directory: Local directory for persistence (None = in-memory)
            host: Chroma server host (None = local mode)
            port: Chroma server port
            anonymized_telemetry: Enable/disable telemetry
            **kwargs: Additional parameters
        """
        super().__init__("chromadb")
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self.anonymized_telemetry = anonymized_telemetry
        self.kwargs = kwargs
        self._client = None
        self._collections = {}
    
    async def connect(self) -> bool:
        """Connect to ChromaDB."""
        try:
            import chromadb
            
            if self.host:
                # Server mode
                self._client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port
                )
            elif self.persist_directory:
                # Persistent local mode
                self._client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=chromadb.Settings(
                        anonymized_telemetry=self.anonymized_telemetry
                    )
                )
            else:
                # In-memory mode
                self._client = chromadb.EphemeralClient(
                    settings=chromadb.Settings(
                        anonymized_telemetry=self.anonymized_telemetry
                    )
                )
            
            self._connected = True
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to ChromaDB: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect (no-op for local mode)."""
        self._connected = False
        return True
    
    async def is_connected(self) -> bool:
        """Check if connected."""
        return self._connected and self._client is not None
    
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        index_type: IndexType = IndexType.AUTO,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """Create a ChromaDB collection."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        # Check if exists
        try:
            self._client.get_collection(name)
            raise ValueError(f"Collection {name} already exists")
        except Exception:
            pass  # Collection doesn't exist, which is what we want
        
        # Map distance metric
        metric_map = {
            DistanceMetric.COSINE: "cosine",
            DistanceMetric.EUCLIDEAN: "l2",
            DistanceMetric.DOT_PRODUCT: "ip"
        }
        
        # Create collection
        collection_metadata = {
            "dimension": dimension,
            "hnsw:space": metric_map.get(metric, "cosine"),
            "created_at": datetime.now().isoformat()
        }
        if metadata:
            collection_metadata.update(metadata)
        
        collection = self._client.create_collection(
            name=name,
            metadata=collection_metadata
        )
        
        self._collections[name] = collection
        return True
    
    async def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        if not self._client:
            return False
        
        try:
            self._client.get_collection(name)
            return True
        except Exception:
            return False
    
    async def get_collection_info(self, name: str) -> CollectionInfo:
        """Get collection information."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            collection = self._client.get_collection(name)
        except Exception:
            raise CollectionNotFoundError(f"Collection {name} not found")
        
        count = collection.count()
        metadata = collection.metadata or {}
        
        # Map metric back
        space = metadata.get("hnsw:space", "cosine")
        metric_map = {
            "cosine": DistanceMetric.COSINE,
            "l2": DistanceMetric.EUCLIDEAN,
            "ip": DistanceMetric.DOT_PRODUCT
        }
        
        created_at_str = metadata.get("created_at", datetime.now().isoformat())
        try:
            created_at = datetime.fromisoformat(created_at_str)
        except Exception:
            created_at = datetime.now()
        
        return CollectionInfo(
            name=name,
            dimension=metadata.get("dimension", 0),
            metric=metric_map.get(space, DistanceMetric.COSINE),
            count=count,
            index_type=IndexType.HNSW,  # ChromaDB uses HNSW
            created_at=created_at,
            metadata=metadata
        )
    
    async def insert(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Insert vectors into collection."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        # Validate vectors
        dimension = coll.metadata.get("dimension")
        if dimension:
            self._validate_vectors(vectors, dimension)
        
        # Prepare data
        generated_ids = ids or [self._generate_id() for _ in vectors]
        vectors_list = [v.tolist() for v in vectors]
        documents = [None] * len(vectors)  # Optional text documents
        
        # Insert in batches
        try:
            for i in range(0, len(vectors), batch_size):
                batch_ids = generated_ids[i:i + batch_size]
                batch_vectors = vectors_list[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size] if metadatas else None
                batch_documents = documents[i:i + batch_size]
                
                coll.add(
                    ids=batch_ids,
                    embeddings=batch_vectors,
                    metadatas=batch_metadatas,
                    documents=batch_documents
                )
            
            return generated_ids
        except Exception as e:
            raise InsertError(f"Failed to insert vectors: {e}")
    
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
        """Search collection."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        # Build where filter
        where = None
        if filter:
            where = self._build_where(filter)
        
        # Search
        include = ["distances"]
        if include_metadata:
            include.append("metadatas")
        if include_vectors:
            include.append("embeddings")
        
        results = coll.query(
            query_embeddings=[query_vector.tolist()],
            n_results=top_k,
            where=where,
            include=include
        )
        
        # Convert results
        search_results = []
        ids = results.get("ids", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0] if include_metadata else [None] * len(ids)
        embeddings = results.get("embeddings", [[]])[0] if include_vectors else [None] * len(ids)
        
        for i, (id_, distance) in enumerate(zip(ids, distances)):
            # Convert distance to similarity score (ChromaDB returns distances)
            # For cosine: similarity = 1 - distance
            score = 1.0 - distance
            
            result = SearchResult(
                id=id_,
                score=float(score),
                vector=np.array(embeddings[i]) if embeddings[i] else None,
                metadata=metas[i] if include_metadata else None,
                created_at=None  # ChromaDB doesn't track timestamps
            )
            search_results.append(result)
        
        return search_results
    
    async def delete(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete vectors."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        count_before = coll.count()
        
        if ids:
            coll.delete(ids=ids)
        elif filter:
            where = self._build_where(filter)
            coll.delete(where=where)
        else:
            raise ValueError("Must provide either ids or filter")
        
        count_after = coll.count()
        return count_before - count_after
    
    async def get(
        self,
        collection: str,
        ids: List[str],
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Get vectors by IDs."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        include = []
        if include_metadata:
            include.append("metadatas")
        if include_vectors:
            include.append("embeddings")
        
        results = coll.get(
            ids=ids,
            include=include if include else None
        )
        
        search_results = []
        result_ids = results.get("ids", [])
        metas = results.get("metadatas", [])
        embeddings = results.get("embeddings", [])
        
        for i, id_ in enumerate(result_ids):
            result = SearchResult(
                id=id_,
                score=1.0,  # Direct fetch, no similarity score
                vector=np.array(embeddings[i]) if include_vectors and embeddings else None,
                metadata=metas[i] if include_metadata and metas else None,
                created_at=None
            )
            search_results.append(result)
        
        return search_results
    
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict[str, Any]] = None,
        upsert: bool = False
    ) -> bool:
        """Update vector or metadata."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        # Check if exists
        existing = await self.get(collection, [id], include_vectors=True, include_metadata=True)
        
        if not existing:
            if upsert and vector is not None:
                await self.insert(collection, [vector], [metadata] if metadata else None, [id])
                return True
            raise ValueError(f"Vector {id} not found")
        
        # Update - ChromaDB uses upsert
        new_vector = vector if vector is not None else existing[0].vector
        new_metadata = {**(existing[0].metadata or {}), **(metadata or {})}
        
        coll.update(
            ids=[id],
            embeddings=[new_vector.tolist()],
            metadatas=[new_metadata]
        )
        
        return True
    
    async def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count vectors."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            coll = self._client.get_collection(collection)
        except Exception:
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        if filter:
            # ChromaDB doesn't support filtered count directly
            where = self._build_where(filter)
            results = coll.get(where=where)
            return len(results.get("ids", []))
        
        return coll.count()
    
    async def drop_collection(self, name: str) -> bool:
        """Drop a collection."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        try:
            self._client.delete_collection(name)
            if name in self._collections:
                del self._collections[name]
            return True
        except Exception:
            raise CollectionNotFoundError(f"Collection {name} not found")
    
    async def list_collections(self) -> List[str]:
        """List all collections."""
        if not self._client:
            raise ConnectionError("Not connected to ChromaDB")
        
        collections = self._client.list_collections()
        return [c.name for c in collections]
    
    def _build_where(self, filter: Dict[str, Any]) -> Dict:
        """Build ChromaDB where clause."""
        # ChromaDB uses specific filter syntax
        conditions = []
        for key, value in filter.items():
            if isinstance(value, dict):
                # Operator already specified
                conditions.append({key: value})
            elif isinstance(value, list):
                conditions.append({key: {"$in": value}})
            else:
                conditions.append({key: value})
        
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
