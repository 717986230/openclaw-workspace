"""
GitHub Issue Handler - SWE-agent 集成
处理 GitHub Issues 的核心模块
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from datetime import datetime

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed
from openclaw.memory import memory_store

logger = logging.getLogger(__name__)


class IssueCategory(Enum):
    """Issue 分类"""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"
    QUESTION = "question"
    UNKNOWN = "unknown"


class IssuePriority(Enum):
    """Issue 优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class IssueAnalysis:
    """Issue 分析结果"""
    category: IssueCategory
    priority: IssuePriority
    confidence: float
    summary: str
    suggested_labels: List[str]
    suggested_assignees: List[str]
    estimated_effort: str  # hours/days
    related_files: List[str]
    dependencies: List[str]
    auto_fix_possible: bool
    fix_suggestion: Optional[str] = None


@dataclass
class Issue:
    """GitHub Issue 数据结构"""
    number: int
    title: str
    body: str
    labels: List[str]
    assignees: List[str]
    state: str
    created_at: datetime
    updated_at: datetime
    repository: str
    url: str


class IssueHandler:
    """
    GitHub Issue 处理器
    
    功能:
    - Issue 自动分类
    - 优先级评估
    - 自动分配
    - 修复建议生成
    - 与 OpenClaw Memory 集成
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        初始化 Issue 处理器
        
        Args:
            github_token: GitHub API token (可选，默认从环境变量读取)
        """
        self.github_token = github_token or self._get_github_token()
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info("IssueHandler initialized")
    
    def _get_github_token(self) -> str:
        """从环境变量获取 GitHub token"""
        import os
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        return token
    
    def fetch_issue(self, repo: str, issue_number: int) -> Issue:
        """
        获取 GitHub Issue 详情
        
        Args:
            repo: 仓库名 (格式: owner/repo)
            issue_number: Issue 编号
            
        Returns:
            Issue 对象
        """
        url = f"{self.api_base}/repos/{repo}/issues/{issue_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            issue = Issue(
                number=data["number"],
                title=data["title"],
                body=data.get("body", ""),
                labels=[label["name"] for label in data.get("labels", [])],
                assignees=[a["login"] for a in data.get("assignees", [])],
                state=data["state"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                updated_at=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00")),
                repository=repo,
                url=data["html_url"]
            )
            
            logger.info(f"Fetched issue #{issue_number} from {repo}")
            return issue
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch issue #{issue_number}: {e}")
            raise
    
    def classify_issue(self, issue: Issue) -> IssueAnalysis:
        """
        使用 LLM 分类 Issue
        
        Args:
            issue: Issue 对象
            
        Returns:
            IssueAnalysis 分析结果
        """
        prompt = f"""分析以下 GitHub Issue 并分类:

标题: {issue.title}

内容:
{issue.body}

请提供:
1. Issue 类型 (bug/feature/improvement/documentation/question)
2. 优先级 (critical/high/medium/low)
3. 简要总结 (1-2句话)
4. 建议的标签
5. 预估工作量
6. 是否可以自动修复
7. 如果可以自动修复，提供修复建议

以 JSON 格式返回结果。"""
        
        try:
            # 使用 OpenClaw LLM 路由
            response = ask_local_ai_routed(
                prompt=prompt,
                mode="claude_only"
            )
            
            # 解析 LLM 响应
            analysis_data = self._parse_llm_response(response)
            
            analysis = IssueAnalysis(
                category=IssueCategory(analysis_data.get("type", "unknown")),
                priority=IssuePriority(analysis_data.get("priority", "medium")),
                confidence=analysis_data.get("confidence", 0.8),
                summary=analysis_data.get("summary", ""),
                suggested_labels=analysis_data.get("labels", []),
                suggested_assignees=analysis_data.get("assignees", []),
                estimated_effort=analysis_data.get("effort", "unknown"),
                related_files=analysis_data.get("files", []),
                dependencies=analysis_data.get("dependencies", []),
                auto_fix_possible=analysis_data.get("auto_fix", False),
                fix_suggestion=analysis_data.get("fix_suggestion")
            )
            
            # 存储到 Memory
            self._store_analysis(issue, analysis)
            
            logger.info(f"Classified issue #{issue.number} as {analysis.category.value}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to classify issue: {e}")
            # 返回默认分析
            return IssueAnalysis(
                category=IssueCategory.UNKNOWN,
                priority=IssuePriority.MEDIUM,
                confidence=0.0,
                summary="自动分类失败",
                suggested_labels=[],
                suggested_assignees=[],
                estimated_effort="unknown",
                related_files=[],
                dependencies=[],
                auto_fix_possible=False
            )
    
    def _parse_llm_response(self, response: str) -> Dict:
        """解析 LLM 返回的 JSON"""
        try:
            # 尝试提取 JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON")
            return {}
    
    def _store_analysis(self, issue: Issue, analysis: IssueAnalysis):
        """存储分析结果到 OpenClaw Memory"""
        try:
            memory_store.store(
                key=f"github_issue:{issue.repository}:{issue.number}",
                value={
                    "issue": asdict(issue),
                    "analysis": asdict(analysis),
                    "timestamp": datetime.now().isoformat()
                },
                metadata={
                    "type": "issue_analysis",
                    "repo": issue.repository,
                    "issue_number": issue.number
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store analysis to memory: {e}")
    
    def auto_label(self, repo: str, issue_number: int, labels: List[str]) -> bool:
        """
        自动添加标签到 Issue
        
        Args:
            repo: 仓库名
            issue_number: Issue 编号
            labels: 标签列表
            
        Returns:
            是否成功
        """
        url = f"{self.api_base}/repos/{repo}/issues/{issue_number}/labels"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"labels": labels}
            )
            response.raise_for_status()
            
            logger.info(f"Added labels {labels} to issue #{issue_number}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to add labels: {e}")
            return False
    
    def auto_assign(self, repo: str, issue_number: int, assignees: List[str]) -> bool:
        """
        自动分配 Issue
        
        Args:
            repo: 仓库名
            issue_number: Issue 编号
            assignees: 分配对象列表
            
        Returns:
            是否成功
        """
        url = f"{self.api_base}/repos/{repo}/issues/{issue_number}/assignees"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"assignees": assignees}
            )
            response.raise_for_status()
            
            logger.info(f"Assigned issue #{issue_number} to {assignees}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to assign issue: {e}")
            return False
    
    def process_issue(self, repo: str, issue_number: int, auto_apply: bool = False) -> IssueAnalysis:
        """
        完整处理一个 Issue
        
        Args:
            repo: 仓库名
            issue_number: Issue 编号
            auto_apply: 是否自动应用标签和分配
            
        Returns:
            IssueAnalysis 分析结果
        """
        # 1. 获取 Issue
        issue = self.fetch_issue(repo, issue_number)
        
        # 2. 分类分析
        analysis = self.classify_issue(issue)
        
        # 3. 自动应用 (可选)
        if auto_apply:
            if analysis.suggested_labels:
                self.auto_label(repo, issue_number, analysis.suggested_labels)
            
            if analysis.suggested_assignees:
                self.auto_assign(repo, issue_number, analysis.suggested_assignees)
        
        logger.info(f"Processed issue #{issue_number}: {analysis.category.value}")
        return analysis
    
    def get_related_issues(self, repo: str, issue: Issue, limit: int = 5) -> List[Issue]:
        """
        获取相关的 Issues
        
        Args:
            repo: 仓库名
            issue: 当前 Issue
            limit: 返回数量限制
            
        Returns:
            相关 Issue 列表
        """
        # 从 Memory 中查找相似 Issue
        try:
            similar = memory_store.search(
                query=f"{issue.title} {issue.body}",
                filters={"type": "issue_analysis", "repo": repo},
                limit=limit
            )
            
            related_issues = []
            for item in similar:
                # 获取完整 Issue 数据
                related_issue = self.fetch_issue(repo, item["value"]["issue"]["number"])
                related_issues.append(related_issue)
            
            return related_issues
            
        except Exception as e:
            logger.warning(f"Failed to get related issues: {e}")
            return []


# 导出
__all__ = [
    "IssueHandler",
    "Issue",
    "IssueAnalysis",
    "IssueCategory",
    "IssuePriority"
]
