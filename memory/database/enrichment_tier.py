#!/usr/bin/env python3
"""
Erbing Enrichment Tier - 丰富化分级系统

实现3级丰富化系统，根据实体的重要性分配不同的资源。

Tier分级：
- Tier 1: 关键人员和公司（10-15 API调用）
- Tier 2: 值得注意的人员（3-5 API调用）
- Tier 3: 次要提及（1-2 API调用）
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


class Tier(Enum):
    """丰富化层级"""
    TIER_1 = 1  # 关键人员和公司
    TIER_2 = 2  # 值得注意的人员
    TIER_3 = 3  # 次要提及


class EnrichmentTier:
    """丰富化分级系统"""

    def __init__(self, db_path: str = None):
        """初始化丰富化分级系统

        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"

        self.db_path = Path(db_path)

        # 核心圈子（Tier 1）
        self.core_circle = set()

        # 值得注意的联系人（Tier 2）
        self.notable_contacts = set()

        # 加载配置
        self._load_config()

        logger.info(f"🎯 Enrichment Tier initialized with database: {self.db_path}")

    def _load_config(self):
        """加载配置"""
        # TODO: 从配置文件或数据库加载核心圈子和值得注意的联系人
        # 这里只是示例

        # 示例：从数据库加载核心圈子
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 加载重要性 >= 8 的实体作为核心圈子
            cursor.execute("""
                SELECT title
                FROM memories
                WHERE importance >= 8
                AND type IN ('person', 'company')
            """)

            for row in cursor.fetchall():
                self.core_circle.add(row[0])

            # 加载重要性 >= 5 的实体作为值得注意的联系人
            cursor.execute("""
                SELECT title
                FROM memories
                WHERE importance >= 5
                AND importance < 8
                AND type IN ('person', 'company')
            """)

            for row in cursor.fetchall():
                self.notable_contacts.add(row[0])

            logger.info(f"📊 Loaded {len(self.core_circle)} core circle entities")
            logger.info(f"📊 Loaded {len(self.notable_contacts)} notable contacts")

        finally:
            conn.close()

    def classify_tier(self, entity: str, entity_type: str = None) -> Tier:
        """分类实体层级

        Args:
            entity: 实体名称
            entity_type: 实体类型（可选）

        Returns:
            层级
        """
        # 检查是否在核心圈子
        if entity in self.core_circle:
            logger.debug(f"🎯 Entity '{entity}' classified as Tier 1 (core circle)")
            return Tier.TIER_1

        # 检查是否在值得注意的联系人
        if entity in self.notable_contacts:
            logger.debug(f"🎯 Entity '{entity}' classified as Tier 2 (notable)")
            return Tier.TIER_2

        # 默认为Tier 3
        logger.debug(f"🎯 Entity '{entity}' classified as Tier 3 (minor)")
        return Tier.TIER_3

    def enrich(self, entity: str, tier: Tier = None) -> Dict[str, Any]:
        """按层级丰富实体

        Args:
            entity: 实体名称
            tier: 层级（可选，如果不提供则自动分类）

        Returns:
            丰富化结果
        """
        # 如果没有提供层级，自动分类
        if tier is None:
            tier = self.classify_tier(entity)

        logger.info(f"🔄 Enriching entity '{entity}' as Tier {tier.value}")

        # 根据层级选择丰富化策略
        if tier == Tier.TIER_1:
            return self.full_enrichment(entity)
        elif tier == Tier.TIER_2:
            return self.standard_enrichment(entity)
        else:
            return self.minimal_enrichment(entity)

    def full_enrichment(self, entity: str) -> Dict[str, Any]:
        """完整丰富化（Tier 1）

        10-15 API调用，包括所有数据源

        Args:
            entity: 实体名称

        Returns:
            丰富化结果
        """
        logger.info(f"🔍 Full enrichment for '{entity}' (Tier 1)")

        result = {
            "entity": entity,
            "tier": 1,
            "enriched_at": datetime.now().isoformat(),
            "data_sources": []
        }

        # TODO: 实现实际的API调用
        # 1. Brain cross-reference（免费，最高价值）
        # 2. Web search（Brave/Exa）
        # 3. X/Twitter深度查询
        # 4. People enrichment（Crustdata/Happenstance）
        # 5. Company/funding data（Captain API）
        # 6. Meeting history（Circleback）
        # 7. Contact data（Google Contacts, CRM sync）

        # 这里只是示例
        result["data_sources"].append({
            "source": "brain_cross_reference",
            "status": "pending",
            "data": {}
        })

        result["data_sources"].append({
            "source": "web_search",
            "status": "pending",
            "data": {}
        })

        logger.info(f"✅ Full enrichment completed for '{entity}'")
        return result

    def standard_enrichment(self, entity: str) -> Dict[str, Any]:
        """标准丰富化（Tier 2）

        3-5 API调用，包括网页搜索 + 社交 + 大脑交叉引用

        Args:
            entity: 实体名称

        Returns:
            丰富化结果
        """
        logger.info(f"🔍 Standard enrichment for '{entity}' (Tier 2)")

        result = {
            "entity": entity,
            "tier": 2,
            "enriched_at": datetime.now().isoformat(),
            "data_sources": []
        }

        # TODO: 实现实际的API调用
        # 1. Brain cross-reference
        # 2. Web search
        # 3. X/Twitter查询

        # 这里只是示例
        result["data_sources"].append({
            "source": "brain_cross_reference",
            "status": "pending",
            "data": {}
        })

        result["data_sources"].append({
            "source": "web_search",
            "status": "pending",
            "data": {}
        })

        logger.info(f"✅ Standard enrichment completed for '{entity}'")
        return result

    def minimal_enrichment(self, entity: str) -> Dict[str, Any]:
        """最小丰富化（Tier 3）

        1-2 API调用，包括大脑交叉引用 + 已知handle的社交查询

        Args:
            entity: 实体名称

        Returns:
            丰富化结果
        """
        logger.info(f"🔍 Minimal enrichment for '{entity}' (Tier 3)")

        result = {
            "entity": entity,
            "tier": 3,
            "enriched_at": datetime.now().isoformat(),
            "data_sources": []
        }

        # TODO: 实现实际的API调用
        # 1. Brain cross-reference
        # 2. 社交查询（如果有已知handle）

        # 这里只是示例
        result["data_sources"].append({
            "source": "brain_cross_reference",
            "status": "pending",
            "data": {}
        })

        logger.info(f"✅ Minimal enrichment completed for '{entity}'")
        return result

    def update_entity_importance(self, entity: str, new_importance: int):
        """更新实体重要性

        Args:
            entity: 实体名称
            new_importance: 新的重要性评分（1-10）
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 更新重要性
            cursor.execute("""
                UPDATE memories
                SET importance = ?,
                    updated_at = datetime('now')
                WHERE title = ?
            """, (new_importance, entity))

            conn.commit()

            # 重新加载配置
            self._load_config()

            logger.info(f"✅ Updated importance for '{entity}' to {new_importance}")

        finally:
            conn.close()

    def get_tier_statistics(self) -> Dict[str, Any]:
        """获取层级统计信息

        Returns:
            统计信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取各层级的实体数量
            cursor.execute("""
                SELECT
                    CASE
                        WHEN importance >= 8 THEN 'Tier 1'
                        WHEN importance >= 5 THEN 'Tier 2'
                        ELSE 'Tier 3'
                    END as tier,
                    COUNT(*) as count
                FROM memories
                WHERE type IN ('person', 'company')
                GROUP BY tier
            """)

            tier_counts = {}
            for row in cursor.fetchall():
                tier, count = row
                tier_counts[tier] = count

            return {
                "tier_1_count": tier_counts.get("Tier 1", 0),
                "tier_2_count": tier_counts.get("Tier 2", 0),
                "tier_3_count": tier_counts.get("Tier 3", 0),
                "total_count": sum(tier_counts.values())
            }

        finally:
            conn.close()

    def generate_enrichment_report(self) -> str:
        """生成丰富化报告

        Returns:
            报告内容
        """
        logger.info("📝 Generating enrichment report...")

        stats = self.get_tier_statistics()

        report = f"""# Enrichment Tier Report

## 📊 统计信息

- Tier 1（关键）: {stats['tier_1_count']} 个实体
- Tier 2（值得注意）: {stats['tier_2_count']} 个实体
- Tier 3（次要）: {stats['tier_3_count']} 个实体
- 总计: {stats['total_count']} 个实体

## 🎯 核心圈子（Tier 1）

{self._format_entity_list(self.core_circle)}

## 📋 值得注意的联系人（Tier 2）

{self._format_entity_list(self.notable_contacts)}

## 🔄 丰富化队列

- 待丰富化: 0
- 进行中: 0
- 已完成: 0

---

*生成时间: {datetime.now().isoformat()}*
*版本: v1.0*
"""

        logger.info("✅ Enrichment report generated")
        return report

    def _format_entity_list(self, entities: set) -> str:
        """格式化实体列表

        Args:
            entities: 实体集合

        Returns:
            格式化的列表
        """
        if not entities:
            return "（无）"

        return "\n".join(f"- {entity}" for entity in sorted(entities))


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Erbing Enrichment Tier - 丰富化分级系统")
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="SQLite数据库路径"
    )
    parser.add_argument(
        "--enrich",
        type=str,
        help="丰富化指定的实体"
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2, 3],
        help="指定层级（1-3）"
    )
    parser.add_argument(
        "--update-importance",
        nargs=2,
        metavar=("ENTITY", "IMPORTANCE"),
        help="更新实体重要性"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成丰富化报告"
    )

    args = parser.parse_args()

    # 创建丰富化分级实例
    enrichment_tier = EnrichmentTier(db_path=args.db_path)

    # 执行操作
    if args.enrich:
        tier = Tier(args.tier) if args.tier else None
        result = enrichment_tier.enrich(args.enrich, tier)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.update_importance:
        entity, importance = args.update_importance
        enrichment_tier.update_entity_importance(entity, int(importance))
    elif args.report:
        report = enrichment_tier.generate_enrichment_report()
        print(report)
    else:
        logger.info("No action specified. Use --enrich, --update-importance, or --report")


if __name__ == "__main__":
    main()
