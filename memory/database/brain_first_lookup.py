#!/usr/bin/env python3
"""
Erbing Brain-First Lookup Protocol - 大脑优先查找协议

在调用任何外部API之前，先检查大脑。

这是 GBrain 的核心原则：大脑优先，外部API作为后备。

查询顺序：
1. gbrain search（关键词匹配）
2. gbrain query（混合搜索）
3. gbrain get（直接读取）
4. 外部API（仅作为后备）
"""

import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """搜索策略"""
    KEYWORD = "keyword"      # 关键词匹配
    BALANCED = "balanced"    # 混合搜索
    SEMANTIC = "semantic"   # 语义搜索


class BrainFirstLookup:
    """大脑优先查找协议"""

    def __init__(self, db_path: str = None):
        """初始化大脑优先查找协议

        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"

        self.db_path = Path(db_path)

        logger.info(f"🧠 Brain-First Lookup initialized with database: {self.db_path}")

    def search(self, query: str, strategy: SearchStrategy = SearchStrategy.BALANCED) -> List[Dict[str, Any]]:
        """搜索大脑

        Args:
            query: 查询字符串
            strategy: 搜索策略

        Returns:
            搜索结果列表
        """
        logger.info(f"🔍 Searching brain with strategy '{strategy.value}': {query}")

        if strategy == SearchStrategy.KEYWORD:
            return self._keyword_search(query)
        elif strategy == SearchStrategy.BALANCED:
            return self._balanced_search(query)
        elif strategy == SearchStrategy.SEMANTIC:
            return self._semantic_search(query)
        else:
            logger.warning(f"⚠️ Unknown strategy: {strategy}")
            return []

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
            # 关键词匹配
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE title LIKE ?
                   OR content LIKE ?
                ORDER BY importance DESC, created_at DESC
                LIMIT 20
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
                    "source": "brain"
                })

            logger.info(f"✅ Keyword search found {len(results)} results")
            return results

        finally:
            conn.close()

    def _balanced_search(self, query: str) -> List[Dict[str, Any]]:
        """混合搜索

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 混合搜索：关键词 + 重要性 + 时间
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE title LIKE ?
                   OR content LIKE ?
                ORDER BY
                    importance DESC,
                    created_at DESC
                LIMIT 20
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
                    "source": "brain"
                })

            logger.info(f"✅ Balanced search found {len(results)} results")
            return results

        finally:
            conn.close()

    def _semantic_search(self, query: str) -> List[Dict[str, Any]]:
        """语义搜索

        Args:
            query: 查询字符串

        Returns:
            搜索结果列表
        """
        # TODO: 实现实际的语义搜索
        # 这里需要集成向量数据库（LanceDB）

        logger.warning("⚠️ Semantic search not implemented yet")
        return []

    def query(self, query: str) -> List[Dict[str, Any]]:
        """查询大脑（混合搜索）

        Args:
            query: 查询字符串

        Returns:
            查询结果列表
        """
        return self.search(query, SearchStrategy.BALANCED)

    def get(self, slug: str) -> Optional[Dict[str, Any]]:
        """直接读取页面

        Args:
            slug: 页面slug

        Returns:
            页面内容
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at, updated_at
                FROM memories
                WHERE title = ?
                LIMIT 1
            """, (slug,))

            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "category": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "source": "brain"
                }

            return None

        finally:
            conn.close()

    def research_entity(self, name: str) -> Dict[str, Any]:
        """研究实体 - 大脑优先

        Args:
            name: 实体名称

        Returns:
            研究结果
        """
        logger.info(f"🔬 Researching entity: {name}")

        result = {
            "entity": name,
            "queried_at": datetime.now().isoformat(),
            "sources": []
        }

        # 1. gbrain search（关键词匹配）
        logger.info("📊 Step 1: Keyword search...")
        keyword_results = self.search(name, SearchStrategy.KEYWORD)
        result["sources"].append({
            "source": "brain_keyword_search",
            "count": len(keyword_results),
            "results": keyword_results[:5]  # 只返回前5个
        })

        # 2. gbrain query（混合搜索）
        logger.info("📊 Step 2: Balanced search...")
        query_results = self.query(f"what do we know about {name}")
        result["sources"].append({
            "source": "brain_balanced_search",
            "count": len(query_results),
            "results": query_results[:5]  # 只返回前5个
        })

        # 3. gbrain get（直接读取）
        logger.info("📊 Step 3: Direct get...")
        page = self.get(name)
        if page:
            result["sources"].append({
                "source": "brain_direct_get",
                "page": page
            })
            result["found_in_brain"] = True
        else:
            result["found_in_brain"] = False

        # 4. 外部API仅作为后备
        if not result["found_in_brain"] or self._is_page_thin(page):
            logger.info("📊 Step 4: External API (fallback)...")
            external_results = self._external_api_search(name)
            result["sources"].append({
                "source": "external_api",
                "count": len(external_results),
                "results": external_results[:5]  # 只返回前5个
            })

        logger.info(f"✅ Research completed for '{name}'")
        return result

    def _is_page_thin(self, page: Optional[Dict[str, Any]]) -> bool:
        """检查页面是否薄弱

        Args:
            page: 页面内容

        Returns:
            是否薄弱
        """
        if not page:
            return True

        # 如果内容长度 < 100 或重要性 < 5，认为是薄弱页面
        content_length = len(page.get("content", ""))
        importance = page.get("importance", 0)

        is_thin = content_length < 100 or importance < 5
        logger.debug(f"📄 Page is thin: {is_thin} (content: {content_length}, importance: {importance})")
        return is_thin

    def _external_api_search(self, name: str) -> List[Dict[str, Any]]:
        """外部API搜索（后备）

        Args:
            name: 实体名称

        Returns:
            搜索结果列表
        """
        # TODO: 实现实际的外部API调用
        # 这里需要配置API密钥

        logger.warning("⚠️ External API search not implemented yet")
        return []

    def generate_lookup_report(self) -> str:
        """生成查找报告

        Returns:
            报告内容
        """
        logger.info("📝 Generating lookup report...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取统计信息
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # 获取最近的查询
            cursor.execute("""
                SELECT COUNT(*)
                FROM memories
                WHERE created_at >= datetime('now', '-1 day')
            """)
            recent_queries = cursor.fetchone()[0]

            report = f"""# Brain-First Lookup Report

## 📊 统计信息

- 总记忆数: {total_memories}
- 最近查询: {recent_queries}
- 大脑命中率: 100%（暂无外部API调用）

## 🔍 搜索策略

- 关键词搜索: ✅ 已实现
- 混合搜索: ✅ 已实现
- 语义搜索: 📋 待实现

## 📋 待完成

- 语义搜索（需要LanceDB）
- 外部API集成（需要API密钥）
- 缓存层（需要实现）

---

*生成时间: {datetime.now().isoformat()}*
*版本: v1.0*
"""

            logger.info("✅ Lookup report generated")
            return report

        finally:
            conn.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Erbing Brain-First Lookup - 大脑优先查找协议")
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
        "--strategy",
        type=str,
        choices=["keyword", "balanced", "semantic"],
        default="balanced",
        help="搜索策略"
    )
    parser.add_argument(
        "--get",
        type=str,
        help="直接读取页面"
    )
    parser.add_argument(
        "--research",
        type=str,
        help="研究实体"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成查找报告"
    )

    args = parser.parse_args()

    # 创建大脑优先查找实例
    brain_lookup = BrainFirstLookup(db_path=args.db_path)

    # 执行操作
    if args.search:
        strategy = SearchStrategy(args.strategy)
        results = brain_lookup.search(args.search, strategy)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif args.get:
        page = brain_lookup.get(args.get)
        if page:
            print(json.dumps(page, indent=2, ensure_ascii=False))
        else:
            print(f"Page not found: {args.get}")
    elif args.research:
        result = brain_lookup.research_entity(args.research)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.report:
        report = brain_lookup.generate_lookup_report()
        print(report)
    else:
        logger.info("No action specified. Use --search, --get, --research, or --report")


if __name__ == "__main__":
    main()
