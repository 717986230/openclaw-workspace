# RAG Integration Examples

This directory contains example code demonstrating how to use the RAG framework.

## Examples

### 1. Basic RAG Pipeline (`basic_rag.py`)

Demonstrates the simplest RAG setup:
- Initialize knowledge base
- Add documents
- Search and retrieve

```bash
python basic_rag.py
```

### 2. Vector Database Comparison (`vector_db_comparison.py`)

Benchmarks different vector databases:
- Insert performance
- Search latency
- Resource usage

```bash
python vector_db_comparison.py
```

### 3. Hybrid Search (`hybrid_search.py`)

Shows hybrid retrieval combining:
- Vector similarity
- Keyword matching (BM25)
- Result fusion

### 4. Multi-Query Retrieval (`multi_query.py`)

Demonstrates query expansion:
- Generate multiple query variations
- Aggregate results
- Improve recall

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_knowledge_base.py -v

# Run with coverage
pytest tests/ --cov=integrations.rag
```

## Example Usage

### Simple RAG

```python
import asyncio
from integrations.rag import KnowledgeBase

async def main():
    kb = KnowledgeBase(
        name="my_kb",
        vector_db="chromadb"
    )
    await kb.initialize()
    
    # Add documents
    await kb.add_text("Your content here...")
    
    # Search
    results = await kb.search("your query", top_k=5)
    
    for result in results:
        print(f"{result.score:.4f}: {result.content}")

asyncio.run(main())
```

### With Reranking

```python
from integrations.rag import KnowledgeBase, CrossEncoderReranker

kb = KnowledgeBase("kb", "chromadb")
await kb.initialize()

# Get initial results
results = await kb.search("query", top_k=20)

# Rerank
reranker = CrossEncoderReranker()
reranked = await reranker.rerank("query", results, top_k=5)
```

### Custom Embeddings

```python
from integrations.rag.retrieval import EmbeddingModel
import numpy as np

class MyEmbedding(EmbeddingModel):
    async def embed(self, text: str) -> np.ndarray:
        # Your embedding logic
        return your_model.encode(text)
    
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        return [self.embed(t) for t in texts]

# Use custom embedding
kb = KnowledgeBase(
    "kb",
    "chromadb",
    embedding_model=MyEmbedding()
)
```

## Configuration Examples

### Minimal (Development)

```yaml
rag:
  vector_db: chromadb
  persist_directory: ./data
```

### Production

```yaml
rag:
  vector_db: milvus
  host: milvus.example.com
  port: 19530
  
  embedding:
    model: text-embedding-ada-002
    
  retrieval:
    top_k: 10
    rerank: true
    
  knowledge_base:
    chunk_size: 1000
    chunk_overlap: 200
```
