"""
简单优先引擎（整合 Karpathy 原则 2: Simplicity First）
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re


class ComplexityLevel(Enum):
    """复杂度级别"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    OVERCOMPLICATED = "overcomplicated"


@dataclass
class CodeAnalysis:
    """代码分析"""
    lines_of_code: int
    cyclomatic_complexity: int
    nesting_depth: int
    abstraction_layers: int
    complexity_level: ComplexityLevel
    issues: List[str]
    suggestions: List[str]


class SimplicityEngine:
    """简单优先引擎"""

    def __init__(self):
        self.analyses: List[CodeAnalysis] = []

    def analyze_code(self, code: str, context: Optional[str] = None) -> CodeAnalysis:
        """分析代码复杂度"""
        lines = self._count_lines(code)
        complexity = self._calculate_cyclomatic_complexity(code)
        nesting = self._calculate_nesting_depth(code)
        abstractions = self._count_abstractions(code)

        complexity_level = self._determine_complexity_level(
            lines, complexity, nesting, abstractions
        )

        issues = self._identify_issues(code, lines, complexity, nesting, abstractions)
        suggestions = self._generate_suggestions(
            code, lines, complexity, nesting, abstractions, issues
        )

        analysis = CodeAnalysis(
            lines_of_code=lines,
            cyclomatic_complexity=complexity,
            nesting_depth=nesting,
            abstraction_layers=abstractions,
            complexity_level=complexity_level,
            issues=issues,
            suggestions=suggestions,
        )

        self.analyses.append(analysis)
        return analysis

    def _count_lines(self, code: str) -> int:
        """统计代码行数"""
        lines = []
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                lines.append(line)
        return len(lines)

    def _calculate_cyclomatic_complexity(self, code: str) -> int:
        """计算圈复杂度"""
        branch_keywords = [
            'if', 'elif', 'else', 'for', 'while', 'try', 'except',
            'and', 'or', 'lambda',
        ]

        complexity = 1
        for line in code.split('\n'):
            stripped = line.strip()
            for keyword in branch_keywords:
                if keyword in stripped:
                    complexity += 1
                    break

        return complexity

    def _calculate_nesting_depth(self, code: str) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0

        for line in code.split('\n'):
            stripped = line.strip()

            if stripped.startswith(('if ', 'elif ', 'for ', 'while ', 'try:', 'except', 'with ', 'def ', 'class ')):
                indent = len(line) - len(line.lstrip())
                depth = indent // 4
                current_depth = max(current_depth, depth)
                max_depth = max(max_depth, depth)

            elif stripped and not stripped.startswith('#'):
                indent = len(line) - len(line.lstrip())
                depth = indent // 4
                current_depth = depth

        return max_depth

    def _count_abstractions(self, code: str) -> int:
        """统计抽象层数"""
        count = 0

        count += len(re.findall(r'^class\s+\w+', code, re.MULTILINE))
        count += len(re.findall(r'^def\s+\w+', code, re.MULTILINE))
        count += len(re.findall(r'^@\w+', code, re.MULTILINE))
        count += len(re.findall(r'lambda\s+', code))

        return count

    def _determine_complexity_level(
        self,
        lines: int,
        complexity: int,
        nesting: int,
        abstractions: int,
    ) -> ComplexityLevel:
        """确定复杂度级别"""
        score = 0

        if lines > 200:
            score += 2
        elif lines > 100:
            score += 1

        if complexity > 15:
            score += 2
        elif complexity > 10:
            score += 1

        if nesting > 5:
            score += 2
        elif nesting > 3:
            score += 1

        if abstractions > 8:
            score += 2
        elif abstractions > 5:
            score += 1

        if score >= 5:
            return ComplexityLevel.OVERCOMPLICATED
        elif score >= 3:
            return ComplexityLevel.COMPLEX
        elif score >= 1:
            return ComplexityLevel.MODERATE
        else:
            return ComplexityLevel.SIMPLE

    def _identify_issues(
        self,
        code: str,
        lines: int,
        complexity: int,
        nesting: int,
        abstractions: int,
    ) -> List[str]:
        """识别问题"""
        issues = []

        if lines > 200:
            issues.append(f"代码行数过多 ({lines} 行)")

        if complexity > 15:
            issues.append(f"圈复杂度过高 ({complexity})")

        if nesting > 5:
            issues.append(f"嵌套过深 ({nesting} 层)")

        if abstractions > 8:
            issues.append(f"抽象层数过多 ({abstractions} 层)")

        return issues

    def _generate_suggestions(
        self,
        code: str,
        lines: int,
        complexity: int,
        nesting: int,
        abstractions: int,
        issues: List[str],
    ) -> List[str]:
        """生成建议"""
        suggestions = []

        if lines > 200:
            suggestions.append("考虑拆分为多个函数")

        if complexity > 15:
            suggestions.append("减少分支逻辑，使用提前返回")

        if nesting > 5:
            suggestions.append("减少嵌套，提取子函数")

        if abstractions > 8:
            suggestions.append("减少抽象层数，考虑是否真的需要")

        return suggestions

    def ask_senior_engineer(self, code: str) -> Tuple[bool, List[str]]:
        """询问高级工程师"""
        analysis = self.analyze_code(code)

        if analysis.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.OVERCOMPLICATED]:
            return False, analysis.issues

        return True, []

    def get_summary(self) -> Dict[str, Any]:
        """获取总结"""
        return {
            "total_analyses": len(self.analyses),
            "by_complexity": {
                level.value: len([a for a in self.analyses if a.complexity_level == level])
                for level in ComplexityLevel
            },
            "recent_analysis": self.analyses[-1].__dict__ if self.analyses else None,
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "analyses": [
                {
                    "lines_of_code": a.lines_of_code,
                    "cyclomatic_complexity": a.cyclomatic_complexity,
                    "nesting_depth": a.nesting_depth,
                    "abstraction_layers": a.abstraction_layers,
                    "complexity_level": a.complexity_level.value,
                    "issues": a.issues,
                    "suggestions": a.suggestions,
                }
                for a in self.analyses
            ],
            "summary": self.get_summary(),
        }
