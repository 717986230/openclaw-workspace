"""
QA 工程师角色

负责质量保证和测试。
"""

from typing import Any, Dict, List, Optional
from .base import Role, Message, Action


class QaEngineer(Role):
    """
    QA 工程师角色
    
    职责：
    - 编写测试用例
    - 执行测试
    - 报告缺陷
    - 验证修复
    """
    
    def __init__(self):
        """初始化 QA 工程师角色"""
        super().__init__(
            name="QaEngineer",
            profile="负责软件质量保证，确保代码符合质量标准",
            goal="发现并报告所有缺陷，确保软件质量",
            constraints=[
                "必须覆盖所有功能点",
                "必须记录详细的测试结果",
                "必须验证所有缺陷修复"
            ]
        )
        
        # 定义 QA 工程师的动作
        self.add_action(Action(
            name="write_test_cases",
            description="编写测试用例",
            inputs=["source_code", "requirements"],
            outputs=["test_cases"]
        ))
        
        self.add_action(Action(
            name="execute_tests",
            description="执行测试",
            inputs=["source_code", "test_cases"],
            outputs=["test_results"]
        ))
        
        self.add_action(Action(
            name="report_bugs",
            description="报告缺陷",
            inputs=["test_results"],
            outputs=["bug_reports"]
        ))
        
        self.add_action(Action(
            name="verify_fix",
            description="验证缺陷修复",
            inputs=["bug_reports", "fixed_code"],
            outputs=["verification_results"]
        ))
    
    async def _observe(self) -> None:
        """观察环境"""
        pass
    
    async def _react(self) -> Message:
        """
        对观察到的内容做出反应
        
        Returns:
            包含测试结果的消息
        """
        pending_messages = self.get_pending_messages()
        
        if not pending_messages:
            return None
        
        message = pending_messages[0]
        message.state = "processing"
        
        # 编写测试用例
        test_cases = await self.write_test_cases(message.content)
        
        # 执行测试
        test_results = await self.execute_tests(test_cases)
        
        # 如果有缺陷，报告缺陷
        if test_results.get("failed", 0) > 0:
            bug_reports = await self.report_bugs(test_results)
        else:
            bug_reports = []
        
        message.state = "completed"
        
        # 返回测试报告给项目经理
        return Message(
            role=self.name,
            content=self._format_report(test_results, bug_reports),
            cause_by="testing_completed",
            send_to="ProjectManager"
        )
    
    async def write_test_cases(self, code_info: str) -> Dict[str, Any]:
        """
        编写测试用例
        
        Args:
            code_info: 代码信息
            
        Returns:
            测试用例
        """
        test_cases = {
            "unit_tests": [],
            "integration_tests": [],
            "e2e_tests": [],
            "edge_cases": []
        }
        
        return test_cases
    
    async def execute_tests(
        self, 
        test_cases: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        执行测试
        
        Args:
            test_cases: 测试用例
            
        Returns:
            测试结果
        """
        test_results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "failures": [],
            "execution_time": 0
        }
        
        return test_results
    
    async def report_bugs(
        self, 
        test_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        报告缺陷
        
        Args:
            test_results: 测试结果
            
        Returns:
            缺陷报告列表
        """
        bug_reports = []
        
        for failure in test_results.get("failures", []):
            bug_reports.append({
                "id": f"BUG-{len(bug_reports)+1}",
                "severity": self._determine_severity(failure),
                "description": failure.get("description", ""),
                "steps_to_reproduce": failure.get("steps", []),
                "expected_result": failure.get("expected", ""),
                "actual_result": failure.get("actual", ""),
                "environment": {}
            })
        
        return bug_reports
    
    async def verify_fix(
        self, 
        bug: Dict[str, Any],
        fixed_code: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        验证缺陷修复
        
        Args:
            bug: 缺陷报告
            fixed_code: 修复后的代码
            
        Returns:
            验证结果
        """
        verification = {
            "bug_id": bug.get("id"),
            "verified": False,
            "comments": ""
        }
        
        return verification
    
    def _determine_severity(self, failure: Dict[str, Any]) -> str:
        """
        确定缺陷严重程度
        
        Args:
            failure: 失败信息
            
        Returns:
            严重程度 (critical, high, medium, low)
        """
        # 简单的判断逻辑
        if "crash" in str(failure).lower():
            return "critical"
        elif "error" in str(failure).lower():
            return "high"
        elif "warning" in str(failure).lower():
            return "medium"
        else:
            return "low"
    
    def _format_report(
        self, 
        test_results: Dict[str, Any],
        bug_reports: List[Dict[str, Any]]
    ) -> str:
        """
        格式化测试报告
        
        Args:
            test_results: 测试结果
            bug_reports: 缺陷报告
            
        Returns:
            测试报告
        """
        report = f"""
# 测试报告

## 1. 测试概要
- 总用例数: {test_results.get('total', 0)}
- 通过: {test_results.get('passed', 0)}
- 失败: {test_results.get('failed', 0)}
- 跳过: {test_results.get('skipped', 0)}
- 执行时间: {test_results.get('execution_time', 0)}s

## 2. 缺陷报告
{self._format_bug_reports(bug_reports)}

## 3. 测试结论
{self._generate_conclusion(test_results)}
"""
        return report
    
    def _format_bug_reports(self, bug_reports: List[Dict[str, Any]]) -> str:
        """格式化缺陷报告"""
        if not bug_reports:
            return "无缺陷"
        
        formatted = []
        for bug in bug_reports:
            formatted.append(f"""
### {bug.get('id', 'Unknown')}
- 严重程度: {bug.get('severity', 'unknown')}
- 描述: {bug.get('description', '')}
- 期望结果: {bug.get('expected_result', '')}
- 实际结果: {bug.get('actual_result', '')}
""")
        
        return "\n".join(formatted)
    
    def _generate_conclusion(self, test_results: Dict[str, Any]) -> str:
        """生成测试结论"""
        if test_results.get('failed', 0) == 0:
            return "✅ 所有测试通过，代码质量良好。"
        elif test_results.get('failed', 0) < test_results.get('total', 0) * 0.2:
            return "⚠️ 存在少量缺陷，建议修复后发布。"
        else:
            return "❌ 缺陷较多，需要重新开发。"