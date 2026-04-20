"""
Knowledge Base Manager - Main entry point for knowledge base operations.
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import hashlib
import json
from datetime import datetime
import asyncio

from ..vector_db import get_vector_db, VectorDBBase, SearchResult
from ..retrieval import (
    EmbeddingModel,
    OpenAIEmbedding,
    RetrievalResult,
    RetrievalConfig
)


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List["Chunk"] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "chunk_count": len(self.chunks),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Chunk:
    """Represents a chunk of a document."""
    id: str
    document_id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    index: int = 0
    start_char: int = 0
    end_char: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "metadata": self.metadata,
            "index": self.index,
            "start_char": self.start_char,
            "end_char": self.end_char
        }


class KnowledgeBase:
    """
    Main knowledge base manager for RAG systems.
    
    Handles document ingestion, chunking, embedding, and retrieval.
    """
    
    def __init__(
        self,
        name: str,
        vector_db: str = "milvus",
        embedding_model: str = "text-embedding-ada-002",
        vector_db_config: Optional[Dict[str, Any]] = None,
        embedding_config: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        **kwargs
    ):
        """
        Initialize knowledge base.
        
        Args:
            name: Knowledge base name
            vector_db: Vector database type
            embedding_model: Embedding model name
            vector_db_config: Vector database configuration
            embedding_config: Embedding model configuration
            chunk_size: Default chunk size
            chunk_overlap: Default chunk overlap
            **kwargs: Additional configuration
        """
        self.name = name
        self.vector_db_type = vector_db
        self.vector_db_config = vector_db_config or {}
        self.embedding_model_name = embedding_model
        self.embedding_config = embedding_config or {}
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.kwargs = kwargs
        
        # Components
        self._vector_db: Optional[VectorDBBase] = None
        self._embedding_model: Optional[EmbeddingModel] = None
        self._document_store: Dict[str, Document] = {}
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the knowledge base."""
        # Initialize vector database
        self._vector_db = get_vector_db(
            self.vector_db_type,
            **self.vector_db_config
        )
        await self._vector_db.connect()
        
        # Create collection if not exists
        if not await self._vector_db.collection_exists(self.name):
            await self._vector_db.create_collection(
                name=self.name,
                dimension=1536,  # Default for ada-002
                **self.kwargs.get("collection_config", {})
            )
        
        # Initialize embedding model
        self._embedding_model = OpenAIEmbedding(
            model=self.embedding_model_name,
            **self.embedding_config
        )
        
        self._initialized = True
        return True
    
    async def _ensure_initialized(self):
        """Ensure knowledge base is initialized."""
        if not self._initialized:
            await self.initialize()
    
    # Document operations
    
    async def add_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """Add text to knowledge base."""
        await self._ensure_initialized()
        
        # Generate document ID
        doc_id = doc_id or self._generate_id(text)
        
        # Create document
        doc = Document(
            id=doc_id,
            content=text,
            metadata=metadata or {}
        )
        
        # Chunk document
        chunks = await self._chunk_document(doc)
        doc.chunks = chunks
        
        # Generate embeddings
        chunk_texts = [c.content for c in chunks]
        embeddings = await self._embedding_model.embed_batch(chunk_texts)
        
        # Store in vector DB
        chunk_vectors = [e for e in embeddings]
        chunk_metadatas = [
            {
                "document_id": doc_id,
                "chunk_index": c.index,
                "content": c.content,
                **c.metadata
            }
            for c in chunks
        ]
        chunk_ids = [c.id for c in chunks]
        
        await self._vector_db.insert(
            collection=self.name,
            vectors=chunk_vectors,
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        
        # Store document metadata
        self._document_store[doc_id] = doc
        
        return doc_id
    
    async def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> List[str]:
        """Add multiple documents."""
        doc_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_tasks = [self.add_text(d.content, d.metadata, d.id) for d in batch]
            batch_ids = await asyncio.gather(*batch_tasks)
            doc_ids.extend(batch_ids)
        
        return doc_ids
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        return self._document_store.get(doc_id)
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete document and its chunks."""
        await self._ensure_initialized()
        
        # Delete chunks from vector DB
        await self._vector_db.delete(
            collection=self.name,
            filter={"document_id": doc_id}
        )
        
        # Remove from document store
        if doc_id in self._document_store:
            del self._document_store[doc_id]
        
        return True
    
    # Search operations
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        min_score: float = 0.0
    ) -> List[RetrievalResult]:
        """Search the knowledge base."""
        await self._ensure_initialized()
        
        # Get query embedding
        query_embedding = await self._embedding_model.embed(query)
        
        # Search vector DB
        results = await self._vector_db.search(
            collection=self.name,
            query_vector=query_embedding,
            top_k=top_k,
            filter=filter,
            include_metadata=True
        )
        
        # Convert to RetrievalResult
        retrieval_results = []
        for result in results:
            if result.score < min_score:
                continue
            
            retrieval_result = RetrievalResult(
                id=result.id,
                content=result.metadata.get("content", ""),
                score=result.score,
                metadata=result.metadata,
                source=result.metadata.get("document_id")
            )
            retrieval_results.append(retrieval_result)
        
        return retrieval_results
    
    async def search_with_reranking(
        self,
        query: str,
        top_k: int = 10,
        rerank_top_k: int = 20
    ) -> List[RetrievalResult]:
        """Search with cross-encoder reranking."""
        from ..retrieval import CrossEncoderReranker
        
        await