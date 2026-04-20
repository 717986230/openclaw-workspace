#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichment Tier System
实体丰富化分级系统

分级规则:
- Tier 1: 核心人员和公司 (10-15 API调用) - 深度丰富
- Tier 2: 值得注意的人员 (3-5 API调用) - 标准丰富
- Tier 3: 次要提及 (1-2 API调用) - 基础丰富

功能:
1. 实体分类
2. 分级丰富
3. 丰富度评估
4. 自动升级/降级
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class EntityTier(Enum):
    """实体层级"""
    TIER_1 = 1  # 核心 - 深度丰富
    TIER_2 = 2  # 值得注意 - 标准丰富
    TIER_3 = 3  # 次要 - 基础丰富
    UNKNOWN = 0  # 未知


@dataclass
class EnrichmentConfig:
    """丰富化配置"""
    tier: int
    name: str
    api_calls: int
    sources: List[str]
    depth: str
    description: str


# 预定义的丰富化配置
ENRICHMENT_CONFIGS = {
    1: EnrichmentConfig(
        tier=1,
        name="Core",
        api_calls=15,
        sources=["linkedin", "twitter", "github", "news", "crunchbase", "company_site", "papers"],
        depth="deep",
        description="核心人员和公司 - 深度丰富化"
    ),
    2: EnrichmentConfig(
        tier=2,
        name="Notable",
        api_calls=5,
        sources=["linkedin", "twitter", "news"],
        depth="standard",
        description="值得注意的人员 - 标准丰富化"
    ),
    3: EnrichmentConfig(
        tier=3,
        name="Mentioned",
        api_calls=2,
        sources=["search"],
        depth="basic",
        description="次要提及 - 基础丰富化"
    )
}


