"""
Bug Detector - SWE-agent 集成
从 Issue 描述中自动检测和提取 Bug 信息
"""

import json
import logging
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed

logger = logging.getLogger(__name__)


class BugSeverity(Enum):
    """Bug 严重程度"""
    CRITICAL = "critical"  # 系统崩溃、数据丢失
    HIGH = "high"          # 功能无法使用
    MEDIUM = "medium"      # 功能部分受影响
    LOW = "low"            # 轻微问题


class BugType(Enum):
    """Bug 类型"""
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPATIBILITY = "compatibility"
    UI_UX = "ui_ux"
    DATA_CORRUPTION = "data_corruption"
    MEMORY_LEAK = "memory_leak"
    UNKNOWN = "unknown"


@dataclass
class BugInfo:
    """Bug 信息"""
    bug_type: BugType
    severity: BugSeverity
    title: str
    description: str
    stack_trace: Optional[str]
    error_message: Optional[str]
    reproduction_steps: List[str]
    expected_behavior: Optional[str]
    actual_behavior: Optional[str]
    environment: Dict[str, str]
    affected_components: List[str]
    suggested_fix: Optional[str]


@dataclass
class StackTrace:
    """堆栈跟踪信息"""
    raw_trace: str
    error_type: str
    error_message: str
    file_paths: List[str]
    line_numbers: List[int]
    function_names: List[str]


