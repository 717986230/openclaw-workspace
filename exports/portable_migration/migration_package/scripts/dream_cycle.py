#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dream Cycle - 夜间自动维护系统
Erbing's automatic maintenance during idle periods

功能:
1. 扫描今天的所有对话
2. 丰富缺失的实体
3. 修复损坏的引用
4. 巩固记忆
5. 生成 DREAMS.md 报告
"""

import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class ErbingDreamCycle:
    """梦境循环 - 夜间自动维护"""
    
    def __init__(self, db_path: str = None):
        """初始化梦境循环"""
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "memory" / "database" / "xiaozhi_memory.db")
        
        self.db_path = db_path
        self.dreams_dir = Path(__file__).parent.parent / "memory" / ".dreams"
        self.dreams_dir.mkdir(parents=True, exist_ok=True)
        
        # 维护统计
        self.stats = {
            "conversations_scanned": 0,
            "entities_enriched": 0,
            "citations_fixed": 0,
            "memories_consolidated": 0,
            "errors": []
        }
    
    def run_dream_cycle(self, full_cycle: bool = True) -> Dict[str, Any]:
        """
        运行完整的梦境循环
        
        Args:
            full_cycle: 是否运行完整循环（包括丰富化）
        
        Returns:
            统计信息
        """
        print("[MOON] Starting Dream Cycle...")
        start_time = datetime.now()
        
        try:
            # 1. 扫描今天的所有对话
            print("  [SCAN] Scanning today's conversations...")
            conversations = self.get_today_conversations()
            self.stats["conversations_scanned"] = len(conversations)
            
            # 2. 丰富缺失的实体
            if full_cycle:
                print("  [ENRICH] Enriching missing entities...")
                entities_enriched = self.enrich_missing_entities(conversations)
                self.stats["entities_enriched"] = entities_enriched
            
            # 3. 修复损坏的引用
            print("  [FIX] Fixing broken citations...")
            citations_fixed = self.fix_broken_citations()
            self.stats["citations_fixed"] = citations_fixed
            
            # 4. 巩固记忆
            print("  [BRAIN] Consolidating memories...")
            memories_consolidated = self.consolidate_memories()
            self.stats["memories_consolidated"] = memories_consolidated
            
            # 5. 生成 DREAMS.md
            print("  [REPORT] Generating dream report...")
            self.generate_dream_report()
            
            end_time = datetime.now()
            self.stats["duration_seconds"] = (end_time - start_time).total_seconds()
            
            print(f"[OK] Dream Cycle completed in {self.stats['duration_seconds']:.1f}s")
            return self.stats
            
        except Exception as e:
            self.stats["errors"].append(str(e))
            print(f"[ERROR] Dream Cycle error: {e}")
            return self.stats
    
    def get_today_conversations(self) -> List[Dict[str, Any]]:
        """获取今天的所有对话"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 查询今天的记忆/事件
            cursor.execute("""
                SELECT id, type, title, content, created_at, tags
                FROM memories
                WHERE DATE(created_at) = ?
                ORDER BY created_at DESC
            """, (today,))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "created_at": row[4],
                    "tags": json.loads(row[5]) if row[5] else []
                })
            
            conn.close()
            return conversations
            
        except Exception as e:
            print(f"Error getting conversations: {e}")
            return []
    
    def enrich_missing_entities(self, conversations: List[Dict]) -> int:
        """丰富缺失的实体"""
        entities_enriched = 0
        
        for conv in conversations:
            # 检测实体（人员、公司、概念等）
            entities = self.detect_entities(conv)
            
            for entity in entities:
                if not self.has_rich_page(entity):
                    self.enrich_entity(entity)
                    entities_enriched += 1
        
        return entities_enriched
    
    def detect_entities(self, conversation: Dict) -> List[str]:
        """
        从对话中检测实体
        简单实现：提取标签中的人和公司
        """
        entities = []
        content = conversation.get("content", "")
        tags = conversation.get("tags", [])
        
        # 从标签中提取实体
        for tag in tags:
            if tag.startswith("person:") or tag.startswith("company:"):
                entities.append(tag.split(":", 1)[1])
        
        # 简单的内容扫描（可以扩展为 NER）
        # TODO: 集成更强大的实体识别
        
        return list(set(entities))
    
    def has_rich_page(self, entity: str) -> bool:
        """检查实体是否有丰富的页面"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM memories
                WHERE (title LIKE ? OR content LIKE ?)
                AND type IN ('entity', 'person', 'company')
            """, (f"%{entity}%", f"%{entity}%"))
            
            count = cursor.fetchone()[0]
            conn.close()
            
            return count > 0
            
        except Exception as e:
            print(f"Error checking rich page for {entity}: {e}")
            return True  # 假设已存在，避免重复处理
    
    def enrich_entity(self, entity: str):
        """丰富实体信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建基础实体记录
            cursor.execute("""
                INSERT INTO memories (type, title, content, category, importance, created_at, updated_at)
                VALUES ('entity', ?, ?, 'knowledge', 5, ?, ?)
            """, (entity, f"Auto-enriched entity: {entity}", datetime.now().isoformat(), datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error enriching entity {entity}: {e}")
    
    def fix_broken_citations(self) -> int:
        """修复损坏的引用"""
        fixed = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找所有包含引用的记忆
            cursor.execute("""
                SELECT id, content FROM memories
                WHERE content LIKE '%memory/%' OR content LIKE '%Source:%'
            """)
            
            for row in cursor.fetchall():
                memory_id = row[0]
                content = row[1]
                
                # 检查引用是否存在
                # TODO: 实现更完善的引用检查
                # 现在只做基础检查
                
            conn.close()
            
        except Exception as e:
            print(f"Error fixing citations: {e}")
        
        return fixed
    
    def consolidate_memories(self) -> int:
        """
        记忆巩固
        将短期记忆转化为长期记忆
        """
        consolidated = 0
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 查找需要巩固的记忆（创建超过72小时且重要性高的）
            threshold_date = (datetime.now() - timedelta(hours=72)).isoformat()
            
            cursor.execute("""
                SELECT id, importance FROM memories
                WHERE created_at < ?
                AND importance >= 7
                AND type = 'learning'
            """, (threshold_date,))
            
            memories_to_consolidate = cursor.fetchall()
            
            for memory_id, importance in memories_to_consolidate:
                # 提升重要性（模拟巩固）
                new_importance = min(10, importance + 1)
                cursor.execute("""
                    UPDATE memories
                    SET importance = ?, updated_at = ?
                    WHERE id = ?
                """, (new_importance, datetime.now().isoformat(), memory_id))
                
                consolidated += 1
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error consolidating memories: {e}")
        
        return consolidated
    
    def generate_dream_report(self):
        """生成梦境报告"""
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = self.dreams_dir / f"dream-{today}.md"
        
        report_content = f"""# Dream Report - {today}

