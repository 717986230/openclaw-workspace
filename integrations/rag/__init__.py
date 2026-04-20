"""
RAG Framework Integration for OpenClaw.

This module provides a comprehensive RAG (Retrieval-Augmented Generation)
framework including:
- Vector database abstraction (Milvus, ChromaDB, Pinecone, Weaviate)
- Retrieval systems (semantic, hybrid, multi-query)
- Knowledge base management (document loading, chunking, indexing)

Quick Start:
    from integrations.rag import KnowledgeBase
    
    kb = KnowledgeBase(
        name="my_knowledge",
        vector_db="chromadb"
    )
    await kb.initialize()
    
    # Add documents
    await kb.add_text("RAG combines retrieval with generation...")
    
    # Search
    results = await kb.search("What is RAG?")
"""

# Version
__version__ = "1.0.0"

# Knowledge Base
from .knowledge_base import KnowledgeBase, Document, Chunk

# Vector Database
from .vector_db import (
    VectorDBBase,
    DistanceMetric,
    IndexType,
    SearchResult,
    CollectionInfo,
    get_vector_db,
    list_vector_dbs,
    register_vector_db
)

# Retrieval
from .retrieval import (
    RetrievalResult,
    RetrievalConfig,
    EmbeddingModel,
    OpenAIEmbedding,
    Reranker,
    CrossEncoderReranker,
    BaseRetriever,
    SemanticRetriever,
    HybridRetriever
)

# Convenience imports
__all__ = [
    # Version
    "__version__",
    
    # Knowledge Base
    "KnowledgeBase",
    "Document",
    "Chunk",
    
    # Vector Database
    "VectorDBBase",
    "DistanceMetric",
    "IndexType",
    "SearchResult",
    "CollectionInfo",
    "get_vector_db",
    "list_vector_dbs",
    "register_vector_db",
    
    # Retrieval
    "RetrievalResult",
    "RetrievalConfig",
    "EmbeddingModel",
    "OpenAIEmbedding",
    "Reranker",
    "CrossEncoderReranker",
    "BaseRetriever",
    "SemanticRetriever",
    "HybridRetriever"
]
