# Vector Database Integration

## Overview

This module provides unified interface for multiple vector databases, enabling seamless switching and consistent API for RAG operations.

## Supported Databases

| Database | Type | Best For | Status |
|----------|------|----------|--------|
| Milvus | Self-hosted/Cloud | Enterprise, large scale | ✅ Stable |
| Pinecone | Cloud-managed | Serverless, ease of use | ✅ Stable |
| Weaviate | Self-hosted/Cloud | GraphQL, semantic native | ✅ Stable |
| ChromaDB | Local/Cloud | Development, lightweight | ✅ Stable |
| FAISS | Local | Research, no network | ✅ Stable |

## Base Interface

All vector database implementations follow this interface:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import numpy as np

class VectorDBBase(ABC):
    """Base class for all vector database implementations."""
    
    @abstractmethod
    async def create_collection(
        self,
        name: str,
        dimension: int,
        metric: str = "cosine",
        **kwargs
    ) -> bool:
        """Create a new collection/index."""
        pass
    
    @abstractmethod
    async def insert(
        self,
        collection: str,
        vectors: List[np.ndarray],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Insert vectors with optional metadata."""
        pass
    
    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict] = None,
        include_metadata: bool = True
    ) -> List[Dict]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def delete(
        self,
        collection: str,
        ids: Optional[List[str]] = None,
        filter: Optional[Dict] = None
    ) -> bool:
        """Delete vectors by ID or filter."""
        pass
    
    @abstractmethod
    async def get(
        self,
        collection: str,
        ids: List[str],
        include_vectors: bool = False
    ) -> List[Dict]:
        """Retrieve vectors by IDs."""
        pass
    
    @abstractmethod
    async def update(
        self,
        collection: str,
        id: str,
        vector: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """Update a vector or its metadata."""
        pass
    
    @abstractmethod
    async def count(self, collection: str) -> int:
        """Count vectors in collection."""
        pass
    
    @abstractmethod
    async def drop_collection(self, name: str) -> bool:
        """Drop a collection."""
        pass
```

## Usage Examples

### Milvus

```python
from integrations.rag.vector_db.milvus import MilvusClient

client = MilvusClient(
    host="localhost",
    port=19530
)

# Create collection
await client.create_collection(
    name="documents",
    dimension=1536,
    metric="cosine"
)

# Insert vectors
ids = await client.insert(
    collection="documents",
    vectors=embeddings,
    metadatas=documents_metadata
)

# Search
results = await client.search(
    collection="documents",
    query_vector=query_embedding,
    top_k=5
)
```

### Pinecone

```python
from integrations.rag.vector_db.pinecone import PineconeClient

client = PineconeClient(
    api_key="your-api-key",
    environment="us-west1-gcp"
)

# Similar API as above
await client.create_collection(
    name="documents",
    dimension=1536,
    metric="cosine"
)
```

### ChromaDB (Local)

```python
from integrations.rag.vector_db.chromadb import ChromaClient

client = ChromaClient(
    persist_directory="./chromadb_data"
)

# Local-first, no network required
results = await client.search(
    collection="documents",
    query_vector=query_embedding,
    top_k=5
)
```

## Unified Factory

```python
from integrations.rag.vector_db import get_vector_db

# Factory pattern for easy switching
milvus = get_vector_db("milvus", host="localhost", port=19530)
pinecone = get_vector_db("pinecone", api_key="key", environment="env")
chroma = get_vector_db("chromadb", persist_directory="./data")

# All implement same interface
await any_db.search("collection", vector, top_k=10)
```

## Configuration

```yaml
vector_db:
  default: milvus
  
  milvus:
    host: ${MILVUS_HOST:localhost}
    port: ${MILVUS_PORT:19530}
    pool_size: 10
    timeout: 30
    
  pinecone:
    api_key: ${PINECONE_API_KEY}
    environment: ${PINECONE_ENV}
    
  chromadb:
    persist_directory: ./data/chromadb
    anonymized_telemetry: false
```

## Performance Considerations

| Database | Insert (vectors/sec) | Query (ms) | Scalability |
|----------|---------------------|------------|-------------|
| Milvus | 10,000+ | 1-5 | Excellent |
| Pinecone | 5,000+ | 5-15 | Good |
| Weaviate | 8,000+ | 2-10 | Excellent |
| ChromaDB | 3,000+ | 1-10 | Moderate |
| FAISS | 50,000+ | <1 | N/A (local) |

*Benchmarks vary by hardware and configuration*

## Error Handling

```python
from integrations.rag.vector_db.exceptions import (
    VectorDBError,
    CollectionNotFoundError,
    ConnectionError,
    InsertError
)

try:
    await client.search("collection", vector)
except CollectionNotFoundError:
    # Handle missing collection
    await client.create_collection("collection", 1536)
except ConnectionError as e:
    # Handle connection issues
    logger.error(f"Connection failed: {e}")
except VectorDBError as e:
    # General error handling
    logger.error(f"Vector DB error: {e}")
```

## Migration Between Databases

```python
from integrations.rag.vector_db.migration import migrate

# Migrate from ChromaDB to Milvus
await migrate(
    source_db="chromadb",
    source_config={"persist_directory": "./data"},
    target_db="milvus",
    target_config={"host": "localhost", "port": 19530},
    collections=["documents", "knowledge"]
)
```

## Testing

```bash
# Run vector DB tests
pytest integrations/rag/vector_db/tests/ -v

# Test specific database
pytest integrations/rag/vector_db/tests/test_milvus.py -v
```

## Contributing

To add a new vector database:
1. Create directory under `vector_db/your_db/`
2. Implement `VectorDBBase` interface
3. Add unit tests
4. Update factory function
5. Document in this README

## API Reference

- [Milvus Implementation](./milvus/README.md)
- [Pinecone Implementation](./pinecone/README.md)
- [Weaviate Implementation](./weaviate/README.md)
- [ChromaDB Implementation](./chromadb/README.md)
- [FAISS Implementation](./faiss/README.md)
