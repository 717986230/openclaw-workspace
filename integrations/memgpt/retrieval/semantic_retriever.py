"""
语义检索器 - Semantic Retriever
基于向量嵌入的相似度搜索
"""

from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
import numpy as np


class EmbeddingProvider(ABC):
    """嵌入提供者基类"""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI 嵌入提供者"""
    
    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        初始化 OpenAI 嵌入提供者
        
        Args:
            model: 模型名称
            api_key: API 密钥
            api_base: API 基础 URL
        """
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """生成嵌入向量"""
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
            
            response = client.embeddings.create(
                model=self.model,
                input=texts
            )
            
            return [item.embedding for item in response.data]
        except Exception as e:
            print(f"Embedding error: {e}")
            # 降级到简单哈希嵌入
            return self._fallback_embed(texts)
    
    def _fallback_embed(self, texts: List[str]) -> List[List[float]]:
        """降级嵌入方法"""
        import hashlib
        
        embeddings = []
        for text in texts:
            # 使用哈希生成简单向量
            hash_bytes = hashlib.sha256(text.encode()).digest()
            vector = [b / 255.0 for b in hash_bytes[:64]]
            # 归一化
            norm = np.sqrt(sum(v * v for v in vector))
            if norm > 0:
                vector = [v / norm for v in vector]
            embeddings.append(vector)
        
        return embeddings


class SemanticRetriever:
    """
    语义检索器
    
    特点：
    - 基于向量相似度
    - 支持多种嵌入模型
    - 高效的近似最近邻搜索
    """
    
    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        similarity_threshold: float = 0.7
    ):
        """
        初始化语义检索器
        
        Args:
            embedding_provider: 嵌入提供者
            similarity_threshold: 相似度阈值
        """
        self.embedding_provider = embedding_provider or OpenAIEmbeddingProvider()
        self.similarity_threshold = similarity_threshold
        self._embedding_cache: Dict[str, List[float]] = {}
        self._cache_size_limit = 1000
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的嵌入向量（带缓存）
        
        Args:
            text: 输入文本
            
        Returns:
            嵌入向量
        """
        # 检查缓存
        cache_key = text[:100]  # 使用前100字符作为键
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        # 生成嵌入
        embeddings = self.embedding_provider.embed([text])
        embedding = embeddings[0] if embeddings else []
        
        # 缓存
        if len(self._embedding_cache) < self._cache_size_limit:
            self._embedding_cache[cache_key] = embedding
        
        return embedding
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量获取嵌入"""
        # 分离已缓存和未缓存的
        uncached_texts = []
        uncached_indices = []
        results = [None] * len(texts)
        
        for i, text in enumerate(texts):
            cache_key = text[:100]
            if cache_key in self._embedding_cache:
                results[i] = self._embedding_cache[cache_key]
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # 批量生成未缓存的嵌入
        if uncached_texts:
            new_embeddings = self.embedding_provider.embed(uncached_texts)
            for idx, embedding in zip(uncached_indices, new_embeddings):
                results[idx] = embedding
                # 更新缓存
                if len(self._embedding_cache) < self._cache_size_limit:
                    self._embedding_cache[uncached_texts[idx][:100]] = embedding
        
        return results
    
    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10,
        threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        语义搜索
        
        Args:
            query: 查询文本
            documents: 文档列表（每个需要有 'embedding' 或 'content' 字段）
            top_k: 返回数量
            threshold: 相似度阈值
            
        Returns:
            [(document, similarity), ...]
        """
        if not documents:
            return []
        
        threshold = threshold or self.similarity_threshold
        
        # 获取查询嵌入
        query_embedding = self.get_embedding(query)
        
        # 计算相似度
        results = []
        for doc in documents:
            # 获取文档嵌入
            if "embedding" in doc and doc["embedding"]:
                doc_embedding = doc["embedding"]
            elif "content" in doc:
                doc_embedding = self.get_embedding(doc["content"])
            else:
                continue
            
            # 计算余弦相似度
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            
            if similarity >= threshold:
                results.append((doc, similarity))
        
        # 排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def batch_search(
        self,
        queries: List[str],
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[List[Tuple[Dict[str, Any], float]]]:
        """
        批量搜索
        
        Args:
            queries: 查询列表
            documents: 文档列表
            top_k: 每个查询返回的数量
            
        Returns:
            每个查询的结果列表
        """
        # 预计算所有嵌入
        query_embeddings = self.get_embeddings(queries)
        
        doc_embeddings = []
        for doc in documents:
            if "embedding" in doc and doc["embedding"]:
                doc_embeddings.append(doc["embedding"])
            elif "content" in doc:
                doc_embeddings.append(self.get_embedding(doc["content"]))
            else:
                doc_embeddings.append(None)
        
        # 计算相似度矩阵
        results = []
        for q_emb in query_embeddings:
            doc_scores = []
            for i, d_emb in enumerate(doc_embeddings):
                if d_emb:
                    similarity = self._cosine_similarity(q_emb, d_emb)
                    doc_scores.append((documents[i], similarity))
            
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            results.append(doc_scores[:top_k])
        
        return results
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        arr1 = np.array(vec1)
        arr2 = np.array(vec2)
        
        dot_product = np.dot(arr1, arr2)
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def clear_cache(self):
        """清空嵌入缓存"""
        self._embedding_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "cache_size": len(self._embedding_cache),
            "cache_limit": self._cache_size_limit,
            "similarity_threshold": self.similarity_threshold,
            "embedding_provider": type(self.embedding_provider).__name__
        }
