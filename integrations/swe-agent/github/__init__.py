"""
GitHub 集成模块 - SWE-agent
"""

from .issue_handler import IssueHandler, Issue, IssueAnalysis, IssueCategory, IssuePriority
from .pr_manager import PRManager, PullRequest, PRStatus, MergeStrategy

__all__ = [
    "IssueHandler",
    "Issue",
    "IssueAnalysis",
    "IssueCategory",
    "IssuePriority",
    "PRManager",
    "PullRequest",
    "PRStatus",
    "MergeStrategy"
]
