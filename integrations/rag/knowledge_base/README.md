# Knowledge Base Management

## Overview

The knowledge base module handles document ingestion, chunking, embedding generation, and index management for RAG systems.

## Architecture

```
knowledge_base/
├── README.md              # This file
├── document_loader/       # Document loading and parsing
│   ├── base.py           # Base document loader
│   ├── file_loader.py    # File-based loaders (PDF, TXT, MD, etc.)
│   ├── web_loader.py     # Web page loader
│   └── database_loader.py # Database source loader
├── chunking/              # Text chunking strategies
│   ├── base.py           # Chunking interface
│   ├── recursive.py      # Recursive chunking
│   ├── semantic.py       # Semantic chunking
│   └── fixed_size.py     # Fixed-size chunking
├── indexing/              # Index management
│   ├── manager.py        # Index lifecycle manager
│   ├── sync.py           # Synchronization utilities
│   └── versioning.py     # Index versioning
└── manager.py             # Main KnowledgeBase manager
```

## Quick Start

### Create Knowledge Base

```python
from integrations.rag.knowledge_base import KnowledgeBase

# Initialize knowledge base
kb = KnowledgeBase(
    name="my_knowledge",
    vector_db="milvus",
    embedding_model="text-embedding-ada-002"
)

# Create collection
await kb.initialize()
```

### Ingest Documents

```python
# From files
await kb.ingest_directory(
    "./documents/",
    recursive=True,
    file_types=[".pdf", ".md", ".txt"]
)

# From single file
await kb.ingest_file("./report.pdf")

# From web
await kb.ingest_web("https://docs.example.com/guide")

# From raw text
await kb.add_text(
    "Machine learning is a subset of AI...",
    metadata={"source": "guide", "section": "intro"}
)
```

### Query Knowledge Base

```python
# Search
results = await kb.search("What is machine learning?", top_k=5)

# Get specific document
doc = await kb.get_document(doc_id="abc123")

# List documents
docs = await kb.list_documents(limit=100, offset=0)
```

## Document Loading

### Supported Formats

| Format | Loader | Features |
|--------|--------|----------|
| PDF | PyPDFLoader | Page extraction, OCR support |
| Markdown | MarkdownLoader | Headers, code blocks |
| HTML | HTMLLoader | Boilerplate removal |
| TXT | TextLoader | Encoding detection |
| DOCX | DocxLoader | Tables, formatting |
| CSV | CSVLoader | Row-based chunking |
| JSON | JSONLoader | Schema extraction |
| Code | CodeLoader | AST-aware chunking |

### File Loader Usage

```python
from integrations.rag.knowledge_base.document_loader import (
    PDFLoader,
    MarkdownLoader,
    TextLoader
)

# Load PDF
loader = PDFLoader()
documents = await loader.load("./report.pdf")

# Each document has:
# - content: str
# - metadata: Dict (source, page, etc.)
# - id: str (auto-generated)

# Load with options
loader = MarkdownLoader(
    remove_code_blocks=False,
    extract_headers=True
)
documents = await loader.load("./guide.md")
```

### Web Loading

```python
from integrations.rag.knowledge_base.document_loader import WebLoader

loader = WebLoader(
    remove_boilerplate=True,
    follow_links=False,
    timeout=30
)

# Load single page
docs = await loader.load("https://example.com/article")

# Load with depth
docs = await loader.load_crawl(
    start_url="https://docs.example.com",
    max_depth=2,
    max_pages=100
)
```

### Database Loading

```python
from integrations.rag.knowledge_base.document_loader import DatabaseLoader

loader = DatabaseLoader(
    connection_string="postgresql://user:pass@localhost/db",
    query="SELECT id, content, metadata FROM articles WHERE published = true"
)

documents = await loader.load()
```

## Chunking Strategies

### Recursive Chunking (Default)

```python
from integrations.rag.knowledge_base.chunking import RecursiveChunker

chunker = RecursiveChunker(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = chunker.chunk(document)
```

### Semantic Chunking

```python
from integrations.rag.knowledge_base.chunking import SemanticChunker

# Uses embedding similarity to find natural boundaries
chunker = SemanticChunker(
    embedding_model="text-embedding-ada-002",
    similarity_threshold=0.8
)

chunks = chunker.chunk(document)
```

### Fixed-Size Chunking

```python
from integrations.rag.knowledge_base.chunking import FixedSizeChunker

chunker = FixedSizeChunker(
    chunk_size=512,
    overlap=50
)

chunks = chunker.chunk(document)
```

