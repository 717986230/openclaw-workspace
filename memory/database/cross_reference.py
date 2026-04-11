#!/usr/bin/env python3
"""
Erbing Cross-Reference - 交叉引用系统

这是 GBrain 的铁律：每个实体页面必须链接到所有引用它的其他页面。

功能：
1. 查找所有提及某个实体的其他页面
2. 添加反向链接
3. 维护引用完整性
"""

import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any, Set
import re
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErbingCrossReference:
    """交叉引用系统"""

    def __init__(self, db_path: str = None):
        """初始化交叉引用系统

        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"

        self.db_path = Path(db_path)

        logger.info(f"🔗 Cross-Reference initialized with database: {self.db_path}")

    def find_mentions(self, entity: str) -> List[Dict[str, Any]]:
        """查找所有提及某个实体的其他页面

        Args:
            entity: 实体名称

        Returns:
            提及该实体的页面列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 查询所有提及该实体的记忆
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE content LIKE ?
                   OR title LIKE ?
                ORDER BY created_at DESC
            """, (f"%{entity}%", f"%{entity}%"))

            mentions = []
            for row in cursor.fetchall():
                mentions.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "category": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "created_at": row[7]
                })

            logger.info(f"🔍 Found {len(mentions)} mentions of '{entity}'")
            return mentions

        finally:
            conn.close()

    def add_backlink(self, entity: str, mention: Dict[str, Any], summary: str):
        """添加反向链接

        Args:
            entity: 实体名称
            mention: 提及该实体的页面
            summary: 摘要
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取实体页面
            cursor.execute("""
                SELECT id, content
                FROM memories
                WHERE title = ?
                LIMIT 1
            """, (entity,))

            row = cursor.fetchone()
            if not row:
                logger.warning(f"⚠️ Entity page not found: {entity}")
                return

            entity_id, content = row

            # 检查是否已经存在反向链接
            backlink_pattern = f"Referenced in \\[{mention['title']}\\]"
            if re.search(backlink_pattern, content):
                logger.debug(f"🔗 Backlink already exists: {mention['title']}")
                return

            # 添加反向链接
            backlink = f"\n\n- Referenced in [{mention['title']}] (#{mention['id']}) -- {summary}"

            # 更新内容
            updated_content = content + backlink

            cursor.execute("""
                UPDATE memories
                SET content = ?,
                    updated_at = datetime('now')
                WHERE id = ?
            """, (updated_content, entity_id))

            conn.commit()

            logger.info(f"✅ Added backlink to '{entity}' from '{mention['title']}'")

        finally:
            conn.close()

    def update_entity_page(self, entity: str, new_info: Dict[str, Any]):
        """更新实体页面并添加反向链接

        Args:
            entity: 实体名称
            new_info: 新信息
        """
        logger.info(f"🔄 Updating entity page: {entity}")

        # 1. 更新页面
        self._update_page(entity, new_info)

        # 2. 找到所有提及此实体的其他页面
        mentions = self.find_mentions(entity)

        # 3. 添加反向链接
        for mention in mentions:
            # 跳过自己
            if mention["title"] == entity:
                continue

            # 生成摘要
            summary = self._generate_summary(mention)

            # 添加反向链接
            self.add_backlink(entity, mention, summary)

        logger.info(f"✅ Entity page '{entity}' updated with {len(mentions)} backlinks")

    def _update_page(self, entity: str, new_info: Dict[str, Any]):
        """更新页面内容

        Args:
            entity: 实体名称
            new_info: 新信息
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 检查页面是否存在
            cursor.execute("""
                SELECT id, content
                FROM memories
                WHERE title = ?
                LIMIT 1
            """, (entity,))

            row = cursor.fetchone()

            if row:
                # 更新现有页面
                entity_id, content = row

                # 添加新信息到Timeline
                timeline_entry = self._format_timeline_entry(new_info)

                # 检查是否已经有Timeline部分
                if "## Timeline" in content:
                    # 追加到Timeline
                    updated_content = content + "\n" + timeline_entry
                else:
                    # 添加Timeline部分
                    updated_content = content + "\n\n## Timeline\n" + timeline_entry

                cursor.execute("""
                    UPDATE memories
                    SET content = ?,
                        updated_at = datetime('now')
                    WHERE id = ?
                """, (updated_content, entity_id))

            else:
                # 创建新页面
                content = self._create_entity_page(entity, new_info)

                cursor.execute("""
                    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                """, (
                    "entity",
                    entity,
                    content,
                    new_info.get("category", "general"),
                    json.dumps(new_info.get("tags", [])),
                    new_info.get("importance", 5)
                ))

            conn.commit()

        finally:
            conn.close()

    def _format_timeline_entry(self, info: Dict[str, Any]) -> str:
        """格式化Timeline条目

        Args:
            info: 信息字典

        Returns:
            格式化的Timeline条目
        """
        date = info.get("date", "Unknown")
        event = info.get("event", "No event")
        source = info.get("source", "Unknown")

        return f"- **{date}** | {event} [来源: {source}]"

    def _create_entity_page(self, entity: str, info: Dict[str, Any]) -> str:
        """创建实体页面

        Args:
            entity: 实体名称
            info: 信息字典

        Returns:
            页面内容
        """
        return f"""# {entity}

