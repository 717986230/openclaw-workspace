"""
GitHub Pull Request Manager - SWE-agent 集成
管理 Pull Requests 的创建、更新和合并
"""

import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import requests
from datetime import datetime

# OpenClaw 集成
from openclaw.tools import ask_local_ai_routed
from openclaw.memory import memory_store

logger = logging.getLogger(__name__)


class PRStatus(Enum):
    """PR 状态"""
    OPEN = "open"
    CLOSED = "closed"
    MERGED = "merged"
    DRAFT = "draft"


class MergeStrategy(Enum):
    """合并策略"""
    MERGE = "merge"
    SQUASH = "squash"
    REBASE = "rebase"


@dataclass
class PRReview:
    """PR 审查结果"""
    security_score: float
    quality_score: float
    performance_score: float
    suggestions: List[str]
    approve: bool
    comments: List[Dict]


@dataclass
class PullRequest:
    """GitHub Pull Request 数据结构"""
    number: int
    title: str
    body: str
    state: PRStatus
    head_branch: str
    base_branch: str
    author: str
    created_at: datetime
    repository: str
    url: str
    mergeable: Optional[bool] = None
    mergeable_state: Optional[str] = None


class PRManager:
    """
    GitHub Pull Request 管理器
    
    功能:
    - PR 创建和管理
    - 自动生成 PR 描述
    - 智能合并策略
    - 冲突检测和解决
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """初始化 PR 管理器"""
        self.github_token = github_token or self._get_github_token()
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info("PRManager initialized")
    
    def _get_github_token(self) -> str:
        """从环境变量获取 GitHub token"""
        import os
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        return token
    
    def create_pr(
        self,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: Optional[str] = None,
        draft: bool = False,
        issue_number: Optional[int] = None
    ) -> PullRequest:
        """
        创建 Pull Request
        
        Args:
            repo: 仓库名 (owner/repo)
            title: PR 标题
            head: 源分支
            base: 目标分支
            body: PR 描述 (可选)
            draft: 是否为草稿
            issue_number: 关联的 Issue 编号 (可选)
            
        Returns:
            PullRequest 对象
        """
        # 如果没有提供 body，自动生成
        if not body:
            body = self._generate_pr_description(repo, head, issue_number)
        
        url = f"{self.api_base}/repos/{repo}/pulls"
        
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "draft": draft
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            pr_data = response.json()
            
            pr = PullRequest(
                number=pr_data["number"],
                title=pr_data["title"],
                body=pr_data.get("body", ""),
                state=PRStatus.DRAFT if draft else PRStatus.OPEN,
                head_branch=pr_data["head"]["ref"],
                base_branch=pr_data["base"]["ref"],
                author=pr_data["user"]["login"],
                created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
                repository=repo,
                url=pr_data["html_url"]
            )
            
            # 关联 Issue
            if issue_number:
                self._link_issue(repo, pr.number, issue_number)
            
            # 存储到 Memory
            self._store_pr(pr)
            
            logger.info(f"Created PR #{pr.number} in {repo}")
            return pr
            
        except requests.RequestException as e:
            logger.error(f"Failed to create PR: {e}")
            raise
    
    def _generate_pr_description(
        self,
        repo: str,
        branch: str,
        issue_number: Optional[int] = None
    ) -> str:
        """
        使用 LLM 生成 PR 描述
        
        Args:
            repo: 仓库名
            branch: 分支名
            issue_number: 关联的 Issue
            
        Returns:
            PR 描述
        """
        # 获取分支的提交信息
        commits = self._get_branch_commits(repo, branch)
        
        # 获取文件变更
        files = self._get_branch_files(repo, branch)
        
        prompt = f"""根据以下信息生成一个专业的 Pull Request 描述:

分支: {branch}
仓库: {repo}

最近的提交:
{json.dumps(commits, indent=2)}

文件变更:
{json.dumps(files, indent=2)}

{"关联的 Issue: #" + str(issue_number) if issue_number else ""}

请生成包含以下部分的 PR 描述:
1. 变更概述
2. 详细描述
3. 测试说明
4. 检查清单

