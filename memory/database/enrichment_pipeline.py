#!/usr/bin/env python3
"""
Erbing Enrichment Pipeline - 7步丰富化流程

完整的7步协议：
1. 识别实体
2. 检查大脑状态
3. 从来源提取信号
4. 数据源查询
5. 保存原始数据
6. 写入大脑
7. 交叉引用
"""

import sqlite3
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    """7步丰富化流程"""

    def __init__(self, db_path: str = None):
        """初始化7步丰富化流程
        
        Args:
            db_path: SQLite数据库路径
        """
        if db_path is None:
            db_path = Path(__file__).parent / "xiaozhi_memory.db"
        
        self.db_path = Path(db_path)
        
        logger.info(f"🔄 Enrichment Pipeline initialized")

    def run(self, entity: str, source_signals: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """运行完整的7步丰富化流程
        
        Args:
            entity: 实体名称
            source_signals: 来源信号（可选）
            
        Returns:
            丰富化结果
        """
        logger.info(f"🔄 Starting 7-step enrichment pipeline for: {entity}")
        
        result = {
            "entity": entity,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "steps": []
        }
        
        try:
            # Step 1: 识别实体
            logger.info("📊 Step 1: Identifying entity...")
            entity_info = self._identify_entity(entity, source_signals)
            result["steps"].append({"step": 1, "name": "identify_entity", "status": "completed", "data": entity_info})

            # Step 2: 检查大脑状态
            logger.info("📊 Step 2: Checking brain state...")
            page = self._check_brain_state(entity)
            result["steps"].append({"step": 2, "name": "check_brain_state", "status": "completed", "data": page})

            # Step 3: 从来源提取信号
            logger.info("📊 Step 3: Extracting signals from sources...")
            signals = self._extract_signals(entity_info)
            result["steps"].append({"step": 3, "name": "extract_signals", "status": "completed", "data": signals})

            # Step 4: 数据源查询
            logger.info("📊 Step 4: Querying data sources...")
            data = self._query_data_sources(entity, signals)
            result["steps"].append({"step": 4, "name": "query_data_sources", "status": "completed", "data": data})

            # Step 5: 保存原始数据
            logger.info("📊 Step 5: Saving raw data...")
            raw_data_path = self._save_raw_data(entity, data)
            result["steps"].append({"step": 5, "name": "save_raw_data", "status": "completed", "data": {"path": str(raw_data_path)}})

            # Step 6: 写入大脑
            logger.info("📊 Step 6: Writing to brain...")
            self._write_to_brain(entity, data, page)
            result["steps"].append({"step": 6, "name": "write_to_brain", "status": "completed"})

            # Step 7: 交叉引用
            logger.info("📊 Step 7: Cross-referencing...")
            self._cross_reference(entity, data)
            result["steps"].append({"step": 7, "name": "cross_reference", "status": "completed"})

            result["status"] = "completed"
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"✅ 7-step enrichment pipeline completed for: {entity}")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.error(f"❌ Enrichment pipeline failed: {e}")
            raise
            
        return result

    def _identify_entity(self, entity: str, source_signals: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Step 1: 识别实体
        
        从输入信号中提取人员名称、公司名称、它们的关联信息
        
        Args:
            entity: 实体名称
            source_signals: 来源信号
            
        Returns:
            实体信息
        """
        logger.debug(f"🔍 Identifying entity: {entity}")
        
        # 这里使用简单的规则来识别实体
        # TODO: 集成NLP模型进行更精确的识别
        
        entity_info = {
            "name": entity,
            "type": self._infer_entity_type(entity),
            "confidence": 0.8,
            "source_signals": source_signals or []
        }
        
        logger.debug(f"📄 Entity info: {entity_info}")
        return entity_info

    def _infer_entity_type(self, entity: str) -> str:
        """推导实体类型
        
        Args:
            entity: 实体名称
            
        Returns:
            实体类型
        """
        # 简单的启发式规则
        if any(keyword in entity.lower() for keyword in ["公司", "corp", "inc", "ltd"]):
            return "company"
        elif any(keyword in entity.lower() for keyword in ["项目", "project", "system"]):
            return "project"
        elif any(keyword in entity.lower() for keyword in ["技术", "tech", "framework"]):
            return "technology"
        else:
            return "person"  # 默认为人

    def _check_brain_state(self, entity: str) -> Optional[Dict[str, Any]]:
        """Step 2: 检查大脑状态
        
        页面存在吗？如果存在，读取它 → UPDATE 路径。如果不存在 → CREATE 路径
        
        Args:
            entity: 实体名称
            
        Returns:
            页面信息（如果存在）
        """
        logger.debug(f"📄 Checking brain state for: {entity}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, type, title, content, category, tags, importance, created_at, updated_at
                FROM memories
                WHERE title = ?
                LIMIT 1
            """, (entity,))
            
            row = cursor.fetchone()
            if row:
                page = {
                    "id": row[0],
                    "type": row[1],
                    "title": row[2],
                    "content": row[3],
                    "category": row[4],
                    "tags": json.loads(row[5]) if row[5] else [],
                    "importance": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "path": "UPDATE"
                }
                logger.debug(f"✅ Page found: {page['title']} - Path: {page['path']}")
                return page
            else:
                logger.debug("✅ Page not found - Path: CREATE")
                return None
                
        finally:
            conn.close()


def main():
    """主函数 - 测试7步丰富化流程"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Erbing Enrichment Pipeline - 7步丰富化流程")
    parser.add_argument("entity", help="实体名称")
    parser.add_argument("--db-path", help="数据库路径", default=None)
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    pipeline = EnrichmentPipeline(db_path=args.db_path)
    result = pipeline.run(args.entity)
    
    print("\n" + "="*60)
    print("Enrichment Pipeline Result")
    print("="*60)
    print(f"Entity: {result['entity']}")
    print(f"Status: {result['status']}")
    print(f"Started: {result['started_at']}")
    print(f"Completed: {result['completed_at']}")
    print("\nSteps:")
    for step in result['steps']:
        print(f"  Step {step['step']}: {step['name']} - {step['status']}")
    print("="*60)


if __name__ == "__main__":
    main()
            conn.close()

    def _extract_signals(self, entity_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Step 3: 从来源提取信号
        
        不仅提取事实 - 提取质感：
        - 他们表达了什么观点？→ What They Believe
        - 他们在构建或发布什么？→ What They're Building
        - 他们表达了情感吗？→ What Makes Them Tick
        - 他们与谁互动？→ Network / Relationship
        - 这是反复出现的话题吗？→ Hobby Horses
        - 他们承诺了什么？→ Open Threads
        - 他们的能量如何？→ Trajectory
        
        Args:
            entity_info: 实体信息
            
        Returns:
            信号列表
        """
        logger.debug(f"📡 Extracting signals for: {entity_info['name']}")
        
        signals = []
        
        # 从来源信号中提取
        for signal in entity_info.get("source_signals", []):
            extracted = {
                "what_they_believe": self._extract_beliefs(signal),
                "what_they_building": self._extract_building(signal),
                "what_makes_them_tick": self._extract_emotions(signal),
                "network_relationship