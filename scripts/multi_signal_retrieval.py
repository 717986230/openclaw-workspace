#!/usr/bin/env python3
"""
Multi-Signal Retrieval System for Erbing Memory
Three-layer parallel retrieval with weighted score fusion.
"""

import sqlite3
import re
import math
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum

DB_PATH = "/Users/xinglong/openclaw-workspace/memory/database/xiaozhi_memory.db"

# Fusion weights
SEMANTIC_WEIGHT = 0.4
KEYWORD_WEIGHT = 0.35
ENTITY_WEIGHT = 0.25

# Memory types
MEMORY_TYPES = ["core_memory", "event", "learning", "preference", "skill"]


@dataclass
class MemoryRecord:
    id: int
    type: str
    title: str
    content: str
    category: str
    tags: str
    importance: int
    created_at: str
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    entity_score: float = 0.0
    final_score: float = 0.0


class TextAnalyzer:
    """Simple semantic analysis without external embedding APIs."""

    def __init__(self):
        # Stopwords for Chinese and English
        self.stopwords = {
            '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
            '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
            '自己', '这', '那', '它', '他', '她', '们', '中', '来', '对', '以', '可以', '把',
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
            'and', 'or', 'but', 'if', 'then', 'because', 'as', 'until', 'while',
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from',
            'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'each',
            'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'into'
        }
        # Common Chinese character patterns
        self.char_pattern = re.compile(r'[\u4e00-\u9fff]+|[a-zA-Z]+')

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words/phrases."""
        if not text:
            return []
        tokens = []
        # Extract Chinese segments and English words
        for match in self.char_pattern.finditer(text.lower()):
            segment = match.group()
            if re.match(r'[\u4e00-\u9fff]+', segment):
                # Chinese: extract consecutive characters in groups of 2-4
                for i in range(len(segment)):
                    for n in [2, 3, 4]:
                        if i + n <= len(segment):
                            token = segment[i:i+n]
                            if token not in self.stopwords:
                                tokens.append(token)
            else:
                # English: split by common delimiters
                words = re.split(r'[_\s\-.,!?;:\'"()\[\]{}]+', segment)
                for w in words:
                    if w and w not in self.stopwords:
                        tokens.append(w)
        return tokens

    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts using token overlap."""
        if not text1 or not text2:
            return 0.0
        tokens1 = set(self.tokenize(text1))
        tokens2 = set(self.tokenize(text2))
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        # Jaccard similarity
        jaccard = len(intersection) / len(union) if union else 0.0
        # Boost for title matches
        title_bonus = 0.0
        if hasattr(self, '_last_title1') and hasattr(self, '_last_title2'):
            title_tokens1 = set(self.tokenize(self._last_title1))
            title_tokens2 = set(self.tokenize(self._last_title2))
            title_intersection = title_tokens1 & title_tokens2
            if title_intersection:
                title_bonus = min(0.3, len(title_intersection) * 0.05)
        return min(1.0, jaccard + title_bonus)


class EntityExtractor:
    """Extract and match named entities."""

    def __init__(self):
        # Common entity patterns
        self.entity_patterns = {
            'person': re.compile(r'[A-Z\u4e00-\u9fff][a-z\u4e00-\u9fff]+(?:\s+[A-Z\u4e00-\u9fff][a-z\u4e00-\u9fff]+)+'),
            'project': re.compile(r'(?:project|项目|作品|产品)[:\s]+([A-Za-z0-9\u4e00-\u9fff_\-]+)', re.I),
            'concept': re.compile(r'(?:概念|concept|理论|theory|原则)[:\s]+([A-Za-z0-9\u4e00-\u9fff_\-]+)', re.I),
            'skill': re.compile(r'(?:skill|技能|技术|能力)[:\s]+([A-Za-z0-9\u4e00-\u9fff_\-]+)', re.I),
            'org': re.compile(r'(?:公司|企业|org|company)[:\s]+([A-Za-z0-9\u4e00-\u9fff_\-]+)', re.I),
        }
        # Capitalized words (potential proper nouns)
        self.capitalized_pattern = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')
        # Quoted terms
        self.quoted_pattern = re.compile(r'["\'"]([^"\']+)["\']')

    def extract_entities(self, text: str) -> set:
        """Extract all entities from text."""
        if not text:
            return set()
        entities = set()
        text_lower = text.lower()
        # Extract by patterns
        for pattern_name, pattern in self.entity_patterns.items():
            for match in pattern.finditer(text):
                if match.groups():
                    entity = match.group(1).strip().lower()
                    if entity:
                        entities.add(entity)
                else:
                    entity = match.group(0).strip().lower()
                    if entity:
                        entities.add(entity)
        # Extract quoted terms
        for match in self.quoted_pattern.finditer(text):
            entity = match.group(1).strip().lower()
            if entity and len(entity) > 1:
                entities.add(entity)
        # Extract capitalized English words/phrases
        for match in self.capitalized_pattern.finditer(text):
            entity = match.group(0).lower()
            if entity and len(entity) > 2:
                entities.add(entity)
        return entities

    def match_score(self, query_entities: set, memory_entities: set) -> float:
        """Compute entity match score."""
        if not query_entities or not memory_entities:
            return 0.0
        intersection = query_entities & memory_entities
        if not intersection:
            return 0.0
        # Jaccard-based score with boost for multiple matches
        jaccard = len(intersection) / len(query_entities | memory_entities)
        return min(1.0, jaccard * (1 + math.log1p(len(intersection))))


