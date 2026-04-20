"""
SWE-agent Main Engine - 核心引擎
整合所有模块的主引擎
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# 导入子模块
from ..github import IssueHandler, PRManager
from ..issues import IssueClassifier, BugDetector
from ..pr import PRCreator, CodeReviewer

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed
from openclaw.memory import memory_store

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent 状态"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING_REVIEW = "waiting_review"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """任务结果"""
    success: bool
    task_type: str
    data: Dict[str, Any]
    message: str
    timestamp: str


class SWEAgent:
    """
    SWE-agent 主引擎
    
    功能:
    - Issue 处理流程
    - PR 创建和管理
    - Bug 修复自动化
    - 代码审查
    - 状态管理
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 SWE-agent
        
        Args:
            config: 配置字典 (可选)
        """
        self.config = config or self._default_config()
        
        # 初始化子模块
        self.issue_handler = IssueHandler()
        self.pr_manager = PRManager()
        self.issue_classifier = IssueClassifier()
        self.bug_detector = BugDetector()
        self.pr_creator = PRCreator()
        self.code_reviewer = CodeReviewer()
        
        # 状态管理
        self.state = AgentState.IDLE
        self.current_task = None
        
        # 统计信息
        self.stats = {
            "issues_processed": 0,
            "prs_created": 0,
            "bugs_fixed": 0,
            "reviews_completed": 0
        }
        
        logger.info("SWE-Agent initialized")
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "auto_fix_enabled": False,
            "auto_merge_enabled": False,
            "require_review": True,
            "max_iterations": 10,
            "timeout": 300
        }
    
    def handle_issue(
        self,
        repo: str,
        issue_number: int,
        auto_fix: bool = False,
        create_pr: bool = True
    ) -> TaskResult:
        """
        处理 GitHub Issue
        
        Args:
            repo: 仓库名 (owner/repo)
            issue_number: Issue 编号
            auto_fix: 是否自动修复
            create_pr: 是否创建 PR
            
        Returns:
            TaskResult 任务结果
        """
        self.state = AgentState.PROCESSING
        self.current_task = f"issue_{repo}_{issue_number}"
        
        try:
            logger.info(f"Processing issue #{issue_number} in {repo}")
            
            # 1. 获取 Issue
            issue = self.issue_handler.fetch_issue(repo, issue_number)
            
            # 2. 分类 Issue
            analysis = self.issue_handler.classify_issue(issue)
            
            result_data = {
                "issue": {
                    "number": issue.number,
                    "title": issue.title,
                    "category": analysis.category.value,
                    "priority": analysis.priority.value
                },
                "analysis": {
                    "auto_fix_possible": analysis.auto_fix_possible,
                    "suggested_fix": analysis.fix_suggestion
                }
            }
            
            # 3. 如果是 Bug 且可以自动修复
            if auto_fix and analysis.category.value == "bug" and analysis.auto_fix_possible:
                fix_result = self._attempt_bug_fix(repo, issue, analysis)
                result_data["fix"] = fix_result
                
                # 4. 创建 PR
                if create_pr and fix_result.get("success"):
                    pr_result = self._create_fix_pr(repo, issue_number, fix_result)
                    result_data["pr"] = pr_result
            
            # 5. 自动标签和分配
            if self.config.get("auto_label", True):
                self.issue_handler.auto_label(repo, issue_number, analysis.suggested_labels)
            
            if self.config.get("auto_assign", True) and analysis.suggested_assignees:
                self.issue_handler.auto_assign(repo, issue_number, analysis.suggested_assignees)
            
            self.state = AgentState.COMPLETED
            self.stats["issues_processed"] += 1
            
            return TaskResult(
                success=True,
                task_type="issue_handling",
                data=result_data,
                message=f"Issue #{issue_number} 处理完成",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.state = AgentState.FAILED
            logger.error(f"Failed to handle issue #{issue_number}: {e}")
            
            return TaskResult(
                success=False,
                task_type="issue_handling",
                data={},
                message=f"Issue 处理失败: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
        
        finally:
            self.current_task = None
            self.state = AgentState.IDLE
    
    def _attempt_bug_fix(self, repo: str, issue: Any, analysis: Any) -> Dict:
        """尝试自动修复 Bug"""
        logger.info(f"Attempting to fix bug in {repo}")
        
        try:
            # 1. 检测 Bug 详情
            bug_info = self.bug_detector.detect_bug(issue.title, issue.body)
            
            # 2. 生成修复方案
            fix_prompt = f"""为以下 Bug 生成修复方案:

仓库: {repo}
Issue: {issue.title}

