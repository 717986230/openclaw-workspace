#!/usr/bin/env python3
"""
Erbing 核心 - GBrain 集成
将 GBrain 核心功能整合到 Erbing 日常工作流程
"""
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingGBrainCore:
    """
    Erbing + GBrain 核心集成

    在每次对话中自动：
    1. 检测并捕获原创想法
    2. 检测实体（人员/公司/概念）
    3. 使用大脑优先查找
    4. 维护 Compiled Truth + Timeline
    """

    def __init__(self):
        self.memory = get_memory()
        self.conn = self.memory.sqlite_conn

        # 原创想法指示词
        self.original_indicators = [
            "我觉得", "我的看法是", "我认为", "这让我想到",
            "我发现", "我意识到", "我的理论是", "我发现一个模式",
            "我的观点", "我观察到", "我的洞察", "我注意到",
            "我的经验是", "我的理解是", "我的判断是"
        ]

        print("[GBRAIN] Core integration initialized")

    def process_message(self, user_message: str, context: str = "") -> Dict:
        """
        处理消息 - GBrain 模式

        这是主入口，自动执行所有 GBrain 流程
        """

        result = {
            "original_captured": False,
            "original_page": None,
            "entities_detected": [],
            "brain_context": None,
            "message": user_message
        }

        # 1. 检测并捕获原创想法（最高优先级）
        original = self._detect_and_capture_original(user_message)
        if original:
            result["original_captured"] = True
            result["original_page"] = original
            self._log(f"[ORIGINAL] Captured: {original['title'][:50]}")

        # 2. 实体检测
        entities = self._detect_entities(user_message)
        result["entities_detected"] = entities

        if entities:
            self._log(f"[ENTITIES] Detected {len(entities)} entities")

        # 3. 对每个实体：大脑优先查找
        for entity in entities:
            brain_result = self._brain_first_lookup(entity)
            if not brain_result["exists"]:
                # 自动丰富缺失实体
                self._auto_enrich_entity(entity)
                self._log(f"[ENRICH] Auto-enriched: {entity['name']}")

        # 4. 加载上下文（用于响应）
        result["brain_context"] = self._load_brain_context(entities)

        return result

    def _detect_and_capture_original(self, message: str) -> Optional[Dict]:
        """检测并捕获原创想法"""

        # 检查是否包含原创想法指示词
        for indicator in self.original_indicators:
            if indicator in message:
                # 找到原创想法！
                # 关键：保留原始措辞
                original_idea = message

                # 创建 slug
                slug = self._create_slug(original_idea)

                # 查找相关原创想法
                related = self._find_related_originals(original_idea)

                # 创建原创页面
                original_page = {
                    "type": "original",
                    "title": original_idea[:100],
                    "content": message,  # 完整原始内容
                    "slug": slug,
                    "cross_links": related,
                    "importance": 9,  # 最高优先级
                    "created_at": datetime.now().isoformat()
                }

                # 保存到数据库
                self._save_to_memory(original_page)

                return original_page

        return None

    def _detect_entities(self, message: str) -> List[Dict]:
        """检测实体"""

        entities = []

        # 检测人员（简化版）
        import re

        # 中文姓名：2-3个汉字
        chinese_names = re.findall(r'[\u4e00-\u9fff]{2,3}', message)

        # 英文名：大写开头
        english_names = re.findall(r'\b[A-Z][a-z]+\b', message)
        english_names = [n for n in english_names if n not in
                        ["The", "This", "That", "If", "When", "What", "Agent", "AI"]]

        # 合并人员
        people = list(set(chinese_names + english_names))
        entities.extend([{"type": "person", "name": p, "tier": 2} for p in people[:3]])

        # 检测公司（简化）
        company_keywords = ["公司", "Inc", "Corp", "LLC", "Ltd"]
        for keyword in company_keywords:
            if keyword in message:
                # 提取公司名
                parts = message.split(keyword)
                if parts:
                    company_name = parts[0].split()[-1] + " " + keyword
                    entities.append({"type": "company", "name": company_name, "tier": 2})

        # 检测概念（简化）
        concept_indicators = ["叫做", "被称为", "概念", "理论", "模型", "架构"]
        for indicator in concept_indicators:
            if indicator in message:
                parts = message.split(indicator)
                if len(parts) > 1:
                    concept = parts[0].strip().split()[-1]
                    if len(concept) > 1:
                        entities.append({"type": "concept", "name": concept, "tier": 3})

        return entities[:5]  # 最多返回5个

    def _brain_first_lookup(self, entity: Dict) -> Dict:
        """大脑优先查找"""

        result = {
            "entity": entity,
            "exists": False,
            "brain_results": None,
            "needs_external": False
        }

        # 1. 关键词搜索（快）
        keyword_results = self.memory.search(entity["name"], limit=3)

        # 2. 混合搜索
        query = f"what do we know about {entity['name']}"
        hybrid_results = self.memory.search(query, limit=3)

        # 3. 判断是否需要外部API
        if keyword_results or hybrid_results:
            result["exists"] = True
            result["brain_results"] = {
                "keyword": keyword_results,
                "hybrid": hybrid_results
            }
        else:
            result["needs_external"] = True

        return result

    def _auto_enrich_entity(self, entity: Dict):
        """自动丰富实体（简化版）"""

        # 创建基础实体页面
        entity_page = {
            "type": entity["type"],
            "title": entity["name"],
            "compiled_truth": {
                "executive_summary": f"Detected from conversation",
                "state": "Unknown",
                "what_they_believe": "",
                "what_they_building": "",
                "assessment": "",
                "trajectory": "",
                "relationship": "",
                "contact": ""
            },
            "timeline": [{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "event": "Entity detected and created",
                "source": "Auto-enrichment"
            }],
            "importance": 7,
            "created_at": datetime.now().isoformat()
        }

        self._save_to_memory(entity_page)

    def _load_brain_context(self, entities: List[Dict]) -> str:
        """加载大脑上下文"""

        if not entities:
            return ""

        context_parts = []

        for entity in entities[:2]:  # 只加载前2个实体的上下文
            results = self.memory.search(entity["name"], limit=1)
            if results:
                r = results[0]
                context_parts.append(f"[{entity['type']}] {entity['name']}: {r.get('content', '')[:100]}...")

        return "\n".join(context_parts)

    def add_timeline_entry(
        self,
        entity_name: str,
        event: str,
        source: str,
        links: List[str] = None
    ) -> bool:
        """添加 Timeline 条目"""

        cursor = self.conn.cursor()

        # 查找实体页面
        cursor.execute(
            "SELECT * FROM memories WHERE title = ? ORDER BY created_at DESC LIMIT 1",
            (entity_name,)
        )

        row = cursor.fetchone()
        if not row:
            return False

        page = dict(row)

        # 解析内容
        try:
            content = json.loads(page["content"]) if page["content"].startswith("{") else {"timeline": []}
        except:
            content = {"timeline": []}

        # 添加 Timeline 条目
        timeline_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "event": event,
            "source": source,
            "links": links or []
        }

        if "timeline" not in content:
            content["timeline"] = []

        content["timeline"].insert(0, timeline_entry)

        # 更新数据库
        cursor.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (json.dumps(content, ensure_ascii=False), datetime.now().isoformat(), page["id"])
        )

        self.conn.commit()
        self._log(f"[TIMELINE] Added entry to {entity_name}")
        return True

    def update_compiled_truth(
        self,
        entity_name: str,
        section: str,
        new_info: str,
        source: str
    ) -> bool:
        """更新 Compiled Truth"""

        cursor = self.conn.cursor()

        # 查找实体页面
        cursor.execute(
            "SELECT * FROM memories WHERE title = ? ORDER BY created_at DESC LIMIT 1",
            (entity_name,)
        )

        row = cursor.fetchone()
        if not row:
            return False

        page = dict(row)

        # 解析内容
        try:
            content = json.loads(page["content"]) if page["content"].startswith("{") else {"compiled_truth": {}}
        except:
            content = {"compiled_truth": {}}

        # 添加 Timeline 条目（记录修改）
        timeline_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "event": f"Updated {section}: {new_info}",
            "source": source
        }

        if "timeline" not in content:
            content["timeline"] = []

        content["timeline"].insert(0, timeline_entry)

        # 更新 Compiled Truth
        if "compiled_truth" not in content:
            content["compiled_truth"] = {}

        content["compiled_truth"][section] = new_info

        # 更新数据库
        cursor.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (json.dumps(content, ensure_ascii=False), datetime.now().isoformat(), page["id"])
        )

        self.conn.commit()
        self._log(f"[COMPILED] Updated {section} for {entity_name}")
        return True

    def _create_slug(self, text: str) -> str:
        """创建 slug"""

        import re

        # 移除标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', text)

        # 中文：取前10个字符
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            slug = text[:10].replace(' ', '-')
        else:
            # 英文：取前5个词
            words = text.split()[:5]
            slug = '-'.join(words)

        return slug.lower()

    def _find_related_originals(self, idea: str) -> List[str]:
        """查找相关的原创想法"""

        results = self.memory.search(idea, limit=5)

        related = []
        for r in results:
            if r.get("type") == "original":
                related.append(r["title"])

        return related

    def _save_to_memory(self, page: Dict):
        """保存到数据库"""

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            page.get("type", "memory"),
            page.get("title", ""),
            json.dumps(page, ensure_ascii=False),
            page.get("type", ""),
            json.dumps(page.get("cross_links", [])),
            page.get("importance", 5)
        ))

        self.conn.commit()

    def _log(self, message: str):
        """日志输出"""

        print(f"[GBRAIN] {message}")


# ==================== 使用示例 ====================

def demo_usage():
    """演示如何在实际对话中使用"""

    print("="*60)
    print("ERBING + GBRAIN INTEGRATION DEMO")
    print("="*60)

    core = ErbingGBrainCore()

    # 模拟用户消息
    test_messages = [
        "我觉得知识的复合增长比简单累积更有价值。",
        "昨天我和 Pedro 讨论了 Agent 架构。",
        "我的理论是：Agent 应该在用户睡觉时自动维护大脑。"
    ]

    for msg in test_messages:
        print(f"\n[USER] {msg}")
        print("-" * 60)

        # 处理消息（自动执行所有 GBrain 流程）
        result = core.process_message(msg)

        # 显示结果
        if result["original_captured"]:
            print(f"[ORIGINAL] Captured!")

        if result["entities_detected"]:
            print(f"[ENTITIES] {len(result['entities_detected'])} detected")
            for e in result["entities_detected"]:
                print(f"  - {e['type']}: {e['name']}")

        if result["brain_context"]:
            print(f"[CONTEXT] Loaded from brain")

        print()

    print("="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == "__main__":
    demo_usage()
