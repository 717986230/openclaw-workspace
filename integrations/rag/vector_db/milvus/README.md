# Milvus Vector Database Integration

## Overview

[Milvus](https://milvus.io/) is an open-source vector database built for scalable similarity search and AI applications.

## Features

- **High Performance**: Designed for billion-scale vector search
- **Multiple Index Types**: FLAT, IVF, HNSW, ANNOY, and more
- **Cloud-Native**: Kubernetes-ready with cloud storage support
- **Hybrid Search**: Combine vector similarity with metadata filtering
- **Distributed**: Horizontally scalable architecture

## Installation

```bash
pip install pymilvus
```

## Quick Start

```python
from integrations.rag.vector_db.milvus import MilvusClient

# Connect
client = MilvusClient(host="localhost", port=19530)
await client.connect()

# Create collection
await client.create_collection(
    name="documents",
    dimension=1536,
    metric="cosine"
)

# Insert vectors
import numpy as np
vectors = [np.random.rand(1536) for _ in range(100)]
ids = await client.insert("documents", vectors)

# Search
query = np.random.rand(1536)
results = await client.search("documents", query, top_k=5)

# Cleanup
await client.disconnect()
```

## Configuration

### Standalone Mode

```yaml
milvus:
  host: localhost
  port: 19530
```

### Cluster Mode

```yaml
milvus:
  hosts:
    - milvus-1.example.com:19530
    - milvus-2.example.com:19530
    - milvus-3.example.com:19530
  pool_size: 10
```

### Authentication

```yaml
milvus:
  host: milvus.example.com
  port: 19530
  user: ${MILVUS_USER}
  password: ${MILVUS_PASSWORD}
  secure: true  # Enable TLS
```

## Index Types

| Type | Build Speed | Search Speed | Memory | Best For |
|------|-------------|--------------|--------|----------|
| FLAT | Fast | Slow | High | Accuracy-first, small datasets |
| IVF_FLAT | Medium | Medium | Medium | Balanced performance |
| IVF_PQ | Slow | Fast | Low | Memory-constrained, large datasets |
| HNSW | Slow | Very Fast | High | Low latency, real-time |
| ANNOY | Medium | Fast | Low | Read-heavy workloads |

### Create Collection with Custom Index

```python
await client.create_collection(
    name="documents",
    dimension=1536,
    index_type=IndexType.HNSW,
    index_params={
        "M": 16,
        "efConstruction": 256
    }
)
```

## Metadata Filtering

```python
# Simple filter
results = await client.search(
    "documents",
    query,
    filter={"category": "technical"}
)

# Multiple conditions
results = await client.search(
    "documents",
    query,
    filter={"category": "technical", "year": 2024}
)

# List filter (IN operator)
results = await client.search(
    "documents",
    query,
    filter={"category": ["technical", "tutorial"]}
)
```

## Batch Operations

```python
# Batch insert
vectors = [np.random.rand(1536) for _ in range(10000)]
metadatas = [{"id": i, "source": "doc"} for i in range(10000)]
ids = await client.insert("documents", vectors, metadatas, batch_size=500)

# Batch delete
await client.delete("documents", ids=id_list)
```

## Performance Optimization

### Index Parameters

```python
# HNSW (best for low latency)
index_params = {
    "M": 32,              # Higher = better recall, more memory
    "efConstruction": 256  # Higher = better index quality
}

# IVF (balanced)
index_params = {
    "nlist": 1024  # Number of clusters
}
search_params = {
    "nprobe": 64   # Number of clusters to search (higher = better recall)
}
```

### Search Parameters

```python
results = await client.search(
    "documents",
    query,
    top_k=10,
    search_params={"nprobe": 64}  # For IVF indexes
)
```

## Deployment Options

### Docker (Development)

```bash
# Download docker-compose.yml
wget https://github.com/milvus-io/milvus/releases/download/v2.3.0/milvus-standalone-docker-compose.yml -O docker-compose.yml

# Start
docker-compose up -d
```

### Kubernetes (Production)

```bash
# Using Helm
helm repo add milvus https://zilliztech.github.io/milvus-helm/
helm install milvus milvus/milvus
```

### Managed Service (Zilliz Cloud)

```python
# Zilliz Cloud configuration
client = MilvusClient(
    host="your-instance.zillizcloud.com",
    port=19530,
    user="db_admin",
    password="your_password",
    secure=True
)
```

## Monitoring

```python
# Get collection stats
info = await client.get_collection_info("documents")
print(f"Vector count: {info.count}")

# Query performance
import time
start = time