#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LM Studio Embedding Integration
LM Studio 本地模型嵌入方案 - 替代 Ollama
"""

import requests
import json
import numpy as np
from typing import List, Optional, Dict

class LMStudioEmbedding:
    """LM Studio 嵌入生成器"""

    def __init__(self, model: str = "nomic-embed-text",
                 base_url: str = "http://localhost:1234/v1"):
        """
        初始化 LM Studio 嵌入

        Args:
            model: 模型名称（LM Studio 中加载的模型）
            base_url: LM Studio API 地址，默认 http://localhost:1234/v1
        """
        self.model = model
        self.base_url = base_url
        self.embeddings_url = f"{base_url}/embeddings"
        self.dimension = None

    def check_connection(self) -> bool:
        """检查 LM Studio 服务"""
        try:
            # LM Studio 使用 OpenAI 兼容 API
            response = requests.get(f"{self.base_url}/models", timeout=5)
            return response.status_code == 200
        except:
            return False

    def embed(self, text: str) -> List[float]:
        """生成嵌入"""
        try:
            # LM Studio 使用 OpenAI 兼容的 embeddings API
            payload = {
                "model": self.model,
                "input": text
            }
            response = requests.post(self.embeddings_url, json=payload, timeout=30)
            result = response.json()

            # LM Studio 返回格式: {"data": [{"embedding": [...]}]}
            if "data" in result and len(result["data"]) > 0:
                embedding = result["data"][0].get("embedding", [])
                if embedding:
                    self.dimension = len(embedding)
                return embedding
            return []
        except Exception as e:
            print(f"Embedding failed: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入"""
        try:
            payload = {
                "model": self.model,
                "input": texts
            }
            response = requests.post(self.embeddings_url, json=payload, timeout=60)
            result = response.json()

            embeddings = []
            if "data" in result:
                for item in result["data"]:
                    emb = item.get("embedding", [])
                    if emb:
                        embeddings.append(emb)
                        if self.dimension is None:
                            self.dimension = len(emb)

            return embeddings
        except Exception as e:
            print(f"Batch embedding failed: {e}")
            return []

    def similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """计算余弦相似度"""
        try:
            v1, v2 = np.array(emb1), np.array(emb2)
            dot = np.dot(v1, v2)
            norm1, norm2 = np.linalg.norm(v1), np.linalg.norm(v2)
            return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
        except:
            return 0.0


class MemoryWithLMStudio:
    """集成 LM Studio 的记忆系统"""

    def __init__(self, memory_system, lm_studio: LMStudioEmbedding = None):
        self.memory = memory_system
        self.lm_studio = lm_studio or LMStudioEmbedding()
        self.cache = {}

    def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """语义搜索"""
        if not self.lm_studio.check_connection():
            print("LM Studio not available, falling back to keyword search")
            return self.memory.search(query, limit)

        # 生成查询嵌入
        query_emb = self.lm_studio.embed(query)
        if not query_emb:
            return self.memory.search(query, limit)

        # 获取所有记忆
        memories = self.memory.query(limit=1000)

        # 计算相似度
        results = []
        for mem in memories:
            text = f"{mem.get('title', '')} {mem.get('content', '')}"
            mem_emb = self.lm_studio.embed(text)
            if mem_emb:
                sim = self.lm_studio.similarity(query_emb, mem_emb)
                results.append((mem, sim))

        # 排序并返回
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:limit]]


# 推荐模型（需要在 LM Studio 中加载）
RECOMMENDED_MODELS = {
    "nomic-embed-text": {"dim": 768, "size": "274MB", "desc": "轻量级"},
    "mxbai-embed-large": {"dim": 1024, "size": "669MB", "desc": "高精度"},
    "all-MiniLM-L6-v2": {"dim": 384, "size": "90MB", "desc": "超轻量"},
    "bge-small-en-v1.5": {"dim": 384, "size": "133MB", "desc": "BGE 小模型"},
    "bge-base-en-v1.5": {"dim": 768, "size": "434MB", "desc": "BGE 基础模型"},
}

if __name__ == "__main__":
    lm_studio = LMStudioEmbedding()
    if lm_studio.check_connection():
        print("LM Studio ready!")
        emb = lm_studio.embed("test")
        print(f"Dimension: {len(emb)}")
    else:
        print("LM Studio not available")
        print("Please start LM Studio and load an embedding model")