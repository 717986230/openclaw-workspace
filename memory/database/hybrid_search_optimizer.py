#!/usr/bin/env python3
"""
Erbing Hybrid Search Optimization - 混合搜索优化

优化四策略检索系统，实现RRF融合和Cross-Encoder重排序。

四策略：
1. 关键词搜索
2. 向量语义搜索
3. 图遍历
4. 时间过滤

融合方法：
- RRF (Reciprocal Rank Fusion)
- Cross-Encoder重排序
"""

import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import math

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HybridSearchOptimizer:
    """混合搜索优化器"""

    def __init__(self, db_path: str = None):
        """初始化混合搜索优化器

        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"

        self.db_path = Path(db_path)

        # RRF参数
        self.rrf_k = 60  # RRF常数

        logger.info(f"🔍 Hybrid Search Optimizer initialized with database: {self.db_path}")

    def search(self, query: str, token_budget: int = 4000) -> List[Dict[str, Any]]:
        """混合搜索

        Args:
            query: 查询字符串
            token_budget: Token预算

        Returns:
            搜索结果列表
        """
        logger.info(f"🔍 Hybrid search: {query}")

        # 1. 四策略并行搜索
        logger.info("📊 Step 1: Four-strategy parallel search...")
        keyword_results = self._keyword_search(query)
        semantic_results = self._semantic_search(query)
        graph_results = self._graph_traversal(query)
        temporal_results = self._temporal_filter(query)

        # 2. RRF融合
        logger.info("📊 Step 2: RRF fusion...")
        fused_results = self._reciprocal_rank_fusion(
            keyword_results,
            semantic_results,
            graph_results,
            temporal_results
        )

        # 3. Cross-Encoder重排序
        logger.info("📊 Step 3: Cross-Encoder rerank...")
        reranked_results = self._cross_encoder_rerank(query, fused_results)

        # 4. Token预算控制
        logger.info("📊 Step 4: Token budget control...")
        final_results = self._apply_token_budget(reranked_results, token_budget)

        logger.info(f"✅ Hybrid search completed: {len(final_results)} results")
        return final_results

    def _keyword_search(self, query: str) -> List[Dict[str, Any]]:
        """关键词搜索

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE title LIKE ?
                   OR content LIKE ?
                ORDER BY importance DESC, created_at DESC
                LIMIT 50
            """, (f"%{query}%", f"%{query}%"))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "category": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "created_at": row[7],
                    "source": "keyword"
                })

            logger.debug(f"🔍 Keyword search: {len(results)} results")
            return results

        finally:
            conn.close()

    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """向量语义搜索

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        # TODO: 实现实际的向量搜索
        # 这里需要集成LanceDB

        logger.warning("⚠️ Semantic search not implemented yet")
        return []

    def _graph_traversal(self, query: str) -> List[Dict[str, Any]]:
        """图遍历

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        # TODO: 实现实际的图遍历
        # 这里需要构建实体关系图

        logger.warning("⚠️ Graph traversal not implemented yet")
        return []

    def _temporal_filter(self, query: str) -> List[Dict[str, Any]]:
        """时间过滤

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取最近30天的记忆
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()

            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE created_at >= ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (thirty_days_ago,))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "category": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "created_at": row[7],
                    "source": "temporal"
                })

            logger.debug(f"🔍 Temporal filter: {len(results)} results")
            return results

        finally:
            conn.close()

    def _reciprocal_rank_fusion(
        self,
        keyword_results: List[Dict[str, Any]],
        semantic_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]],
        temporal_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """RRF融合

        Args:
            keyword_results: 关键词搜索结果
            semantic_results: 语义搜索结果
            graph_results: 图遍历结果
            temporal_results: 时间过滤结果

        Returns:
            融合后的结果列表
        """
        # 收集所有结果
        all_results = {
            "keyword": keyword_results,
            "semantic": semantic_results,
            "graph": graph_results,
            "temporal": temporal_results
        }

        # 计算RRF分数
        rrf_scores = defaultdict(float)
        result_map = {}

        for source, results in all_results.items():
            for rank, result in enumerate(results, start=1):
                result_id = result["id"]

                # RRF公式: 1 / (k + rank)
                rrf_score = 1 / (self.rrf_k + rank)
                rrf_scores[result_id] += rrf_score

                # 保存结果
                if result_id not in result_map:
                    result_map[result_id] = result.copy()
                    result_map[result_id]["sources"] = []
                    result_map[result_id]["rrf_score"] = 0

                result_map[result_id]["sources"].append(source)
                result_map[result_id]["rrf_score"] = rrf_scores[result_id]

        # 按RRF分数排序
        sorted_results = sorted(
            result_map.values(),
            key=lambda x: x["rrf_score"],
            reverse=True
        )

        logger.debug(f"🔍 RRF fusion: {len(sorted_results)} results")
        return sorted_results

    def _cross_encoder_rerank(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Cross-Encoder重排序

        Args:
            query: 查询字符串
            results: 搜索结果

        Returns:
            重排序后的结果列表
        """
        # TODO: 实现实际的Cross-Encoder重排序
        # 这里需要集成Cross-Encoder模型

        # 简单实现：保持原有顺序
        logger.debug(f"🔍 Cross-Encoder rerank: {len(results)} results")
        return results

    def _apply_token_budget(
        self,
        results: List[Dict[str, Any]],
        token_budget: int
    ) -> List[Dict[str, Any]]:
        """应用Token预算

        Args:
            results: 搜索结果
            token_budget: Token预算

        Returns:
            符合预算的结果列表
        """
        # 简单实现：限制结果数量
        # 假设每个结果平均100 tokens
        max_results = token_budget // 100

        final_results = results[:max_results]

        logger.debug(f"🔍 Token budget: {len(final_results)} results (budget: {token_budget})")
        return final_results

    def generate_search_report(self) -> str:
        """生成搜索报告

        Returns:
            报告内容
        """
        logger.info("📝 Generating search report...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取统计信息
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # 获取最近的记忆
            cursor.execute("""
                SELECT COUNT(*)
                FROM memories
                WHERE created_at >= datetime('now', '-30 days')
            """)
            recent_memories = cursor.fetchone()[0]

            report = f"""# Hybrid Search Report

## 📊 统计信息

- 总记忆数: {total_memories}
- 最近30天记忆: {recent_memories}
- RRF常数: {self.rrf_k}

## 🔍 搜索策略

- 关键词搜索: ✅ 已实现
- 语义搜索: 📋 待实现（需要LanceDB）
- 图遍历: 📋 待实现（需要实体关系图）
- 时间过滤: ✅ 已实现

## 🔄 融合方法

- RRF融合: ✅ 已实现
- Cross-Encoder重排序: 📋 待实现（需要模型）

## 📋 待完成

- 语义搜索（需要LanceDB）
- 图遍历（需要实体关系图）
- Cross-Encoder重排序（需要模型）
- 性能优化（需要缓存）

---

*生成时间: {datetime.now().isoformat()}*
*版本: v1.0*
"""

            logger.info("✅ Search report generated")
            return report

        finally:
            conn.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Erbing Hybrid Search Optimization - 混合搜索优化")
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="SQLite数据库路径"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="搜索查询"
    )
    parser.add_argument(
        "--token-budget",
        type=int,
        default=4000,
        help="Token预算"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成搜索报告"
    )

    args = parser.parse_args()

    # 创建混合搜索优化器实例
    search_optimizer = HybridSearchOptimizer(db_path=args.db_path)

    # 执行操作
    if args.search:
        results = search_optimizer.search(args.search, args.token_budget)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.report:
        report = search_optimizer.generate_search_report()
        print(report)
    else:
        logger.info("No action specified. Use --search or --report")


if __name__ == "__main__":
    main()