Bug 信息:
- 类型: {bug_info.bug_type.value}
- 严重程度: {bug_info.severity.value}
- 错误消息: {bug_info.error_message}

{analysis.fix_suggestion}

请提供:
1. 需要修改的文件列表
2. 修改内容
3. 测试用例

以 JSON 格式返回。"""
            
            fix_response = ask_local_ai_routed(
                prompt=fix_prompt,
                mode="claude_only"
            )
            
            # 解析修复方案
            fix_plan = self._parse_fix_response(fix_response)
            
            # 3. 应用修复 (实际实现需要 Git 操作)
            # 这里返回修复计划
            return {
                "success": True,
                "bug_type": bug_info.bug_type.value,
                "fix_plan": fix_plan,
                "files_changed": fix_plan.get("files", [])
            }
            
        except Exception as e:
            logger.error(f"Bug fix attempt failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_fix_response(self, response: str) -> Dict:
        """解析修复响应"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception:
            return {}
    
    def _create_fix_pr(self, repo: str, issue_number: int, fix_result: Dict) -> Dict:
        """创建修复 PR"""
        try:
            pr_data = self.pr_creator.create_from_fix(
                repo=repo,
                issue_number=issue_number,
                files_changed=fix_result.get("files_changed", []),
                commit_message=f"Fix: Issue #{issue_number}"
            )
            
            # 实际创建 PR (通过 PRManager)
            # pr = self.pr_manager.create_pr(**pr_data)
            
            self.stats["prs_created"] += 1
            self.stats["bugs_fixed"] += 1
            
            return {
                "success": True,
                "pr_url": f"https://github.com/{repo}/pull/TODO",
                "branch": pr_data["head"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create PR: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def review_pr(
        self,
        repo: str,
        pr_number: int,
        check_security: bool = True,
        check_quality: bool = True,
        check_performance: bool = True
    ) -> TaskResult:
        """
        审查 Pull Request
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            check_security: 是否检查安全
            check_quality: 是否检查质量
            check_performance: 是否检查性能
            
        Returns:
            TaskResult 审查结果
        """
        self.state = AgentState.PROCESSING
        
        try:
            logger.info(f"Reviewing PR #{pr_number} in {repo}")
            
            # 1. 获取 PR 信息
            pr = self.pr_manager.get_pr(repo, pr_number)
            
            # 2. 获取代码变更 (简化实现)
            # 实际应该从 GitHub API 获取
            code_changes = {
                "file1.py": "# Example code change\nprint('hello')"
            }
            
            # 3. 执行审查
            review_result = self.code_reviewer.review_pr(
                repo=repo,
                pr_number=pr_number,
                code_changes=code_changes,
                check_security=check_security,
                check_quality=check_quality,
                check_performance=check_performance
            )
            
            self.state = AgentState.COMPLETED
            self.stats["reviews_completed"] += 1
            
            return TaskResult(
                success=True,
                task_type="pr_review",
                data={
                    "overall_score": review_result.overall_score,
                    "security_score": review_result.security_score,
                    "quality_score": review_result.quality_score,
                    "performance_score": review_result.performance_score,
                    "approve": review_result.approve,
                    "comments_count": len(review_result.comments),
                    "summary": review_result.summary,
                    "recommendations": review_result.recommendations[:5]
                },
                message=f"PR #{pr_number} 审查完成，评分: {review_result.overall_score}/10",
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            self.state = AgentState.FAILED
            logger.error(f"Failed to review PR: {e}")
            
            return TaskResult(
                success=False,
                task_type="pr_review",
                data={},
                message=f"PR 审查失败: {str(e)}",
                timestamp=datetime.now().isoformat()
            )
        
        finally:
            self.state = AgentState.IDLE
    
    def get_status(self) -> Dict:
        """获取 Agent 状态"""
        return {
            "state": self.state.value,
            "current_task": self.current_task,
            "stats": self.stats,
            "config": self.config
        }
    
    def batch_process_issues(
        self,
        repo: str,
        issue_numbers: List[int],
        auto_fix: bool = False
    ) -> List[TaskResult]:
        """
        批量处理 Issues
        
        Args:
            repo: 仓库名
            issue_numbers: Issue 编号列表
            auto_fix: 是否自动修复
            
        Returns:
            任务结果列表
        """
        results = []
        
        for issue_number in issue_numbers:
            result = self.handle_issue(repo, issue_number, auto_fix=auto_fix)
            results.append(result)
        
        return results


# 导出
__all__ = [
    "SWEAgent",
    "AgentState",
    "TaskResult"
]
