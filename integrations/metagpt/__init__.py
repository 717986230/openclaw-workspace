"""
MetaGPT Integration for OpenClaw

将 MetaGPT 多智能体协作框架集成到 OpenClaw。

主要功能：
- 角色扮演：产品经理、架构师、工程师、QA、项目经理
- 工作流程：软件开发、代码审查、敏捷迭代
- 代码生成：模板化代码生成和验证
"""

from .roles import (
    ProductManager,
    Architect,
    Engineer,
    QaEngineer,
    ProjectManager,
)

from .workflows import (
    SoftwareDevelopmentWorkflow,
    CodeReviewWorkflow,
)

from .code_gen import (
    CodeGenerator,
    CodeValidator,
)

__version__ = "1.0.0"

__all__ = [
    # 角色
    "ProductManager",
    "Architect",
    "Engineer",
    "QaEngineer",
    "ProjectManager",
    
    # 工作流
    "SoftwareDevelopmentWorkflow",
    "CodeReviewWorkflow",
    
    # 代码生成
    "CodeGenerator",
    "CodeValidator",
]


def create_software_team():
    """
    创建软件开发团队
    
    快捷方法，创建一个包含所有角色的开发团队。
    
    Returns:
        包含所有角色的字典
    """
    return {
        "product_manager": ProductManager(),
        "architect": Architect(),
        "engineer": Engineer(),
        "qa_engineer": QaEngineer(),
        "project_manager": ProjectManager(),
    }


async def develop(requirement: str, project_name: str = "default_project"):
    """
    快捷开发方法
    
    使用标准工作流快速开发一个项目。
    
    Args:
        requirement: 需求描述
        project_name: 项目名称
        
    Returns:
        开发结果
    """
    workflow = SoftwareDevelopmentWorkflow()
    return await workflow.run(
        requirement=requirement,
        project_name=project_name
    )


async def review_code(source_code: dict, project_name: str = "default_project"):
    """
    快捷代码审查方法
    
    Args:
        source_code: 源代码字典 {文件名: 代码}
        project_name: 项目名称
        
    Returns:
        审查结果
    """
    workflow = CodeReviewWorkflow()
    return await workflow.run(
        source_code=source_code,
        project_name=project_name
    )
