"""
检索管理器 - Retrieval Manager
统一管理检索策略和配置
"""

from typing import List, Dict, Any, Tuple, Optional
from enum import Enum
from .semantic_retriever import SemanticRetriever, OpenAIEmbeddingProvider
from .keyword_retriever import KeywordRetriever
from .hybrid_retriever import HybridRetriever


class RetrievalMethod(str, Enum):
    """检索方法"""
    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    ADAPTIVE = "adaptive"


class RetrievalManager:
    """
    检索管理器
    
    统一管理不同的检索策略，提供统一的接口
    """
    
    def __init__(
        self,
        default_method: RetrievalMethod = RetrievalMethod.HYBRID,
        embedding_model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None
    ):
        """
        初始化检索管理器
        
        Args:
            default_method: 默认检索方法
            embedding_model: 嵌入模型
            api_key: API 密钥
            api_base: API 基础 URL
        """
        self.default_method = default_method
        
        # 初始化各个检索器
        embedding_provider = OpenAIEmbeddingProvider(
            model=embedding_model,
            api_key=api_key,
            api_base=api_base
        )
        
        self.semantic_retriever = SemanticRetriever(
            embedding_provider=embedding_provider
        )
        self.keyword_retriever = KeywordRetriever()
        self.hybrid_retriever = HybridRetriever(
            semantic_retriever=self.semantic_retriever,
            keyword_retriever=self.keyword_retriever
        )
        
        # 配置
        self.config = {
            "default_top_k": 10,
            "semantic_threshold": 0.7,
            "cache_embeddings": True,
            "cache_size": 1000
        }
    
    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        method: Optional[RetrievalMethod] = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        统一搜索接口
        
        Args:
            query: 查询文本
            documents: 文档列表
            method: 检索方法
            top_k: 返回数量
            filters: 过滤条件
            
        Returns:
            [(document, score), ...]
        """
        method = method or self.default_method
        
        # 应用过滤
        if filters:
            documents = self._apply_filters(documents, filters)
        
        if not documents:
            return []
        
        # 根据方法调用不同检索器
        if method == RetrievalMethod.SEMANTIC:
            results = self.semantic_retriever.search(
                query=query,
                documents=documents,
                top_k=top_k
            )
        elif method == RetrievalMethod.KEYWORD:
            # 清空并重建索引
            self.keyword_retriever.clear()
            self.keyword_retriever.index_documents(documents)
            results = self.keyword_retriever.search(
                query=query,
                top_k=top_k
            )
        elif method == RetrievalMethod.HYBRID:
            results = self.hybrid_retriever.search(
                query=query,
                documents=documents,
                top_k=top_k
            )
        elif method == RetrievalMethod.ADAPTIVE:
            results = self.hybrid_retriever.adaptive_search(
                query=query,
                documents=documents,
                top_k=top_k
            )
        else:
            results = []
        
        return results
    
    def _apply_filters(
        self,
        documents: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        应用过滤条件
        
        Args:
            documents: 文档列表
            filters: 过滤条件
            
        Returns:
            过滤后的文档列表
        """
        filtered = documents
        
        # 类别过滤
        if "category" in filters:
            category = filters["category"]
            filtered = [
                d for d in filtered
                if d.get("category") == category
            ]
        
        # 重要性过滤
        if "min_importance" in filters:
            min_imp = filters["min_importance"]
            filtered = [
                d for d in filtered
                if d.get("importance", 0) >= min_imp
            ]
        
        # 时间范围过滤
        if "date_from" in filters or "date_to" in filters:
            from datetime import datetime
            date_from = filters.get("date_from")
            date_to = filters.get("date_to")
            
            def check_date(doc):
                doc_date = doc.get("created_at") or doc.get("timestamp")
                if not doc_date:
                    return True
                
                if isinstance(doc_date, str):
                    doc_date = datetime.fromisoformat(doc_date)
                
                if date_from:
                    if isinstance(date_from, str):
                        date_from_dt = datetime.fromisoformat(date_from)
                    else:
                        date_from_dt = date_from
                    if doc_date < date_from_dt:
                        return False
                
                if date_to:
                    if isinstance(date_to, str):
                        date_to_dt = datetime.fromisoformat(date_to)
                    else:
                        date_to_dt = date_to
                    if doc_date > date_to_dt:
                        return False
                
                return True
            
            filtered = [d for d in filtered if check_date(d)]
        
        # 标签过滤
        if "tags" in filters:
            required_tags = set(filters["tags"])
            filtered = [
                d for d in filtered
                if required_tags.issubset(set(d.get("tags", [])))
            ]
        
        return filtered
    
    def search_by_category(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        category: str,
        top_k: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """按类别搜索"""
        return self.search(
            query=query,
            documents=documents,
            top_k=top_k,
            filters={"category": category}
        )
    
    def search_recent(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        days: int = 7,
        top_k: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """搜索最近的文档"""
        from datetime import datetime, timedelta
        
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        return self.search(
            query=query,
            documents=documents,
            top_k=top_k,
            filters={"date_from": date_from}
        )
    
    def search_high_importance(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        min_importance: float = 0.7,
        top_k: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """搜索高重要性文档"""
        return self.search(
            query=query,
            documents=documents,
            top_k=top_k,
            filters={"min_importance": min_importance}
        )
    
    def multi_query_search(
        self,
        queries: List[str],
        documents: List[Dict[str, Any]],
        method: RetrievalMethod = RetrievalMethod.SEMANTIC,
        top_k_per_query: int = 5,
        merge_strategy: str = "union"
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        多查询搜索
        
        Args:
            queries: 查询列表
            documents: 文档列表
            method: 检索方法
            top_k_per_query: 每个查询返回的数量
            merge_strategy: 合并策略 (union, intersect, weighted)
            
        Returns:
            合并后的结果
        """
        all_results = []
        
        for query in queries:
            results = self.search(
                query=query,
                documents=documents,
                method=method,
                top_k=top_k_per_query
            )
            all_results.append(results)
        
        # 合并结果
        if merge_strategy == "union":
            return self._merge_union(all_results)
        elif merge_strategy == "intersect":
            return self._merge_intersect(all_results)
        elif merge_strategy == "weighted":
            return self._merge_weighted(all_results, len(queries))
        else:
            return all_results[0] if all_results else []
    
    def _merge_union(
        self,
        results: List[List[Tuple[Dict[str, Any], float]]]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """合并策略：取并集"""
        merged: Dict[int, Tuple[Dict[str, Any], float, int]] = {}
        
        for query_results in results:
            for doc, score in query_results:
                doc_id = id(doc)
                if doc_id in merged:
                    # 保留最高分
                    _, existing_score, count = merged[doc_id]
                    merged[doc_id] = (doc, max(existing_score, score), count + 1)
                else:
                    merged[doc_id] = (doc, score, 1)
        
        # 按分数排序
        final = [(doc, score) for doc, score, _ in merged.values()]
        final.sort(key=lambda x: x[1], reverse=True)
        return final
    
    def _merge_intersect(
        self,
        results: List[List[Tuple[Dict[str, Any], float]]]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """合并策略：取交集"""
        if not results:
            return []
        
        # 找出所有查询都返回的文档
        doc_appearances: Dict[int, int] = {}
        
        for query_results in results:
            seen = set()
            for doc, _ in query_results:
                doc_id = id(doc)
                if doc_id not in seen:
                    doc_appearances[doc_id] = doc_appearances.get(doc_id, 0) + 1
                    seen.add(doc_id)
        
        total_queries = len(results)
        
        # 只保留在所有查询中出现的文档
        final = []
        for query_results in results:
            for doc, score in query_results:
                if doc_appearances.get(id(doc), 0) == total_queries:
                    final.append((doc, score))
        
        # 去重并排序
        seen = set()
        unique = []
        for doc, score in final:
            if id(doc) not in seen:
                seen.add(id(doc))
                unique.append((doc, score))
        
        unique.sort(key=lambda x: x[1], reverse=True)
        return unique
    
    def _merge_weighted(
        self,
        results: List[List[Tuple[Dict[str, Any], float]]],
        total_queries: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """合并策略：加权平均"""
        doc_scores: Dict[int, Tuple[Dict[str, Any], float, int]] = {}
        
        for i, query_results in enumerate(results):
            # 第一个查询权重更高
            weight = 1.5 if i == 0 else 1.0
            
            for doc, score in query_results:
                doc_id = id(doc)
                if doc_id in doc_scores:
                    _, total_score, count = doc_scores[doc_id]
                    doc_scores[doc_id] = (doc, total_score + score * weight, count + weight)
                else:
                    doc_scores[doc_id] = (doc, score * weight, weight)
        
        # 计算加权平均
        final = [
            (doc, total_score / count)
            for doc, total_score, count in doc_scores.values()
        ]
        final.sort(key=lambda x: x[1], reverse=True)
        return final
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "default_method": self.default_method.value,
            "config": self.config,
            "semantic_retriever": self.semantic_retriever.get_stats(),
            "keyword_retriever": self.keyword_retriever.get_index_stats(),
            "hybrid_retriever": self.hybrid_retriever.get_stats()
        }
    
    def clear_caches(self):
        """清空所有缓存"""
        self.semantic_retriever.clear_cache()
        self.keyword_retriever.clear()
