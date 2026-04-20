"""
关键词检索器 - Keyword Retriever
传统全文搜索和关键词匹配
"""

from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
import re


class KeywordRetriever:
    """
    关键词检索器
    
    特点：
    - 基于词频的检索
    - 支持布尔查询
    - 支持通配符
    - 支持短语匹配
    """
    
    def __init__(
        self,
        min_word_length: int = 2,
        stop_words: Optional[Set[str]] = None
    ):
        """
        初始化关键词检索器
        
        Args:
            min_word_length: 最小词长
            stop_words: 停用词集合
        """
        self.min_word_length = min_word_length
        self.stop_words = stop_words or self._default_stop_words()
        self._index: Dict[str, List[Tuple[int, int]]] = defaultdict(list)  # word -> [(doc_id, position)]
        self._documents: Dict[int, Dict[str, Any]] = {}  # doc_id -> document
        self._doc_counter = 0
    
    def _default_stop_words(self) -> Set[str]:
        """默认停用词（中英文混合）"""
        return {
            # 英文停用词
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might",
            "this", "that", "these", "those", "it", "its", "they", "them", "their",
            "he", "she", "him", "her", "his", "hers", "we", "us", "our", "you", "your",
            # 中文停用词
            "的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一",
            "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有",
            "看", "好", "自己", "这", "那", "什么", "他", "她", "它", "们", "这个"
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 输入文本
            
        Returns:
            词列表
        """
        # 转小写
        text = text.lower()
        
        # 简单分词（支持中英文混合）
        # 英文单词
        words = re.findall(r"[a-z]+", text)
        
        # 中文字符（每个字作为词，或使用简单的二字切分）
        chinese_chars = re.findall(r"[\u4e00-\u9fff]+", text)
        for chars in chinese_chars:
            if len(chars) >= 4:
                # 二字切分
                for i in range(len(chars) - 1):
                    words.append(chars[i:i+2])
            else:
                words.append(chars)
        
        # 过滤
        words = [
            w for w in words
            if len(w) >= self.min_word_length and w not in self.stop_words
        ]
        
        return words
    
    def index_document(self, document: Dict[str, Any]) -> int:
        """
        索引文档
        
        Args:
            document: 文档对象（需要有 'content' 字段）
            
        Returns:
            文档ID
        """
        doc_id = self._doc_counter
        self._doc_counter += 1
        
        content = document.get("content", "")
        words = self.tokenize(content)
        
        # 记录位置
        for position, word in enumerate(words):
            self._index[word].append((doc_id, position))
        
        self._documents[doc_id] = document
        
        return doc_id
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> List[int]:
        """批量索引文档"""
        return [self.index_document(doc) for doc in documents]
    
    def remove_document(self, doc_id: int) -> bool:
        """移除文档"""
        if doc_id not in self._documents:
            return False
        
        # 从索引中移除
        for word in list(self._index.keys()):
            self._index[word] = [
                (d, p) for d, p in self._index[word] if d != doc_id
            ]
            if not self._index[word]:
                del self._index[word]
        
        del self._documents[doc_id]
        return True
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        exact_match: bool = False
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        关键词搜索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            exact_match: 是否精确匹配
            
        Returns:
            [(document, score), ...]
        """
        query_words = self.tokenize(query)
        
        if not query_words:
            return []
        
        # 计算文档得分
        doc_scores: Dict[int, float] = defaultdict(float)
        doc_matches: Dict[int, Set[str]] = defaultdict(set)
        
        for word in query_words:
            if word in self._index:
                for doc_id, position in self._index[word]:
                    doc_scores[doc_id] += 1.0
                    doc_matches[doc_id].add(word)
        
        # 精确匹配：需要所有词都匹配
        if exact_match:
            required_words = set(query_words)
            doc_scores = {
                doc_id: score
                for doc_id, score in doc_scores.items()
                if doc_matches[doc_id] >= required_words
            }
        
        # 归一化得分
        max_score = max(doc_scores.values()) if doc_scores else 1.0
        results = [
            (self._documents[doc_id], score / max_score)
            for doc_id, score in doc_scores.items()
        ]
        
        # 排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_boolean(
        self,
        query: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        布尔搜索
        
        支持操作符：AND, OR, NOT
        例如："python AND (web OR api) NOT django"
        
        Args:
            query: 布尔查询
            top_k: 返回数量
            
        Returns:
            文档列表
        """
        # 解析布尔表达式
        # 简化版：只支持 AND, OR, NOT
        query = query.upper()
        
        # 分割
        tokens = re.split(r"\s+(AND|OR|NOT)\s+", query)
        
        # 收集必须包含和排除的词
        must_have: Set[str] = set()
        should_have: Set[str] = set()
        must_not_have: Set[str] = set()
        
        current_op = "AND"
        for token in tokens:
            token = token.strip()
            if token in ("AND", "OR", "NOT"):
                current_op = token
            else:
                words = self.tokenize(token)
                if current_op == "AND":
                    must_have.update(words)
                elif current_op == "OR":
                    should_have.update(words)
                elif current_op == "NOT":
                    must_not_have.update(words)
        
        # 筛选文档
        results = []
        for doc_id, doc in self._documents.items():
            content_words = set(self.tokenize(doc.get("content", "")))
            
            # 检查排除
            if must_not_have & content_words:
                continue
            
            # 检查必须
            if not must_have.issubset(content_words):
                continue
            
            # 检查可选
            if should_have and not (should_have & content_words):
                continue
            
            results.append(doc)
        
        return results[:top_k]
    
    def search_prefix(
        self,
        prefix: str,
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        前缀搜索（自动补全）
        
        Args:
            prefix: 前缀
            top_k: 返回数量
            
        Returns:
            匹配的文档
        """
        prefix = prefix.lower()
        matching_words = [
            word for word in self._index.keys()
            if word.startswith(prefix)
        ]
        
        # 收集文档
        doc_set: Set[int] = set()
        for word in matching_words:
            for doc_id, _ in self._index[word]:
                doc_set.add(doc_id)
        
        results = [self._documents[doc_id] for doc_id in doc_set]
        return results[:top_k]
    
    def get_document_frequency(self, word: str) -> int:
        """获取词的文档频率"""
        word = word.lower()
        if word not in self._index:
            return 0
        
        doc_ids = {doc_id for doc_id, _ in self._index[word]}
        return len(doc_ids)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """获取索引统计"""
        total_terms = len(self._index)
        total_docs = len(self._documents)
        
        avg_doc_length = 0
        if total_docs > 0:
            total_positions = sum(
                len(positions) for positions in self._index.values()
            )
            avg_doc_length = total_positions / total_docs
        
        return {
            "total_terms": total_terms,
            "total_documents": total_docs,
            "avg_document_length": avg_doc_length,
            "stop_words_count": len(self.stop_words)
        }
    
    def clear(self):
        """清空索引"""
        self._index.clear()
        self._documents.clear()
        self._doc_counter = 0
