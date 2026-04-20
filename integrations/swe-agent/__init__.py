"""
SWE-agent - OpenClaw Integration
Software Engineering Agent for automated Issue handling and PR management
"""

__version__ = "1.0.0"
__author__ = "OpenClaw Team"
__description__ = "AI-powered Software Engineering Agent"

# Core imports
from .core.agent import SWEAgent, AgentState, TaskResult

# GitHub integration
from .github import (
    IssueHandler,
    Issue,
    IssueAnalysis,
    IssueCategory,
    IssuePriority,
    PRManager,
    PullRequest,
    PRStatus,
    MergeStrategy
)

# Issues module
from .issues import (
    IssueClassifier,
    ClassificationResult,
    BugDetector,
    BugInfo,
    BugSeverity,
    BugType
)

# PR module
from .pr import (
    PRCreator,
    FileChange,
    PRTemplate,
    CodeReviewer,
    CodeReviewResult,
    ReviewComment,
    ReviewSeverity
)

__all__ = [
    # Core
    "SWEAgent",
    "AgentState",
    "TaskResult",
    
    # GitHub
    "IssueHandler",
    "Issue",
    "IssueAnalysis",
    "IssueCategory",
    "IssuePriority",
    "PRManager",
    "PullRequest",
    "PRStatus",
    "MergeStrategy",
    
    # Issues
    "IssueClassifier",
    "ClassificationResult",
    "BugDetector",
    "BugInfo",
    "BugSeverity",
    "BugType",
    
    # PR
    "PRCreator",
    "FileChange",
    "PRTemplate",
    "CodeReviewer",
    "CodeReviewResult",
    "ReviewComment",
    "ReviewSeverity"
]


def create_agent(config: dict = None) -> SWEAgent:
    """
    创建 SWE-agent 实例的便捷函数
    
    Args:
        config: 配置字典 (可选)
        
    Returns:
        SWEAgent 实例
    """
    return SWEAgent(config=config)


def handle_issue(repo: str, issue_number: int, **kwargs) -> TaskResult:
    """
    处理 Issue 的便捷函数
    
    Args:
        repo: 仓库名 (owner/repo)
        issue_number: Issue 编号
        **kwargs: 其他参数
        
    Returns:
        TaskResult 处理结果
    """
    agent = create_agent()
    return agent.handle_issue(repo, issue_number, **kwargs)


def review_pr(repo: str, pr_number: int, **kwargs) -> TaskResult:
    """
    审查 PR 的便捷函数
    
    Args:
        repo: 仓库名
        pr_number: PR 编号
        **kwargs: 其他参数
        
    Returns:
        TaskResult 审查结果
    """
    agent = create_agent()
    return agent.review_pr(repo, pr_number, **kwargs)