使用 Markdown 格式。"""
        
        try:
            response = ask_local_ai_routed(
                prompt=prompt,
                mode="claude_only"
            )
            return response
            
        except Exception as e:
            logger.warning(f"Failed to generate PR description: {e}")
            return self._generate_default_description(commits, files, issue_number)
    
    def _generate_default_description(
        self,
        commits: List[Dict],
        files: List[str],
        issue_number: Optional[int]
    ) -> str:
        """生成默认 PR 描述"""
        description = "## 变更概述\n\n"
        
        if commits:
            description += "### 提交信息\n"
            for commit in commits[:5]:
                description += f"- {commit.get('message', 'N/A')}\n"
        
        if files:
            description += "\n### 文件变更\n"
            for file in files[:10]:
                description += f"- {file}\n"
        
        if issue_number:
            description += f"\nFixes #{issue_number}\n"
        
        return description
    
    def _get_branch_commits(self, repo: str, branch: str) -> List[Dict]:
        """获取分支的提交历史"""
        url = f"{self.api_base}/repos/{repo}/commits?sha={branch}&per_page=10"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            commits = []
            for commit in response.json():
                commits.append({
                    "sha": commit["sha"],
                    "message": commit["commit"]["message"],
                    "author": commit["commit"]["author"]["name"]
                })
            
            return commits
            
        except requests.RequestException as e:
            logger.warning(f"Failed to get branch commits: {e}")
            return []
    
    def _get_branch_files(self, repo: str, branch: str) -> List[str]:
        """获取分支相对于主分支的文件变更"""
        # 简化实现：返回空列表
        # 实际实现需要使用 GitHub Compare API
        return []
    
    def _link_issue(self, repo: str, pr_number: int, issue_number: int):
        """关联 Issue 到 PR"""
        # 在 PR 描述中添加 Fixes #issue_number
        # 或者使用 GitHub API 的关联功能
        pass
    
    def _store_pr(self, pr: PullRequest):
        """存储 PR 到 Memory"""
        try:
            memory_store.store(
                key=f"github_pr:{pr.repository}:{pr.number}",
                value=asdict(pr),
                metadata={
                    "type": "pull_request",
                    "repo": pr.repository,
                    "pr_number": pr.number,
                    "state": pr.state.value
                }
            )
        except Exception as e:
            logger.warning(f"Failed to store PR to memory: {e}")
    
    def update_pr(
        self,
        repo: str,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[PRStatus] = None
    ) -> bool:
        """
        更新 Pull Request
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            title: 新标题 (可选)
            body: 新描述 (可选)
            state: 新状态 (可选)
            
        Returns:
            是否成功
        """
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_number}"
        
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state.value
        
        try:
            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            logger.info(f"Updated PR #{pr_number}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to update PR: {e}")
            return False
    
    def merge_pr(
        self,
        repo: str,
        pr_number: int,
        strategy: MergeStrategy = MergeStrategy.SQUASH,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None
    ) -> bool:
        """
        合并 Pull Request
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            strategy: 合并策略
            commit_title: 合并提交标题 (可选)
            commit_message: 合并提交信息 (可选)
            
        Returns:
            是否成功
        """
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_number}/merge"
        
        data = {
            "merge_method": strategy.value
        }
        
        if commit_title:
            data["commit_title"] = commit_title
        if commit_message:
            data["commit_message"] = commit_message
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if result.get("merged"):
                logger.info(f"Merged PR #{pr_number}")
                return True
            else:
                logger.warning(f"PR #{pr_number} not merged: {result.get('message')}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Failed to merge PR: {e}")
            return False
    
    def check_merge_conflicts(self, repo: str, pr_number: int) -> Dict:
        """
        检查合并冲突
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            
        Returns:
            冲突检查结果
        """
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            pr_data = response.json()
            
            return {
                "mergeable": pr_data.get("mergeable"),
                "mergeable_state": pr_data.get("mergeable_state"),
                "has_conflicts": pr_data.get("mergeable") is False,
                "message": self._get_mergeable_message(pr_data.get("mergeable_state"))
            }
            
        except requests.RequestException as e:
            logger.error(f"Failed to check merge conflicts: {e}")
            return {
                "mergeable": None,
                "has_conflicts": None,
                "message": f"检查失败: {str(e)}"
            }
    
    def _get_mergeable_message(self, state: Optional[str]) -> str:
        """获取合并状态说明"""
        messages = {
            "clean": "可以合并",
            "dirty": "存在合并冲突",
            "unstable": "CI 检查未通过",
            "blocked": "被阻塞",
            "behind": "分支落后于目标分支",
            "unknown": "合并状态未知"
        }
        return messages.get(state, "合并状态未知")
    
    def get_pr(self, repo: str, pr_number: int) -> PullRequest:
        """
        获取 Pull Request 详情
        
        Args:
            repo: 仓库名
            pr_number: PR 编号
            
        Returns:
            PullRequest 对象
        """
        url = f"{self.api_base}/repos/{repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            pr = PullRequest(
                number=data["number"],
                title=data["title"],
                body=data.get("body", ""),
                state=PRStatus(data["state"]),
                head_branch=data["head"]["ref"],
                base_branch=data["base"]["ref"],
                author=data["user"]["login"],
                created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                repository=repo,
                url=data["html_url"],
                mergeable=data.get("mergeable"),
                mergeable_state=data.get("mergeable_state")
            )
            
            return pr
            
        except requests.RequestException as e:
            logger.error(f"Failed to get PR: {e}")
            raise


# 导出
__all__ = [
    "PRManager",
    "PullRequest",
    "PRReview",
    "PRStatus",
    "MergeStrategy"
]
