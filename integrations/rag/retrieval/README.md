# RAG Retrieval System

## Overview

The retrieval module provides advanced retrieval capabilities for RAG systems, including semantic search, hybrid search, and result reranking.

## Architecture

```
retrieval/
├── README.md              # This file
├── semantic_search/       # Semantic search engine
│   ├── engine.py         # Core search engine
│   └── query_builder.py  # Query construction
├── reranker/             # Result reranking
│   ├── cross_encoder.py  # Cross-encoder reranking
│   └── diversity.py      # Diversity-based reranking
├── hybrid_search/        # Hybrid search (keyword + vector)
│   ├── bm25.py          # BM25 keyword search
│   └── fusion.py        # Result fusion strategies
└── multi_query/         # Multi-query retrieval
    └── strategies.py    # Query expansion strategies
```

## Core Components

### 1. Semantic Search

```python
from integrations.rag.retrieval import SemanticSearchEngine

engine = SemanticSearchEngine(
    vector_db="milvus",
    embedding_model="text-embedding-ada-002"
)

# Search
results = await engine.search(
    query="What is machine learning?",
    collection="documents",
    top_k=10
)
```

### 2. Hybrid Search

Combines vector similarity with keyword matching for better recall.

```python
from integrations.rag.retrieval import HybridSearch

hybrid = HybridSearch(
    vector_weight=0.7,
    keyword_weight=0.3
)

results = await hybrid.search(
    query="machine learning algorithms",
    collection="documents",
    top_k=20
)
```

### 3. Reranking

Improves relevance through cross-encoder or diversity-based reranking.

```python
from integrations.rag.retrieval import CrossEncoderReranker

reranker = CrossEncoderReranker(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Rerank initial results
reranked = await reranker.rerank(
    query="What is deep learning?",
    results=initial_results,
    top_k=5
)
```

## Usage Examples

### Basic Semantic Search

```python
from integrations.rag import RAGRetriever

retriever = RAGRetriever(
    vector_db="milvus",
    collection="knowledge_base"
)

# Simple search
results = await retriever.search("What is RAG?")

# With metadata filtering
results = await retriever.search(
    query="RAG techniques",
    filter={"category": "technical", "year": 2024}
)

# With threshold
results = await retriever.search(
    query="vector databases",
    min_score=0.7
)
```

### Hybrid Search with Reranking

```python
from integrations.rag.retrieval import HybridRetriever

retriever = HybridRetriever(
    vector_db_config={"type": "milvus", "host": "localhost"},
    keyword_weight=0.3,
    vector_weight=0.7,
    rerank=True,
    reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2"
)

# Two-stage retrieval:
# 1. Hybrid search (vector + keyword) gets top_k * 2 results
# 2. Reranker selects top_k most relevant
results = await retriever.retrieve(
    query="How to implement RAG pipeline?",
    top_k=10
)
```

### Multi-Query Retrieval

Generates multiple query variations for better recall.

```python
from integrations.rag.retrieval import MultiQueryRetriever

retriever = MultiQueryRetriever(
    base_retriever=semantic_retriever,
    llm_model="gpt-4",
    num_queries=3
)

# Generates:
# - Original: "RAG systems"
# - Query 1: "Retrieval augmented generation architecture"
# - Query 2: "RAG implementation best practices"
# - Query 3: "Vector database integration with LLMs"
results = await retriever.retrieve("RAG systems")
```

### Query Expansion

```python
from integrations.rag.retrieval import QueryExpander

expander = QueryExpander(
    method="hyde",  # or "multi_query", "query2doc"
    llm_model="gpt-4"
)

# HyDE: Generate hypothetical document
expanded_query = await expander.expand(
    query="What are vector databases?"
)
# Expanded query is now a hypothetical document that answers the question
```

## Configuration

