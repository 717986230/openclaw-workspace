#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自我改进推理
Self-Improving Reasoning

基于Reasoning-from-Scratch项目的自我改进推理技术
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class ImprovementMethod(Enum):
    """改进方法"""
    SELF_CRITIQUE = "self_critique"
    SELF_CORRECTION = "self_correction"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    ERROR_DETECTION = "error_detection"

@dataclass
class ImprovementConfig:
    """改进配置"""
    method: ImprovementMethod
    max_iterations: int = 3
    critique_threshold: float = 0.7
    enable_error_detection: bool = True
    enable_refinement: bool = True

class SelfCritique:
    """自我批评"""

    def __init__(self, critique_fn):
        self.critique_fn = critique_fn

    def critique(self, query: str, response: str) -> Dict:
        """批评响应"""
        critique = self.critique_fn(query, response)

        return {
            'query': query,
            'response': response,
            'critique': critique,
            'score': self._compute_score(critique),
            'issues': self._extract_issues(critique),
            'suggestions': self._extract_suggestions(critique)
        }

    def _compute_score(self, critique: str) -> float:
        """计算批评分数"""
        # 这里可以添加更复杂的逻辑
        # 简化版：根据批评的长度和关键词
        positive_keywords = ['good', 'excellent', 'correct', 'accurate', 'clear']
        negative_keywords = ['bad', 'wrong', 'incorrect', 'unclear', 'confusing']

        score = 0.5  # 基础分数

        for keyword in positive_keywords:
            if keyword in critique.lower():
                score += 0.1

        for keyword in negative_keywords:
            if keyword in critique.lower():
                score -= 0.1

        return max(0.0, min(1.0, score))

    def _extract_issues(self, critique: str) -> List[str]:
        """提取问题"""
        issues = []

        # 简化版：查找问题关键词
        issue_keywords = ['issue', 'problem', 'error', 'mistake', 'flaw', 'weakness']

        for keyword in issue_keywords:
            if keyword in critique.lower():
                issues.append(keyword)

        return issues

    def _extract_suggestions(self, critique: str) -> List[str]:
        """提取建议"""
        suggestions = []

        # 简化版：查找建议关键词
        suggestion_keywords = ['suggest', 'recommend', 'improve', 'enhance', 'better']

        for keyword in suggestion_keywords:
            if keyword in critique.lower():
                suggestions.append(keyword)

        return suggestions


class SelfCorrection:
    """自我修正"""

    def __init__(self, correction_fn):
        self.correction_fn = correction_fn

    def correct(self, query: str, response: str, critique: Dict) -> str:
        """修正响应"""
        correction_prompt = self._build_correction_prompt(query, response, critique)
        corrected_response = self.correction_fn(correction_prompt)

        return corrected_response

    def _build_correction_prompt(self, query: str, response: str, critique: Dict) -> str:
        """构建修正提示"""
        prompt = f"""Original Query: {query}

Original Response: {response}

Critique:
- Score: {critique['score']}
- Issues: {', '.join(critique['issues'])}
- Suggestions: {', '.join(critique['suggestions'])}

Please provide a corrected response that addresses the issues and incorporates the suggestions:"""

        return prompt