class EnrichmentTierEngine:
    """丰富化分级引擎"""
    
    def __init__(self, db_path: str = None):
        """初始化丰富化分级引擎"""
        if db_path is None:
            db_path = str(Path(__file__).parent / "xiaozhi_memory.db")
        
        self.db_path = db_path
        self._init_tables()
        
        # 核心圈（可以手动配置）
        self.core_circle = set()
        self.notable_contacts = set()
    
    def _init_tables(self):
        """初始化丰富化表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建实体丰富化表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entity_enrichment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT NOT NULL,
                entity_type TEXT,
                tier INTEGER DEFAULT 3,
                enrichment_score REAL DEFAULT 0,
                last_enriched TEXT,
                enrichment_count INTEGER DEFAULT 0,
                sources_used TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(entity_name)
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enrichment_tier
            ON entity_enrichment(tier)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_enrichment_score
            ON entity_enrichment(enrichment_score)
        """)
        
        conn.commit()
        conn.close()
    
    def classify_tier(self, entity: str, context: Dict[str, Any] = None) -> int:
        """
        分类实体层级
        
        Args:
            entity: 实体名称
            context: 上下文信息
        
        Returns:
            层级 (1-3)
        """
        # 1. 检查是否在核心圈
        if entity in self.core_circle:
            return 1
        
        # 2. 检查是否在值得注意名单
        if entity in self.notable_contacts:
            return 2
        
        # 3. 检查历史提及频率
        mention_count = self._get_mention_count(entity)
        
        if mention_count >= 10:
            return 1  # 高频提及 -> 核心
        elif mention_count >= 3:
            return 2  # 中频提及 -> 值得注意
        
        # 4. 检查上下文（如果提供）
        if context:
            if context.get("importance") == "high":
                return 1
            elif context.get("importance") == "medium":
                return 2
        
        # 5. 默认为 Tier 3
        return 3
    
    def _get_mention_count(self, entity: str) -> int:
        """获取实体提及次数"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM memories
                WHERE title LIKE ? OR content LIKE ?
            """, (f"%{entity}%", f"%{entity}%"))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count
            
        except Exception:
            return 0
    
    def get_enrichment_config(self, tier: int) -> EnrichmentConfig:
        """获取丰富化配置"""
        return ENRICHMENT_CONFIGS.get(tier, ENRICHMENT_CONFIGS[3])
    
    def enrich(self, entity: str, tier: int = None, context: Dict = None) -> Dict[str, Any]:
        """
        按层级丰富实体
        
        Args:
            entity: 实体名称
            tier: 层级（可选，自动分类）
            context: 上下文信息
        
        Returns:
            丰富化结果
        """
        # 自动分类层级
        if tier is None:
            tier = self.classify_tier(entity, context)
        
        config = self.get_enrichment_config(tier)
        
        result = {
            "entity": entity,
            "tier": tier,
            "config": {
                "name": config.name,
                "api_calls": config.api_calls,
                "sources": config.sources,
                "depth": config.depth
            },
            "enriched": False,
            "data": {}
        }
        
        # 执行丰富化
        if tier == 1:
            result["data"] = self._full_enrichment(entity, config)
        elif tier == 2:
            result["data"] = self._standard_enrichment(entity, config)
        else:
            result["data"] = self._minimal_enrichment(entity, config)
        
        # 更新数据库
        self._update_enrichment_record(entity, tier, result["data"])
        result["enriched"] = True
        
        return result
    
    def _full_enrichment(self, entity: str, config: EnrichmentConfig) -> Dict[str, Any]:
        """
        深度丰富化 (Tier 1)
        10-15 API调用
        """
        data = {
            "sources_queried": [],
            "fields_collected": [],
            "confidence": 0
        }
        
        # 模拟丰富化过程
        # TODO: 集成真实的外部 API
        
        # 搜索每个数据源
        for source in config.sources:
            # 这里应该调用相应的 API
            # 现在只是模拟
            data["sources_queried"].append(source)
        
        data["fields_collected"] = [
            "name", "title", "company", "bio",
            "social_links", "recent_activity", "connections"
        ]
        data["confidence"] = 0.95
        
        return data
    
    def _standard_enrichment(self, entity: str, config: EnrichmentConfig) -> Dict[str, Any]:
        """
        标准丰富化 (Tier 2)
        3-5 API调用
        """
        data = {
            "sources_queried": [],
            "fields_collected": [],
            "confidence": 0
        }
        
        # 只查询主要数据源
        for source in config.sources:
            data["sources_queried"].append(source)
        
        data["fields_collected"] = [
            "name", "title", "company", "social_links"
        ]
        data["confidence"] = 0.75
        
        return data
    
    def _minimal_enrichment(self, entity: str, config: EnrichmentConfig) -> Dict[str, Any]:
        """
        基础丰富化 (Tier 3)
        1-2 API调用
        """
        data = {
            "sources_queried": config.sources,
            "fields_collected": ["name"],
            "confidence": 0.5
        }
        
        return data
    
    def _update_enrichment_record(self, entity: str, tier: int, data: Dict):
        """更新丰富化记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            # 检查是否已存在
            cursor.execute("""
                SELECT id, enrichment_count FROM entity_enrichment
                WHERE entity_name = ?
            """, (entity,))
            
            row = cursor.fetchone()
            
            if row:
                # 更新现有记录
                new_count = row[1] + 1
                cursor.execute("""
                    UPDATE entity_enrichment
                    SET tier = ?, 
                        enrichment_score = ?,
                        last_enriched = ?,
                        enrichment_count = ?,
                        sources_used = ?,
                        updated_at = ?
                    WHERE entity_name = ?
                """, (
                    tier,
                    data.get("confidence", 0),
                    now,
                    new_count,
                    json.dumps(data.get("sources_queried", [])),
                    now,
                    entity
                ))
            else:
                # 创建新记录
                cursor.execute("""
                    INSERT INTO entity_enrichment
                    (entity_name, tier, enrichment_score, last_enriched, 
                     enrichment_count, sources_used, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entity,
                    tier,
                    data.get("confidence", 0),
                    now,
                    1,
                    json.dumps(data.get("sources_queried", [])),
                    now,
                    now
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error updating enrichment record: {e}")
    
    def assess_enrichment_level(self, entity: str) -> Dict[str, Any]:
        """
        评估实体的丰富度
        
        Args:
            entity: 实体名称
        
        Returns:
            丰富度评估结果
        """
        assessment = {
            "entity": entity,
            "current_tier": 3,
            "enrichment_score": 0,
            "last_enriched": None,
            "needs_enrichment": True,
            "recommendation": ""
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT tier, enrichment_score, last_enriched, enrichment_count
                FROM entity_enrichment
                WHERE entity_name = ?
            """, (entity,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                assessment["current_tier"] = row[0]
                assessment["enrichment_score"] = row[1]
                assessment["last_enriched"] = row[2]
                
                # 检查是否需要重新丰富
                if row[2]:  # last_enriched
                    last_enriched = datetime.fromisoformat(row[2])
                    days_since = (datetime.now() - last_enriched).days
                    
                    if days_since > 30:  # 超过30天
                        assessment["needs_enrichment"] = True
                        assessment["recommendation"] = f"Last enriched {days_since} days ago. Consider re-enrichment."
                    else:
                        assessment["needs_enrichment"] = False
                        assessment["recommendation"] = "Enrichment is recent."
            
        except Exception as e:
            assessment["error"] = str(e)
        
        return assessment
    
    def promote_entity(self, entity: str, new_tier: int) -> bool:
        """
        提升实体层级
        
        Args:
            entity: 实体名称
            new_tier: 新层级
        
        Returns:
            是否成功
        """
        if new_tier not in [1, 2, 3]:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE entity_enrichment
                SET tier = ?, updated_at = ?
                WHERE entity_name = ?
            """, (new_tier, datetime.now().isoformat(), entity))
            
            conn.commit()
            conn.close()
            
            # 更新内存中的集合
            if new_tier == 1:
                self.core_circle.add(entity)
            elif new_tier == 2:
                self.notable_contacts.add(entity)
            
            return True
            
        except Exception as e:
            print(f"Error promoting entity: {e}")
            return False
    
    def batch_enrich_entities(self, entities: List[str], 
                              auto_tier: bool = True) -> Dict[str, Any]:
        """
        批量丰富实体
        
        Args:
            entities: 实体列表
            auto_tier: 是否自动分类层级
        
        Returns:
            批量丰富化结果
        """
        results = {
            "total": len(entities),
            "enriched": 0,
            "by_tier": {1: 0, 2: 0, 3: 0},
            "entities": []
        }
        
        for entity in entities:
            tier = None if auto_tier else 3
            result = self.enrich(entity, tier)
            results["enriched"] += 1
            results["by_tier"][result["tier"]] += 1
            results["entities"].append(result)
        
        return results
    
    def generate_tier_report(self) -> str:
        """生成层级报告"""
        report = "# Enrichment Tier Report\n\n"
        report += f"Generated: {datetime.now().isoformat()}\n\n"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 统计各级别实体数量
            cursor.execute("""
                SELECT tier, COUNT(*) as count, AVG(enrichment_score) as avg_score
                FROM entity_enrichment
                GROUP BY tier
                ORDER BY tier
            """)
            
            report += "## Tier Distribution\n\n"
            report += "| Tier | Count | Avg Score | Description |\n"
            report += "|------|-------|-----------|-------------|\n"
            
            for row in cursor.fetchall():
                tier = row[0]
                config = self.get_enrichment_config(tier)
                report += f"| {tier} | {row[1]} | {row[2]:.2f} | {config.description} |\n"
            
            # 需要重新丰富的实体
            threshold = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute("""
                SELECT entity_name, tier, last_enriched
                FROM entity_enrichment
                WHERE last_enriched < ? OR last_enriched IS NULL
                ORDER BY tier, last_enriched
            """, (threshold,))
            
            report += "\n## Entities Needing Re-enrichment\n\n"
            needs_enrichment = cursor.fetchall()
            if needs_enrichment:
                for row in needs_enrichment:
                    report += f"- [[{row[0]}]] (Tier {row[1]}, last: {row[2] or 'never'})\n"
            else:
                report += "All entities are up to date.\n"
            
            conn.close()
            
        except Exception as e:
            report += f"\n**Error:** {e}\n"
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enrichment Tier System")
    parser.add_argument("--enrich", type=str, help="Enrich a specific entity")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3], help="Force specific tier")
    parser.add_argument("--assess", type=str, help="Assess enrichment level")
    parser.add_argument("--promote", type=str, help="Promote entity to --tier")
    parser.add_argument("--report", action="store_true", help="Generate tier report")
    parser.add_argument("--batch", type=str, help="Batch enrich entities (comma-separated)")
    
    args = parser.parse_args()
    
    engine = EnrichmentTierEngine()
    
    if args.enrich:
        print(f"🔍 Enriching: {args.enrich}")
        result = engine.enrich(args.enrich, args.tier)
        print(f"  Tier: {result['tier']} ({result['config']['name']})")
        print(f"  Sources: {result['config']['sources']}")
        print(f"  Confidence: {result['data'].get('confidence', 0):.2f}")
    
    elif args.assess:
        print(f"📊 Assessing: {args.assess}")
        assessment = engine.assess_enrichment_level(args.assess)
        print(f"  Current Tier: {assessment['current_tier']}")
        print(f"  Score: {assessment['enrichment_score']}")
        print(f"  Recommendation: {assessment['recommendation']}")
    
    elif args.promote and args.tier:
        print(f"⬆️ Promoting {args.promote} to Tier {args.tier}")
        success = engine.promote_entity(args.promote, args.tier)
        print(f"  Result: {'Success' if success else 'Failed'}")
    
    elif args.report:
        report = engine.generate_tier_report()
        print(report)
    
    elif args.batch:
        entities = [e.strip() for e in args.batch.split(",")]
        print(f"📦 Batch enriching {len(entities)} entities...")
        results = engine.batch_enrich_entities(entities)
        print(f"  Total: {results['total']}")
        print(f"  By Tier: {results['by_tier']}")
    