```yaml
retrieval:
  default:
    top_k: 10
    min_score: 0.5
    
  semantic_search:
    embedding_model: text-embedding-ada-002
    batch_size: 32
    
  hybrid_search:
    vector_weight: 0.7
    keyword_weight: 0.3
    bm25_k1: 1.5
    bm25_b: 0.75
    
  reranking:
    enabled: true
    model: cross-encoder/ms-marco-MiniLM-L-6-v2
    batch_size: 16
    
  multi_query:
    enabled: false
    num_queries: 3
    temperature: 0.5
```

## Advanced Features

### Metadata Filtering

```python
# Exact match
filter = {"category": "technical"}

# Range queries
filter = {"year": {"$gte": 2020, "$lte": 2024}}

# Array membership
filter = {"tags": {"$in": ["AI", "ML", "NLP"]}}

# Logical operators
filter = {
    "$and": [
        {"category": "technical"},
        {"status": "published"}
    ]
}

filter = {
    "$or": [
        {"author": "john"},
        {"author": "jane"}
    ],
    "$not": {"draft": true}
}
```

### Score Thresholding

```python
# Minimum similarity score
results = await retriever.search(
    query="...",
    min_score=0.7
)

# Dynamic threshold based on score distribution
results = await retriever.search(
    query="...",
    threshold_method="adaptive",
    min_score_delta=0.1  # Include results within 0.1 of top score
)
```

### Diversity Reranking

```python
from integrations.rag.retrieval import DiversityReranker

reranker = DiversityReranker(
    diversity_threshold=0.85,
    lambda_param=0.5  # Balance relevance vs diversity
)

# Results will be diverse (not all from same source)
results = await reranker.rerank(initial_results)
```

### Context Window Optimization

```python
from integrations.rag.retrieval import ContextOptimizer

optimizer = ContextOptimizer(
    max_tokens=4000,
    strategy="truncate"  # or "compress", "select"
)

# Optimize results to fit context window
optimized = await optimizer.optimize(results, max_tokens=4000)
```

## Performance Optimization

### Batch Search

```python
# Search multiple queries efficiently
results = await retriever.batch_search(
    queries=["query1", "query2", "query3"],
    collection="documents",
    top_k=10
)
```

### Caching

```python
from integrations.rag.retrieval import CachedRetriever

retriever = CachedRetriever(
    base_retriever=base_retriever,
    cache_type="redis",  # or "memory", "disk"
    ttl_seconds=3600
)

# Repeated queries hit cache
results = await retriever.search("frequent query")
```

### Embedding Pre-computation

```python
# Pre-compute query embeddings for batch processing
query_embeddings = await engine.embed_queries(queries)

# Use pre-computed embeddings
for query, embedding in zip(queries, query_embeddings):
    results = await engine.search_with_embedding(embedding)
```

## Integration with LangChain

```python
from langchain.retrievers import VectorStoreRetriever
from integrations.rag.vector_db import get_vector_db

# Use as LangChain retriever
vector_db = get_vector_db("milvus", host="localhost")
langchain_retriever = VectorStoreRetriever(
    vectorstore=vector_db,
    search_type="similarity",
    search_kwargs={"k": 10}
)
```

## Monitoring

```python
from integrations.rag.retrieval.monitoring import RetrievalMonitor

monitor = RetrievalMonitor()

# Track metrics
monitor.log_search(query, results, latency_ms)
monitor.log_rerank(initial_results, reranked_results)

# Get statistics
stats = monitor.get_stats()
print(f"Avg latency: {stats['avg_latency_ms']}ms")
print(f"Mean reciprocal rank: {stats['mrr']}")
```

## Testing

```bash
# Run retrieval tests
pytest integrations/rag/retrieval/tests/ -v

# Test specific component
pytest integrations/rag/retrieval/tests/test_reranker.py -v
```

## API Reference

- [Semantic Search API](./semantic_search/README.md)
- [Reranker API](./reranker/README.md)
- [Hybrid Search API](./hybrid_search/README.md)
