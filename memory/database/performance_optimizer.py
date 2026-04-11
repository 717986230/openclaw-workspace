#!/usr/bin/env python3
"""
Erbing Performance Optimizer - 性能优化器

优化查询性能：
1. 缓存层
2. 数据库查询优化
3. 批量操作
4. 连接池
"""

import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from contextlib import contextmanager
import threading
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self, db_path: str = None):
        """初始化性能优化器

        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"

        self.db_path = Path(db_path)

        # 连接池
        self._connections = {}
        self._lock = threading.Lock()

        # 缓存
        self._cache = {}
        self._cache_ttl = 3600  # 1小时

        logger.info(f"⚡ Performance Optimizer initialized with database: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """获取数据库连接（连接池）"""
        thread_id = threading.current_thread().ident

        with self._lock:
            if thread_id not in self._connections:
                self._connections[thread_id] = sqlite3.connect(self.db_path)
                self._connections[thread_id].row_factory = sqlite3.Row

        try:
            yield self._connections[thread_id]
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            raise

    def add_indexes(self):
        """添加数据库索引"""
        logger.info("🔍 Adding database indexes...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 为常用查询添加索引
            indexes = [
                ("idx_memories_type", "memories(type)"),
                ("idx_memories_category", "memories(category)"),
                ("idx_memories_importance", "memories(importance)"),
                ("idx_memories_created_at", "memories(created_at)"),
                ("idx_memories_title", "memories(title)"),
                ("idx_memories_content", "memories(content)"),
            ]

            for index_name, columns in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {columns}")
                    logger.info(f"✅ Index created: {index_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to create index {index_name}: {e}")

            conn.commit()

        logger.info("✅ Database indexes added")

    def optimize_database(self):
        """优化数据库"""
        logger.info("🗄️ Optimizing database...")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 运行VACUUM
            cursor.execute("VACUUM")
            logger.info("✅ VACUUM completed")

            # 运行ANALYZE
            cursor.execute("ANALYZE")
            logger.info("✅ ANALYZE completed")

            conn.commit()

        logger.info("✅ Database optimization completed")

    def batch_insert(self, memories: List[Dict[str, Any]]) -> int:
        """批量插入记忆

        Args:
            memories: 记忆列表

        Returns:
            插入数量
        """
        logger.info(f"📥 Batch inserting {len(memories)} memories...")

        inserted = 0

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 使用事务
            cursor.execute("BEGIN TRANSACTION")

            try:
                for memory in memories:
                    cursor.execute("""
                        INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        ON CONFLICT(title) DO UPDATE SET
                            content = excluded.content,
                            category = excluded.category,
                            tags = excluded.tags,
                            importance = excluded.importance,
                            updated_at = datetime('now')
                    """, (
                        memory.get("type", "general"),
                        memory.get("title", ""),
                        memory.get("content", ""),
                        memory.get("category", "general"),
                        json.dumps(memory.get("tags", [])),
                        memory.get("importance", 5)
                    ))
                    inserted += 1

                conn.commit()
                logger.info(f"✅ Batch insert completed: {inserted} memories")

            except Exception as e:
                conn.rollback()
                logger.error(f"❌ Batch insert failed: {e}")
                raise

        return inserted

    def cache_get(self, key: str) -> Optional[Any]:
        """获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                logger.debug(f"💾 Cache hit: {key}")
                return value
            else:
                del self._cache[key]

        logger.debug(f"💾 Cache miss: {key}")
        return None

    def cache_set(self, key: str, value: Any):
        """设置缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        self._cache[key] = (value, time.time())
        logger.debug(f"💾 Cache set: {key}")

    def cache_clear(self):
        """清除缓存"""
        self._cache.clear()
        logger.info("🗑️ Cache cleared")

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计

        Returns:
            性能统计
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # 获取数据库大小
            cursor.execute("SELECT page_count * page_size FROM pragma_page_count(), pragma_page_size()")
            db_size = cursor.fetchone()[0]
            stats["database_size_bytes"] = db_size
            stats["database_size_mb"] = db_size / (1024 * 1024)

            # 获取表统计
            cursor.execute("SELECT COUNT(*) FROM memories")
            stats["total_memories"] = cursor.fetchone()[0]

            # 获取索引统计
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            stats["total_indexes"] = len(cursor.fetchall())

            # 获取缓存统计
            stats["cache_size"] = len(self._cache)
            stats["cache_hits"] = len([v for v in self._cache.values() if time.time() - v[1] < self._cache_ttl])

            return stats

    def generate_performance_report(self) -> str:
        """生成性能报告

        Returns:
            报告内容
        """
        logger.info("📝 Generating performance report...")

        stats = self.get_performance_stats()

        report = f"""# Performance Report

## 📊 数据库统计

- 数据库大小: {stats['database_size_mb']:.2f} MB
- 总记忆数: {stats['total_memories']}
- 索引数量: {stats['total_indexes']}

## 💾 缓存统计

- 缓存大小: {stats['cache_size']}
- 缓存命中: {stats['cache_hits']}
- 缓存TTL: {self._cache_ttl}秒

## ⚡ 优化建议

- ✅ 已添加数据库索引
- ✅ 已启用连接池
- ✅ 已实现批量操作
- 📋 待实现：LanceDB向量索引
- 📋 待实现：Redis缓存层

---

*生成时间: {datetime.now().isoformat()}*
*版本: v1.0*
"""

        logger.info("✅ Performance report generated")
        return report


def main():
    """主函数"""
    import argparse
