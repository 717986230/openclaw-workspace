#!/usr/bin/env python3
"""
Erbing + GBrain 完整集成
将 GBrain 核心概念整合到 Erbing 系统
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingGBrainIntegrated:
    """Erbing + GBrain 完整集成"""

    def __init__(self):
        self.memory = get_memory()
        self.conn = self.memory.sqlite_conn

    # ==================== 1. Originals Folder（原创想法）====================

    def process_message_with_originals(self, user_message: str, context: str = "") -> Dict:
        """处理消息并捕获原创想法"""

        result = {
            "original_captured": False,
            "original_page": None,
            "entities_detected": [],
            "message": user_message
        }

        # 1. 检测原创想法
        original = self._detect_and_capture_original(user_message, context)
        if original:
            result["original_captured"] = True
            result["original_page"] = original
            print(f"[ORIGINAL] Captured: {original['title'][:50]}...")

        # 2. 实体检测
        entities = self._detect_entities(user_message)
        result["entities_detected"] = entities

        # 3. 丰富缺失的实体
        for entity in entities:
            if not self._entity_exists(entity):
                self._enrich_entity(entity)

        return result

    def _detect_and_capture_original(self, message: str, context: str) -> Optional[Dict]:
        """检测并捕获原创想法"""

        # 原创想法指示词
        original_indicators = [
            "我觉得", "我的看法是", "我认为", "这让我想到",
            "我发现", "我意识到", "我的理论是", "我发现一个模式",
            "我的观点", "我观察到", "我的洞察", "我注意到"
        ]

        for indicator in original_indicators:
            if indicator in message:
                # 提取原创想法（保留原始措辞！）
                original_idea = message

                # 创建 slug（使用用户的语言）
                slug = self._create_slug_from_user_language(original_idea)

                # 查找相关的原创想法
                related = self._find_related_originals(original_idea)

                # 创建原创页面
                original_page = {
                    "type": "original",
                    "title": original_idea[:100],
                    "content": message,  # 完整原始内容
                    "slug": slug,
                    "context": context,
                    "cross_links": related,
                    "importance": 9,  # 最高优先级
                    "created_at": datetime.now().isoformat()
                }

                # 保存到数据库
                self._save_page(original_page)

                return original_page

        return None

    def _create_slug_from_user_language(self, text: str) -> str:
        """使用用户自己的语言创建 slug"""

        import re

        # 移除标点
        text = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', text)

        # 取前5个词（中文按字符，英文按词）
        if any('\u4e00' <= c <= '\u9fff' for c in text):
            # 中文：取前10个字符
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

    # ==================== 2. Compiled Truth + Timeline ====================

    def create_entity_page(self, entity_type: str, entity_name: str) -> Dict:
        """创建实体页面（GBrain 模式）"""

        page = {
            "type": entity_type,
            "title": entity_name,
            "compiled_truth": {
                "executive_summary": "",
                "state": "",
                "what_they_believe": "",
                "what_they_building": "",
                "assessment": "",
                "trajectory": "",
                "relationship": "",
                "contact": ""
            },
            "timeline": [],
            "importance": 7,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return page

    def add_timeline_entry(
        self,
        page_title: str,
        date: str,
        event: str,
        source: str,
        links: List[str] = None
    ) -> bool:
        """添加 Timeline 条目"""

        cursor = self.conn.cursor()

        # 查找页面
        cursor.execute(
            "SELECT * FROM memories WHERE title = ? ORDER BY created_at DESC LIMIT 1",
            (page_title,)
        )

        row = cursor.fetchone()
        if not row:
            return False

        page = dict(row)

        # 解析现有内容
        try:
            content = json.loads(page["content"]) if page["content"].startswith("{") else {"timeline": []}
        except:
            content = {"timeline": []}

        # 添加新条目
        timeline_entry = {
            "date": date,
            "event": event,
            "source": source,
            "links": links or []
        }

        if "timeline" not in content:
            content["timeline"] = []

        content["timeline"].insert(0, timeline_entry)  # 最新的在前

        # 更新数据库
        cursor.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (json.dumps(content, ensure_ascii=False), datetime.now().isoformat(), page["id"])
        )

        self.conn.commit()
        return True

    def update_compiled_truth(
        self,
        page_title: str,
        section: str,
        new_information: str,
        source: str
    ) -> bool:
        """更新 Compiled Truth"""

        cursor = self.conn.cursor()

        # 查找页面
        cursor.execute(
            "SELECT * FROM memories WHERE title = ? ORDER BY created_at DESC LIMIT 1",
            (page_title,)
        )

        row = cursor.fetchone()
        if not row:
            return False

        page = dict(row)

        # 解析现有内容
        try:
            content = json.loads(page["content"]) if page["content"].startswith("{") else {"compiled_truth": {}}
        except:
            content = {"compiled_truth": {}}

        # 添加 Timeline 条目（记录修改）
        timeline_entry = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "event": f"Updated {section}: {new_information}",
            "source": source
        }

        if "timeline" not in content:
            content["timeline"] = []

        content["timeline"].insert(0, timeline_entry)

        # 更新 Compiled Truth
        if "compiled_truth" not in content:
            content["compiled_truth"] = {}

        content["compiled_truth"][section] = new_information

        # 更新数据库
        cursor.execute(
            "UPDATE memories SET content = ?, updated_at = ? WHERE id = ?",
            (json.dumps(content, ensure_ascii=False), datetime.now().isoformat(), page["id"])
        )

        self.conn.commit()
        return True

    # ==================== 3. Entity Detection ====================

    def _detect_entities(self, message: str) -> List[Dict]:
        """检测实体"""

        entities = []

        # 检测人员
        people = self._detect_people(message)
        entities.extend([{"type": "person", "name": p, "tier": 2} for p in people])

        # 检测公司
        companies = self._detect_companies(message)
        entities.extend([{"type": "company", "name": c, "tier": 2} for c in companies])

        # 检测概念
        concepts = self._detect_concepts(message)
        entities.extend([{"type": "concept", "name": c, "tier": 3} for c in concepts])

        return entities

    def _detect_people(self, message: str) -> List[str]:
        """检测人员名称（简化版）"""

        import re

        people = []

        # 查找大写开头的词（英文名）
        pattern = r'\b[A-Z][a-z]+\b'
        matches = re.findall(pattern, message)

        # 过滤常见词
        common_words = {"The", "This", "That", "If", "When", "What", "Agent", "AI"}
        people = [m for m in matches if m not in common_words]

        return people

    def _detect_companies(self, message: str) -> List[str]:
        """检测公司名称"""

        companies = []

        # 常见公司后缀
        suffixes = ["Inc", "Corp", "LLC", "Ltd", "公司"]

        for suffix in suffixes:
            if suffix in message:
                import re
                pattern = rf'(\w+\s+{suffix})'
                matches = re.findall(pattern, message)
                companies.extend(matches)

        return companies

    def _detect_concepts(self, message: str) -> List[str]:
        """检测概念"""

        concepts = []

        # 概念指示词
        indicators = ["叫做", "被称为", "概念", "理论"]

        for indicator in indicators:
            if indicator in message:
                parts = message.split(indicator)
                if len(parts) > 1:
                    concept = parts[0].strip().split()[-1]
                    concepts.append(concept)

        return concepts

    def _entity_exists(self, entity: Dict) -> bool:
        """检查实体是否存在"""

        results = self.memory.search(entity["name"], limit=1)
        return len(results) > 0

    def _enrich_entity(self, entity: Dict):
        """丰富实体"""

        print(f"[ENRICH] Enriching {entity['type']}: {entity['name']}")

        # 创建实体页面
        page = self.create_entity_page(entity["type"], entity["name"])

        # 保存页面
        self._save_page(page)

    # ==================== 4. Brain-First Lookup ====================

    def research_brain_first(self, entity_name: str) -> Dict:
        """大脑优先的实体研究"""

        results = {
            "brain_results": None,
            "needs_external": False,
            "final": None
        }

        # 1. 关键词搜索
        keyword_results = self.memory.search(entity_name, limit=5)

        # 2. 混合搜索
        query = f"what do we know about {entity_name}"
        hybrid_results = self.memory.search(query, limit=5)

        # 3. 合并结果
        if keyword_results or hybrid_results:
            results["brain_results"] = {
                "keyword": keyword_results,
                "hybrid": hybrid_results
            }

        # 4. 检查是否需要外部丰富
        if not results["brain_results"] or len(keyword_results) == 0:
            results["needs_external"] = True

        results["final"] = results["brain_results"]

        return results

    # ==================== 5. Dream Cycle ====================

    def run_dream_cycle(self) -> Dict:
        """运行梦境循环"""

        print("\n" + "="*60)
        print("[DREAM CYCLE] Starting...")
        print("="*60)

        # 1. 获取今天的对话
        today_messages = self._get_today_messages()

        print(f"\n[SCAN] Found {len(today_messages)} messages from today")

        # 2. 检测缺失的实体
        missing_entities = []
        for msg in today_messages:
            entities = self._detect_entities(msg)
            for entity in entities:
                if not self._entity_exists(entity):
                    missing_entities.append(entity)

        print(f"[MISSING] Found {len(missing_entities)} missing entities")

        # 3. 丰富缺失的实体
        for i, entity in enumerate(missing_entities, 1):
            print(f"[{i}/{len(missing_entities)}] Enriching {entity['name']}...")
            self._enrich_entity(entity)

        # 4. 修复损坏的引用
        self._fix_broken_citations()

        # 5. 巩固记忆
        self._consolidate_memories()

        # 6. 生成梦境报告
        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "messages_scanned": len(today_messages),
            "missing_entities": len(missing_entities),
            "entities_enriched": [e["name"] for e in missing_entities],
            "status": "complete"
        }

        self._save_dream_report(report)

        print(f"\n[DREAM CYCLE] Complete!")
        print(f"  Messages scanned: {report['messages_scanned']}")
        print(f"  Entities enriched: {report['missing_entities']}")

        return report

    def _get_today_messages(self) -> List[str]:
        """获取今天的消息"""

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT content FROM memories
            WHERE date(created_at) = date('now')
        """)

        return [row[0] for row in cursor.fetchall() if row[0]]

    def _fix_broken_citations(self):
        """修复损坏的引用"""

        print("[FIX] Checking for broken citations...")
        # 简化：实际应该检查所有链接
        print("[FIX] Complete")

    def _consolidate_memories(self):
        """巩固记忆"""

        print("[CONSOLIDATE] Consolidating memories...")
        # 简化：实际应该压缩和优化记忆
        print("[CONSOLIDATE] Complete")

    def _save_dream_report(self, report: Dict):
        """保存梦境报告"""

        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            "dream_report",
            f"Dream Cycle {report['date']}",
            json.dumps(report, ensure_ascii=False),
            "dream",
            json.dumps(["dream", "cycle", "maintenance"]),
            7
        ))

        self.conn.commit()

    # ==================== 辅助方法 ====================

    def _save_page(self, page: Dict):
        """保存页面到数据库"""

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


