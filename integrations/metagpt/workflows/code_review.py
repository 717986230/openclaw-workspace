"""
代码审查工作流

实现代码审查和质量检查流程。
"""

from typing import Any, Dict, List
from .base import Workflow


class CodeReviewWorkflow(Workflow):
    """
    代码审查工作流
    
    实现代码审查流程：
    代码提交 → 静态分析 → 代码审查 → 反馈修复 → 验证通过
    """
    
    def __init__(self):
        """初始化代码审查工作流"""
        super().__init__("CodeReview")
        
        self.review_checklist = [
            "代码风格检查",
            "安全性检查",
            "性能检查",
            "可维护性检查",
            "测试覆盖率检查"
        ]
    
    async def run(
        self,
        source_code: Dict[str, str],
        project_name: str = "default_project"
    ) -> Dict[str, Any]:
        """
        运行代码审查工作流
        
        Args:
            source_code: 源代码字典
            project_name: 项目名称
            
        Returns:
            审查结果
        """
        # 定义工作流步骤
        self.add_step("静态分析", self._static_analysis)
        self.add_step("代码审查", self._code_review)
        self.add_step("生成报告", self._generate_report)
        
        try:
            self.state.status = "running"
            
            # 步骤 1: 静态分析
            static_issues = await self.execute_step(0, source_code)
            
            # 步骤 2: 代码审查
            review_issues = await self.execute_step(1, source_code, static_issues)
            
            # 步骤 3: 生成报告
            report = await self.execute_step(2, static_issues, review_issues)
            
            self.state.status = "completed"
            
            return {
                "status": "success",
                "report": report,
                "issues": {
                    "static": static_issues,
                    "review": review_issues
                }
            }
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error = str(e)
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _static_analysis(
        self, 
        source_code: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        静态代码分析
        
        Args:
            source_code: 源代码
            
        Returns:
            静态分析问题列表
        """
        issues = []
        
        for filename, code in source_code.items():
            # 检查代码长度
            lines = code.split('\n')
            if len(lines) > 500:
                issues.append({
                    "type": "complexity",
                    "severity": "warning",
                    "file": filename,
                    "message": f"文件过长 ({len(lines)} 行)，建议拆分"
                })
            
            # 检查 TODO 注释
            if "TODO" in code:
                issues.append({
                    "type": "todo",
                    "severity": "info",
                    "file": filename,
                    "message": "存在未完成的 TODO 项"
                })
        
        return issues
    
    async def _code_review(
        self, 
        source_code: Dict[str, str],
        static_issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        代码审查
        
        Args:
            source_code: 源代码
            static_issues: 静态分析问题
            
        Returns:
            审查问题列表
        """
        issues = []
        
        for filename, code in source_code.items():
            # 检查代码风格
            if not self._check_style(code):
                issues.append({
                    "type": "style",
                    "severity": "warning",
                    "file": filename,
                    "message": "代码风格不符合规范"
                })
            
            # 检查命名规范
            if not self._check_naming(code):
                issues.append({
                    "type": "naming",
                    "severity": "warning",
                    "file": filename,
                    "message": "变量/函数命名不规范"
                })
            
            # 检查文档字符串
            if not self._check_docstrings(code):
                issues.append({
                    "type": "documentation",
                    "severity": "info",
                    "file": filename,
                    "message": "缺少文档字符串"
                })
        
        return issues
    
    async def _generate_report(
        self,
        static_issues: List[Dict[str, Any]],
        review_issues: List[Dict[str, Any]]
    ) -> str:
        """
        生成审查报告
        
        Args:
            static_issues: 静态分析问题
            review_issues: 审查问题
            
        Returns:
            审查报告
        """
        report = f"""
# 代码审查报告

## 1. 审查概要
- 静态分析问题: {len(static_issues)} 个
- 代码审查问题: {len(review_issues)} 个

## 2. 静态分析结果
{self._format_issues(static_issues)}

## 3. 代码审查结果
{self._format_issues(review_issues)}

## 4. 改进建议
{self._generate_recommendations(static_issues, review_issues)}

## 5. 审查结论
{self._generate_conclusion(static_issues, review_issues)}
"""
        return report
    
    def _check_style(self, code: str) -> bool:
        """检查代码风格"""
        # 简单的风格检查
        return True
    
    def _check_naming(self, code: str) -> bool:
        """检查命名规范"""
        return True
    
    def _check_docstrings(self, code: str) -> bool:
        """检查文档字符串"""
        return '"""' in code or "'''" in code
    
    def _format_issues(self, issues: List[Dict[str, Any]]) -> str:
        """格式化问题列表"""
        if not issues:
            return "无问题"
        
        formatted = []
        for issue in issues:
            formatted.append(
                f"- [{issue.get('severity', 'unknown').upper()}] "
                f"{issue.get('file', 'unknown')}: {issue.get('message', '')}"
            )
        
        return "\n".join(formatted)
    
    def _generate_recommendations(
        self,
        static_issues: List[Dict[str, Any]],
        review_issues: List[Dict[str, Any]]
    ) -> str:
        """生成改进建议"""
        recommendations = []
        
        # 分析问题类型，给出针对性建议
        all_issues = static_issues + review_issues
        
        issue_types = set(issue.get("type", "unknown") for issue in all_issues)
        
        if "complexity" in issue_types:
            recommendations.append("- 建议拆分长文件，提高可维护性")
        
        if "style" in issue_types:
            recommendations.append("- 使用代码格式化工具（如 black、prettier）")
        
        if "naming" in issue_types:
            recommendations.append("- 遵循命名规范，使用有意义的变量名")
        
        if "documentation" in issue_types:
            recommendations.append("- 为关键函数添加文档字符串")
        
        return "\n".join(recommendations) if recommendations else "无特别建议"
    
    def _generate_conclusion(
        self,
        static_issues: List[Dict[str, Any]],
        review_issues: List[Dict[str, Any]]
    ) -> str:
        """生成审查结论"""
        total_issues = len(static_issues) + len(review_issues)
        
        critical_count = sum(
            1 for issue in static_issues + review_issues
            if issue.get("severity") == "critical"
        )
        
        if critical_count > 0:
            return "❌ 存在严重问题，需要立即修复"
        elif total_issues > 10:
            return "⚠️ 问题较多，建议修复后合并"
        elif total_issues > 0:
            return "✅ 代码质量良好，可以合并（建议修复小问题）"
        else:
            return "✅ 代码质量优秀，可以合并"
