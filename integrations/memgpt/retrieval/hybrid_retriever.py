"""
混合检索器 - Hybrid Retriever
融合多种检索策略
"""

from typing import List, Dict, Any, Tuple, Optional
from .semantic_retriever import SemanticRetriever
from .keyword_retriever import KeywordRetriever


class HybridRetriever:
    """
    混合检索器
    
    特点：
    - 融合语义检索和关键词检索
    - 可配置权重
    - 支持重排序
    - 自适应融合策略
    """
    
    def __init__(
        self,
        semantic_retriever: Optional[SemanticRetriever] = None,
        keyword_retriever: Optional[KeywordRetriever] = None,
        semantic_weight: float = 0.6,
        keyword_weight: float = 0.4,
        rerank: bool = True
    ):
        """
        初始化混合检索器
        
        Args:
            semantic_retriever: 语义检索器
            keyword_retriever: 关键词检索器
            semantic_weight: 语义检索权重
            keyword_weight: 关键词检索权重
            rerank: 是否重排序
        """
        self.semantic_retriever = semantic_retriever or SemanticRetriever()
        self.keyword_retriever = keyword_retriever or KeywordRetriever()
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight
        self.rerank = rerank
    
    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10,
        semantic_top_k: int = 20,
        keyword_top_k: int = 20
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        混合搜索
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 最终返回数量
            semantic_top_k: 语义检索候选数量
            keyword_top_k: 关键词检索候选数量
            
        Returns:
            [(document, combined_score), ...]
        """
        if not documents:
            return []
        
        # 归一化权重
        total_weight = self.semantic_weight + self.keyword_weight
        norm_semantic_weight = self.semantic_weight / total_weight
        norm_keyword_weight = self.keyword_weight / total_weight
        
        # 语义检索
        semantic_results = self.semantic_retriever.search(
            query=query,
            documents=documents,
            top_k=semantic_top_k
        )
        
        # 关键词检索（需要先索引）
        self.keyword_retriever.clear()
        for doc in documents:
            self.keyword_retriever.index_document(doc)
        
        keyword_results = self.keyword_retriever.search(
            query=query,
            top_k=keyword_top_k
        )
        
        # 融合结果
        combined_scores: Dict[int, Tuple[Dict[str, Any], float, float]] = {}
        
        # 语义得分
        for doc, score in semantic_results:
            doc_id = id(doc)
            if doc_id not in combined_scores:
                combined_scores[doc_id] = (doc, 0.0, 0.0)
            _, s_score, k_score = combined_scores[doc_id]
            combined_scores[doc_id] = (doc, score, k_score)
        
        # 关键词得分
        for doc, score in keyword_results:
            doc_id = id(doc)
            if doc_id not in combined_scores:
                combined_scores[doc_id] = (doc, 0.0, 0.0)
            _, s_score, k_score = combined_scores[doc_id]
            combined_scores[doc_id] = (doc, s_score, score)
        
        # 计算综合得分
        final_results = []
        for doc, s_score, k_score in combined_scores.values():
            combined = (
                s_score * norm_semantic_weight +
                k_score * norm_keyword_weight
            )
            final_results.append((doc, combined))
        
        # 排序
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        # 重排序
        if self.rerank and len(final_results) > top_k:
            final_results = self._rerank(query, final_results, top_k)
        
        return final_results[:top_k]
    
    def _rerank(
        self,
        query: str,
        results: List[Tuple[Dict[str, Any], float]],
        top_k: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        重排序结果
        
        Args:
            query: 查询文本
            results: 初步结果
            top_k: 目标数量
            
        Returns:
            重排序后的结果
        """
        # 简单的重排序策略：
        # 1. 提升精确匹配
        # 2. 提升查询词覆盖率
        
        query_words = set(query.lower().split())
        
        reranked = []
        for doc, score in results:
            content = doc.get("content", "").lower()
            
            # 精确匹配加分
            exact_match_bonus = 0.0
            if query.lower() in content:
                exact_match_bonus = 0.2
            
            # 词覆盖率加分
            content_words = set(content.split())
            coverage = len(query_words & content_words) / len(query_words) if query_words else 0
            coverage_bonus = coverage * 0.1
            
            final_score = score + exact_match_bonus + coverage_bonus
            reranked.append((doc, final_score))
        
        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:top_k]
    
    def adaptive_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        自适应混合搜索
        
        根据查询特征自动调整权重
        
        Args:
            query: 查询文本
            documents: 文档列表
            top_k: 返回数量
            
        Returns:
            [(document, score), ...]
        """
        # 分析查询特征
        query_length = len(query.split())
        has_special_chars = any(c in query for c in ['"', "'", '*', '?'])
        is_question = query.strip().endswith('?')
        
        # 调整权重
        if has_special_chars:
            # 精确查询，偏向关键词
            self.semantic_weight = 0.3
            self.keyword_weight = 0.7
        elif query_length <= 3:
            # 短查询，偏向关键词
            self.semantic_weight = 0.4
            self.keyword_weight = 0.6
        elif is_question:
            # 问题，偏向语义
            self.semantic_weight = 0.7
            self.keyword_weight = 0.3
        else:
            # 默认权重
            self.semantic_weight = 0.6
            self.keyword_weight = 0.4
        
        return self.search(query, documents, top_k)
    
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
        results = []
        for query in queries:
            query_results = self.search(query, documents, top_k)
            results.append(query_results)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "rerank_enabled": self.rerank,
            "semantic_retriever": self.semantic_retriever.get_stats(),
            "keyword_retriever": self.keyword_retriever.get_index_stats()
        }
