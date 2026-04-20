"""
工程师角色

负责代码实现。
"""

from typing import Any, Dict, List, Optional
from .base import Role, Message, Action


class Engineer(Role):
    """
    工程师角色
    
    职责：
    - 实现系统功能
    - 编写代码
    - 编写单元测试
    - 代码重构
    """
    
    def __init__(self):
        """初始化工程师角色"""
        super().__init__(
            name="Engineer",
            profile="负责代码实现，将架构设计转化为可运行的代码",
            goal="高质量地实现系统功能",
            constraints=[
                "代码必须符合编码规范",
                "必须有单元测试覆盖",
                "必须遵循架构设计"
            ]
        )
        
        self.tech_stack = []  # 工程师掌握的技术栈
        
        # 定义工程师的动作
        self.add_action(Action(
            name="implement",
            description="实现系统功能",
            inputs=["architecture_design", "tech_stack"],
            outputs=["source_code"]
        ))
        
        self.add_action(Action(
            name="write_tests",
            description="编写单元测试",
            inputs=["source_code"],
            outputs=["test_code"]
        ))
        
        self.add_action(Action(
            name="refactor",
            description="代码重构",
            inputs=["source_code", "refactoring_requirements"],
            outputs=["refactored_code"]
        ))
    
    async def _observe(self) -> None:
        """观察环境"""
        pass
    
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        Returns:
            包含代码实现的消息
        """
        pending_messages = self.get_pending_messages()
        
        if not pending_messages:
            return None
        
        message = pending_messages[0]
        message.state = "processing"
        
        # 实现代码
        source_code = await self.implement(message.content)
        
        # 编写测试
        test_code = await self.write_tests(source_code)
        
        message.state = "completed"
        
        # 返回代码给 QA
        return Message(
            role=self.name,
            content=self._format_output(source_code, test_code),
            cause_by="code_implemented",
            send_to="QaEngineer"
        )
    
    async def implement(self, design: str) -> Dict[str, str]:
        """
        实现代码
        
        Args:
            design: 架构设计文档
            
        Returns:
            源代码字典 {文件名: 代码内容}
        """
        # 在实际实现中，这里会使用 LLM 生成代码
        source_code = {
            "main.py": "# Main entry point\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n",
            "config.py": "# Configuration\n\nCONFIG = {}\n",
            "utils.py": "# Utility functions\n\ndef helper():\n    pass\n"
        }
        
        return source_code
    
    async def write_tests(self, source_code: Dict[str, str]) -> Dict[str, str]:
        """
        编写单元测试
        
        Args:
            source_code: 源代码
            
        Returns:
            测试代码字典
        """
        test_code = {
            "test_main.py": "# Test main module\n\ndef test_main():\n    assert True\n",
            "test_utils.py": "# Test utility functions\n\ndef test_helper():\n    pass\n"
        }
        
        return test_code
    
    async def refactor(
        self, 
        source_code: Dict[str, str],
        requirements: List[str]
    ) -> Dict[str, str]:
        """
        代码重构
        
        Args:
            source_code: 源代码
            requirements: 重构需求
            
        Returns:
            重构后的代码
        """
        # 在实际实现中，这里会进行实际的代码重构
        return source_code
    
    def set_tech_stack(self, tech_stack: List[str]) -> None:
        """
        设置技术栈
        
        Args:
            tech_stack: 技术栈列表
        """
        self.tech_stack = tech_stack
    
    def _format_output(
        self, 
        source_code: Dict[str, str],
        test_code: Dict[str, str]
    ) -> str:
        """
        格式化输出
        
        Args:
            source_code: 源代码
            test_code: 测试代码
            
        Returns:
            格式化的输出文档
        """
        output = "# 代码实现\n\n## 源代码\n\n"
        
        for filename, code in source_code.items():
            output += f"### {filename}\n\n```\n{code}\n```\n\n"
        
        output += "\n## 测试代码\n\n"
        
        for filename, code in test_code.items():
            output += f"### {filename}\n\n```\n{code}\n```\n\n"
        
        return output
