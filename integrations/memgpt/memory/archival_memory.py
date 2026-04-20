"""
归档记忆层 - Archival Memory Layer
长期记忆存储，支持检索
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
import sqlite3
import json
import hashlib
import os


class ArchivalMemoryEntry(BaseModel):
    """归档记忆条目"""
    id: str
    content: str
    summary: Optional[str] = None
    source_session: Optional[str] = None
    category: str = Field(default="general")
    importance: float = Field(default=0.5)
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = Field(default=0)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def estimate_tokens(self) -> int:
        """估算令牌数"""
        return len(self.content) // 4 + 1
    
    def to_search_text(self) -> str:
        """生成搜索文本"""
        parts = [self.content]
        if self.summary:
            parts.append(self.summary)
        parts.extend(self.tags)
        return " ".join(parts)


class ArchivalMemory:
    """
    归档记忆管理器
    
    特点：
    - 持久化存储
    - 支持语义检索
    - 自动压缩和摘要
    - 支持多种存储后端
    """
    
    def __init__(
        self,
        db_path: str = "memory/archival.db",
        agent_id: str = "default"
    ):
        """
        初始化归档记忆
        
        Args:
            db_path: 数据库路径
            agent_id: 代理ID
        """
        self.db_path = db_path
        self.agent_id = agent_id
        self._init_db()
        
    def _init_db(self):
        """初始化数据库"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archival_memory (
                id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                source_session TEXT,
                category TEXT DEFAULT 'general',
                importance REAL DEFAULT 0.5,
                embedding BLOB,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_id 
            ON archival_memory(agent_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON archival_memory(agent_id, category)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON archival_memory(agent_id, created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_importance 
            ON archival_memory(agent_id, importance DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def add(
        self,
        content: str,
        summary: Optional[str] = None,
        source_session: Optional[str] = None,
        category: str = "general",
        importance: float = 0.5,
        embedding: Optional[List[float]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        添加归档记忆
        
        Args:
            content: 记忆内容
            summary: 摘要
            source_session: 来源会话
            category: 类别
            importance: 重要性
            embedding: 嵌入向量
            tags: 标签列表
            metadata: 元数据
            
        Returns:
            条目ID
        """
        # 生成ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        entry_id = f"arch_{timestamp}_{content_hash}"
        
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO archival_memory 
            (id, agent_id, content, summary, source_session, category, 
             importance, embedding, created_at, last_accessed, access_count, 
             tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry_id,
            self.agent_id,
            content,
            summary,
            source_session,
            category,
            importance,
            json.dumps(embedding) if embedding else None,
            now,
            now,
            0,
            json.dumps(tags or []),
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        conn.close()
        
        return entry_id
    
    def get(self, entry_id: str) -> Optional[ArchivalMemoryEntry]:
        """获取条目并标记访问"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, summary, source_session, category, 
                   importance, embedding, created_at, last_accessed, 
                   access_count, tags, metadata
            FROM archival_memory
            WHERE id = ? AND agent_id = ?
        """, (entry_id, self.agent_id))
        
        row = cursor.fetchone()
        
        if row:
            # 更新访问计数
            cursor.execute("""
                UPDATE archival_memory
                SET access_count = access_count + 1,
                    last_accessed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), entry_id))
            conn.commit()
        
        conn.close()
        
        if row:
            return self._row_to_entry(row)
        return None
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[str] = None,
        min_importance: float = 0.0,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Tuple[ArchivalMemoryEntry, float]]:
        """
        搜索归档记忆
        
        Args:
            query: 搜索查询
            top_k: 返回数量
            category: 类别过滤
            min_importance: 最小重要性
            date_from: 起始日期
            date_to: 结束日期
            
        Returns:
            [(entry, relevance_score), ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 构建查询
        sql = """
            SELECT id, content, summary, source_session, category, 
                   importance, embedding, created_at, last_accessed, 
                   access_count, tags, metadata
            FROM archival_memory
            WHERE agent_id = ?
        """
        params = [self.agent_id]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if min_importance > 0:
            sql += " AND importance >= ?"
            params.append(min_importance)
        
        if date_from:
            sql += " AND created_at >= ?"
            params.append(date_from)
        
        if date_to:
            sql += " AND created_at <= ?"
            params.append(date_to)
        
        sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
        params.append(top_k * 2)  # 多取一些用于排序
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        # 简单的文本相关性计算
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        for row in rows:
            entry = self._row_to_entry(row)
            text = entry.to_search_text().lower()
            
            # 计算简单相关性分数
            score = 0.0
            for word in query_words:
                if word in text:
                    score += 1.0
            
            # 加入重要性权重
            score = score * (0.5 + 0.5 * entry.importance)
            
            if score > 0:
                results.append((entry, score))
        
        # 按分数排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        threshold: float = 0.7
    ) -> List[Tuple[ArchivalMemoryEntry, float]]:
        """
        基于嵌入向量的语义搜索
        
        Args:
            query_embedding: 查询嵌入
            top_k: 返回数量
            threshold: 相似度阈值
            
        Returns:
            [(entry, similarity), ...]
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, summary, source_session, category, 
                   importance, embedding, created_at, last_accessed, 
                   access_count, tags, metadata
            FROM archival_memory
            WHERE agent_id = ? AND embedding IS NOT NULL
        """, (self.agent_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entry = self._row_to_entry(row)
            if entry.embedding:
                # 计算余弦相似度
                similarity = self._cosine_similarity(query_embedding, entry.embedding)
                if similarity >= threshold:
                    results.append((entry, similarity))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_by_category(self, category: str, limit: int = 100) -> List[ArchivalMemoryEntry]:
        """按类别获取条目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, summary, source_session, category, 
                   importance, embedding, created_at, last_accessed, 
                   access_count, tags, metadata
            FROM archival_memory
            WHERE agent_id = ? AND category = ?
            ORDER BY importance DESC, created_at DESC
            LIMIT ?
        """, (self.agent_id, category, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def get_recent(self, days: int = 7, limit: int = 100) -> List[ArchivalMemoryEntry]:
        """获取最近的条目"""
        from datetime import timedelta
        
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, summary, source_session, category, 
                   importance, embedding, created_at, last_accessed, 
                   access_count, tags, metadata
            FROM archival_memory
            WHERE agent_id = ? AND created_at >= ?
            ORDER BY created_at DESC
            LIMIT ?
        """, (self.agent_id, date_from, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_entry(row) for row in rows]
    
    def delete(self, entry_id: str) -> bool:
        """删除条目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM archival_memory
            WHERE id = ? AND agent_id = ?
        """, (entry_id, self.agent_id))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM archival_memory WHERE agent_id = ?
        """, (self.agent_id,))
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT category, COUNT(*) 
            FROM archival_memory 
            WHERE agent_id = ?
            GROUP BY category
        """, (self.agent_id,))
        by_category = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT AVG(importance) 
            FROM archival_memory 
            WHERE agent_id = ?
        """, (self.agent_id,))
        avg_importance = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "total_entries": total,
            "by_category": by_category,
            "avg_importance": avg_importance,
            "db_path": self.db_path
        }
    
    def _row_to_entry(self, row: tuple) -> ArchivalMemoryEntry:
        """将数据库行转换为条目对象"""
        return ArchivalMemoryEntry(
            id=row[0],
            content=row[1],
            summary=row[2],
            source_session=row[3],
            category=row[4],
            importance=row[5],
            embedding=json.loads(row[6]) if row[6] else None,
            created_at=datetime.fromisoformat(row[7]),
            last_accessed=datetime.fromisoformat(row[8]),
            access_count=row[9],
            tags=json.loads(row[10]),
            metadata=json.loads(row[11])
        )
