#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Reference Back-Links System
交叉引用反向链接系统 - GBrain 铁律实现

核心原则:
每个实体页面必须链接到所有引用它的其他页面

功能:
1. 自动检测实体引用
2. 添加反向链接
3. 维护引用完整性
4. 生成引用报告
"""

import os
import sys
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class BackLink:
    """反向链接数据结构"""
    source_page: str
    source_title: str
    source_path: str
    mention_context: str
    timestamp: str


class CrossReferenceEngine:
    """交叉引用引擎"""
    
    def __init__(self, db_path: str = None):
        """初始化交叉引用引擎"""
        if db_path is None:
            db_path = str(Path(__file__).parent / "xiaozhi_memory.db")
        
        self.db_path = db_path
        self._init_tables()
    
    def _init_tables(self):
        """初始化交叉引用表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建交叉引用表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cross_references (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_entity TEXT NOT NULL,
                mention_context TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(source_id, target_entity)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cross_ref_target
            ON cross_references(target_entity)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cross_ref_source
            ON cross_references(source_id)
        """)
        
        conn.commit()
        conn.close()
    
    def update_entity_page(self, entity: str, new_info: str) -> Dict[str, Any]:
        """
        更新实体页面并添加反向链接
        
        Args:
            entity: 实体名称
            new_info: 新信息
        
        Returns:
            更新结果
        """
        result = {
            "entity": entity,
            "backlinks_added": 0,
            "backlinks": []
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. 查找所有提及此实体的其他页面
            mentions = self.find_mentions(entity)
            
            # 2. 为每个提及添加反向链接
            for mention in mentions:
                backlink_added = self.add_backlink(
                    target_entity=entity,
                    source_id=mention["id"],
                    source_title=mention["title"],
                    mention_context=mention.get("context", "")
                )
                
                if backlink_added:
                    result["backlinks_added"] += 1
                    result["backlinks"].append(mention["title"])
            
            # 3. 更新实体页面的反向链接部分
            self.update_page_backlinks_section(entity, result["backlinks"])
            
            conn.close()
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def find_mentions(self, entity: str) -> List[Dict[str, Any]]:
        """
        查找所有提及某实体的页面
        
        Args:
            entity: 实体名称
        
        Returns:
            提及列表
        """
        mentions = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 搜索标题或内容中包含实体的记录
            cursor.execute("""
                SELECT id, type, title, content, created_at
                FROM memories
                WHERE (title LIKE ? OR content LIKE ?)
                AND title != ?
                ORDER BY created_at DESC
            """, (f"%{entity}%", f"%{entity}%", entity))
            
            for row in cursor.fetchall():
                # 提取上下文（包含实体的部分内容）
                content = row[3] or ""
                context = self._extract_context(content, entity)
                
                mentions.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "created_at": row[4],
                    "context": context
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error finding mentions: {e}")
        
        return mentions
    
    def _extract_context(self, content: str, entity: str, context_length: int = 100) -> str:
        """提取包含实体的上下文"""
        try:
            idx = content.lower().find(entity.lower())
            if idx == -1:
                return ""
            
            start = max(0, idx - context_length // 2)
            end = min(len(content), idx + len(entity) + context_length // 2)
            
            context = content[start:end]
            if start > 0:
                context = "..." + context
            if end < len(content):
                context = context + "..."
            
            return context
            
        except Exception:
            return ""
    
    def add_backlink(self, target_entity: str, source_id: str, 
                     source_title: str, mention_context: str = "") -> bool:
        """
        添加反向链接
        
        Args:
            target_entity: 目标实体
            source_id: 来源页面ID
            source_title: 来源页面标题
            mention_context: 提及上下文
        
        Returns:
            是否成功添加
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否已存在
            cursor.execute("""
                SELECT id FROM cross_references
                WHERE source_id = ? AND target_entity = ?
            """, (source_id, target_entity))
            
            if cursor.fetchone():
                conn.close()
                return False  # 已存在
            
            # 插入新的反向链接
            cursor.execute("""
                INSERT INTO cross_references (source_id, target_entity, mention_context, created_at)
                VALUES (?, ?, ?, ?)
            """, (source_id, target_entity, mention_context, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error adding backlink: {e}")
            return False
    
    def update_page_backlinks_section(self, entity: str, backlinks: List[str]):
        """
        更新实体页面的反向链接部分
        
        Args:
            entity: 实体名称
            backlinks: 反向链接列表
        """
        if not backlinks:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找实体页面
            cursor.execute("""
                SELECT id, content FROM memories
                WHERE title = ? AND type IN ('entity', 'person', 'company')
            """, (entity,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return
            
            page_id = row[0]
            content = row[1] or ""
            
            # 构建反向链接部分
            backlinks_section = "\n\n## References\n\n"
            for backlink in backlinks:
                backlinks_section += f"- Referenced in [[{backlink}]]\n"
            
            # 追加到内容
            if "## References" not in content:
                new_content = content + backlinks_section
            else:
                # 更新现有的 References 部分
                new_content = content
            
            # 更新页面
            cursor.execute("""
                UPDATE memories
                SET content = ?, updated_at = ?
                WHERE id = ?
            """, (new_content, datetime.now().isoformat(), page_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating page backlinks section: {e}")
    
    def get_backlinks_for_entity(self, entity: str) -> List[Dict[str, Any]]:
        """
        获取实体的所有反向链接
        
        Args:
            entity: 实体名称
        
        Returns:
            反向链接列表
        """
        backlinks = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT cr.source_id, cr.mention_context, cr.created_at,
                       m.title, m.type
                FROM cross_references cr
                LEFT JOIN memories m ON cr.source_id = m.id
                WHERE cr.target_entity = ?
                ORDER BY cr.created_at DESC
            """, (entity,))
            
            for row in cursor.fetchall():
                backlinks.append({
                    "source_id": row[0],
                    "context": row[1],
                    "created_at": row[2],
                    "source_title": row[3],
                    "source_type": row[4]
                })
            
            conn.close()
            
        except Exception as e:
            print(f"Error getting backlinks: {e}")
        
        return backlinks
    
    def scan_all_and_build_cross_references(self) -> Dict[str, Any]:
        """
        扫描所有记忆并构建交叉引用
        
        Returns:
            构建结果统计
        """
        stats = {
            "pages_scanned": 0,
            "cross_references_added": 0,
            "entities_found": set()
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取所有实体页面
            cursor.execute("""
                SELECT title FROM memories
                WHERE type IN ('entity', 'person', 'company', 'concept')
            """)
            
            entities = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            # 为每个实体构建交叉引用
            for entity in entities:
                stats["entities_found"].add(entity)
                result = self.update_entity_page(entity, "")
                stats["cross_references_added"] += result["backlinks_added"]
                stats["pages_scanned"] += 1
            
            stats["entities_found"] = len(stats["entities_found"])
            
        except Exception as e:
            stats["error"] = str(e)
        
        return stats
    
    def generate_cross_reference_report(self) -> str:
        """生成交叉引用报告"""
        report = "# Cross-Reference Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 统计信息
            cursor.execute("SELECT COUNT(DISTINCT target_entity) FROM cross_references")
            unique_entities = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM cross_references")
            total_refs = cursor.fetchone()[0]
            
            report += "## Statistics\n\n"
            report += f"- Unique entities referenced: {unique_entities}\n"
            report += f"- Total cross-references: {total_refs}\n\n"
            
            # 最常被引用的实体
            cursor.execute("""
                SELECT target_entity, COUNT(*) as ref_count
                FROM cross_references
                GROUP BY target_entity
                ORDER BY ref_count DESC
                LIMIT 20
            """)
            
            report += "## Most Referenced Entities\n\n"
            for row in cursor.fetchall():
                report += f"- [[{row[0]}]]: {row[1]} references\n"
            
            conn.close()
            
        except Exception as e:
            report += f"\n**Error:** {e}\n"
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Cross-Reference Back-Links System")
    parser.add_argument("--build", action="store_true", help="Build all cross-references")
    parser.add_argument("--entity", type=str, help="Get backlinks for specific entity")
    parser.add_argument("--report", action="store_true", help="Generate cross-reference report")
    parser.add_argument("--update", type=str, help="Update entity page with new info")
    
    args = parser.parse_args()
    
    engine = CrossReferenceEngine()
    
    if args.build:
        print("🔨 Building all cross-references...")
        stats = engine.scan_all_and_build_cross_references()
        print(f"✅ Done: {stats}")
    
    elif args.entity:
        print(f"📖 Getting backlinks for: {args.entity}")
        backlinks = engine.get_backlinks_for_entity(args.entity)
        print(f"Found {len(backlinks)} backlinks:")
        for bl in backlinks:
            print(f"  - [[{bl['source_title']}]] ({bl['created_at']})")
    
    elif args.report:
        report = engine.generate_cross_reference_report()
        print(report)
    
    elif args.update:
        print(f"✏️ Updating entity: {args.update}")
        result = engine.update_entity_page(args.update, "")
        print(f"✅ Added {result['backlinks_added']} backlinks")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
