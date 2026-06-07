#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用本地 sentence-transformers 重建记忆向量索引
替代 OpenAI embedding，彻底摆脱 API 依赖
"""

import sqlite3
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# 尝试导入 LanceDB
try:
    import lancedb
    import pyarrow as pa
    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False

# 向量模型
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

BASE_PATH = Path(__file__).parent
SQLITE_DB = BASE_PATH / "xiaozhi_memory.db"
LANCEDB_PATH = BASE_PATH / "lancedb"

# 默认本地模型（小而快，支持中文）
DEFAULT_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


class VectorMemoryIndexer:
    """本地向量记忆索引器"""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        if not LANCEDB_AVAILABLE:
            raise RuntimeError("LanceDB not installed: pip install lancedb")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise RuntimeError("sentence-transformers not installed: pip install sentence-transformers")

        print(f"[VectorMemoryIndexer] 加载模型: {model_name}")
        self.model = SentenceTransformer(model_name)

        LANCEDB_PATH.mkdir(parents=True, exist_ok=True)
        self.db = lancedb.connect(LANCEDB_PATH)
        self._init_table()

    def _init_table(self):
        """初始化 LanceDB 表"""
        if "memory_vectors" not in self.db.table_names():
            schema = pa.schema([
                pa.field("memory_id", pa.int64()),
                pa.field("type", pa.string()),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("category", pa.string()),
                pa.field("vector", pa.list_(pa.float32(), 384)),
                pa.field("created_at", pa.string()),
            ])
            self.db.create_table("memory_vectors", schema=schema)
            print("[VectorMemoryIndexer] 创建新表 memory_vectors")
        else:
            print("[VectorMemoryIndexer] 表 memory_vectors 已存在")

    def index_sqlite_memories(self, limit: int = 500):
        """从 SQLite 读取记忆并索引到 LanceDB"""
        conn = sqlite3.connect(SQLITE_DB)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, type, title, content, category, created_at
            FROM memories
            WHERE content IS NOT NULL AND content != ''
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        print(f"[Indexer] 准备索引 {len(rows)} 条记忆...")

        texts = []
        records = []

        for row in rows:
            memory_id, type_, title, content, category, created_at = row
            text = f"{title}。{content}" if content else title
            texts.append(text)
            records.append({
                "memory_id": memory_id,
                "type": type_ or "",
                "title": title or "",
                "content": content or "",
                "category": category or "",
                "created_at": created_at or "",
            })

        # 批量编码
        print("[Indexer] 生成向量...")
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

        # 写入 LanceDB
        table = self.db.open_table("memory_vectors")
        # 删除旧数据（用 where 1=1 删除所有）
        try:
            table.delete("memory_id IS NOT NULL")
        except Exception:
            pass  # 表为空时忽略

        data = []
        for emb, rec in zip(embeddings, records):
            data.append({
                **rec,
                "vector": emb.tolist(),
            })

        table.add(data)
        print(f"[Indexer] 完成！已索引 {len(data)} 条记忆，向量维度: {embeddings[0].shape[0]}")

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """向量搜索记忆"""
        table = self.db.open_table("memory_vectors")
        query_vector = self.model.encode(query, convert_to_numpy=True).tolist()

        results = table.search(query_vector, vector_column_name="vector").limit(top_k).to_list()
        return results


def main():
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("[ERROR] sentence-transformers not available")
        return

    if not LANCEDB_AVAILABLE:
        print("[ERROR] lancedb not available")
        return

    indexer = VectorMemoryIndexer()

    print("\n" + "=" * 50)
    print("重建记忆向量索引")
    print("=" * 50)

    # 索引
    indexer.index_sqlite_memories()

    # 测试搜索
    print("\n[TEST] 向量搜索测试:")
    test_queries = ["我是谁", "大饼的偏好", "学到了什么"]

    for q in test_queries:
        results = indexer.search(q, top_k=3)
        print(f"\n  查询: {q}")
        for r in results:
            print(f"    → [{r['type']}] {r['title']}")


if __name__ == "__main__":
    main()