### Code-Aware Chunking

```python
from integrations.rag.knowledge_base.chunking import CodeChunker

# Respects function/class boundaries
chunker = CodeChunker(
    language="python",
    max_chunk_size=500
)

chunks = chunker.chunk(code_document)
```

## Index Management

### Creating Index

```python
from integrations.rag.knowledge_base import IndexManager

manager = IndexManager(
    vector_db="milvus",
    collection="knowledge_base"
)

# Create with settings
await manager.create_index(
    dimension=1536,
    metric="cosine",
    index_type="HNSW"
)
```

### Updating Index

```python
# Add documents
await manager.add_documents(documents)

# Remove documents
await manager.remove_documents(doc_ids)

# Rebuild index
await manager.rebuild_index()
```

### Index Versioning

```python
# Create versioned index
await manager.create_version(
    version="v1.0",
    description="Initial index"
)

# List versions
versions = await manager.list_versions()

# Rollback to previous version
await manager.rollback("v0.9")
```

### Synchronization

```python
from integrations.rag.knowledge_base.indexing import IndexSync

sync = IndexSync(knowledge_base=kb)

# Sync with file system changes
await sync.sync_directory("./documents/")

# Incremental sync (only changed files)
await sync.incremental_sync()

# Verify integrity
issues = await sync.verify()
```

## Knowledge Base Operations

### Search with Filters

```python
# Metadata filtering
results = await kb.search(
    query="machine learning",
    filter={
        "category": "tutorial",
        "year": {"$gte": 2023}
    }
)

# Source filtering
results = await kb.search(
    query="neural networks",
    sources=["wikipedia", "arxiv"]
)
```

### Document Management

```python
# Get document with chunks
doc = await kb.get_document(doc_id, include_chunks=True)

# Update document
await kb.update_document(
    doc_id,
    metadata={"verified": True}
)

# Delete document
await kb.delete_document(doc_id)

# Batch operations
await kb.batch_delete(filter={"obsolete": True})
```

### Statistics

```python
# Get knowledge base stats
stats = await kb.get_stats()
print(f"Documents: {stats['document_count']}")
print(f"Total chunks: {stats['chunk_count']}")
print(f"Index size: {stats['index_size_mb']} MB")
```

## Configuration

```yaml
knowledge_base:
  name: default
  
  document_loader:
    default_encoding: utf-8
    pdf:
      extract_images: false
      ocr_enabled: false
    markdown:
      extract_headers: true
      
  chunking:
    strategy: recursive
    chunk_size: 1000
    chunk_overlap: 200
    
  indexing:
    dimension: 1536
    metric: cosine
    index_type: HNSW
    auto_reindex: true
    reindex_threshold: 10000
```

## Integration Examples

### With OpenClaw Memory

```python
from integrations.rag.knowledge_base import KnowledgeBase
from openclaw.memory import MemoryStore

kb = KnowledgeBase("openclaw_memory")

# Sync with memory
await kb.sync_from_memory(MemoryStore)

# Search memory via RAG
results = await kb.search("past decisions about API design")
```

### With LangChain

```python
from langchain.retrievers import VectorStoreRetriever
from integrations.rag.knowledge_base import KnowledgeBase

kb = KnowledgeBase("langchain_kb")

# Convert to LangChain retriever
lc_retriever = kb.as_langchain_retriever(
    search_type="similarity",
    search_kwargs={"k": 10}
)
```

## Performance Tips

1. **Batch Operations**: Use batch insert for better throughput
2. **Chunking Strategy**: Choose based on content type
3. **Embedding Caching**: Cache embeddings for repeated documents
4. **Incremental Updates**: Use incremental sync for large corpora
5. **Index Optimization**: Rebuild index periodically for performance

## Monitoring

```python
from integrations.rag.knowledge_base.monitoring import KBMonitor

monitor = KBMonitor(kb)

# Track metrics
monitor.track_ingestion_rate()
monitor.track_search_latency()
monitor.track_index_health()

# Get report
report = monitor.get_report()
```

## Testing

```bash
# Run knowledge base tests
pytest integrations/rag/knowledge_base/tests/ -v

# Test specific component
pytest integrations/rag/knowledge_base/tests/test_chunking.py -v
```

## API Reference

- [Document Loader API](./document_loader/README.md)
- [Chunking API](./chunking/README.md)
- [Indexing API](./indexing/README.md)
