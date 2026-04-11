#!/usr/bin/env python3
"""
GBrain 架构进化实现计划
将 GBrain 的关键概念整合到 Erbing
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "memory" / "database"))
from hybrid_memory import get_memory


class ErbingGBrainEvolution:
    """Erbing + GBrain 架构融合"""

    def __init__(self):
        self.memory = get_memory()

    # ==================== Phase 1: Compiled Truth + Timeline ====================

    def create_compiled_truth_page(self, entity_type: str, entity_name: str) -> Dict:
        """创建编译真相页面（GBrain 模式）"""

        page_structure = {
            "type": entity_type,  # person, company, concept
            "title": entity_name,
            "compiled_truth": {
                "executive_summary": "",  # 一段话概述
                "state": "",               # 当前状态
                "what_they_believe": "",   # 世界观
                "what_they_building": "",  # 正在构建
                "assessment": "",          # 评估
                "trajectory": "",          # 轨迹
                "relationship": "",        # 关系
                "contact": ""              # 联系方式
            },
            "timeline": [],  # 追加式日志
            "importance": 7,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return page_structure

    def add_timeline_entry(
        self,
        page: Dict,
        date: str,
        event: str,
        source: str,
        links: List[str] = None
    ) -> Dict:
        """添加 Timeline 条目（永不重写）"""

        timeline_entry = {
            "date": date,
            "event": event,
            "source": source,
            "links": links or []
        }

        page["timeline"].insert(0, timeline_entry)  # 最新的在前
        page["updated_at"] = datetime.now().isoformat()

        return page

    def update_compiled_truth(
        self,
        page: Dict,
        section: str,
        new_information: str,
        source: str
    ) -> Dict:
        """更新 Compiled Truth（当新证据改变图景时）"""

        # 追加到 Timeline
        self.add_timeline_entry(
            page,
            date=datetime.now().strftime("%Y-%m-%d"),
            event=f"Updated {section}: {new_information}",
            source=source
        )

        # 重写 Compiled Truth
        page["compiled_truth"][section] = new_information
        page["updated_at"] = datetime.now().isoformat()

        return page

    # ==================== Phase 1: Originals Folder ====================

    def capture_original_thinking(
        self,
        user_message: str,
        context: str = ""
    ) -> Dict:
        """捕获用户的原创想法（最高价值信号）"""

        # 提取原创想法
        original_idea = self._extract_original_idea(user_message)

        if not original_idea:
            return None

        # 保留原始措辞！这是关键
        slug = self._create_slug(original_idea)

        original_page = {
            "type": "original",
            "title": original_idea[:100],  # 原始措辞作为标题
            "content": user_message,       # 完整原始内容
            "slug": slug,
            "captured_at": datetime.now().isoformat(),
            "context": context,
            "cross_links": self._find_related_originals(original_idea),
            "importance": 9  # 原创想法最高优先级
        }

        # 保存到数据库
        self._save_to_memory(original_page)

        return original_page

    def _extract_original_idea(self, message: str) -> Optional[str]:
        """提取原创想法"""

        # 指示原创想法的模式
        original_patterns = [
            "我觉得",
            "我的看法是",
            "我认为",
            "这让我想到",
            "我发现",
            "我意识到",
            "我的理论是",
            "我发现一个模式",
        ]

        for pattern in original_patterns:
            if pattern in message:
                return message

        return None

    def _create_slug(self, text: str) -> str:
        """创建 slug（使用用户自己的语言）"""

        # 提取关键词
        import re

        # 移除标点
        text = re.sub(r'[^\w\s-]', '', text)

        # 取前5个词
        words = text.split()[:5]

        # 连接成 slug
        slug = '-'.join(words).lower()

        return slug

    def _find_related_originals(self, idea: str) -> List[str]:
        """找到相关的原创想法"""

        # 搜索数据库中的相关 originals
        results = self.memory.search(idea, limit=5)

        related = []
        for r in results:
            if r.get("type") == "original":
                related.append(r["title"])

        return related

    # ==================== Phase 1: Entity Detection ====================

    def detect_entities_on_message(self, message: str) -> List[Dict]:
        """在每条消息上检测实体"""

        entities = []

        # 检测人员名称
        people = self._detect_people(message)
        entities.extend([{"type": "person", "name": p} for p in people])

        # 检测公司名称
        companies = self._detect_companies(message)
        entities.extend([{"type": "company", "name": c} for c in companies])

        # 检测概念
        concepts = self._detect_concepts(message)
        entities.extend([{"type": "concept", "name": c} for c in concepts])

        # 对每个实体检查大脑状态
        for entity in entities:
            entity["exists"] = self._check_entity_exists(entity)
            entity["tier"] = self._classify_entity_tier(entity, message)

        return entities

    def _detect_people(self, message: str) -> List[str]:
        """检测人员名称（简化版）"""

        # 实际实现应该使用 NER 或 LLM
        # 这里用简化规则
        people = []

        # 查找大写开头的词（简化）
        import re
        pattern = r'\b[A-Z][a-z]+\b'
        matches = re.findall(pattern, message)

        # 过滤常见词
        common_words = {"The", "This", "That", "If", "When", "What"}
        people = [m for m in matches if m not in common_words]

        return people

    def _detect_companies(self, message: str) -> List[str]:
        """检测公司名称"""

        companies = []

        # 常见公司后缀
        suffixes = ["Inc", "Corp", "LLC", "Ltd", "公司"]

        for suffix in suffixes:
            if suffix in message:
                # 提取公司名称（简化）
                import re
                pattern = rf'\b(\w+\s+{suffix})\b'
                matches = re.findall(pattern, message)
                companies.extend(matches)

        return companies

    def _detect_concepts(self, message: str) -> List[str]:
        """检测概念"""

        concepts = []

        # 概念指示词
        indicators = ["叫做", "被称为", "是", "定义"]

        for indicator in indicators:
            if indicator in message:
                # 提取概念（简化）
                parts = message.split(indicator)
                if len(parts) > 1:
                    concept = parts[0].strip().split()[-1]
                    concepts.append(concept)

        return concepts

    def _check_entity_exists(self, entity: Dict) -> bool:
        """检查实体是否存在于记忆中"""

        results = self.memory.search(entity["name"], limit=1)
        return len(results) > 0

    def _classify_entity_tier(self, entity: Dict, message: str) -> int:
        """分类实体重要性层级"""

        # Tier 1: 关键人物/公司
        # 检查是否在关键列表中或频繁提及

        # Tier 2: 值得注意
        # 偶尔提及

        # Tier 3: 次要提及
        # 仅提及一次

        # 简化：默认 Tier 2
        return 2

    # ==================== Phase 2: Brain-First Lookup ====================

    def research_entity_brain_first(self, entity_name: str) -> Dict:
        """大脑优先的实体研究"""

        results = {
            "brain_results": None,
            "external_results": None,
            "final": None
        }

        # 1. 关键词搜索（快）
        keyword_results = self.memory.search(entity_name, limit=5)

        # 2. 混合搜索（需要嵌入）
        query = f"what do we know about {entity_name}"
        hybrid_results = self.memory.search(query, limit=5)

        # 3. 合并大脑结果
        if keyword_results or hybrid_results:
            results["brain_results"] = {
                "keyword": keyword_results,
                "hybrid": hybrid_results
            }

        # 4. 检查是否需要外部API
        needs_external = self._needs_external_enrichment(results["brain_results"])

        if needs_external:
            # 5. 调用外部API（仅作为后备）
            results["external_results"] = self._call_external_api(entity_name)

        # 6. 合并结果
        results["final"] = self._merge_results(results)

        return results

    def _needs_external_enrichment(self, brain_results) -> bool:
        """检查是否需要外部丰富"""

        if not brain_results:
            return True

        # 检查是否页面薄弱
        if len(brain_results.get("keyword", [])) == 0:
            return True

        return False

    def _call_external_api(self, entity_name: str) -> Dict:
        """调用外部API（占位符）"""

        # 实际实现应该调用：
        # - Brave Search
        # - X/Twitter API
        # - LinkedIn API
        # - etc.

        return {"note": "External API call placeholder"}

    def _merge_results(self, results: Dict) -> Dict:
        """合并大脑和外部结果"""

        merged = {}

        if results["brain_results"]:
            merged["from_brain"] = results["brain_results"]

        if results["external_results"]:
            merged["from_external"] = results["external_results"]

        return merged

    # ==================== Phase 2: Dream Cycle ====================

    def run_dream_cycle(self):
        """梦境循环 - 夜间自动维护"""

        print("[DREAM] Starting dream cycle...")

        # 1. 获取今天的所有对话
        today_conversations = self._get_today_conversations()

        # 2. 检测缺失的实体
        missing_entities = []
        for conv in today_conversations:
            entities = self.detect_entities_on_message(conv)
            for entity in entities:
                if not entity["exists"]:
                    missing_entities.append(entity)

        # 3. 后台丰富缺失实体
        for entity in missing_entities:
            self._enrich_entity_background(entity)

        # 4. 修复损坏的引用
        self._fix_broken_citations()

        # 5. 巩固记忆
        self._consolidate_memories()

        # 6. 生成梦境报告
        dream_report = self._generate_dream_report(missing_entities)

        print(f"[DREAM] Cycle complete. Enriched {len(missing_entities)} entities.")

        return dream_report

    def _get_today_conversations(self) -> List[str]:
        """获取今天的对话"""

        # 从数据库查询今天的消息
        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        cursor.execute("""
            SELECT content FROM memories
            WHERE date(created_at) = date('now')
        """)

        return [row[0] for row in cursor.fetchall()]

    def _enrich_entity_background(self, entity: Dict):
        """后台丰富实体"""

        print(f"[ENRICH] Enriching {entity['type']}: {entity['name']}")

        # 根据Tier决定丰富程度
        if entity["tier"] == 1:
            # 完整丰富
            self._full_enrichment(entity)
        elif entity["tier"] == 2:
            # 标准丰富
            self._standard_enrichment(entity)
        else:
            # 最小丰富
            self._minimal_enrichment(entity)

    def _full_enrichment(self, entity: Dict):
        """完整丰富（10-15 API调用）"""
        pass  # 实现完整丰富流程

    def _standard_enrichment(self, entity: Dict):
        """标准丰富（3-5 API调用）"""
        pass

    def _minimal_enrichment(self, entity: Dict):
        """最小丰富（1-2 API调用）"""
        pass

    def _fix_broken_citations(self):
        """修复损坏的引用"""
        print("[FIX] Fixing broken citations...")

    def _consolidate_memories(self):
        """巩固记忆"""
        print("[CONSOLIDATE] Consolidating memories...")

    def _generate_dream_report(self, enriched_entities: List[Dict]) -> Dict:
        """生成梦境报告"""

        report = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "enriched_entities": len(enriched_entities),
            "entities": [e["name"] for e in enriched_entities],
            "status": "complete"
        }

        # 保存报告
        self._save_dream_report(report)

        return report

    def _save_dream_report(self, report: Dict):
        """保存梦境报告到数据库"""

        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            "dream_report",
            f"Dream Cycle {report['date']}",
            json.dumps(report, ensure_ascii=False),
            "dream",
            "dream, cycle, maintenance",
            7
        ))

        conn.commit()

    def _save_to_memory(self, page: Dict):
        """保存页面到数据库"""

        conn = self.memory.sqlite_conn
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO memories (type, title, content, category, tags, importance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            page.get("type", "memory"),
            page.get("title", ""),
            json.dumps(page, ensure_ascii=False),
            page.get("category", ""),
            json.dumps(page.get("tags", []), ensure_ascii=False),
            page.get("importance", 5)
        ))

        conn.commit()


# 示例使用
def example_usage():
    """示例：使用 GBrain 进化的 Erbing"""

    evolution = ErbingGBrainEvolution()

    print("="*60)
    print("ERBING + GBRAIN EVOLUTION")
    print("="*60)

    # 1. 捕获原创想法
    print("\n[1] Capturing original thinking...")
    user_message = "我觉得知识的价值在于它能够自动复合增长，而不是简单的累积。"
    original = evolution.capture_original_thinking(user_message)
    if original:
        print(f"   Captured: {original['title'][:50]}...")

    # 2. 实体检测
    print("\n[2] Detecting entities...")
    message = "我昨天和 Pedro 讨论了关于 AI Agent 架构的设计。"
    entities = evolution.detect_entities_on_message(message)
    print(f"   Detected: {len(entities)} entities")
    for e in entities:
        print(f"   - {e['type']}: {e['name']} (Tier {e['tier']})")

    # 3. 大脑优先研究
    print("\n[3] Brain-first research...")
    results = evolution.research_entity_brain_first("Erbing")
    print(f"   Brain results: {len(results['brain_results'].get('keyword', []))} keyword matches")

    # 4. 梦境循环
    print("\n[4] Running dream cycle...")
    report = evolution.run_dream_cycle()
    print(f"   Dream report: enriched {report['enriched_entities']} entities")


if __name__ == "__main__":
    example_usage()