class MultiSignalRetrieval:
    """Multi-signal retrieval engine with three-layer parallel search."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.text_analyzer = TextAnalyzer()
        self.entity_extractor = EntityExtractor()
        self._conn: Optional[sqlite3.Connection] = None

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _semantic_search(self, query: str, limit: int = 20) -> Dict[int, float]:
        """Layer 1: Semantic similarity search using FTS5."""
        conn = self._get_connection()
        scores = {}
        query_tokens = self.text_analyzer.tokenize(query)
        if not query_tokens:
            return scores
        # Use FTS5 for initial filtering
        fts_query = ' OR '.join(query_tokens[:10])
        try:
            cursor = conn.execute("""
                SELECT id, title, content, tags
                FROM memories m
                INNER JOIN memory_index idx ON m.id = idx.rowid
                WHERE memory_index MATCH ?
                LIMIT 100
            """, (fts_query,))
            rows = cursor.fetchall()
        except Exception:
            # Fallback to LIKE search if FTS fails
            like_pattern = '%' + '%'.join(query_tokens[:3]) + '%'
            cursor = conn.execute("""
                SELECT id, title, content, tags
                FROM memories
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                LIMIT 100
            """, (like_pattern, like_pattern, like_pattern))
            rows = cursor.fetchall()
        # Compute semantic scores
        for row in rows:
            memory_title = row['title'] or ''
            memory_content = row['content'] or ''
            self.text_analyzer._last_title1 = query
            self.text_analyzer._last_title2 = memory_title
            score = self.text_analyzer.compute_similarity(query, memory_title)
            content_score = self.text_analyzer.compute_similarity(query, memory_content)
            scores[row['id']] = max(score, content_score * 0.7)
        return scores

    def _keyword_search(self, query: str, limit: int = 20) -> Dict[int, float]:
        """Layer 2: Keyword exact matching."""
        conn = self._get_connection()
        scores = {}
        # Parse query into search terms
        terms = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z0-9_\-]+', query.lower())
        if not terms:
            return scores
        # Build SQL with OR conditions for each term
        conditions = []
        params = []
        for term in terms:
            conditions.append("(title LIKE ? OR content LIKE ? OR tags LIKE ?)")
            pattern = f"%{term}%"
            params.extend([pattern, pattern, pattern])
        sql = f"""
            SELECT id, title, content, tags, category
            FROM memories
            WHERE {' OR '.join(conditions)}
            LIMIT 100
        """
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()
        for row in rows:
            matched_fields = 0
            total_fields = 0
            title = row['title'] or ''
            content = row['content'] or ''
            tags = row['tags'] or ''
            # Count matches per field
            for field_text in [title, content, tags]:
                total_fields += 1
                field_lower = field_text.lower()
                if any(term in field_lower for term in terms):
                    matched_fields += 1
            # Title matches weighted higher
            title_lower = title.lower()
            if any(term in title_lower for term in terms):
                matched_fields += 0.5
            # Calculate score
            max_possible = total_fields + 0.5
            scores[row['id']] = min(1.0, matched_fields / max_possible)
        return scores

    def _entity_search(self, query: str, limit: int = 20) -> Dict[int, float]:
        """Layer 3: Entity matching."""
        conn = self._get_connection()
        scores = {}
        query_entities = self.entity_extractor.extract_entities(query)
        if not query_entities:
            return scores
        # Get all memories and compute entity matches
        cursor = conn.execute("""
            SELECT id, title, content, tags, category
            FROM memories
            LIMIT 100
        """)
        rows = cursor.fetchall()
        for row in rows:
            combined_text = ' '.join([
                row['title'] or '',
                row['content'] or '',
                row['tags'] or '',
                row['category'] or ''
            ])
            memory_entities = self.entity_extractor.extract_entities(combined_text)
            scores[row['id']] = self.entity_extractor.match_score(query_entities, memory_entities)
        return scores

    def _fetch_all_memories(self) -> List[MemoryRecord]:
        """Fetch all memories from database."""
        conn = self._get_connection()
        cursor = conn.execute("""
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [MemoryRecord(**dict(row)) for row in rows]

    def _normalize_scores(self, scores: Dict[int, float]) -> Dict[int, float]:
        """Normalize scores to 0-1 range."""
        if not scores:
            return scores
        max_score = max(scores.values())
        if max_score == 0:
            return {k: 0.0 for k in scores}
        return {k: v / max_score for k, v in scores.items()}

    def search(self, query: str, limit: int = 10, memory_type: Optional[str] = None) -> List[MemoryRecord]:
        """
        Execute multi-signal retrieval with parallel search and score fusion.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return
            memory_type: Optional filter by memory type
            
        Returns:
            List of MemoryRecord objects sorted by final_score descending
        """
        # Execute three-layer search in parallel
        semantic_scores = {}
        keyword_scores = {}
        entity_scores = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._semantic_search, query): 'semantic',
                executor.submit(self._keyword_search, query): 'keyword',
                executor.submit(self._entity_search, query): 'entity'
            }
            for future in as_completed(futures):
                signal_type = futures[future]
                try:
                    result = future.result()
                    if signal_type == 'semantic':
                        semantic_scores = result
                    elif signal_type == 'keyword':
                        keyword_scores = result
                    else:
                        entity_scores = result
                except Exception as e:
                    print(f"Error in {signal_type} search: {e}")
        # Normalize scores
        semantic_norm = self._normalize_scores(semantic_scores)
        keyword_norm = self._normalize_scores(keyword_scores)
        entity_norm = self._normalize_scores(entity_scores)
        # Get all memory IDs involved
        all_ids = set(semantic_norm) | set(keyword_norm) | set(entity_norm)
        # Fetch memory records
        conn = self._get_connection()
        placeholders = ','.join('?' * len(all_ids)) if all_ids else 'NULL'
        sql = f"""
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories
            WHERE id IN ({placeholders})
        """
        if memory_type:
            sql = f"""
                SELECT id, type, title, content, category, tags, importance, created_at
                FROM memories
                WHERE id IN ({placeholders}) AND type = ?
            """
            cursor = conn.execute(sql, list(all_ids) + [memory_type])
        else:
            cursor = conn.execute(sql, list(all_ids))
        rows = cursor.fetchall()
        records = []
        for row in rows:
            record = MemoryRecord(**dict(row))
            record.semantic_score = semantic_norm.get(row['id'], 0.0)
            record.keyword_score = keyword_norm.get(row['id'], 0.0)
            record.entity_score = entity_norm.get(row['id'], 0.0)
            record.final_score = (
                SEMANTIC_WEIGHT * record.semantic_score +
                KEYWORD_WEIGHT * record.keyword_score +
                ENTITY_WEIGHT * record.entity_score
            )
            records.append(record)
        # Sort by final score and limit
        records.sort(key=lambda r: r.final_score, reverse=True)
        return records[:limit]

    def search_by_category(self, query: str, category: str, limit: int = 10) -> List[MemoryRecord]:
        """Search memories within a specific category."""
        conn = self._get_connection()
        placeholders = ','.join('?' * len(MEMORY_TYPES))
        sql = f"""
            SELECT id, type, title, content, category, tags, importance, created_at
            FROM memories
            WHERE category = ?
        """
        cursor = conn.execute(sql, (category,))
        rows = cursor.fetchall()
        all_ids = [row['id'] for row in rows]
        if not all_ids:
            return []
        # Run searches restricted to category memories
        semantic_scores = {}
        keyword_scores = {}
        entity_scores = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._semantic_search, query): 'semantic',
                executor.submit(self._keyword_search, query): 'keyword',
                executor.submit(self._entity_search, query): 'entity'
            }
            for future in as_completed(futures):
                signal_type = futures[future]
                try:
                    result = future.result()
                    result = {k: v for k, v in result.items() if k in all_ids}
                    if signal_type == 'semantic':
                        semantic_scores = result
                    elif signal_type == 'keyword':
                        keyword_scores = result
                    else:
                        entity_scores = result
                except Exception as e:
                    print(f"Error in {signal_type} search: {e}")
        semantic_norm = self._normalize_scores(semantic_scores)
        keyword_norm = self._normalize_scores(keyword_scores)
        entity_norm = self._normalize_scores(entity_scores)
        records = []
        for row in rows:
            record = MemoryRecord(**dict(row))
            record.semantic_score = semantic_norm.get(row['id'], 0.0)
            record.keyword_score = keyword_norm.get(row['id'], 0.0)
            record.entity_score = entity_norm.get(row['id'], 0.0)
            record.final_score = (
                SEMANTIC_WEIGHT * record.semantic_score +
                KEYWORD_WEIGHT * record.keyword_score +
                ENTITY_WEIGHT * record.entity_score
            )
            records.append(record)
        records.sort(key=lambda r: r.final_score, reverse=True)
        return records[:limit]


