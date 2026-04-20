"""
Code Reviewer - SWE-agent 集成
智能代码审查工具
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed

logger = logging.getLogger(__name__)


class ReviewSeverity(Enum):
    """审查严重程度"""
    CRITICAL = "critical"    # 必须修复
    MAJOR = "major"          # 强烈建议修复
    MINOR = "minor"          # 建议修复
    INFO = "info"            # 信息性提示


@dataclass
class ReviewComment:
    """审查评论"""
    file: str
    line: Optional[int]
    severity: ReviewSeverity
    category: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class CodeReviewResult:
    """代码审查结果"""
    overall_score: float  # 0-10
    security_score: float
    quality_score: float
    performance_score: float
    comments: List[ReviewComment]
    approve: bool
    summary: str
    recommendations: List[str]


class CodeReviewer:
    """
    智能代码审查器
    
    功能:
    - 安全漏洞检测
    - 代码质量评估
    - 性能分析
    - 最佳实践检查
    - 自动生成审查报告
    """
    
    def __init__(self):
        """初始化代码审查器"""
        self.security_patterns = self._load_security_patterns()
        self.quality_rules = self._load_quality_rules()
        self.performance_rules = self._load_performance_rules()
        logger.info("CodeReviewer initialized")
    
    def _load_security_patterns(self) -> Dict:
        """加载安全漏洞模式"""
        return {
            "sql_injection": {
                "patterns": [
                    r"execute\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                    r"cursor\.execute\s*\(\s*f[\"']",
                    r"query\s*=\s*[\"'].*\+",
                ],
                "message": "潜在的 SQL 注入漏洞",
                "severity": ReviewSeverity.CRITICAL
            },
            "xss": {
                "patterns": [
                    r"innerHTML\s*=",
                    r"document\.write\s*\(",
                    r"dangerouslySetInnerHTML",
                ],
                "message": "潜在的 XSS 漏洞",
                "severity": ReviewSeverity.CRITICAL
            },
            "hardcoded_secrets": {
                "patterns": [
                    r"password\s*=\s*[\"'][^\"']+[\"']",
                    r"api_key\s*=\s*[\"'][^\"']+[\"']",
                    r"secret\s*=\s*[\"'][^\"']+[\"']",
                    r"token\s*=\s*[\"'][^\"']+[\"']",
                ],
                "message": "硬编码的敏感信息",
                "severity": ReviewSeverity.CRITICAL
            },
            "path_traversal": {
                "patterns": [
                    r"open\s*\(\s*[\"'].*\+",
                    r"readFile\s*\(\s*[\"'].*\+",
                ],
                "message": "潜在的路径遍历漏洞",
                "severity": ReviewSeverity.MAJOR
            }
        }
    
    def _load_quality_rules(self) -> Dict:
        """加载代码质量规则"""
        return {
            "long_function": {
                "check": lambda lines: len(lines) > 50,
                "message": "函数过长，建议拆分",
                "severity": ReviewSeverity.MINOR
            },
            "deep_nesting": {
                "patterns": [r"(\s{8,})\w"],  # 4+ 层嵌套
                "message": "嵌套层级过深",
                "severity": ReviewSeverity.MINOR
            },
            "magic_numbers": {
                "patterns": [r"(?<!['\"])\b\d{2,}\b(?!['\"])"],
                "message": "魔法数字，建议使用常量",
                "severity": ReviewSeverity.INFO
            },
            "todo_comments": {
                "patterns": [r"#\s*TODO", r"//\s*TODO", r"/\*\s*TODO"],
                "message": "未完成的 TODO",
                "severity": ReviewSeverity.INFO
            }
        }
    
    def _load_performance_rules(self) -> Dict:
        """加载性能规则"""
        return {
            "n_plus_one": {
                "patterns": [
                    r"for\s+\w+\s+in\s+.+:\s*\n\s*.*\.query",
                    r"for.*\{[\s\S]*?query",
                ],
                "message": "潜在的 N+1 查询问题",
                "severity": ReviewSeverity.MAJOR
            },
            "large_loop": {
                "check": lambda code: "for" in code and "range(10000" in code,
                "message": "大循环可能影响性能",
                "severity": ReviewSeverity.MINOR
            },
            "sync_io_in_loop": {
                "patterns": [
                    r"for\s+.*:\s*\n.*read\s*\(",
                    r"for\s+.*:\s*\n.*write\s*\(",
                ],
                "message": "循环中的同步 I/O 操作",
                "severity": ReviewSeverity.MAJOR
            }
        }
    
    def review_pr(
        self,
        repo: str,
        pr_number: int,
        code_changes: Dict[str, str],
        check_security: bool = True,
        check_quality: bool = True,
        check_performance: bool = True
    ) -> CodeReviewResult:
        """
        审查 Pull Request
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            code_changes: {文件路径: 代码内容} 字典
            check_security: 是否检查安全
            check_quality: 是否检查质量
            check_performance: 是否检查性能
            
        Returns:
            CodeReviewResult 审查结果
        """
        all_comments = []
        
        # 1. 安全检查
        security_score = 10.0
        if check_security:
            security_comments, security_score = self._check_security(code_changes)
            all_comments.extend(security_comments)
        
        # 2. 质量检查
        quality_score = 10.0
        if check_quality:
            quality_comments, quality_score = self._check_quality(code_changes)
            all_comments.extend(quality_comments)
        
        # 3. 性能检查
        performance_score = 10.0
        if check_performance:
            performance_comments, performance_score = self._check_performance(code_changes)
            all_comments.extend(performance_comments)
        
        # 4. LLM 深度审查
        llm_comments = self._llm_deep_review(code_changes)
        all_comments.extend(llm_comments)
        
        # 5. 计算总分
        overall_score = (security_score * 0.4 + quality_score * 0.35 + performance_score * 0.25)
        
        # 6. 决定是否批准
        approve = overall_score >= 7.0 and not any(
            c.severity == ReviewSeverity.CRITICAL for c in all_comments
        )
        
        # 7. 生成总结和建议
        summary = self._generate_summary(all_comments, overall_score)
        recommendations = self._generate_recommendations(all_comments)
        
        return CodeReviewResult(
            overall_score=round(overall_score, 1),
            security_score=round(security_score, 1),
            quality_score=round(quality_score, 1),
            performance_score=round(performance_score, 1),
            comments=all_comments,
            approve=approve,
            summary=summary,
            recommendations=recommendations
        )
    
    def _check_security(self, code_changes: Dict[str, str]) -> Tuple[List[ReviewComment], float]:
        """检查安全问题"""
        comments = []
        score = 10.0
        
        for file_path, code in code_changes.items():
            for vuln_name, vuln_info in self.security_patterns.items():
                for pattern in vuln_info["patterns"]:
                    matches = re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE)
                    
                    for match in matches:
                        # 计算行号
                        line_num = code[:match.start()].count('\n') + 1
                        
                        comments.append(ReviewComment(
                            file=file_path,
                            line=line_num,
                            severity=vuln_info["severity"],
                            category="security",
                            message=vuln_info["message"],
                            suggestion="使用参数化查询或输入验证"
                        ))
                        
                        # 扣分
                        score -= vuln_info["severity"].value * 1.5
        
        return comments, max(score, 0.0)
    
    def _check_quality(self, code_changes: Dict[str, str]) -> Tuple[List[ReviewComment], float]:
        """检查代码质量"""
        comments = []
        score = 10.0
        
        for file_path, code in code_changes.items():
            lines = code.split('\n')
            
            for rule_name, rule_info in self.quality_rules.items():
                if "patterns" in rule_info:
                    for pattern in rule_info["patterns"]:
                        matches = re.finditer(pattern, code, re.MULTILINE)
                        
                        for match in matches:
                            line_num = code[:match.start()].count('\n') + 1
                            
                            comments.append(ReviewComment(
                                file=file_path,
                                line=line_num,
                                severity=rule_info["severity"],
                                category="quality",
                                message=rule_info["message"]
                            ))
                            
                            score -= 0.5
        
        return comments, max(score, 0.0)
    
    def _check_performance(self, code_changes: Dict[str, str]) -> Tuple[List[ReviewComment], float]:
        """检查性能问题"""
        comments = []
        score = 10.0
        
        for file_path, code in code_changes.items():
            for rule_name, rule_info in self.performance_rules.items():
                if "patterns" in rule_info:
                    for pattern in rule_info["patterns"]:
                        matches = re.finditer(pattern, code, re.MULTILINE | re.DOTALL)
                        
                        for match in matches:
                            line_num = code[:match.start()].count('\n') + 1
                            
                            comments.append(ReviewComment(
                                file=file_path,
                                line=line_num,
                                severity=rule_info["severity"],
                                category="performance",
                                message=rule_info["message"]
                            ))
                            
                            score -= 1.0
        
        return comments, max(score, 0.0)
    
    def _llm_deep_review(self, code_changes: Dict[str, str]) -> List[ReviewComment]:
        """使用 LLM 深度审查"""
        comments = []
        
        for file_path, code in code_changes.items():
            if len(code) < 50:  # 忽略小文件
                continue
            
            prompt = f"""审查以下代码并提供改进建议:

文件: {file_path}

代码:
```
{code[:2000]}
```

请从以下方面审查:
1. 代码可读性
2. 错误处理
3. 边界条件
4. 潜在 Bug

以 JSON 格式返回审查意见:
{{
  "issues": [
    {{
      "line": <行号>,
      "severity": "critical|major|minor|info",
      "message": "问题描述",
      "suggestion": "改进建议"
    }}
  ]
}}

如果没有问题，返回空列表。"""
            
            try:
                response = ask_local_ai_routed(
                    prompt=prompt,
                    mode="claude_then_codex_review"
                )
                
                # 解析响应
                result = self._parse_review_response(response)
                
                for issue in result.get("issues", []):
                    comments.append(ReviewComment(
                        file=file_path,
                        line=issue.get("line"),
                        severity=ReviewSeverity(issue.get("severity", "info")),
                        category="llm_review",
                        message=issue.get("message", ""),
                        suggestion=issue.get("suggestion")
                    ))
                    
            except Exception as e:
                logger.warning(f"LLM review failed for {file_path}: {e}")
        
        return comments
    
    def _parse_review_response(self, response: str) -> Dict:
        """解析审查响应"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"issues": []}
        except json.JSONDecodeError:
            return {"issues": []}
    
    def _generate_summary(self, comments: List[ReviewComment], score: float) -> str:
        """生成审查总结"""
        critical = sum(1 for c in comments if c.severity == ReviewSeverity.CRITICAL)
        major = sum(1 for c in comments if c.severity == ReviewSeverity.MAJOR)
        minor = sum(1 for c in comments if c.severity == ReviewSeverity.MINOR)
        
        summary = f"代码审查完成。整体评分: {score}/10\n\n"
        summary += f"发现问题: {len(comments)} 个\n"
        summary += f"- 严重: {critical} 个\n"
        summary += f"- 重要: {major} 个\n"
        summary += f"- 次要: {minor} 个\n"
        
        if critical > 0:
            summary += "\n⚠️ 存在严重问题，建议修复后再合并。"
        elif major > 0:
            summary += "\n⚡ 存在重要问题，建议优先处理。"
        else:
            summary += "\n✅ 代码质量良好，可以合并。"
        
        return summary
    
    def _generate_recommendations(self, comments: List[ReviewComment]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 按严重程度排序
        severity_order = {
            ReviewSeverity.CRITICAL: 0,
            ReviewSeverity.MAJOR: 1,
            ReviewSeverity.MINOR: 2,
            ReviewSeverity.INFO: 3
        }
        
        sorted_comments = sorted(comments, key=lambda c: severity_order[c.severity])
        
        for comment in sorted_comments[:10]:  # 最多 10 条建议
            rec = f"[{comment.severity.value.upper()}] {comment.file}"
            if comment.line:
                rec += f":{comment.line}"
            rec += f" - {comment.message}"
            
            if comment.suggestion:
                rec += f"\n  建议: {comment.suggestion}"
            
            recommendations.append(rec)
        
        return recommendations


# 导出
__all__ = [
    "CodeReviewer",
    "CodeReviewResult",
    "ReviewComment",
    "ReviewSeverity"
]
