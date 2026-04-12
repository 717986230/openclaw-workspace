"""
基因神经元记忆系统 - 数据库模块

处理所有数据库操作
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager
import json


class GeneticMemoryDatabase:
    """基因神经元记忆数据库"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def setup_tables(self):
        """创建所有表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 记忆基因表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_genes (
                    memory_id INTEGER PRIMARY KEY,
                    activation_threshold REAL DEFAULT 0.5,
                    decay_rate REAL DEFAULT 0.05,
                    plasticity REAL DEFAULT 0.8,
                    strengthening_rate REAL DEFAULT 0.1,
                    weakening_rate REAL DEFAULT 0.15,
                    consolidation_level INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    failure_count INTEGER DEFAULT 0,
                    total_attempts INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 突触连接表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS synapses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    weight REAL DEFAULT 0.0,
                    last_co_activation TIMESTAMP,
                    co_activation_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_id) REFERENCES memories(id),
                    FOREIGN KEY (target_id) REFERENCES memories(id),
                    UNIQUE(source_id, target_id)
                )
            """)

            # 神经元激活历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER NOT NULL,
                    activation_value REAL NOT NULL,
                    query_embedding TEXT,
                    context_tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 记忆巩固历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consolidation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER NOT NULL,
                    from_level INTEGER NOT NULL,
                    to_level INTEGER NOT NULL,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 基因进化历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evolution_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER NOT NULL,
                    evolution_type TEXT NOT NULL,
                    before_state TEXT,
                    after_state TEXT,
                    fitness REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories(id)
                )
            """)

            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_synapses_source
                ON synapses(source_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_synapses_target
                ON synapses(target_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_synapses_weight
                ON synapses(weight)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_history_memory
                ON activation_history(memory_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_history_created
                ON activation_history(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_consolidation_memory
                ON consolidation_history(memory_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_evolution_memory
                ON evolution_history(memory_id)
                """)

            conn.commit()

    def insert_gene(self, memory_id: int, gene_data: Dict) -> bool:
        """插入基因数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO memory_genes (
                        memory_id, activation_threshold, decay_rate, plasticity,
                        strengthening_rate, weakening_rate, consolidation_level,
                        last_accessed, access_count, success_rate,
                        failure_count, total_attempts
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    gene_data.get('activation_threshold', 0.5),
                    gene_data.get('decay_rate', 0.05),
                    gene_data.get('plasticity', 0.8),
                    gene_data.get('strengthening_rate', 0.1),
                    gene_data.get('weakening_rate', 0.15),
                    gene_data.get('consolidation_level', 0),
                    gene_data.get('last_accessed'),
                    gene_data.get('access_count', 0),
                    gene_data.get('success_rate', 0.0),
                    gene_data.get('failure_count', 0),
                    gene_data.get('total_attempts', 0)
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting gene: {e}")
            return False

    def get_gene(self, memory_id: int) -> Optional[Dict]:
        """获取基因数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM memory_genes WHERE memory_id = ?
            """, (memory_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_gene(self, memory_id: int, gene_data: Dict) -> bool:
        """更新基因数据"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE memory_genes SET
                        activation_threshold = ?,
                        decay_rate = ?,
                        plasticity = ?,
                        strengthening_rate = ?,
                        weakening_rate = ?,
                        consolidation_level = ?,
                        last_accessed = ?,
                        access_count = ?,
                        success_rate = ?,
                        failure_count = ?,
                        total_attempts = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE memory_id = ?
                """, (
                    gene_data.get('activation_threshold', 0.5),
                    gene_data.get('decay_rate', 0.05),
                    gene_data.get('plasticity', 0.8),
                    gene_data.get('strengthening_rate', 0.1),
                    gene_data.get('weakening_rate', 0.15),
                    gene_data.get('consolidation_level', 0),
                    gene_data.get('last_accessed'),
                    gene_data.get('access_count', 0),
                    gene_data.get('success_rate', 0.0),
                    gene_data.get('failure_count', 0),
                    gene_data.get('total_attempts', 0),
                    memory_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating gene: {e}")
            return False

    def insert_synapse(self, source_id: int, target_id: int, weight: float = 0.0) -> bool:
        """插入突触连接"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO synapses
                    (source_id, target_id, weight, co_activation_count, created_at, updated_at)
                    VALUES (?, ?, ?, COALESCE((SELECT co_activation_count FROM synapses
                        WHERE source_id = ? AND target_id = ?), 0) + 1,
                        COALESCE((SELECT created_at FROM synapses
                        WHERE source_id = ? AND target_id = ?), CURRENT_TIMESTAMP),
                        CURRENT_TIMESTAMP)
                """, (source_id, target_id, weight, source_id, target_id, source_id, target_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting synapse: {e}")
            return False

    def get_synapses(self, source_id: int) -> List[Dict]:
        """获取突触连接列表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM synapses WHERE source_id = ?
            """, (source_id,))
            return [dict(row) for row in cursor.fetchall()]

    def update_synapse_weight(self, source_id: int, target_id: int, weight: float) -> bool:
        """更新突触权重"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE synapses SET
                        weight = ?,
                        last_co_activation = CURRENT_TIMESTAMP,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE source_id = ? AND target_id = ?
                """, (weight, source_id, target_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating synapse weight: {e}")
            return False

    def record_activation(self, memory_id: int, activation_value: float,
                        query_embedding: Optional[List[float]] = None,
                        context_tags: Optional[List[str]] = None) -> bool:
        """记录激活历史"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO activation_history
                    (memory_id, activation_value, query_embedding, context_tags)
                    VALUES (?, ?, ?, ?)
                """, (
                    memory_id,
                    activation_value,
                    json.dumps(query_embedding) if query_embedding else None,
                    json.dumps(context_tags) if context_tags else None
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording activation: {e}")
            return False

    def record_consolidation(self, memory_id: int, from_level: int,
                           to_level: int, reason: str = "") -> bool:
        """记录巩固历史"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO consolidation_history
                    (memory_id, from_level, to_level, reason)
                    VALUES (?, ?, ?, ?)
                """, (memory_id, from_level, to_level, reason))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording consolidation: {e}")
            return False

    def record_evolution(self, memory_id: int, evolution_type: str,
                        before_state: Dict, after_state: Dict, fitness: float) -> bool:
        """记录进化历史"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO evolution_history
                    (memory_id, evolution_type, before_state, after_state, fitness)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    memory_id,
                    evolution_type,
                    json.dumps(before_state),
                    json.dumps(after_state),
                    fitness
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording evolution: {e}")
            return False

    def get_all_genes(self) -> List[Dict]:
        """获取所有基因数据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memory_genes")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_synapses(self) -> List[Dict]:
        """获取所有突触连接"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM synapses")
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 记忆数量
            cursor.execute("SELECT COUNT(*) FROM memory_genes")
            total_memories = cursor.fetchone()[0]

            # 突触数量
            cursor.execute("SELECT COUNT(*) FROM synapses")
            total_synapses = cursor.fetchone()[0]

            # 巩固级别分布
            cursor.execute("""
                SELECT consolidation_level, COUNT(*)
                FROM memory_genes
                GROUP BY consolidation_level
            """)
            consolidation_distribution = {row[0]: row[1] for row in cursor.fetchall()}

            # 平均成功率
            cursor.execute("SELECT AVG(success_rate) FROM memory_genes")
            avg_success_rate = cursor.fetchone()[0] or 0.0

            # 平均访问次数
            cursor.execute("SELECT AVG(access_count) FROM memory_genes")
            avg_access_count = cursor.fetchone()[0] or 0.0

            return {
                "total_memories": total_memories,
                "total_synapses": total_synapses,
                "consolidation_distribution": consolidation_distribution,
                "avg_success_rate": avg_success_rate,
                "avg_access_count": avg_access_count
            }


def setup_genetic_tables(db_path: str):
    """设置基因神经元表"""
    db = GeneticMemoryDatabase(db_path)
    db.setup_tables()
    print(f"✓ 基因神经元表已创建: {db_path}")