# SQLite-compatible interface functions
def create_retrieval_engine(db_path: str = DB_PATH) -> MultiSignalRetrieval:
    """Create a retrieval engine instance."""
    return MultiSignalRetrieval(db_path)


def search_memories(
    query: str,
    limit: int = 10,
    memory_type: Optional[str] = None,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """
    Search memories using multi-signal retrieval.
    
    SQLite-compatible interface function.
    
    Args:
        query: Search query string
        limit: Maximum results to return
        memory_type: Optional filter by memory type
        db_path: Path to SQLite database
        
    Returns:
        List of memory dictionaries with scores
    """
    engine = MultiSignalRetrieval(db_path)
    try:
        records = engine.search(query, limit, memory_type)
        results = []
        for r in records:
            results.append({
                'id': r.id,
                'type': r.type,
                'title': r.title,
                'content': r.content,
                'category': r.category,
                'tags': r.tags,
                'importance': r.importance,
                'created_at': r.created_at,
                'semantic_score': round(r.semantic_score, 4),
                'keyword_score': round(r.keyword_score, 4),
                'entity_score': round(r.entity_score, 4),
                'final_score': round(r.final_score, 4)
            })
        return results
    finally:
        engine.close()


def search_by_category(
    query: str,
    category: str,
    limit: int = 10,
    db_path: str = DB_PATH
) -> List[Dict[str, Any]]:
    """Search memories within a specific category."""
    engine = MultiSignalRetrieval(db_path)
    try:
        records = engine.search_by_category(query, category, limit)
        results = []
        for r in records:
            results.append({
                'id': r.id,
                'type': r.type,
                'title': r.title,
                'content': r.content,
                'category': r.category,
                'tags': r.tags,
                'importance': r.importance,
                'created_at': r.created_at,
                'semantic_score': round(r.semantic_score, 4),
                'keyword_score': round(r.keyword_score, 4),
                'entity_score': round(r.entity_score, 4),
                'final_score': round(r.final_score, 4)
            })
        return results
    finally:
        engine.close()


# CLI for testing
if __name__ == '__main__':
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    engine = MultiSignalRetrieval()
    if query:
        results = engine.search(query, limit=10)
        print(f"\n=== Multi-Signal Retrieval Results ===")
        print(f"Query: {query}")
        print(f"Found {len(results)} results\n")
        for r in results:
            print(f"[{r.final_score:.4f}] [{r.type}] {r.title}")
            print(f"  semantic={r.semantic_score:.3f}, keyword={r.keyword_score:.3f}, entity={r.entity_score:.3f}")
            print(f"  {r.content[:100]}..." if r.content and len(r.content) > 100 else f"  {r.content}")
            print()
    else:
        print("Usage: python multi_signal_retrieval.py <query>")
    engine.close()