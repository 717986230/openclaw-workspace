# RAG Framework Integration Guide

## Overview

RAG (Retrieval-Augmented Generation) enhances LLM capabilities by combining retrieval systems with generative AI. This integration provides a comprehensive RAG framework for OpenClaw.

## Architecture

```
integrations/rag/
├── INTEGRATION.md          # This file - integration guide
├── vector_db/              # Vector database integrations
│   ├── README.md
│   ├── milvus/            # Milvus vector DB
│   ├── pinecone/          # Pinecone integration
│   ├── weaviate/          # Weaviate integration
│   └── chromadb/          # ChromaDB integration
├── retrieval/              # Retrieval systems
│   ├── README.md
│   ├── semantic_search/   # Semantic search engine
│   ├── reranker/          # Result reranking
│   └── hybrid_search/     # Hybrid (keyword + vector) search
├── knowledge_base/         # Knowledge management
│   ├── README.md
│   ├── document_loader/   # Document loading & parsing
│   ├── chunking/          # Text chunking strategies
│   └── indexing/          # Index management
└── examples/              # Example implementations
    └── tests/             # Test files
```

## Core Components

### 1. Vector Database Integration

Supports multiple vector databases:
- **Milvus**: Enterprise-grade, highly scalable
- **Pinecone**: Fully managed, serverless option
- **Weaviate**: GraphQL-based, semantic search native
- **ChromaDB**: Lightweight, local-first

### 2. Retrieval System

Key features:
- Semantic similarity search
- Hybrid search (combining keyword and vector)
- Result reranking for improved relevance
- Multi-query retrieval strategies

### 3. Knowledge Base Management

Handles:
- Document ingestion from multiple sources
- Intelligent chunking strategies
- Embedding generation and storage
- Index lifecycle management

## Quick Start

### Installation

```bash
# Core dependencies
pip install langchain langchain-openai
pip install sentence-transformers
pip install faiss-cpu  # or faiss-gpu for GPU support

# Vector database (choose one)
pip install pymilvus
pip install pinecone-client
pip install weaviate-client
pip install chromadb
```

### Basic Usage

```python
from integrations.rag import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(
    vector_db="milvus",
    embedding_model="text-embedding-ada-002",
    collection_name="openclaw_knowledge"
)

# Index documents
rag.index_documents("./documents/")

# Query
results = rag.query("What is OpenClaw?")
print(results)
```

## Configuration

### Environment Variables

```bash
# OpenAI (for embeddings)
OPENAI_API_KEY=your_key

# Vector Database
MILVUS_HOST=localhost
MILVUS_PORT=19530

PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env

WEAVIATE_URL=http://localhost:8080
```

### Configuration File

```yaml
# config/rag_config.yaml
rag:
  vector_db:
    type: milvus
    host: ${MILVUS_HOST}
    port: ${MILVUS_PORT}
    
  embedding:
    model: text-embedding-ada-002
    dimension: 1536
    
  retrieval:
    top_k: 5
    rerank: true
    hybrid_search: false
    
  chunking:
    strategy: recursive
    chunk_size: 1000
    chunk_overlap: 200
```

## Integration Points

### With OpenClaw Memory System

```python
from integrations.rag.knowledge_base import KnowledgeBase
from openclaw.memory import MemoryStore

# Sync with memory
kb = KnowledgeBase()
kb.sync_with_memory(MemoryStore)
```

### With LangChain Integration

```python
from integrations.langchain import LangChainIntegration
from integrations.rag.retrieval import Retriever

# Use as LangChain retriever
retriever = Retriever.as_langchain_retriever()
chain = LangChainIntegration.create_qa_chain(retriever)
```

### With MemGPT Integration

```python
from integrations.memgpt import MemGPTIntegration
from integrations.rag.knowledge_base import KnowledgeBase

# Attach knowledge base to MemGPT agent
kb = KnowledgeBase.load("agent_knowledge")
agent = MemGPTIntegration.create_agent(knowledge_base=kb)
```

## Best Practices

### 1. Chunking Strategy
- Use recursive chunking for mixed content
- Adjust chunk_size based on content type
- Maintain overlap for context preservation

### 2. Embedding Selection
- Use domain-specific embeddings when available
- Consider multilingual models for diverse content
- Balance quality vs. inference speed

### 3. Retrieval Optimization
- Implement reranking for large result sets
- Use hybrid search for better recall
- Cache frequent queries

### 4. Index Management
- Regular index optimization
- Version control for embeddings
- Backup strategies for collections

## Monitoring & Observability

```python
from integrations.rag.monitoring import RAGMonitor

monitor = RAGMonitor()
monitor.track_query_latency()
monitor.track_retrieval_metrics()
monitor.track_embedding_usage()
```

## Troubleshooting

### Common Issues

1. **Connection errors**: Check vector DB service status
2. **Slow queries**: Optimize index, reduce top_k
3. **Poor relevance**: Adjust chunking, try different embeddings
4. **Memory issues**: Reduce batch size, use streaming

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## API Reference

See individual component READMEs for detailed API documentation:
- [Vector DB API](./vector_db/README.md)
- [Retrieval API](./retrieval/README.md)
- [Knowledge Base API](./knowledge_base/README.md)

## Examples

- [Basic RAG Pipeline](./examples/basic_rag.py)
- [Multi-language Support](./examples/multilingual.py)
- [Streaming RAG](./examples/streaming_rag.py)
- [Custom Embeddings](./examples/custom_embeddings.py)

## Contributing

To add new vector database support:
1. Create new directory under `vector_db/`
2. Implement standard interface (see `vector_db/base.py`)
3. Add tests in `examples/tests/`
4. Update this documentation

## License

Part of OpenClaw integration framework.