class IterativeRefinement:
    """迭代优化"""

    def __init__(self, refine_fn, max_iterations: int = 3):
        self.refine_fn = refine_fn
        self.max_iterations = max_iterations

    def refine(self, query: str, initial_response: str) -> Tuple[str, List[Dict]]:
        """迭代优化"""
        current_response = initial_response
        history = []

        for iteration in range(self.max_iterations):
            # 构建优化提示
            refine_prompt = self._build_refine_prompt(query, current_response, iteration)

            # 生成优化后的响应
            refined_response = self.refine_fn(refine_prompt)

            # 记录历史
            history.append({
                'iteration': iteration,
                'response': current_response,
                'refined_response': refined_response
            })

            # 检查是否收敛
            if self._is_converged(current_response, refined_response):
                break

            current_response = refined_response

        return current_response, history

    def _build_refine_prompt(self, query: str, response: str, iteration: int) -> str:
        """构建优化提示"""
        prompt = f"""Query: {query}

Current Response (Iteration {iteration}):
{response}

Please refine and improve this response. Focus on:
1. Clarity and precision
2. Completeness and accuracy
3. Logical consistency
4. Relevance to the query

Refined Response:"""

        return prompt

    def _is_converged(self, response1: str, response2: str, threshold: float = 0.95) -> bool:
        """检查是否收敛"""
        # 简化版：比较响应的相似度
        # 这里可以使用更复杂的相似度计算
        similarity = self._compute_similarity(response1, response2)
        return similarity >= threshold

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算相似度"""
        # 简化版：使用Jaccard相似度
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        if union == 0:
            return 0.0

        return intersection / union


class ErrorDetection:
    """错误检测"""

    def __init__(self, error_patterns: List[Dict] = None):
        self.error_patterns = error_patterns or self._default_error_patterns()

    def _default_error_patterns(self) -> List[Dict]:
        """默认错误模式"""
        return [
            {'pattern': 'contradiction', 'keywords': ['but', 'however', 'although', 'yet']},
            {'pattern': 'inconsistency', 'keywords': ['different', 'various', 'multiple']},
            {'pattern': 'uncertainty', 'keywords': ['maybe', 'perhaps', 'possibly', 'might']},
            {'pattern': 'vagueness', 'keywords': ['some', 'several', 'many', 'few']},
            {'pattern': 'repetition', 'keywords': ['again', 'repeat', 'same', 'similar']}
        ]

    def detect(self, query: str, response: str) -> List[Dict]:
        """检测错误"""
        errors = []

        for pattern in self.error_patterns:
            error = self._check_pattern(query, response, pattern)
            if error:
                errors.append(error)

        return errors

    def _check_pattern(self, query: str, response: str, pattern: Dict) -> Optional[Dict]:
        """检查特定模式"""
        pattern_type = pattern['pattern']
        keywords = pattern['keywords']

        # 检查响应中是否包含关键词
        found_keywords = [kw for kw in keywords if kw in response.lower()]

        if found_keywords:
            return {
                'type': pattern_type,
                'keywords': found_keywords,
                'severity': self._compute_severity(found_keywords),
                'location': self._find_location(response, found_keywords[0])
            }

        return None

    def _compute_severity(self, keywords: List[str]) -> str:
        """计算严重程度"""
        if len(keywords) >= 3:
            return 'high'
        elif len(keywords) >= 2:
            return 'medium'
        else:
            return 'low'

    def _find_location(self, text: str, keyword: str) -> str:
        """查找关键词位置"""
        index = text.lower().find(keyword)
        if index == -1:
            return 'unknown'

        # 返回关键词周围的上下文
        start = max(0, index - 20)
        end = min(len(text), index + len(keyword) + 20)

        return text[start:end]


class SelfImprovingReasoning:
    """自我改进推理"""

    def __init__(self, config: ImprovementConfig, critique_fn=None, correction_fn=None, refine_fn=None):
        self.config = config

        # 初始化各个组件
        if critique_fn:
            self.critique = SelfCritique(critique_fn)
        if correction_fn:
            self.correction = SelfCorrection(correction_fn)
        if refine_fn:
            self.refinement = IterativeRefinement(refine_fn, config.max_iterations)
        if config.enable_error_detection:
            self.error_detection = ErrorDetection()

    def improve(self, query: str, initial_response: str) -> Dict:
        """改进推理"""
        result = {
            'query': query,
            'initial_response': initial_response,
            'improved_response': initial_response,
            'iterations': [],
            'errors': [],
            'final_score': 0.0
        }

        # 1. 错误检测
        if self.config.enable_error_detection:
            errors = self.error_detection.detect(query, initial_response)
            result['errors'] = errors

        # 2. 自我批评
        if hasattr(self, 'critique'):
            critique = self.critique.critique(query, initial_response)
            result['critique'] = critique

            # 3. 自我修正
            if hasattr(self, 'correction') and critique['score'] < self.config.critique_threshold:
                corrected_response = self.correction.correct(query, initial_response, critique)
                result['improved_response'] = corrected_response
                result['iterations'].append({
                    'type': 'correction',
                    'response': corrected_response
                })

        # 4. 迭代优化
        if hasattr(self, 'refinement') and self.config.enable_refinement:
            refined_response, history = self.refinement.refine(query, result['improved_response'])
            result['improved_response'] = refined_response
            result['iterations'].extend(history)

        # 5. 计算最终分数
        result['final_score'] = self._compute_final_score(result)

        return result

    def _compute_final_score(self, result: Dict) -> float:
        """计算最终分数"""
        # 简化版：基于错误数量和迭代次数
        base_score = 1.0

        # 错误扣分
        error_penalty = len(result['errors']) * 0.1
        base_score -= error_penalty

        # 迭代加分
        iteration_bonus = len(result['iterations']) * 0.05
        base_score += iteration_bonus

        return max(0.0, min(1.0, base_score))


if __name__ == "__main__":
    # 测试代码
    print("Testing Self-Improving Reasoning...")

    # 测试错误检测
    error_detection = ErrorDetection()

    query = "What is the capital of France?"
    response = "The capital of France is Paris, but some people think it's Lyon, although it's definitely Paris."

    errors = error_detection.detect(query, response)
    print(f"Detected errors: {errors}")

    # 测试自我改进推理
    config = ImprovementConfig(
        method=ImprovementMethod.SELF_CRITIQUE,
        max_iterations=3,
        critique_threshold=0.7,
        enable_error_detection=True,
        enable_refinement=True
    )

    reasoning = SelfImprovingReasoning(config)

    # 模拟改进过程
    result = reasoning.improve(query, response)

    print(f"Initial response: {result['initial_response']}")
    print(f"Improved response: {result['improved_response']}")
    print(f"Errors: {result['errors']}")
    print(f"Final score: {result['final_score']}")

    print("Self-Improving Reasoning test complete!")
