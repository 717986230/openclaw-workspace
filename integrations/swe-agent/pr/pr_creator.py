"""
PR Creator - SWE-agent 集成
自动创建 Pull Requests
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed
from openclaw.memory import memory_store

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """文件变更"""
    path: str
    change_type: str  # added, modified, deleted
    additions: int
    deletions: int
    content: Optional[str] = None


@dataclass
class PRTemplate:
    """PR 模板"""
    title_template: str
    body_template: str
    checklist: List[str]


class PRCreator:
    """
    Pull Request 创建器
    
    功能:
    - 从 Bug 修复生成 PR
    - 自动生成 PR 描述
    - 模板管理
    - 与 Issue 关联
    """
    
    def __init__(self):
        """初始化 PR 创建器"""
        self.templates = self._load_templates()
        logger.info("PRCreator initialized")
    
    def _load_templates(self) -> Dict[str, PRTemplate]:
        """加载 PR 模板"""
        return {
            "bug_fix": PRTemplate(
                title_template="Fix: {description}",
                body_template="""## 修复描述
{description}

## 变更内容
{changes}

## 测试
{test_plan}

Fixes #{issue_number}
""",
                checklist=[
                    "- [ ] 代码审查完成",
                    "- [ ] 单元测试通过",
                    "- [ ] 集成测试通过",
                    "- [ ] 文档已更新"
                ]
            ),
            "feature": PRTemplate(
                title_template="Feat: {description}",
                body_template="""## 功能描述
{description}

## 实现细节
{changes}

## 测试计划
{test_plan}

Closes #{issue_number}
""",
                checklist=[
                    "- [ ] 功能测试完成",
                    "- [ ] 性能测试通过",
                    "- [ ] 安全审查完成",
                    "- [ ] 文档已更新"
                ]
            ),
            "refactor": PRTemplate(
                title_template="Refactor: {description}",
                body_template="""## 重构描述
{description}

## 重构原因
{reason}

## 影响范围
{impact}

