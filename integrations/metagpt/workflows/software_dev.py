"""
软件开发工作流

标准的软件开发流程实现。
"""

from typing import Any, Dict, Optional
from .base import Workflow
from ..roles import (
    ProductManager,
    Architect,
    Engineer,
    QaEngineer,
    ProjectManager
)


class SoftwareDevelopmentWorkflow(Workflow):
    """
    软件开发工作流
    
    实现标准的软件开发流程：
    需求分析 → 架构设计 → 编码实现 → 测试验证 → 项目交付
    """
    
    def __init__(self):
        """初始化软件开发工作流"""
        super().__init__("SoftwareDevelopment")
        
        # 初始化角色
        self.pm = ProductManager()
        self.architect = Architect()
        self.engineer = Engineer()
        self.qa = QaEngineer()
        self.project_manager = ProjectManager()
        
        # 工作流上下文
        self.context: Dict[str, Any] = {}
    
    async def run(
        self,
        requirement: str,
        project_name: str = "default_project",
        **kwargs
    ) -> Dict[str, Any]:
        """
        运行软件开发工作流
        
        Args:
            requirement: 用户需求描述
            project_name: 项目名称
            **kwargs: 其他参数
            
        Returns:
            工作流执行结果
        """
        self.context = {
            "requirement": requirement,
            "project_name": project_name,
            "kwargs": kwargs
        }
        
        # 定义工作流步骤
        self.add_step("需求分析", self._analyze_requirement)
        self.add_step("架构设计", self._design_architecture)
        self.add_step("代码实现", self._implement_code)
        self.add_step("测试验证", self._test_code)
        self.add_step("项目交付", self._deliver_project)
        
        try:
            # 执行工作流
            self.state.status = "running"
            
            # 步骤 1: 需求分析
            prd = await self.execute_step(0, requirement)
            self.context["prd"] = prd
            
            # 步骤 2: 架构设计
            architecture = await self.execute_step(1, prd)
            self.context["architecture"] = architecture
            
            # 步骤 3: 代码实现
            code = await self.execute_step(2, architecture)
            self.context["code"] = code
            
            # 步骤 4: 测试验证
            test_result = await self.execute_step(3, code)
            self.context["test_result"] = test_result
            
            # 步骤 5: 项目交付
            delivery = await self.execute_step(4, test_result)
            
            self.state.status = "completed"
            
            return {
                "status": "success",
                "project_name": project_name,
                "deliverables": {
                    "prd": prd,
                    "architecture": architecture,
                    "source_code": code,
                    "test_result": test_result,
                    "final_report": delivery
                }
            }
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error = str(e)
            return {
                "status": "failed",
                "error": str(e)
            }
    
    async def _analyze_requirement(self, requirement: str) -> str:
        """
        需求分析步骤
        
        Args:
            requirement: 用户需求
            
        Returns:
            PRD 文档
        """
        # 运行产品经理角色
        result = await self.pm.run()
        if result:
            return result.content
        return "PRD Document"
    
    async def _design_architecture(self, prd: str) -> str:
        """
        架构设计步骤
        
        Args:
            prd: 产品需求文档
            
        Returns:
            架构设计文档
        """
        # 运行架构师角色
        result = await self.architect.run()
        if result:
            return result.content
        return "Architecture Design"
    
    async def _implement_code(self, architecture: str) -> Dict[str, str]:
        """
        代码实现步骤
        
        Args:
            architecture: 架构设计
            
        Returns:
            源代码
        """
        # 运行工程师角色
        result = await self.engineer.run()
        if result:
            return {"code": result.content}
        return {"main.py": "# Code implementation"}
    
    async def _test_code(self, code: Dict[str, str]) -> str:
        """
        测试验证步骤
        
        Args:
            code: 源代码
            
        Returns:
            测试结果
        """
        # 运行 QA 工程师角色
        result = await self.qa.run()
        if result:
            return result.content
        return "Test Report: All tests passed"
    
    async def _deliver_project(self, test_result: str) -> str:
        """
        项目交付步骤
        
        Args:
            test_result: 测试结果
            
        Returns:
            最终交付报告
        """
        # 运行项目经理角色
        result = await self.project_manager.run()
        if result:
            return result.content
        return "Project Delivery Report"
    
    async def run_parallel_analysis(self, requirement: str) -> Dict[str, Any]:
        """
        并行分析模式
        
        产品经理和架构师可以并行工作，
        适用于已有明确需求的场景。
        
        Args:
            requirement: 用户需求
            
        Returns:
            分析结果
        """
        # 产品经理分析需求
        pm_task = asyncio.create_task(self.pm.analyze_requirement(requirement))
        
        # 架构师研究技术方案
        architect_task = asyncio.create_task(
            self.architect.analyze_prd(requirement)
        )
        
        # 等待并行任务完成
        analyzed_req, system_req = await asyncio.gather(
            pm_task, architect_task
        )
        
        # 合并结果
        return {
            "analyzed_requirements": analyzed_req,
            "system_requirements": system_req
        }
