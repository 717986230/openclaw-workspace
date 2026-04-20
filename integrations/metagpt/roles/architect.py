"""
架构师角色

负责系统架构设计、技术选型。
"""

from typing import Any, Dict, List, Optional
from .base import Role, Message, Action


class Architect(Role):
    """
    架构师角色
    
    职责：
    - 设计系统架构
    - 技术选型
    - 定义系统模块和接口
    - 评估技术风险
    """
    
    def __init__(self):
        """初始化架构师角色"""
        super().__init__(
            name="Architect",
            profile="负责系统架构设计和技术选型，确保系统的可扩展性、可靠性和性能",
            goal="设计满足需求的高质量系统架构",
            constraints=[
                "架构设计必须满足 PRD 中定义的功能需求",
                "必须考虑系统的可扩展性和可维护性",
                "技术选型需要权衡成本和收益"
            ]
        )
        
        # 定义架构师的动作
        self.add_action(Action(
            name="analyze_prd",
            description="分析产品需求文档，理解系统需求",
            inputs=["prd_document"],
            outputs=["system_requirements"]
        ))
        
        self.add_action(Action(
            name="design_architecture",
            description="设计系统架构",
            inputs=["system_requirements"],
            outputs=["architecture_design"]
        ))
        
        self.add_action(Action(
            name="select_tech_stack",
            description="技术选型",
            inputs=["architecture_design"],
            outputs=["tech_stack"]
        ))
    
    async def _observe(self) -> None:
        """观察环境"""
        pass
    
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        Returns:
            包含架构设计的消息
        """
        pending_messages = self.get_pending_messages()
        
        if not pending_messages:
            return None
        
        message = pending_messages[0]
        message.state = "processing"
        
        # 分析 PRD
        requirements = await self.analyze_prd(message.content)
        
        # 设计架构
        architecture = await self.design_architecture(requirements)
        
        # 技术选型
        tech_stack = await self.select_tech_stack(architecture)
        
        message.state = "completed"
        
        # 返回架构设计给工程师
        return Message(
            role=self.name,
            content=self._combine_output(architecture, tech_stack),
            cause_by="architecture_designed",
            send_to="Engineer"
        )
    
    async def analyze_prd(self, prd: str) -> Dict[str, Any]:
        """
        分析产品需求文档
        
        Args:
            prd: 产品需求文档内容
            
        Returns:
            系统需求分析结果
        """
        # 在实际实现中，这里会使用 LLM 分析 PRD
        requirements = {
            "functional_requirements": [],
            "non_functional_requirements": {
                "performance": {},
                "scalability": {},
                "security": {},
                "availability": {}
            },
            "constraints": [],
            "dependencies": []
        }
        
        return requirements
    
    async def design_architecture(
        self, 
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        设计系统架构
        
        Args:
            requirements: 系统需求
            
        Returns:
            架构设计文档
        """
        architecture = {
            "system_type": self._determine_system_type(requirements),
            "components": [],
            "modules": [],
            "interfaces": [],
            "data_flow": [],
            "deployment_architecture": {}
        }
        
        return architecture
    
    async def select_tech_stack(
        self, 
        architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        技术选型
        
        Args:
            architecture: 架构设计
            
        Returns:
            技术栈选择
        """
        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "infrastructure": [],
            "tools": [],
            "justifications": {}
        }
        
        return tech_stack
    
    def _determine_system_type(
        self, 
        requirements: Dict[str, Any]
    ) -> str:
        """
        确定系统类型
        
        Args:
            requirements: 系统需求
            
        Returns:
            系统类型（monolithic, microservice, serverless 等）
        """
        # 简单的决策逻辑
        # 在实际实现中，这里会有更复杂的决策逻辑
        return "monolithic"
    
    def _combine_output(
        self, 
        architecture: Dict[str, Any],
        tech_stack: Dict[str, Any]
    ) -> str:
        """
        合并架构设计和技术选型输出
        
        Args:
            architecture: 架构设计
            tech_stack: 技术栈
            
        Returns:
            合并后的文档
        """
        return f"""
# 系统架构设计文档

## 1. 架构概述
- 系统类型: {architecture.get('system_type', 'unknown')}
- 核心组件: {len(architecture.get('components', []))} 个

## 2. 系统组件
{self._format_components(architecture.get('components', []))}

## 3. 模块划分
{self._format_modules(architecture.get('modules', []))}

## 4. 接口定义
{self._format_interfaces(architecture.get('interfaces', []))}

## 5. 数据流
{self._format_data_flow(architecture.get('data_flow', []))}

## 6. 技术栈
{self._format_tech_stack(tech_stack)}

## 7. 部署架构
{self._format_deployment(architecture.get('deployment_architecture', {}))}
"""
    
    def _format_components(self, components: List[Dict]) -> str:
        """格式化组件列表"""
        if not components:
            return "待定义"
        return "\n".join(
            f"- {c.get('name', 'unnamed')}: {c.get('description', '')}" 
            for c in components
        )
    
    def _format_modules(self, modules: List[Dict]) -> str:
        """格式化模块列表"""
        if not modules:
            return "待定义"
        return "\n".join(
            f"- {m.get('name', 'unnamed')}" 
            for m in modules
        )
    
    def _format_interfaces(self, interfaces: List[Dict]) -> str:
        """格式化接口列表"""
        if not interfaces:
            return "待定义"
        return "\n".join(
            f"- {i.get('name', 'unnamed')}: {i.get('type', 'unknown')}" 
            for i in interfaces
        )
    
    def _format_data_flow(self, flows: List[Dict]) -> str:
        """格式化数据流"""
        if not flows:
            return "待定义"
        return "\n".join(
            f"- {f.get('from', 'unknown')} -> {f.get('to', 'unknown')}" 
            for f in flows
        )
    
    def _format_tech_stack(self, tech_stack: Dict[str, Any]) -> str:
        """格式化技术栈"""
        sections = []
        
        for key in ["languages", "frameworks", "databases", "infrastructure", "tools"]:
            items = tech_stack.get(key, [])
            if items:
                sections.append(f"### {key.capitalize()}\n" + "\n".join(f"- {item}" for item in items))
        
        return "\n\n".join(sections) if sections else "待定义"
    
    def _format_deployment(self, deployment: Dict[str, Any]) -> str:
        """格式化部署架构"""
        if not deployment:
            return "待定义"
        return str(deployment)