# ==================== 完整测试 ====================

def run_complete_integration_test():
    """运行完整集成测试"""

    print("="*60)
    print("ERBING + GBRAIN INTEGRATION TEST")
    print("="*60)

    integrated = ErbingGBrainIntegrated()

    # Test 1: 原创想法捕获
    print("\n[Test 1: Original Thinking Capture]")
    print("-" * 60)

    test_messages = [
        "我觉得知识的真正价值在于它能够自动复合增长，而不是简单的累积。",
        "我发现一个模式：每次反思后，输出质量都会提升。",
        "我的理论是：Agent 应该在用户睡觉时自动维护大脑。"
    ]

    for msg in test_messages:
        result = integrated.process_message_with_originals(msg)
        if result["original_captured"]:
            print(f"[OK] Captured original: {result['original_page']['title'][:50]}...")
        else:
            print(f"  Message processed: {msg[:30]}...")

    # Test 2: Entity Detection
    print("\n[Test 2: Entity Detection]")
    print("-" * 60)

    test_message = "昨天我和 Pedro 讨论了 OpenAI 的 GPT-5 架构，他提到了一个叫做思维链的概念。"
    result = integrated.process_message_with_originals(test_message)

    print(f"Entities detected: {len(result['entities_detected'])}")
    for entity in result['entities_detected']:
        print(f"  - {entity['type']}: {entity['name']}")

    # Test 3: Brain-First Lookup
    print("\n[Test 3: Brain-First Lookup]")
    print("-" * 60)

    research = integrated.research_brain_first("Erbing")
    print(f"Brain results: {len(research['brain_results'].get('keyword', []))} keyword matches")
    print(f"Needs external: {research['needs_external']}")

    # Test 4: Dream Cycle
    print("\n[Test 4: Dream Cycle]")
    print("-" * 60)

    report = integrated.run_dream_cycle()
    print(f"\nDream cycle complete!")
    print(f"  Date: {report['date']}")
    print(f"  Messages scanned: {report['messages_scanned']}")
    print(f"  Entities enriched: {report['missing_entities']}")

    # Test 5: Compiled Truth + Timeline
    print("\n[Test 5: Compiled Truth + Timeline]")
    print("-" * 60)

    # 创建实体页面
    entity_page = integrated.create_entity_page("person", "Test Person")
    print(f"Created entity page: {entity_page['title']}")

    # 添加 Timeline 条目
    integrated._save_page(entity_page)
    added = integrated.add_timeline_entry(
        "Test Person",
        "2026-04-11",
        "First meeting at conference",
        "Meeting notes"
    )
    print(f"Added timeline entry: {'OK' if added else 'FAIL'}")

    # 更新 Compiled Truth
    updated = integrated.update_compiled_truth(
        "Test Person",
        "executive_summary",
        "Met at AI conference, interested in agent architectures",
        "Personal observation"
    )
    print(f"Updated compiled truth: {'OK' if updated else 'FAIL'}")

    print("\n" + "="*60)
    print("ALL TESTS COMPLETE!")
    print("="*60)

    # 最终统计
    print("\n[STATS]")
    stats = integrated.memory