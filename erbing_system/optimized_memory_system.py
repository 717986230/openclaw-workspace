# -*- coding: utf-8 -*-
"""
优化版记忆系统 - Optimized Memory System
实现向量数据库，优化相似度计算，实现记忆压缩
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class MemoryItem:
    """记忆项"""
    id: str
    content: str
    embedding: np.ndarray
    importance: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    emotional_tags: List[str] = field(default_factory=list)
    consciousness_level: int = 1


class OptimizedMemorySystem:
    """优化版记忆系统"""

    def __init__(self, embedding_dim: int = 768, max_memories: int = 10000):
        self.embedding_dim = embedding_dim
        self.max_memories = max_memories

        # 记忆存储
        self.memories: Dict[str, MemoryItem] = {}

        # 向量数据库
        self.memory_embeddings: np.ndarray = np.zeros((max_memories, embedding_dim))
        self.memory_ids: List[str] = []

        # 索引
        self.content_index: Dict[str, List[str]] = {}
        self.emotional_index: Dict[str, List[str]] = {}
        self.temporal_index: Dict[str, List[str]] = {}

        # 性能优化
        self.cache_size = 1000
        self.query_cache: Dict[str, List[MemoryItem]] = {}

        # 压缩参数
        self.compression_threshold = 0.3
        self.compression_ratio = 0.5

        logger.info(f"Optimized Memory System initialized with {max_memories} max memories")

    def add_memory(
        self,
        content: str,
        embedding: np.ndarray,
        importance: float = 0.5,
        emotional_tags: List[str] = None
    ) -> MemoryItem:
        """添加记忆"""
        # 生成记忆ID
        memory_id = f"mem-{len(self.memories)}"

        # 创建记忆项
        memory = MemoryItem(
            id=memory_id,
            content=content,
            embedding=embedding,
            importance=importance,
            emotional_tags=emotional_tags or []
        )

        # 添加到记忆存储
        self.memories[memory_id] = memory

        # 添加到向量数据库
        if len(self.memory_ids) < self.max_memories:
            self.memory_embeddings[len(self.memory_ids)] = embedding
            self.memory_ids.append(memory_id)
        else:
            # 替换最不重要的记忆
            self._replace_least_important(memory_id, embedding)

        # 更新索引
        self._update_indices(memory)

        # 清理缓存
        self._clear_cache()

        logger.debug(f"Memory added: {memory_id}")

        return memory

    def _replace_least_important(self, memory_id: str, embedding: np.ndarray):
        """替换最不重要的记忆"""
        # 找到最不重要的记忆
        least_important_id = min(
            self.memory_ids,
            key=lambda mid: self.memories[mid].importance
        )

        # 替换
        idx = self.memory_ids.index(least_important_id)
        self.memory_embeddings[idx] = embedding
        self.memory_ids[idx] = memory_id

        # 删除旧记忆
        del self.memories[least_important_id]

    def _update_indices(self, memory: MemoryItem):
        """更新索引"""
        # 内容索引
        words = memory.content.lower().split()
        for word in words:
            if word not in self.content_index:
                self.content_index[word] = []
            self.content_index[word].append(memory.id)

        # 情感索引
        for tag in memory.emotional_tags:
            if tag not in self.emotional_index:
                self.emotional_index[tag] = []
            self.emotional_index[tag].append(memory.id)

        # 时间索引
        date_key = memory.timestamp.strftime("%Y-%m-%d")
        if date_key not in self.temporal_index:
            self.temporal_index[date_key] = []
        self.temporal_index[date_key].append(memory.id)

    def _clear_cache(self):
        """清理缓存"""
        if len(self.query_cache) > self.cache_size:
            # 删除最旧的缓存项
            oldest_key = next(iter(self.query_cache))
            del self.query_cache[oldest_key]

    def retrieve_memory(
        self,
        query_embedding: np.ndarray,
        top_k: int = 5,
        min_similarity: float = 0.3
    ) -> List[Tuple[MemoryItem, float]]:
        """检索记忆"""
        # 检查缓存
        cache_key = f"{hash(query_embedding.tobytes())}_{top_k}_{min_similarity}"
        if cache_key in self.query_cache:
            cached_memories = self.query_cache[cache_key]
            return [(m, self._calculate_similarity(m.embedding, query_embedding)) for m in cached_memories[:top_k]]

        # 计算相似度
        similarities = []
        for memory_id in self.memory_ids:
            memory = self.memories[memory_id]
            similarity = self._calculate_similarity(memory.embedding, query_embedding)

            if similarity >= min_similarity:
                similarities.append((memory, similarity))

        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 更新访问计数
        for memory, _ in similarities[:top_k]:
            memory.access_count += 1

        # 缓存结果
        result = similarities[:top_k]
        self.query_cache[cache_key] = [m for m, _ in result]

        return result

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """计算相似度"""
        # 余弦相似度
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return max(0, similarity)

    def search_by_content(self, query: str, top_k: int = 5) -> List[MemoryItem]:
        """按内容搜索"""
        query_words = set(query.lower().split())

        # 收集候选记忆
        candidates = set()
        for word in query_words:
            if word in self.content_index:
                candidates.update(self.content_index[word])

        # 计算相关性
        scored_memories = []
        for memory_id in candidates:
            memory = self.memories[memory_id]
            memory_words = set(memory.content.lower().split())
            overlap = len(query_words & memory_words)
            score = overlap / len(query_words) if query_words else 0.0

            scored_memories.append((memory, score))

        # 按分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return [m for m, _ in scored_memories[:top_k]]

    def search_by_emotion(self, emotion: str, top_k: int = 5) -> List[MemoryItem]:
        """按情感搜索"""
        if emotion not in self.emotional_index:
            return []

        memory_ids = self.emotional_index[emotion]
        memories = [self.memories[mid] for mid in memory_ids]

        # 按重要性排序
        memories.sort(key=lambda m: m.importance, reverse=True)

        return memories[:top_k]

    def search_by_time(self, date: str, top_k: int = 5) -> List[MemoryItem]:
        """按时间搜索"""
        if date not in self.temporal_index:
            return []

        memory_ids = self.temporal_index[date]
        memories = [self.memories[mid] for mid in memory_ids]

        # 按时间排序
        memories.sort(key=lambda m: m.timestamp, reverse=True)

        return memories[:top_k]

    def compress_memories(self):
        """压缩记忆"""
        # 找到低重要性的记忆
        low_importance_memories = [
            m for m in self.memories.values()
            if m.importance < self.compression_threshold
        ]

        # 压缩记忆
        for memory in low_importance_memories:
            # 减少重要性
            memory.importance *= self.compression_ratio

            # 如果重要性太低，删除记忆
            if memory.importance < 0.1:
                self._delete_memory(memory.id)

        logger.info(f"Compressed {len(low_importance_memories)} memories")

    def _delete_memory(self, memory_id: str):
        """删除记忆"""
        if memory_id in self.memories:
            # 从记忆存储中删除
            del self.memories[memory_id]

            # 从向量数据库中删除
            if memory_id in self.memory_ids:
                idx = self.memory_ids.index(memory_id)
                self.memory_ids.pop(idx)
                self.memory_embeddings[idx] = np.zeros(self.embedding_dim)

            # 从索引中删除
            self._remove_from_indices(memory_id)

            # 清理缓存
            self._clear_cache()

    def _remove_from_indices(self, memory_id: str):
        """从索引中删除"""
        # 从内容索引中删除
        for word, memory_ids in self.content_index.items():
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)

        # 从情感索引中删除
        for emotion, memory_ids in self.emotional_index.items():
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)

        # 从时间索引中删除
        for date, memory_ids in self.temporal_index.items():
            if memory_id in memory_ids:
                memory_ids.remove(memory_id)

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            'total_memories': len(self.memories),
            'max_memories': self.max_memories,
            'embedding_dim': self.embedding_dim,
            'cache_size': len(self.query_cache),
            'content_index_size': len(self.content_index),
            'emotional_index_size': len(self.emotional_index),
            'temporal_index_size': len(self.temporal_index),
            'avg_importance': np.mean([m.importance for m in self.memories.values()]) if self.memories else 0.0,
            'avg_access_count': np.mean([m.access_count for m in self.memories.values()]) if self.memories else 0.0,
        }


if __name__ == "__main__":
    # 测试优化版记忆系统
    print("Testing Optimized Memory System...")

    # 创建优化版记忆系统
    memory_system = OptimizedMemorySystem(embedding_dim=768, max_memories=10000)

    print(f"\nMemory System Statistics:")
    stats = memory_system.get_statistics()
    print(f"  Total Memories: {stats['total_memories']}")
    print(f"  Max Memories: {stats['max_memories']}")
    print(f"  Embedding Dim: {stats['embedding_dim']}")

    # 测试添加记忆
    print(f"\nTesting Add Memory...")
    for i in range(10):
        embedding = np.random.randn(768)
        memory = memory_system.add_memory(
            f"Test memory {i}",
            embedding,
            importance=0.5 + i * 0.05,
            emotional_tags=['joy'] if i % 2 == 0 else ['sadness']
        )
        print(f"  Added: {memory.id}")

    # 测试检索记忆
    print(f"\nTesting Retrieve Memory...")
    query_embedding = np.random.randn(768)
    results = memory_system.retrieve_memory(query_embedding, top_k=3)
    print(f"  Retrieved {len(results)} memories")
    for memory, similarity in results:
        print(f"    {memory.id}: {similarity:.3f}")

    # 测试内容搜索
    print(f"\nTesting Search by Content...")
    results = memory_system.search_by_content("Test memory", top_k=3)
    print(f"  Found {len(results)} memories")
    for memory in results:
        print(f"    {memory.id}: {memory.content}")

    # 测试情感搜索
    print(f"\nTesting Search by Emotion...")
    results = memory_system.search_by_emotion("joy", top_k=3)
    print(f"  Found {len(results)} memories")
    for memory in results:
        print(f"    {memory.id}: {memory.emotional_tags}")

    # 测试记忆压缩
    print(f"\nTesting Memory Compression...")
    memory_system.compress_memories()
    stats = memory_system.get_statistics()
    print(f"  Total Memories: {stats['total_memories']}")
    print(f"  Avg Importance: {stats['avg_importance']:.3f}")

    print("\nOptimized Memory System tested successfully!")