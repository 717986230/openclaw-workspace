# ChromaDB Integration

## Overview

[ChromaDB](https://www.trychroma.com/) is a lightweight, open-source vector database designed for simplicity and local-first development.

## Features

- **Local-First**: Run entirely in-memory or with local persistence
- **Zero Configuration**: Works out of the box
- **Python Native**: Built specifically for Python developers
- **HNSW Index**: High-performance approximate nearest neighbor
- **Metadata Filtering**: Rich filtering capabilities

## Installation

```bash
pip install chromadb
```

## Quick Start

### In-Memory Mode

```python
from integrations.rag.vector_db.chromadb import ChromaClient

# In-memory (data lost on restart)
client = ChromaClient()
await client.connect()

# Use it...
```

### Persistent Mode

```python
# Persistent (data saved to disk)
client = ChromaClient(persist_directory="./chromadb_data")
await client.connect()

# Create collection
await client.create_collection(
    name="documents",
    dimension=1536
)

# Insert
ids = await client.insert("documents", vectors, metadatas)

# Search
results = await client.search("documents", query_vector, top_k=5)
```

### Server Mode

```python
# Connect to ChromaDB server
client = ChromaClient(host="localhost", port=8000)
await client.connect()
```

## Configuration

```yaml
chromadb:
  persist_directory: ./data/chromadb
  anonymized_telemetry: false
  
  # Or use server mode
  host: localhost
  port: 8000
```

## Usage Examples

### Basic Operations

```python
# Create collection with metadata
await client.create_collection(
    name="knowledge",
    dimension=768,
    metric="cosine",
    metadata={"description": "Knowledge base for RAG"}
)

# Insert with metadata
import numpy as np
vectors = [np.random.rand(768) for _ in range(100)]
metadatas = [
    {"source": "doc1", "page": i, "category": "tech"}
    for i in range(100)
]
ids = await client.insert("knowledge", vectors, metadatas)

# Search with filtering
results = await client.search(
    "knowledge",
    query_vector,
    top_k=10,
    filter={"category": "tech"}
)
```

### Metadata Filtering

```python
# Simple equality
filter = {"category": "technical"}

# List membership
filter = {"category": {"$in": ["technical", "tutorial"]}}

# Numeric comparison
filter = {"page": {"$gte": 5, "$lte": 10}}

# Logical operators
filter = {
    "$and": [
        {"category": "technical"},
        {"year": {"$gte": 2024}}
    ]
}

filter = {
    "$or": [
        {"source": "doc1"},
        {"source": "doc2"}
    ]
}
```

### Document Storage

```python
# ChromaDB can store text documents alongside embeddings
collection = client._client.get_collection("documents")

collection.add(
    ids=["doc1", "doc2"],
    embeddings=[[...], [...]],
    documents=["This is document 1", "This is document 2"],
    metadatas=[{"source": "file1.txt"}, {"source": "file2.txt"}]
)

# Search returns matching documents
results = collection.query(
    query_embeddings=[[...]],
    n_results=5,
    include=["documents", "metadatas", "distances"]
)
```

## Running as Server

### Docker

```bash
# Pull and run
docker run -d -p 8000:8000 chromadb/chroma:latest

# With persistence
docker run -d -p 8000:8000 -v ./chromadb-data:/chromadb-data chromadb/chroma:latest
```

### Python Server

```bash
chroma run --host localhost --port 8000 --path ./chromadb-data
```

## Performance

ChromaDB uses HNSW (Hierarchical Navigable Small World) algorithm for fast approximate nearest neighbor search.

| Metric | Typical Performance |
|--------|---------------------|
| Insert | 1,000-5,000 vectors/sec |
| Query | 1-10 ms (top 10) |
| Memory | ~1KB per vector + metadata |

## When to Use ChromaDB

**Good for:**
- Development and prototyping
- Small to medium datasets (<