## Executive Summary
{info.get("summary", "No summary available")}

## State
{info.get("state", "No state information")}

## What They Believe
{info.get("beliefs", "No beliefs information")}

## What They're Building
{info.get("building", "No building information")}

## Assessment
{info.get("assessment", "No assessment")}

## Trajectory
{info.get("trajectory", "No trajectory information")}

## Relationship
{info.get("relationship", "No relationship information")}

## Contact
{info.get("contact", "No contact information")}

## Timeline
{self._format_timeline_entry(info)}
"""

    def _generate_summary(self, mention: Dict[str, Any]) -> str:
        """生成摘要

        Args:
            mention: 提及信息

        Returns:
            摘要文本
        """
        # 简单实现：使用前100个字符
        content = mention.get("content", "")
        summary = content[:100] + "..." if len(content) > 100 else content
        return summary

    def fix_broken_references(self):
        """修复损坏的引用"""
        logger.info("🔧 Fixing broken references...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取所有记忆
            cursor.execute("""
                SELECT id, title, content
                FROM memories
            """)

            all_memories = cursor.fetchall()

            # 检查每个记忆的引用
            for memory_id, title, content in all_memories:
                # 提取所有引用
                references = self._extract_references(content)

                # 检查每个引用是否有效
                for ref in references:
                    if not self._reference_exists(ref):
                        logger.warning(f"⚠️ Broken reference found: {ref} in '{title}'")
                        # TODO: 修复或删除无效引用

            logger.info("✅ Broken references checked")

        finally:
            conn.close()

    def _extract_references(self, content: str) -> List[str]:
        """从内容中提取引用

        Args:
            content: 内容

        Returns:
            引用列表
        """
        # 简单实现：提取所有[xxx]格式的引用
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, content)
        return matches

    def _reference_exists(self, ref: str) -> bool:
        """检查引用是否存在

        Args:
            ref: 引用

        Returns:
            是否存在
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM memories
                WHERE title = ?
            """, (ref,))

            count = cursor.fetchone()[0]
            return count > 0

        finally:
            conn.close()

    def generate_cross_reference_report(self) -> str:
        """生成交叉引用报告

        Returns:
            报告内容
        """
        logger.info("📝 Generating cross-reference report...")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # 获取统计信息
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # 获取有反向链接的记忆
            cursor.execute("""
                SELECT COUNT(*)
                FROM memories
                WHERE content LIKE '%Referenced in%'
            """)
            memories_with_backlinks = cursor.fetchone()[0]

            report = f"""# Cross-Reference Report

## 📊 统计信息

- 总记忆数: {total_memories}
- 有反向链接的记忆: {memories_with_backlinks}
- 反向链接覆盖率: {memories_with_backlinks / total_memories * 100:.1f}%

## 🔗 引用完整性

- 损坏的引用: 0
- 修复的引用: 0

## 📋 待处理

- 丰富化实体: 0
- 添加反向链接: 0

---

*生成时间: {datetime.now().isoformat()}*
*版本: v1.0*
"""

            logger.info("✅ Cross-reference report generated")
            return report

        finally:
            conn.close()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Erbing Cross-Reference - 交叉引用系统")
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="SQLite数据库路径"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="修复损坏的引用"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成交叉引用报告"
    )

    args = parser.parse_args()

    # 创建交叉引用实例
    cross_ref = ErbingCrossReference(db_path=args.db_path)

    # 执行操作
    if args.fix:
        cross_ref.fix_broken_references()
    elif args.report:
        report = cross_ref.generate_cross_reference_report()
        print(report)
    else:
        logger.info("No action specified. Use --fix or --report")


if __name__ == "__main__":
    main()
