"""
Milvus vector database implementation.
"""

from typing import List, Dict, Optional, Any
import numpy as np
from datetime import datetime

from ..base import (
    VectorDBBase,
    DistanceMetric,
    IndexType,
    SearchResult,
    CollectionInfo
)
from ..exceptions import ConnectionError, CollectionNotFoundError, InsertError


class MilvusClient(VectorDBBase):
    """
    Milvus vector database client implementation.
    
    Milvus is an enterprise-grade vector database designed for
    massive scale and high performance.
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 19530,
        alias: str = "default",
        user: Optional[str] = None,
        password: Optional[str] = None,
        secure: bool = False,
        **kwargs
    ):
        """
        Initialize Milvus client.
        
        Args:
            host: Milvus server host
            port: Milvus server port
            alias: Connection alias
            user: Optional username
            password: Optional password
            secure: Use TLS/SSL
            **kwargs: Additional connection parameters
        """
        super().__init__("milvus")
        self.host = host
        self.port = port
        self.alias = alias
        self.user = user
        self.password = password
        self.secure = secure
        self.connection_kwargs = kwargs
        self._client = None
    
    async def connect(self) -> bool:
        """Connect to Milvus server."""
        try:
            from pymilvus import connections, utility
            
            connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                secure=self.secure,
                **self.connection_kwargs
            )
            self._connected = True
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Milvus: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from Milvus server."""
        try:
            from pymilvus import connections
            connections.disconnect(self.alias)
            self._connected = False
            return True
        except Exception:
            return False
    
    async def is_connected(self) -> bool:
        """Check if connected."""
        try:
            from pymilvus import connections
            return connections.has_connection(self.alias)
        except Exception:
            return False
    
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: DistanceMetric = DistanceMetric.COSINE,
        index_type: IndexType = IndexType.AUTO,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """Create a Milvus collection."""
        from pymilvus import (
            Collection, FieldSchema, CollectionSchema,
            DataType, connections, utility
        )
        
        if utility.has_collection(name):
            raise ValueError(f"Collection {name} already exists")
        
        # Map distance metric
        metric_map = {
            DistanceMetric.COSINE: "COSINE",
            DistanceMetric.EUCLIDEAN: "L2",
            DistanceMetric.DOT_PRODUCT: "IP"
        }
        
        # Create schema
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=256, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="metadata", dtype=DataType.JSON, enable_dynamic=True),
            FieldSchema(name="created_at", dtype=DataType.INT64)
        ]
        
        schema = CollectionSchema(fields=fields, description=f"RAG collection: {name}")
        
        # Create collection
        collection = Collection(name=name, schema=schema)
        
        # Create index
        index_map = {
            IndexType.FLAT: "FLAT",
            IndexType.IVF: "IVF_FLAT",
            IndexType.HNSW: "HNSW",
            IndexType.ANNOY: "ANNOY",
            IndexType.AUTO: "AUTOINDEX"
        }
        
        index_params = {
            "metric_type": metric_map.get(metric, "COSINE"),
            "index_type": index_map.get(index_type, "AUTOINDEX"),
            "params": kwargs.get("index_params", {})
        }
        
        collection.create_index(field_name="embedding", index_params=index_params)
        
        return True
    
    async def collection_exists(self, name: str) -> bool:
        """Check if collection exists."""
        from pymilvus import utility
        return utility.has_collection(name)
    
    async def get_collection_info(self, name: str) -> CollectionInfo:
        """Get collection information."""
        from pymilvus import Collection, utility
        
        if not utility.has_collection(name):
            raise CollectionNotFoundError(f"Collection {name} not found")
        
        collection = Collection(name)
        collection.load()
        
        # Get schema info
        schema = collection.schema
        dim = None
        for field in schema.fields:
            if field.name == "embedding":
                dim = field.params.get("dim")
                break
        
        # Map metric type
        metric_str = "COSINE"
        for index in collection.indexes:
            if index.field_name == "embedding":
                metric_str = index.params.get("metric_type", "COSINE")
        
        metric_map = {
            "COSINE": DistanceMetric.COSINE,
            "L2": DistanceMetric.EUCLIDEAN,
            "IP": DistanceMetric.DOT_PRODUCT
        }
        
        return CollectionInfo(
            name=name,
            dimension=dim or 0,
            metric=metric_map.get(metric_str, DistanceMetric.COSINE),
            count=collection.num_entities,
            index_type=IndexType.AUTO,
            created_at=datetime.now(),  # Milvus doesn't store creation time
            metadata={"description": schema.description}
        )
    
    async def insert(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        batch_size: int = 100
    ) -> List[str]:
        """Insert vectors into Milvus collection."""
        from pymilvus import Collection, utility
        
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        coll = Collection(collection)
        dimension = None
        for field in coll.schema.fields:
            if field.name == "embedding":
                dimension = field.params.get("dim")
                break
        
        self._validate_vectors(vectors, dimension)
        
        # Prepare data
        generated_ids = ids or [self._generate_id() for _ in vectors]
        timestamps = [int(datetime.now().timestamp()) for _ in vectors]
        metadatas = metadatas or [{} for _ in vectors]
        
        # Insert
        try:
            data = [
                generated_ids,
                [v.tolist() for v in vectors],
                metadatas,
                timestamps
            ]
            coll.insert(data)
            coll.flush()
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
        """Search Milvus collection."""
        from pymilvus import Collection, utility
        
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        coll = Collection(collection)
        coll.load()
        
        # Build search params
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 10}
        }
        
        # Build filter expression
        expr = None
        if filter:
            expr = self._build_filter_expr(filter)
        
        # Search
        results = coll.search(
            data=[query_vector.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["metadata", "created_at"] if include_metadata else None
        )
        
        # Convert results
        search_results = []
        for hits in results:
            for hit in hits:
                result = SearchResult(
                    id=str(hit.id),
                    score=float(hit.score),
                    vector=None,
                    metadata=hit.entity.get("metadata") if include_metadata else None,
                    created_at=datetime.fromtimestamp(hit.entity.get("created_at", 0))
                )
                search_results.append(result)
        
        return search_results
    
    async def delete(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict[str, Any]] = None
    ) -> int:
        """Delete vectors from collection."""
        from pymilvus import Collection, utility
        
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        coll = Collection(collection)
        
        if ids:
            expr = f'id in {ids}'
        elif filter:
            expr = self._build_filter_expr(filter)
        else:
            raise ValueError("Must provide either ids or filter")
        
        result = coll.delete(expr)
        coll.flush()
        return len(result) if hasattr(result, '__len__') else 0
    
    async def get(
        self,
        collection: str,
        ids: List[str],
        include_vectors: bool = False,
        include_metadata: bool = True
    ) -> List[SearchResult]:
        """Get vectors by IDs."""
        from pymilvus import Collection, utility
        
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        coll = Collection(collection)
        coll.load()
        
        output_fields = ["metadata", "created_at"]
        if include_vectors:
            output_fields.append("embedding")
        
        results = coll.query(
            expr=f'id in {ids}',
            output_fields=output_fields
        )
        
        search_results = []
        for result in results:
            sr = SearchResult(
                id=result["id"],
                score=1.0,
                vector=np.array(result["embedding"]) if include_vectors else None,
                metadata=result.get("metadata") if include_metadata else None,
                created_at=datetime.fromtimestamp(result.get("created_at", 0))
            )
            search_results.append(sr)
        
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
        # Milvus doesn't have native update, need to delete and insert
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        # Get existing record
        existing = await self.get(collection, [id], include_vectors=True, include_metadata=True)
        
        if not existing:
            if upsert and vector is not None:
                await self.insert(collection, [vector], [metadata] if metadata else None, [id])
                return True
            raise ValueError(f"Vector {id} not found")
        
        # Delete and re-insert
        await self.delete(collection, ids=[id])
        
        new_vector = vector or existing[0].vector
        new_metadata = {**(existing[0].metadata or {}), **(metadata or {})}
        
        await self.insert(collection, [new_vector], [new_metadata], [id])
        return True
    
    async def count(self, collection: str, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count vectors in collection."""
        from pymilvus import Collection, utility
        
        if not await self.collection_exists(collection):
            raise CollectionNotFoundError(f"Collection {collection} not found")
        
        coll = Collection(collection)
        coll.flush()
        
        if filter:
            expr = self._build_filter_expr(filter)
            results = coll.query(expr=expr, output_fields=["count(*)"])
            return len(results)
        
        return coll.num_entities
    
    async def drop_collection(self, name: str) -> bool:
        """Drop a collection."""
        from pymilvus import utility
        
        if not utility.has_collection(name):
            raise CollectionNotFoundError(f"Collection {name} not found")
        
        utility.drop_collection(name)
        return True
    
    async def list_collections(self) -> List[str]:
        """List all collections."""
        from pymilvus import utility
        return utility.list_collections()
    
    def _build_filter_expr(self, filter: Dict[str, Any]) -> str:
        """Build Milvus filter expression."""
        # Simple filter building - can be extended for complex queries
        parts = []
        for key, value in filter.items():
            if isinstance(value, str):
                parts.append(f'{key} == "{value}"')
            elif isinstance(value, (int, float)):
                parts.append(f'{key} == {value}')
            elif isinstance(value, list):
                parts.append(f'{key} in {value}')
        
        return " and ".join(parts)