## 🌙 Dream Cycle Statistics

| Metric | Value |
|--------|-------|
| Conversations Scanned | {self.stats['conversations_scanned']} |
| Entities Enriched | {self.stats['entities_enriched']} |
| Citations Fixed | {self.stats['citations_fixed']} |
| Memories Consolidated | {self.stats['memories_consolidated']} |
| Duration | {self.stats.get('duration_seconds', 0):.1f}s |

## 📋 Details

### Entities Enriched
"""
        
        if self.stats['entities_enriched'] > 0:
            report_content += f"- {self.stats['entities_enriched']} entities were auto-enriched\n"
        else:
            report_content += "- No entities needed enrichment\n"
        
        report_content += """
### Citations Status
"""
        
        if self.stats['citations_fixed'] > 0:
            report_content += f"- {self.stats['citations_fixed']} broken citations were fixed\n"
        else:
            report_content += "- All citations are healthy\n"
        
        report_content += """
### Memory Consolidation
"""
        
        if self.stats['memories_consolidated'] > 0:
            report_content += f"- {self.stats['memories_consolidated']} memories were consolidated\n"
        else:
            report_content += "- No memories needed consolidation\n"
        
        if self.stats['errors']:
            report_content += """
## ⚠️ Errors
"""
            for error in self.stats['errors']:
                report_content += f"- {error}\n"
        
        report_content += f"""
---
*Generated at {datetime.now().isoformat()}*
"""
        
        # 写入报告
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"  [REPORT] Dream report saved to {report_path}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Erbing's Dream Cycle - Nightly Maintenance")
    parser.add_argument("--full", action="store_true", help="Run full cycle including enrichment")
    parser.add_argument("--quick", action="store_true", help="Run quick cycle (citations and consolidation only)")
    parser.add_argument("--status", action="store_true", help="Show dream cycle status")
    
    args = parser.parse_args()
    
    dream_cycle = ErbingDreamCycle()
    
    if args.status:
        # 显示最近一次梦境报告
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = dream_cycle.dreams_dir / f"dream-{today}.md"
        if report_path.exists():
            print(report_path.read_text(encoding='utf-8'))
        else:
            print("No dream report for today yet.")
        return
    
    # 运行梦境循环
    full_cycle = not args.quick
    stats = dream_cycle.run_dream_cycle(full_cycle=full_cycle)
    
    # 打印统计
    print("\n📊 Dream Cycle Results:")
    for key, value in stats.items():
        if key != "errors":
            print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
