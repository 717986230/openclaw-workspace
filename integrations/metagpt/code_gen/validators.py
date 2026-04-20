"""
代码验证器

验证生成的代码质量。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import ast
import re


@dataclass
class ValidationResult:
    """验证结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]


class CodeValidator:
    """
    代码验证器
    
    验证代码质量和规范性。
    """
    
    def __init__(self):
        """初始化代码验证器"""
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Dict[str, Any]]:
        """加载验证规则"""
        return [
            {"name": "syntax_check", "enabled": True, "severity": "error"},
            {"name": "naming_convention", "enabled": True, "severity": "warning"},
            {"name": "docstring_check", "enabled": True, "severity": "info"},
            {"name": "complexity_check", "enabled": True, "severity": "warning"},
            {"name": "import_check", "enabled": True, "severity": "info"}
        ]
    
    async def validate(
        self,
        code: str,
        language: str = "python"
    ) -> ValidationResult:
        """
        验证代码
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        metrics = {}
        
        # 语法检查
        syntax_errors = await self._check_syntax(code, language)
        errors.extend(syntax_errors)
        
        # 命名规范检查
        naming_warnings = await self._check_naming(code, language)
        warnings.extend(naming_warnings)
        
        # 文档字符串检查
        docstring_info = await self._check_docstrings(code, language)
        warnings.extend(docstring_info)
        
        # 复杂度检查
        complexity_warnings, complexity_metrics = await self._check_complexity(code)
        warnings.extend(complexity_warnings)
        metrics.update(complexity_metrics)
        
        # 导入检查
        import_warnings = await self._check_imports(code, language)
        warnings.extend(import_warnings)
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    async def validate_file(
        self,
        filename: str,
        code: str
    ) -> ValidationResult:
        """
        验证单个文件
        
        Args:
            filename: 文件名
            code: 代码内容
            
        Returns:
            验证结果
        """
        result = await self.validate(code)
        
        # 添加文件信息到错误和警告
        result.errors = [f"{filename}: {err}" for err in result.errors]
        result.warnings = [f"{filename}: {warn}" for warn in result.warnings]
        
        return result
    
    async def validate_project(
        self,
        files: Dict[str, str]
    ) -> Dict[str, ValidationResult]:
        """
        验证整个项目
        
        Args:
            files: 文件字典 {文件名: 代码}
            
        Returns:
            验证结果字典
        """
        results = {}
        
        for filename, code in files.items():
            results[filename] = await self.validate_file(filename, code)
        
        return results
    
    async def _check_syntax(
        self, 
        code: str, 
        language: str
    ) -> List[str]:
        """
        检查语法错误
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            错误列表
        """
        errors = []
        
        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f"Syntax error: {e.msg} at line {e.lineno}")
        
        return errors
    
    async def _check_naming(
        self, 
        code: str, 
        language: str
    ) -> List[str]:
        """
        检查命名规范
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            警告列表
        """
        warnings = []
        
        if language == "python":
            # 检查类名（应该使用 CamelCase）
            class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            for match in re.finditer(class_pattern, code):
                class_name = match.group(1)
                if not class_name[0].isupper():
                    warnings.append(
                        f"Class name '{class_name}' should use CamelCase"
                    )
            
            # 检查函数名（应该使用 snake_case）
            func_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
            for match in re.finditer(func_pattern, code):
                func_name = match.group(1)
                if func_name[0].isupper():
                    warnings.append(
                        f"Function name '{func_name}' should use snake_case"
                    )
        
        return warnings
    
    async def _check_docstrings(
        self, 
        code: str, 
        language: str
    ) -> List[str]:
        """
        检查文档字符串
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            信息列表
        """
        info = []
        
        if language == "python":
            # 检查模块文档字符串
            if not code.strip().startswith('"""') and not code.strip().startswith("'''"):
                info.append("Module lacks docstring")
            
            # 检查类和方法是否有文档字符串
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            info.append(
                                f"{node.__class__.__name__} '{node.name}' lacks docstring"
                            )
            except:
                pass
        
        return info
    
    async def _check_complexity(self, code: str) -> tuple:
        """
        检查代码复杂度
        
        Args:
            code: 源代码
            
        Returns:
            (警告列表, 复杂度指标)
        """
        warnings = []
        metrics = {}
        
        lines = code.split('\n')
        
        # 行数
        metrics['lines_of_code'] = len([line for line in lines if line.strip()])
        
        # 圈复杂度（简化版）
        complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'and', 'or']
        cyclomatic_complexity = 1
        for keyword in complexity_keywords:
            cyclomatic_complexity += code.count(f' {keyword} ')
        
        metrics['cyclomatic_complexity'] = cyclomatic_complexity
        
        if metrics['lines_of_code'] > 500:
            warnings.append(
                f"File too long ({metrics['lines_of_code']} lines), consider splitting"
            )
        
        if cyclomatic_complexity > 10:
            warnings.append(
                f"High complexity ({cyclomatic_complexity}), consider refactoring"
            )
        
        return warnings, metrics
    
    async def _check_imports(
        self, 
        code: str, 
        language: str
    ) -> List[str]:
        """
        检查导入规范
        
        Args:
            code: 源代码
            language: 编程语言
            
        Returns:
            警告列表
        """
        warnings = []
        
        if language == "python":
            # 检查是否使用了通配符导入
            if 'import *' in code:
                warnings.append("Wildcard import (import *) is not recommended")
            
            # 检查未使用的导入（简化检查）
            import_pattern = r'^(?:from\s+\S+\s+)?import\s+(\S+)'
            imports = re.findall(import_pattern, code, re.MULTILINE)
            
            for imp in imports:
                # 移除 'as' 别名部分
                module = imp.split(' as ')[0].strip()
                # 简单检查：如果导入的模块名不在代码中（除了导入行）
                # 这是一个非常简化的检查
                pass
        
        return warnings
    
    def get_quality_score(self, result: ValidationResult) -> float:
        """
        计算代码质量分数
        
        Args:
            result: 验证结果
            
        Returns:
            质量分数 (0-100)
        """
        score = 100.0
        
        # 错误扣分较多
        score -= len(result.errors) * 20
        
        # 警告扣分较少
        score -= len(result.warnings) * 5
        
        # 确保分数在 0-100 之间
        return max(0.0, min(100.0, score))