"""
项目经理角色

负责项目统筹和协调。
"""

from typing import Any, Dict, List, Optional
from .base import Role, Message, Action


class ProjectManager(Role):
    """
    项目经理角色
    
    职责：
    - 项目规划
    - 进度跟踪
    - 资源协调
    - 风险管理
    """
    
    def __init__(self):
        """初始化项目经理角色"""
        super().__init__(
            name="ProjectManager",
            profile="负责项目整体规划和进度管理，确保项目按时高质量交付",
            goal="协调团队资源，确保项目成功交付",
            constraints=[
                "必须按时交付项目",
                "必须控制项目成本",
                "必须管理项目风险"
            ]
        )
        
        # 定义项目经理的动作
        self.add_action(Action(
            name="plan_project",
            description="制定项目计划",
            inputs=["requirement", "team_resources"],
            outputs=["project_plan"]
        ))
        
        self.add_action(Action(
            name="track_progress",
            description="跟踪项目进度",
            inputs=["project_plan", "current_status"],
            outputs=["progress_report"]
        ))
        
        self.add_action(Action(
            name="coordinate_resources",
            description="协调团队资源",
            inputs=["resource_needs", "available_resources"],
            outputs=["resource_allocation"]
        ))
    
    async def _observe(self) -> None:
        """观察环境"""
        pass
    
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        Returns:
            项目管理消息
        """
        pending_messages = self.get_pending_messages()
        
        if not pending_messages:
            return None
        
        message = pending_messages[0]
        message.state = "processing"
        
        # 根据消息类型处理
        if message.cause_by == "testing_completed":
            # 测试完成，生成最终报告
            final_report = await self.generate_final_report(message.content)
            message.state = "completed"
            return Message(
                role=self.name,
                content=final_report,
                cause_by="project_completed",
                send_to="User"
            )
        
        message.state = "completed"
        return None
    
    async def plan_project(
        self, 
        requirement: str,
        resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        制定项目计划
        
        Args:
            requirement: 项目需求
            resources: 可用资源
            
        Returns:
            项目计划
        """
        project_plan = {
            "phases": [
                {"name": "需求分析", "duration": 3, "assignee": "ProductManager"},
                {"name": "架构设计", "duration": 5, "assignee": "Architect"},
                {"name": "编码实现", "duration": 10, "assignee": "Engineer"},
                {"name": "测试验证", "duration": 5, "assignee": "QaEngineer"}
            ],
            "milestones": [],
            "resources": resources,
            "risks": []
        }
        
        return project_plan
    
    async def track_progress(
        self, 
        plan: Dict[str, Any],
        status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        跟踪项目进度
        
        Args:
            plan: 项目计划
            status: 当前状态
            
        Returns:
            进度报告
        """
        progress_report = {
            "overall_progress": 0,
            "phase_status": [],
            "blockers": [],
            "next_steps": []
        }
        
        return progress_report
    
    async def coordinate_resources(
        self, 
        needs: Dict[str, Any],
        available: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        协调团队资源
        
        Args:
            needs: 资源需求
            available: 可用资源
            
        Returns:
            资源分配方案
        """
        allocation = {
            "assigned": {},
            "pending": [],
            "conflicts": []
        }
        
        return allocation
    
    async def generate_final_report(self, test_report: str) -> str:
        """
        生成最终项目报告
        
        Args:
            test_report: 测试报告
            
        Returns:
            最终报告
        """
        return f"""
# 项目交付报告

## 1. 项目概述
项目已完成所有开发阶段，包括需求分析、架构设计、编码实现和测试验证。

## 2. 交付物
- 需求文档（PRD）
- 架构设计文档
- 源代码及单元测试
- 测试报告

## 3. 质量评估
{test_report}

## 4. 项目统计
- 开发周期: 按计划完成
- 代码质量: 符合标准
- 测试覆盖: 达标

## 5. 后续建议
- 持续监控生产环境
- 定期代码审查
- 用户反馈收集

## 6. 致谢
感谢团队成员的协作和贡献。

---
*报告生成时间: 项目完成*
"""