## 测试
{test_plan}
""",
                checklist=[
                    "- [ ] 重构后功能正常",
                    "- [ ] 性能未退化",
                    "- [ ] 测试覆盖率保持",
                    "- [ ] 代码审查完成"
                ]
            )
        }
    
    def create_from_fix(
        self,
        repo: str,
        issue_number: int,
        files_changed: List[str],
        commit_message: str,
        branch_name: Optional[str] = None,
        test_results: Optional[Dict] = None
    ) -> Dict:
        """
        从 Bug 修复创建 PR
        
        Args:
            repo: 仓库名
            issue_number: 关联的 Issue 编号
            files_changed: 变更的文件列表
            commit_message: 提交消息
            branch_name: 分支名 (可选)
            test_results: 测试结果 (可选)
            
        Returns:
            PR 创建结果
        """
        # 生成分支名
        if not branch_name:
            branch_name = self._generate_branch_name("fix", issue_number)
        
        # 获取文件变更详情
        file_changes = self._get_file_changes(files_changed)
        
        # 生成 PR 标题和描述
        title, body = self._generate_pr_content(
            template_type="bug_fix",
            description=commit_message,
            issue_number=issue_number,
            file_changes=file_changes,
            test_results=test_results
        )
        
        return {
            "repo": repo,
            "title": title,
            "body": body,
            "head": branch_name,
            "base": "main",
            "issue_number": issue_number,
            "files_changed": files_changed,
            "created_at": datetime.now().isoformat()
        }
    
    def _generate_branch_name(self, pr_type: str, issue_number: int) -> str:
        """生成分支名"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"{pr_type}/issue-{issue_number}-{timestamp}"
    
    def _get_file_changes(self, files: List[str]) -> List[FileChange]:
        """获取文件变更详情"""
        # 简化实现：只记录文件路径
        return [
            FileChange(
                path=file,
                change_type="modified",
                additions=0,
                deletions=0
            )
            for file in files
        ]
    
    def _generate_pr_content(
        self,
        template_type: str,
        description: str,
        issue_number: int,
        file_changes: List[FileChange],
        test_results: Optional[Dict] = None
    ) -> tuple:
        """
        生成 PR 标题和描述
        
        Args:
            template_type: 模板类型
            description: 描述
            issue_number: Issue 编号
            file_changes: 文件变更列表
            test_results: 测试结果
            
        Returns:
            (title, body) 元组
        """
        template = self.templates.get(template_type, self.templates["bug_fix"])
        
        # 生成标题
        title = template.title_template.format(
            description=description.split('\n')[0][:80]
        )
        
        # 生成变更内容
        changes_text = self._format_changes(file_changes)
        
        # 生成测试计划
        test_plan = self._generate_test_plan(test_results)
        
        # 生成 body
        body = template.body_template.format(
            description=description,
            changes=changes_text,
            test_plan=test_plan,
            issue_number=issue_number
        )
        
        # 添加 checklist
        body += "\n\n## Checklist\n" + "\n".join(template.checklist)
        
        return title, body
    
    def _format_changes(self, file_changes: List[FileChange]) -> str:
        """格式化变更内容"""
        if not file_changes:
            return "无文件变更"
        
        lines = []
        for change in file_changes:
            icon = {
                "added": "➕",
                "modified": "✏️",
                "deleted": "➖"
            }.get(change.change_type, "📄")
            
            lines.append(f"{icon} {change.path}")
            if change.additions > 0 or change.deletions > 0:
                lines.append(f"   +{change.additions} -{change.deletions}")
        
        return "\n".join(lines)
    
    def _generate_test_plan(self, test_results: Optional[Dict]) -> str:
        """生成测试计划"""
        if not test_results:
            return "- [ ] 手动测试待执行"
        
        lines = []
        
        if "unit_tests" in test_results:
            status = "✅" if test_results["unit_tests"].get("passed") else "❌"
            lines.append(f"{status} 单元测试: {test_results['unit_tests'].get('summary', 'N/A')}")
        
        if "integration_tests" in test_results:
            status = "✅" if test_results["integration_tests"].get("passed") else "❌"
            lines.append(f"{status} 集成测试: {test_results['integration_tests'].get('summary', 'N/A')}")
        
        return "\n".join(lines) if lines else "- [ ] 手动测试待执行"
    
    def create_from_feature(
        self,
        repo: str,
        issue_number: int,
        feature_description: str,
        files_changed: List[str],
        implementation_details: str
    ) -> Dict:
        """
        从功能开发创建 PR
        
        Args:
            repo: 仓库名
            issue_number: 关联的 Issue 编号
            feature_description: 功能描述
            files_changed: 变更的文件列表
            implementation_details: 实现细节
            
        Returns:
            PR 创建结果
        """
        branch_name = self._generate_branch_name("feat", issue_number)
        file_changes = self._get_file_changes(files_changed)
        
        title, body = self._generate_pr_content(
            template_type="feature",
            description=feature_description,
            issue_number=issue_number,
            file_changes=file_changes
        )
        
        # 添加实现细节
        body = body.replace("{changes}", f"{implementation_details}\n\n## 文件变更\n{self._format_changes(file_changes)}")
        
        return {
            "repo": repo,
            "title": title,
            "body": body,
            "head": branch_name,
            "base": "main",
            "issue_number": issue_number,
            "files_changed": files_changed,
            "created_at": datetime.now().isoformat()
        }
    
    def generate_ai_description(
        self,
        commit_messages: List[str],
        file_changes: List[str],
        issue_context: Optional[str] = None
    ) -> str:
        """
        使用 AI 生成 PR 描述
        
        Args:
            commit_messages: 提交消息列表
            file_changes: 文件变更列表
            issue_context: Issue 上下文 (可选)
            
        Returns:
            生成的 PR 描述
        """
        prompt = f"""根据以下信息生成一个专业的 Pull Request 描述:

提交消息:
{json.dumps(commit_messages, indent=2, ensure_ascii=False)}

文件变更:
{json.dumps(file_changes, indent=2, ensure_ascii=False)}

{f"关联 Issue: {issue_context}" if issue_context else ""}

请生成包含以下部分的描述:
1. 变更概述 (简短描述)
2. 详细变更 (列出主要变更)
3. 测试说明
4. 检查清单

使用 Markdown 格式，保持简洁专业。"""
        
        try:
            response = ask_local_ai_routed(
                prompt=prompt,
                mode="claude_only"
            )
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate AI description: {e}")
            return self._generate_default_description(commit_messages, file_changes)
    
    def _generate_default_description(
        self,
        commit_messages: List[str],
        file_changes: List[str]
    ) -> str:
        """生成默认描述"""
        description = "## 变更概述\n\n"
        
        if commit_messages:
            description += "### 提交历史\n"
            for msg in commit_messages[:5]:
                description += f"- {msg}\n"
        
        if file_changes:
            description += "\n### 文件变更\n"
            for file in file_changes[:10]:
                description += f"- {file}\n"
        
        return description


# 导出
__all__ = [
    "PRCreator",
    "FileChange",
    "PRTemplate"
]