class BugDetector:
    """
    Bug 检测器
    
    功能:
    - 从 Issue 描述提取错误信息
    - 解析堆栈跟踪
    - 评估 Bug 严重程度
    - 生成修复建议
    """
    
    def __init__(self):
        """初始化 Bug 检测器"""
        self.error_patterns = {
            # Python
            "python": {
                "patterns": [
                    r"Traceback \(most recent call last\):",
                    r"(\w+Error): (.+)",
                    r'File "([^"]+)", line (\d+)',
                ],
                "error_types": [
                    "ValueError", "TypeError", "KeyError", "AttributeError",
                    "ImportError", "RuntimeError", "NameError", "IndexError"
                ]
            },
            # JavaScript
            "javascript": {
                "patterns": [
                    r"Error: (.+)",
                    r"at (.+) \(([^:]+):(\d+):(\d+)\)",
                    r"TypeError: (.+)",
                    r"ReferenceError: (.+)"
                ],
                "error_types": [
                    "TypeError", "ReferenceError", "SyntaxError",
                    "RangeError", "URIError"
                ]
            },
            # Java
            "java": {
                "patterns": [
                    r"Exception in thread .+",
                    r"at ([^.]+)\.([^.(]+)\(([^)]+)\)",
                    r"Caused by: (.+)"
                ],
                "error_types": [
                    "NullPointerException", "ArrayIndexOutOfBoundsException",
                    "IllegalArgumentException", "IOException", "SQLException"
                ]
            }
        }
        
        self.severity_keywords = {
            BugSeverity.CRITICAL: ["crash", "崩溃", "数据丢失", "data loss", "security vulnerability", "安全漏洞"],
            BugSeverity.HIGH: ["无法使用", "无法工作", "not working", "broken", "失败", "failed"],
            BugSeverity.MEDIUM: ["部分功能", "间歇性", "intermittent", "sometimes"],
            BugSeverity.LOW: ["轻微", "minor", "cosmetic", "显示问题", "display issue"]
        }
        
        logger.info("BugDetector initialized")
    
    def detect_bug(self, title: str, body: str) -> BugInfo:
        """
        检测并提取 Bug 信息
        
        Args:
            title: Issue 标题
            body: Issue 内容
            
        Returns:
            BugInfo Bug 信息
        """
        text = f"{title}\n\n{body}"
        
        # 1. 检测 Bug 类型
        bug_type = self._detect_bug_type(text)
        
        # 2. 评估严重程度
        severity = self._assess_severity(text)
        
        # 3. 提取错误信息
        error_message = self._extract_error_message(text)
        stack_trace = self._extract_stack_trace(text)
        
        # 4. 提取复现步骤
        reproduction_steps = self._extract_reproduction_steps(text)
        
        # 5. 提取环境信息
        environment = self._extract_environment(text)
        
        # 6. 提取期望和实际行为
        expected, actual = self._extract_behaviors(text)
        
        # 7. 生成修复建议
        suggested_fix = self._generate_fix_suggestion(
            bug_type, error_message, stack_trace, title, body
        )
        
        bug_info = BugInfo(
            bug_type=bug_type,
            severity=severity,
            title=title,
            description=body,
            stack_trace=stack_trace,
            error_message=error_message,
            reproduction_steps=reproduction_steps,
            expected_behavior=expected,
            actual_behavior=actual,
            environment=environment,
            affected_components=self._identify_components(stack_trace, text),
            suggested_fix=suggested_fix
        )
        
        logger.info(f"Detected bug: {bug_type.value} with severity {severity.value}")
        return bug_info
    
    def _detect_bug_type(self, text: str) -> BugType:
        """检测 Bug 类型"""
        text_lower = text.lower()
        
        type_keywords = {
            BugType.RUNTIME_ERROR: ["exception", "error", "crash", "崩溃", "运行时"],
            BugType.LOGIC_ERROR: ["逻辑错误", "结果不对", "incorrect", "wrong result"],
            BugType.PERFORMANCE: ["性能", "慢", "slow", "timeout", "超时", "内存泄漏", "memory leak"],
            BugType.SECURITY: ["安全", "security", "漏洞", "vulnerability", "XSS", "注入"],
            BugType.COMPATIBILITY: ["兼容性", "compatibility", "浏览器", "browser", "版本"],
            BugType.UI_UX: ["UI", "显示", "display", "样式", "style", "布局", "layout"],
            BugType.DATA_CORRUPTION: ["数据损坏", "data corruption", "数据丢失", "data loss"]
        }
        
        for bug_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return bug_type
        
        return BugType.UNKNOWN
    
    def _assess_severity(self, text: str) -> BugSeverity:
        """评估 Bug 严重程度"""
        text_lower = text.lower()
        
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return severity
        
        return BugSeverity.MEDIUM
    
    def _extract_error_message(self, text: str) -> Optional[str]:
        """提取错误消息"""
        # 尝试匹配常见错误模式
        patterns = [
            r"(Error: .+)",
            r"(Exception: .+)",
            r"(\w+Error: .+)",
            r"(错误[:：]\s*.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_stack_trace(self, text: str) -> Optional[str]:
        """提取堆栈跟踪"""
        # 匹配多行堆栈跟踪
        patterns = [
            r"Traceback \(most recent call last\):[\s\S]+?(?=\n\n|\Z)",
            r"Error:[\s\S]+?at .+\(.+:\d+:\d+\)[\s\S]+?(?=\n\n|\Z)",
            r"Exception in thread[\s\S]+?at [\w.]+\([\w.]+:\d+\)[\s\S]+?(?=\n\n|\Z)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _extract_reproduction_steps(self, text: str) -> List[str]:
        """提取复现步骤"""
        steps = []
        
        # 匹配步骤列表
        step_patterns = [
            r"复现步骤[:：]\s*([\s\S]+?)(?=\n\n|\n期望|\n实际|\Z)",
            r"Steps to reproduce[:：]\s*([\s\S]+?)(?=\n\n|\nExpected|\nActual|\Z)",
            r"重现步骤[:：]\s*([\s\S]+?)(?=\n\n|\Z)"
        ]
        
        for pattern in step_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                steps_text = match.group(1)
                # 解析步骤
                for line in steps_text.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                        steps.append(line.lstrip('0123456789.-* '))
        
        return steps
    
    def _extract_environment(self, text: str) -> Dict[str, str]:
        """提取环境信息"""
        environment = {}
        
        # 常见环境信息模式
        env_patterns = {
            "os": r"(?:OS|操作系统|系统)[:：]\s*([^\n]+)",
            "version": r"(?:Version|版本)[:：]\s*([^\n]+)",
            "browser": r"(?:Browser|浏览器)[:：]\s*([^\n]+)",
            "python_version": r"Python\s+(\d+\.\d+\.\d+)",
            "node_version": r"Node\.js\s+(\d+\.\d+\.\d+)",
            "java_version": r"Java\s+(\d+)"
        }
        
        for key, pattern in env_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                environment[key] = match.group(1).strip()
        
        return environment
    
    def _extract_behaviors(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """提取期望和实际行为"""
        expected = None
        actual = None
        
        # 期望行为
        expected_patterns = [
            r"(?:Expected|期望)[:：]\s*([^\n]+(?:\n(?!实际|Actual)[^\n]+)*)",
        ]
        
        for pattern in expected_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                expected = match.group(1).strip()
                break
        
        # 实际行为
        actual_patterns = [
            r"(?:Actual|实际)[:：]\s*([^\n]+(?:\n(?!期望|Expected)[^\n]+)*)",
        ]
        
        for pattern in actual_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                actual = match.group(1).strip()
                break
        
        return expected, actual
    
    def _identify_components(self, stack_trace: Optional[str], text: str) -> List[str]:
        """识别受影响的组件"""
        components = []
        
        if stack_trace:
            # 从堆栈跟踪提取文件路径
            file_pattern = r'(?:File "([^"]+)"|at [^(]+\(([^:]+):)'
            matches = re.findall(file_pattern, stack_trace)
            
            for match in matches:
                file_path = match[0] or match[1]
                if file_path:
                    # 提取文件名作为组件
                    component = file_path.split('/')[-1].split('\\')[-1]
                    if component and component not in components:
                        components.append(component)
        
        return components[:5]  # 最多返回 5 个组件
    
    def _generate_fix_suggestion(
        self,
        bug_type: BugType,
        error_message: Optional[str],
        stack_trace: Optional[str],
        title: str,
        body: str
    ) -> Optional[str]:
        """使用 LLM 生成修复建议"""
        prompt = f"""分析以下 Bug 并提供修复建议:

标题: {title}

Bug 类型: {bug_type.value}

错误信息: {error_message or '无'}

堆栈跟踪: {stack_trace or '无'}

问题描述:
{body[:500]}

请提供:
1. Bug 根因分析
2. 修复步骤
3. 预防措施

用简洁的中文回答。"""
        
        try:
            response = ask_local_ai_routed(
                prompt=prompt,
                mode="claude_only"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate fix suggestion: {e}")
            return None
    
    def parse_stack_trace(self, stack_trace: str) -> StackTrace:
        """
        解析堆栈跟踪
        
        Args:
            stack_trace: 原始堆栈跟踪字符串
            
        Returns:
            StackTrace 解析后的对象
        """
        # 提取错误类型和消息
        error_type = "UnknownError"
        error_message = ""
        
        type_match = re.search(r'(\w+Error|\w+Exception): (.+)', stack_trace)
        if type_match:
            error_type = type_match.group(1)
            error_message = type_match.group(2)
        
        # 提取文件路径
        file_paths = re.findall(r'(?:File "([^"]+)"|at [^(]+\(([^:]+):)', stack_trace)
        files = [f[0] or f[1] for f in file_paths]
        
        # 提取行号
        line_numbers = []
        line_matches = re.findall(r':(\d+)(?::\d+)?\)', stack_trace)
        line_numbers = [int(n) for n in line_matches if n.isdigit()]
        
        # 提取函数名
        function_names = re.findall(r'(?:in |at )(\w+)\(', stack_trace)
        
        return StackTrace(
            raw_trace=stack_trace,
            error_type=error_type,
            error_message=error_message,
            file_paths=files,
            line_numbers=line_numbers,
            function_names=function_names
        )


# 导出
__all__ = [
    "BugDetector",
    "BugInfo",
    "BugSeverity",
    "BugType",
    "StackTrace"
]
