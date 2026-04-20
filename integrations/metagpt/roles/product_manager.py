"""
产品经理角色

负责需求分析、编写 PRD（产品需求文档）。
"""

from typing import Any, Dict, List, Optional
from .base import Role, Message, Action


class ProductManager(Role):
    """
    产品经理角色
    
    职责：
    - 分析用户需求
    - 编写产品需求文档（PRD）
    - 定义产品功能优先级
    - 与团队沟通需求
    """
    
    def __init__(self):
        """初始化产品经理角色"""
        super().__init__(
            name="Product Manager",
            profile="负责需求分析和产品规划，编写详细的产品需求文档",
            goal="将模糊的用户需求转化为清晰、可执行的产品需求文档",
            constraints=[
                "需求文档必须包含完整的功能描述",
                "每个功能必须有明确的验收标准",
                "必须考虑用户体验和可行性"
            ]
        )
        
        # 定义产品经理的动作
        self.add_action(Action(
            name="analyze_requirement",
            description="分析用户需求，提取核心功能点",
            inputs=["user_requirement"],
            outputs=["analyzed_requirements"]
        ))
        
        self.add_action(Action(
            name="write_prd",
            description="编写产品需求文档",
            inputs=["analyzed_requirements"],
            outputs=["prd_document"]
        ))
        
        self.add_action(Action(
            name="prioritize_features",
            description="对功能进行优先级排序",
            inputs=["feature_list"],
            outputs=["prioritized_features"]
        ))
    
    async def _observe(self) -> None:
        """
        观察环境，检查是否有新的需求输入
        """
        # 在实际实现中，这里会检查输入队列
        pass
    
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        Returns:
            包含 PRD 文档的消息
        """
        pending_messages = self.get_pending_messages()
        
        if not pending_messages:
            return None
        
        # 处理第一个待处理消息
        message = pending_messages[0]
        message.state = "processing"
        
        # 分析需求
        analyzed = await self.analyze_requirement(message.content)
        
        # 编写 PRD
        prd = await self.write_prd(analyzed)
        
        # 更新消息状态
        message.state = "completed"
        
        # 返回 PRD 给架构师
        return Message(
            role=self.name,
            content=prd,
            cause_by="requirement_analyzed",
            send_to="Architect"
        )
    
    async def analyze_requirement(self, requirement: str) -> Dict[str, Any]:
        """
        分析用户需求
        
        Args:
            requirement: 用户需求描述
            
        Returns:
            分析后的需求结构
        """
        # 在实际实现中，这里会使用 LLM 进行分析
        analyzed = {
            "original_requirement": requirement,
            "core_features": [],
            "user_stories": [],
            "acceptance_criteria": [],
            "assumptions": [],
            "constraints": []
        }
        
        return analyzed
    
    async def write_prd(self, analyzed: Dict[str, Any]) -> str:
        """
        编写产品需求文档
        
        Args:
            analyzed: 分析后的需求结构
            
        Returns:
            PRD 文档内容
        """
        # PRD 模板
        prd_template = f"""
# 产品需求文档 (PRD)

## 1. 概述
{analyzed.get('original_requirement', '')}

## 2. 核心功能
{self._format_features(analyzed.get('core_features', []))}

## 3. 用户故事
{self._format_user_stories(analyzed.get('user_stories', []))}

## 4. 验收标准
{self._format_acceptance_criteria(analyzed.get('acceptance_criteria', []))}

## 5. 假设与约束
### 假设
{self._format_list(analyzed.get('assumptions', []))}

### 约束
{self._format_list(analyzed.get('constraints', []))}

## 6. 非功能性需求
- 性能要求
- 安全性要求
- 可用性要求

## 7. 里程碑
- Phase 1: 核心功能
- Phase 2: 增强功能
- Phase 3: 优化与维护
"""
        return prd_template
    
    async def prioritize_features(
        self, 
        features: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        对功能进行优先级排序
        
        Args:
            features: 功能列表
            
        Returns:
            排序后的功能列表
        """
        # 使用 MoSCoW 方法进行优先级排序
        # Must have, Should have, Could have, Won't have
        prioritized = sorted(
            features,
            key=lambda x: x.get('priority', 0),
            reverse=True
        )
        return prioritized
    
    def _format_features(self, features: List[str]) -> str:
        """格式化功能列表"""
        if not features:
            return "待定义"
        return "\n".join(f"- {f}" for f in features)
    
    def _format_user_stories(self, stories: List[str]) -> str:
        """格式化用户故事"""
        if not stories:
            return "待定义"
        return "\n\n".join(f"**Story {i+1}:** {s}" for i, s in enumerate(stories))
    
    def _format_acceptance_criteria(self, criteria: List[str]) -> str:
        """格式化验收标准"""
        if not criteria:
            return "待定义"
        return "\n".join(f"{i+1}. {c}" for i, c in enumerate(criteria))
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表项"""
        if not items:
            return "无"
        return "\n".join(f"- {item}" for item in items)
