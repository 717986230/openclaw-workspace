"""
RAG Retrieval Engine - Main retriever implementation.
"""

from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import numpy as np
from datetime import datetime

from ..vector_db import get_vector_db, VectorDBBase, SearchResult


@dataclass
class RetrievalResult:
    """Enhanced retrieval result with metadata."""
    id: str
    content: str
    score: float
    embedding: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    rerank_score: Optional[float] = None
    retrieval_method: str = "semantic"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "score": self.score,
            "rerank_score": self.rerank_score,
            "metadata": self.metadata,
            "source": self.source,
            "retrieval_method": self.retrieval_method
        }


@dataclass
class RetrievalConfig:
    """Configuration for retrieval."""
    top_k: int = 10
    min_score: float = 0.0
    filter: Optional[Dict[str, Any]] = None
    include_vectors: bool = False
    include_metadata: bool = True
    
    # Hybrid search
    use_hybrid: bool = False
    vector_weight: float = 0.7
    keyword_weight: float = 0.3
    
    # Reranking
    rerank: bool = False
    rerank_top_k: int = 20
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Multi-query
    multi_query: bool = False
    num_queries: int = 3


class EmbeddingModel(ABC):
    """Abstract embedding model."""
    
    @abstractmethod
    async def embed(self, text: str) -> np.ndarray:
        """Embed single text."""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts."""
        pass


class OpenAIEmbedding(EmbeddingModel):
    """OpenAI embedding model."""
    
    def __init__(
        self,
        model: str = "text-embedding-ada-002",
        api_key: Optional[str] = None,
        batch_size: int = 32
    ):
        self.model = model
        self.api_key = api_key
        self.batch_size = batch_size
        self._client = None
    
    async def _get_client(self):
        """Get OpenAI client."""
        if self._client is None:
            import openai
            self._client = openai.AsyncOpenAI(api_key=self.api_key)
        return self._client
    
    async def embed(self, text: str) -> np.ndarray:
        """Embed single text."""
        embeddings = await self.embed_batch([text])
        return embeddings[0]
    
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple texts."""
        client = await self._get_client()
        
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = await client.embeddings.create(
                model=self.model,
                input=batch
            )
            
            for item in response.data:
                all_embeddings.append(np.array(item.embedding))
        
        return all_embeddings


class Reranker(ABC):
    """Abstract reranker."""
    
    @abstractmethod
    async def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int
    ) -> List[RetrievalResult]:
        """Rerank results."""
        pass


class CrossEncoderReranker(Reranker):
    """Cross-encoder based reranker."""
    
    def __init__(self, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model
        self._model = None
    
    def _load_model(self):
        """Load cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    async def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int
    ) -> List[RetrievalResult]:
        """Rerank using cross-encoder."""
        if not results:
            return results
        
        model = self._load_model()
        
        # Prepare pairs
        pairs = [(query, r.content) for r in results]
        
        # Score
        scores = model.predict(pairs)
        
        # Sort by score
        scored_results = list(zip(results, scores))
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Update rerank scores
        reranked = []
        for i, (result, score) in enumerate(scored[:top_k]):
            result.rerank_score = float(score)
            result.retrieval_method = "reranked"
            reranked.append(result)
        
        return reranked


class BaseRetriever(ABC):
    """Abstract base retriever."""
    
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents."""
        pass
    
    @abstractmethod
    async def retrieve_with_embedding(
        self,
        embedding: np.ndarray,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Retrieve using pre-computed embedding."""
        pass


class SemanticRetriever(BaseRetriever):
    """Semantic search retriever."""
    
    def __init__(
        self,
        vector_db: VectorDBBase,
        embedding_model: EmbeddingModel,
        collection: str
    ):
        self.vector_db = vector_db
        self.embedding_model = embedding_model
        self.collection = collection
    
    async def retrieve(
        self,
        query: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Retrieve using semantic search."""
        config = config or RetrievalConfig()
        
        # Get embedding
        embedding = await self.embedding_model.embed(query)
        
        return await self.retrieve_with_embedding(embedding, config)
    
    async def retrieve_with_embedding(
        self,
        embedding: np.ndarray,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Retrieve using embedding."""
        config = config or RetrievalConfig()
        
        # Search
        search_results = await self.vector_db.search(
            collection=self.collection,
            query_vector=embedding,
            top_k=config.top_k,
            filter=config.filter,
            include_vectors=config.include_vectors,
            include_metadata=config.include_metadata
        )
        
        # Convert to RetrievalResult
        results = []
        for sr in search_results:
            if sr.score < config.min_score:
                continue
            
            result = RetrievalResult(
                id=sr.id,
                content=sr.metadata.get("content", "") if sr.metadata else "",
                score=sr.score,
                embedding=sr.vector,
                metadata=sr.metadata or {},
                source=sr.metadata.get("source") if sr.metadata else None
            )
            results.append(result)
        
        return results


class HybridRetriever(BaseRetriever):
    """Hybrid search retriever combining vector and keyword search."""
    
    def __init__(
        self,
        vector_retriever: BaseRetriever,
        keyword_searcher: Optional[Any] = None,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        self.vector_retriever = vector_retriever
        self.keyword_searcher = keyword_searcher
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    async def retrieve(
        self,
        query: str,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Hybrid retrieval."""
        config = config or RetrievalConfig()
        
        # Get more results for fusion
        fetch_k = config.top_k * 2 if config.use_hybrid else config.top_k
        hybrid_config = RetrievalConfig(top_k=fetch_k, **{k: v for k, v in config.__dict__.items() if k != "top_k"})
        
        # Vector search
        vector_results = await self.vector_retriever.retrieve(query, hybrid_config)
        
        if not self.keyword_searcher or not config.use_hybrid:
            return vector_results[:config.top_k]
        
        # Keyword search (BM25)
        keyword_results = await self.keyword_searcher.search(query, fetch_k)
        
        # Reciprocal rank fusion
        fused = self._reciprocal_rank_fusion(
            vector_results,
            keyword_results,
            config.top_k
        )
        
        return fused
    
    async def retrieve_with_embedding(
        self,
        embedding: np.ndarray,
        config: Optional[RetrievalConfig] = None
    ) -> List[RetrievalResult]:
        """Retrieve with embedding (vector only)."""
        return await self