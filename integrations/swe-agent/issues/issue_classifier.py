"""
Issue Classifier - SWE-agent 集成
智能 Issue 分类器，使用 LLM 进行深度分析
"""

import json
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
import re

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed
from openclaw.memory import memory_store

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """分类结果"""
    category: str
    subcategory: str
    confidence: float
    reasoning: str
    keywords: List[str]


class IssueClassifier:
    """
    智能 Issue 分类器
    
    功能:
    - 多维度分类 (类型、严重程度、影响范围)
    - 关键词提取
    - 相似 Issue 检测
    - 分类历史学习
    """
    
    def __init__(self):
        """初始化分类器"""
        self.category_hierarchy = {
            "bug": {
                "crash": ["崩溃", "crash", "exception", "错误"],
                "performance": ["性能", "performance", "慢", "卡顿", "内存泄漏"],
                "security": ["安全", "security", "漏洞", "vulnerability", "XSS"],
                "compatibility": ["兼容性", "compatibility", "版本", "浏览器"],
                "regression": ["回归", "regression", "之前正常"]
            },
            "feature": {
                "new": ["新功能", "new feature", "新增", "添加"],
                "enhancement": ["增强", "enhancement", "改进", "优化"],
                "integration": ["集成", "integration", "API", "接口"]
            },
            "improvement": {
                "refactor": ["重构", "refactor", "代码质量"],
                "performance": ["性能优化", "优化"],
                "accessibility": ["无障碍", "accessibility", "可访问性"]
            },
            "documentation": {
                "missing": ["缺失文档", "文档不全", "缺少说明"],
                "error": ["文档错误", "文档有误", "example错误"],
                "improvement": ["改进文档", "文档建议"]
            },
            "question": {
                "howto": ["如何", "how to", "怎么"],
                "clarification": ["澄清", "clarification", "不确定"]
            }
        }
        
        # 加载历史分类数据
        self.classification_history = self._load_history()
        logger.info("IssueClassifier initialized")
    
    def _load_history(self) -> List[Dict]:
        """从 Memory 加载分类历史"""
        try:
            history = memory_store.query(
                filters={"type": "issue_classification"},
                limit=100
            )
            return [item["value"] for item in history]
        except Exception as e:
            logger.warning(f"Failed to load classification history: {e}")
            return []
    
    def classify(self, title: str, body: str) -> ClassificationResult:
        """
        分类 Issue
        
        Args:
            title: Issue 标题
            body: Issue 内容
            
        Returns:
            ClassificationResult 分类结果
        """
        # 1. 关键词匹配（快速路径）
        keyword_result = self._keyword_matching(title, body)
        
        # 2. LLM 深度分析
        llm_result = self._llm_classification(title, body)
        
        # 3. 综合结果
        final_result = self._combine_results(keyword_result, llm_result)
        
        # 4. 存储分类历史
        self._store_classification(title, body, final_result)
        
        return final_result
    
    def _keyword_matching(self, title: str, body: str) -> Dict:
        """关键词匹配分类"""
        text = f"{title} {body}".lower()
        
        matches = {}
        
        for category, subcategories in self.category_hierarchy.items():
            for subcategory, keywords in subcategories.items():
                match_count = 0
                matched_keywords = []
                
                for keyword in keywords:
                    if keyword.lower() in text:
                        match_count += 1
                        matched_keywords.append(keyword)
                
                if match_count > 0:
                    key = f"{category}/{subcategory}"
                    matches[key] = {
                        "count": match_count,
                        "keywords": matched_keywords,
                        "confidence": min(0.5 + match_count * 0.1, 0.9)
                    }
        
        # 找到最佳匹配
        if matches:
            best_match = max(matches.items(), key=lambda x: x[1]["confidence"])
            category, subcategory = best_match[0].split("/")
            return {
                "category": category,
                "subcategory": subcategory,
                "confidence": best_match[1]["confidence"],
                "keywords": best_match[1]["keywords"],
                "method": "keyword"
            }
        
        return {
            "category": "unknown",
            "subcategory": "unknown",
            "confidence": 0.0,
            "keywords": [],
            "method": "keyword"
        }
    
    def _llm_classification(self, title: str, body: str) -> Dict:
        """LLM 深度分类"""
        prompt = f"""分析以下 GitHub Issue 并进行详细分类:

标题: {title}

内容:
{body[:1000] if len(body) > 1000 else body}

请提供:
1. 主分类 (bug/feature/improvement/documentation/question)
2. 子分类 (如 bug/crash, feature/new)
3. 置信度 (0.0-1.0)
4. 分类理由 (一句话)
5. 关键词 (列表)

以 JSON 格式返回:
{{
  "category": "...",
  "subcategory": "...",
  "confidence": 0.95,
  "reasoning": "...",
  "keywords": ["..."]
}}"""
        
        try:
            response = ask_local_ai_routed(
                prompt=prompt,
                mode="claude_only"
            )
            
            # 解析 JSON
            result = self._parse_json_response(response)
            result["method"] = "llm"
            
            return result
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return {
                "category": "unknown",
                "subcategory": "unknown",
                "confidence": 0.0,
                "reasoning": f"LLM 分析失败: {str(e)}",
                "keywords": [],
                "method": "llm"
            }
    
    def _parse_json_response(self, response: str) -> Dict:
        """解析 JSON 响应"""
        try:
            # 提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
            return {}
    
    def _combine_results(self, keyword_result: Dict, llm_result: Dict) -> ClassificationResult:
        """综合关键词和 LLM 结果"""
        # LLM 结果优先级更高，但关键词结果作为补充
        if llm_result["confidence"] > 0.8:
            # 高置信度 LLM 结果
            return ClassificationResult(
                category=llm_result["category"],
                subcategory=llm_result["subcategory"],
                confidence=llm_result["confidence"],
                reasoning=llm_result.get("reasoning", ""),
                keywords=list(set(llm_result.get("keywords", []) + keyword_result.get("keywords", [])))
            )
        
        elif keyword_result["confidence"] > 0.7:
            # 高置信度关键词结果
            return ClassificationResult(
                category=keyword_result["category"],
                subcategory=keyword_result["subcategory"],
                confidence=keyword_result["confidence"],
                reasoning=f"关键词匹配: {', '.join(keyword_result['keywords'])}",
                keywords=keyword_result["keywords"]
            )
        
        else:
            # 低置信度：使用 LLM 结果但标记不确定性
            return ClassificationResult(
                category=llm_result["category"],
                subcategory=llm_result["subcategory"],
                confidence=max(llm_result["confidence"], keyword_result["confidence"]) * 0.8,
                reasoning=f"分类不确定。关键词: {keyword_result.get('keywords', [])}. LLM: {llm_result.get('reasoning', '')}",
                keywords=list(set(llm_result.get("keywords", []) + keyword_result.get("keywords", [])))
            )
    
    def _store_classification(self, title: str, body: str, result: ClassificationResult):
        """存储分类历史"""
        try:
            # 创建简化的存储内容
            content_hash = hash(f"{title}{body[:100]}")
            
            memory_store.store(
                key=f"issue_classification:{content_hash}",
                value={
                    "title": title[:100],
                    "category": result.category,
                    "subcategory": result.subcategory,
                    "confidence": result.confidence,
                    "keywords": result.keywords
                },
                metadata={
                    "type": "issue_classification"
                }
            )
            
            # 更新本地历史
            self.classification_history.append({
                "title": title,
                "category": result.category,
                "subcategory": result.subcategory
            })
            
            # 限制历史长度
            if len(self.classification_history) > 1000:
                self.classification_history = self.classification_history[-1000:]
                
        except Exception as e:
            logger.warning(f"Failed to store classification: {e}")
    
    def batch_classify(self, issues: List[Tuple[str, str]]) -> List[ClassificationResult]:
        """
        批量分类 Issues
        
        Args:
            issues: [(title, body), ...] 列表
            
        Returns:
            分类结果列表
        """
        results = []
        
        for title, body in issues:
            result = self.classify(title, body)
            results.append(result)
        
        return results
    
    def get_similar_issues(self, title: str, body: str, limit: int = 5) -> List[Dict]:
        """
        查找相似的已分类 Issues
        
        Args:
            title: Issue 标题
            body: Issue 内容
            limit: 返回数量限制
            
        Returns:
            相似 Issue 列表
        """
        try:
            similar = memory_store.search(
                query=f"{title} {body[:200]}",
                filters={"type": "issue_classification"},
                limit=limit
            )
            
            return [item["value"] for item in similar]
            
        except Exception as e:
            logger.warning(f"Failed to get similar issues: {e}")
            return []


# 导出
__all__ = ["IssueClassifier", "ClassificationResult"]
