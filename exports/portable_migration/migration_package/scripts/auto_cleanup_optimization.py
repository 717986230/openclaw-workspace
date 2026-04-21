#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动清理和优化
Auto Cleanup and Optimization
"""

import sqlite3
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class CleanupType(Enum):
    EXPIRED = "expired"
    DUPLICATE = "duplicate"
    ISOLATED = "isolated"
    INDEX_OPTIMIZATION = "index_optimization"

@dataclass
class CleanupResult:
    cleanup_type: str
    items_cleaned: int
    space_freed: int
    explanation: str

class AutoCleanupOptimization:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def cleanup_expired_memories(self, days_threshold: int = 365) -> CleanupResult:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        threshold_date = (datetime.now() - timedelta(days=days_threshold)).isoformat()

        cursor.execute("""
            SELECT COUNT(*) FROM memories
            WHERE created_at < ?
            AND importance < 5
        """, (threshold_date,))

        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute("""
                DELETE FROM memories
                WHERE created_at < ?
                AND importance < 5
            """, (threshold_date,))

            conn.commit()

        conn.close()

        return CleanupResult(
            cleanup_type='expired',
            items_cleaned=count,
            space_freed=count * 1024,
            explanation=f'Cleaned up {count} expired memories older than {days_threshold} days'
        )

    def merge_duplicate_memories(self, similarity_threshold: float = 0.9) -> CleanupResult:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content FROM memories")
        memories = cursor.fetchall()

        duplicates = []
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                id1, title1, content1 = memories[i]
                id2, title2, content2 = memories[j]
                similarity = self._compute_similarity(title1 + ' ' + content1, title2 + ' ' + content2)
                if similarity >= similarity_threshold:
                    duplicates.append((id1, id2, similarity))

        merged_count = 0
        for id1, id2, similarity in duplicates:
            cursor.execute("DELETE FROM memories WHERE id = ?", (id2,))
            merged_count += 1

        conn.commit()
        conn.close()

        return CleanupResult(
            cleanup_type='duplicate',
            items_cleaned=merged_count,
            space_freed=merged_count * 512,
            explanation=f'Merged {merged_count} duplicate memories with similarity >= {similarity_threshold}'
        )

    def detect_isolated_memories(self) -> CleanupResult:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM memories")
        all_memory_ids = set(row[0] for row in cursor.fetchall())

        cursor.execute("SELECT DISTINCT source_memory_id FROM knowledge_relations")
        related_source_ids = set(row[0] for row in cursor.fetchall())

        cursor.execute("SELECT DISTINCT target_memory_id FROM knowledge_relations")
        related_target_ids = set(row[0] for row in cursor.fetchall())

        cursor.execute("SELECT DISTINCT cause_memory_id FROM causal_relations")
        causal_source_ids = set(row[0] for row in cursor.fetchall())

        cursor.execute("SELECT DISTINCT effect_memory_id FROM causal_relations")
        causal_target_ids = set(row[0] for row in cursor.fetchall())

        related_ids = related_source_ids | related_target_ids | causal_source_ids | causal_target_ids
        isolated_ids = all_memory_ids - related_ids

        isolated_count = len(isolated_ids)

        conn.close()

        return CleanupResult(
            cleanup_type='isolated',
            items_cleaned=isolated_count,
            space_freed=isolated_count * 256,
            explanation=f'Detected {isolated_count} isolated memories with no relations'
        )

    def optimize_indexes(self) -> CleanupResult:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = cursor.fetchall()

        optimized_count = 0
        for (index_name,) in indexes:
            try:
                cursor.execute(f"REINDEX {index_name}")
                optimized_count += 1
            except:
                pass

        conn.commit()
        conn.close()

        return CleanupResult(
            cleanup_type='index_optimization',
            items_cleaned=optimized_count,
            space_freed=optimized_count * 128,
            explanation=f'Optimized {optimized_count} database indexes'
        )

    def comprehensive_cleanup(self) -> Dict:
        results = {}
        results['expired'] = self.cleanup_expired_memories()
        results['duplicate'] = self.merge_duplicate_memories()
        results['isolated'] = self.detect_isolated_memories()
        results['index'] = self.optimize_indexes()
        return results

    def _compute_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union

    def get_cleanup_statistics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM knowledge_relations")
        total_relations = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM causal_relations")
        total_causal = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(LENGTH(title) + LENGTH(content)) FROM memories")
        total_size = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_memories': total_memories,
            'total_relations': total_relations,
            'total_causal': total_causal,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }

if __name__ == "__main__":
    print("Testing Auto Cleanup and Optimization...")
    cleanup = AutoCleanupOptimization("memory/database/xiaozhi_memory.db")
    result = cleanup.cleanup_expired_memories()
    print(f"Expired cleanup: {result.explanation}")
    result = cleanup.merge_duplicate_memories()
    print(f"Duplicate cleanup: {result.explanation}")
    result = cleanup.detect_isolated_memories()
    print(f"Isolated detection: {result.explanation}")
    result = cleanup.optimize_indexes()
    print(f"Index optimization: {result.explanation}")
    results = cleanup.comprehensive_cleanup()
    print(f"Comprehensive cleanup: {results}")
    stats = cleanup.get_cleanup_statistics()
    print(f"Statistics: {stats}")
    print("Auto Cleanup and Optimization test complete!")
