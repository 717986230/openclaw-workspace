"""
AutoGPT Integration - Advanced Usage Example
高级使用示例
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

from integrations.autogpt.planning import (
    TaskPlanner, Plan, Task, TaskStatus, TaskPriority,
    PlanExecutor, ExecutionReport
)
from integrations.autogpt.goals import (
    GoalManager, Goal, GoalStatus, GoalTracker, GoalValidator
)
from integrations.autogpt.reflection import (
    Reflector, AnalysisResult, ImprovementSuggestion
)


class AutoGPTAgent:
    """
    AutoGPT 代理示例
    
    展示如何整合所有组件创建一个自主代理
    """
    
    def __init__(self, name: str):
        """初始化代理"""
        self.name = name
        
        # 核心组件
        self.planner = TaskPlanner()
        self.executor = PlanExecutor(max_parallel_tasks=3)
        self.goal_manager = GoalManager()
        self.goal_tracker = GoalTracker(self.goal_manager)
        self.goal_validator = GoalValidator(self.goal_manager)
        self.reflector = Reflector()
        
        # 当前状态
        self.current_plan: Plan = None
        self.current_goal: Goal = None
        self.iteration_count = 0
        self.max_iterations = 10
    
    async def set_goal(self, goal_description: str) -> Goal:
        """设置目标"""
        # 创建目标
        goal = self.goal_manager.create_goal(
            name=goal_description[:50],
            description=goal_description,
            priority="high",
            goal_type="achievement",
            metrics=[
                {"name": "完成度", "target_value": 100, "unit": "%"}
            ]
        )
        
        self.current_goal = goal
        self.goal_manager.start_goal(goal.id)
        self.goal_tracker.track_goal(goal.id)
        
        print(f"[{self.name}] 目标已设置: {goal.name}")
        
        return goal
    
    async def plan(self) -> Plan:
        """制定计划"""
        if not self.current_goal:
            raise ValueError("未设置目标")
        
        # 使用规划器创建计划
        plan = await self.planner.create_plan(
            self.current_goal.description,
            context={"goal_id": self.current_goal.id}
        )
        
        self.current_plan = plan
        
        print(f"[{self.name}] 计划已创建: {len(plan.tasks)} 个任务")
        
        return plan
    
    async def execute(self) -> ExecutionReport:
        """执行计划"""
        if not self.current_plan:
            raise ValueError("未创建计划")
        
        # 注册自定义任务处理器
        self._register_task_handlers()
        
        # 执行计划
        report = await self.executor.execute_plan(
            self.current_plan,
            progress_callback=self._on_progress
        )
        
        print(f"[{self.name}] 执行完成")
        print(f"  成功率: {report.success_rate:.2%}")
        
        return report
    
    async def reflect(self, report: ExecutionReport) -> AnalysisResult:
        """反思执行结果"""
        # 分析执行报告
        analysis = await self.reflector.analyze_execution(report)
        
        print(f"[{self.name}] 反思完成")
        print(f"  发现模式: {len(analysis.patterns)}")
        print(f"  反思点: {len(analysis.points)}")
        
        return analysis
    
    async def improve(self, analysis: AnalysisResult) -> list:
        """基于反思改进"""
        # 获取改进建议
        suggestions = await self.reflector.suggest_improvements(analysis)
        
        print(f"[{self.name}] 改进建议: {len(suggestions)} 条")
        
        for suggestion in suggestions[:3]:
            print(f"  - [{suggestion.priority}] {suggestion.description}")
        
        return suggestions
    
    async def run(self, goal: str) -> Dict[str, Any]:
        """
        运行代理
        
        完整的规划-执行-反思循环
        """
        print(f"\n[{self.name}] 开始运行")
        print("=" * 60)
        
        # 设置目标
        await self.set_goal(goal)
        
        results = []
        
        for iteration in range(self.max_iterations):
            self.iteration_count = iteration + 1
            print(f"\n--- 迭代 {self.iteration_count} ---")
            
            # 规划
            plan = await self.plan()
            
            # 执行
            report = await self.execute()
            
            # 反思
            analysis = await self.reflect(report)
            
            # 改进
            suggestions = await self.improve(analysis)
            
            # 记录结果
            results.append({
                "iteration": self.iteration_count,
                "success_rate": report.success_rate,
                "analysis": analysis,
                "suggestions": suggestions
            })
            
            # 检查是否达到目标
            if report.success_rate >= 0.9:
                print(f"\n[{self.name}] 目标达成!")
                break
            
            # 检查是否有改进建议
            if not suggestions:
                print(f"\n[{self.name}] 无更多改进建议")
                break
        
        # 更新目标状态
        final_result = results[-1] if results else None
        if final_result and final_result["success_rate"] >= 0.8:
            self.goal_manager.complete_goal(self.current_goal.id)
        else:
            self.goal_manager.fail_goal(self.current_goal.id, "未达到目标")
        
        # 生成最终报告
        final_report = {
            "goal": self.current_goal.to_dict(),
            "iterations": self.iteration_count,
            "final_success_rate": final_result["success_rate"] if final_result else 0,
            "results": results
        }
        
        print(f"\n[{self.name}] 运行结束")
        print("=" * 60)
        
        return final_report
    
    def _register_task_handlers(self):
        """注册任务处理器"""
        async def default_handler(task: Task) -> Any:
            # 模拟任务执行
            await asyncio.sleep(0.1)
            return {"status": "completed", "task_id": task.id}
        
        self.executor.register_task_handler("default", default_handler)
    
    def _on_progress(self, progress: Dict[str, Any]):
        """进度回调"""
        completed = progress["completed"]
        total = progress["total_tasks"]
        percentage = progress["completion_percentage"]
        
        print(f"[{self.name}] 进度: {completed}/{total} ({percentage:.1f}%)")


async def example_multi_goal_agent():
    """多目标代理示例"""
    print("\n=== 多目标代理示例 ===\n")
    
    agent = AutoGPTAgent("多目标代理")
    
    # 创建多个目标
    goals = [
        "完成数据分析报告",
        "优化系统性能",
        "编写技术文档"
    ]
    
    results = []
    
    for goal_desc in goals:
        print(f"\n处理目标: {goal_desc}")
        result = await agent.run(goal_desc)
        results.append(result)
    
    # 汇总结果
    print("\n=== 汇总结果 ===")
    for i, result in enumerate(results):
        print(f"\n目标 {i+1}: {result['goal']['name']}")
        print(f"  最终成功率: {result['final_success_rate']:.2%}")
        print(f"  迭代次数: {result['iterations']}")
    
    return results


async def example_goal_decomposition():
    """目标分解示例"""
    print("\n=== 目标分解示例 ===\n")
    
    manager = GoalManager()
    
    # 创建主目标
    main_goal = manager.create_goal(
        name="软件开发项目",
        description="完成一个完整的软件开发项目",
        priority="critical",
        goal_type="milestone",
        deadline=datetime.now() + timedelta(days=30)
    )
    
    print(f"主目标: {main_goal.name}")
    print(f"截止日期: {main_goal.deadline}")
    
    # 分解为阶段
    phases = [
        ("需求分析", "分析和定义项目需求", "high"),
        ("设计", "设计系统架构和界面", "high"),
        ("开发", "编写代码实现功能", "high"),
        ("测试", "测试和质量保证", "high"),
        ("部署", "部署和发布", "medium")
    ]
    
    for name, desc, priority in phases:
        phase_goal = manager.create_goal(
            name=name,
            description=desc,
            priority=priority,
            parent_goal=main_goal.id
        )
        print(f"\n阶段目标: {phase_goal.name}")
    
    # 显示目标树
    tree = manager.get_goal_tree(main_goal.id)
    print(f"\n目标树结构:")
    print_goal_tree(tree, level=0)
    
    return manager


def print_goal_tree(node: Dict, level: int):
    """打印目标树"""
    indent = "  " * level
    name = node.get("name", "")
    status = node.get("status", "")
    progress = node.get("progress_percentage", 0)
    
    print(f"{indent}- {name} [{status}] ({progress:.0f}%)")
    
    for subgoal in node.get("subgoals", []):
        print_goal_tree(subgoal, level + 1)


async def example_reflection_cycle():
    """反思循环示例"""
    print("\n=== 反思循环示例 ===\n")
    
    reflector = Reflector()
    
    # 模拟多次执行和反思
    class MockReport:
        def __init__(self, success_rate, total_tasks=10):
            self.plan_id = "plan_001"
            self.start_time = datetime.now()
            self.end_time = datetime.now()
            self.total_tasks = total_tasks
            self.completed_tasks = int(success_rate * total_tasks)
            self.failed_tasks = total_tasks - self.completed_tasks
            self.success_rate = success_rate
            self.results = []
    
    # 逐渐改进的执行
    success_rates = [0.3, 0.5, 0.7, 0.85, 0.95]
    
    for i, rate in enumerate(success_rates):
        print(f"\n--- 执行 {i+1} ---")
        print(f"成功率: {rate:.0%}")
        
        report = MockReport(success_rate=rate)
        analysis = await reflector.analyze_execution(report)
        
        print(f"识别模式: {analysis.patterns}")
        print(f"反思点数: {len(analysis.points)}")
        
        suggestions = await reflector.suggest_improvements(analysis)
        print(f"改进建议: {len(suggestions)} 条")
        
        if suggestions:
            print(f"优先建议: {suggestions[0].description}")
    
    # 查看反思摘要
    summary = reflector.get_reflection_summary()
    print(f"\n=== 反思摘要 ===")
    print(f"总分析数: {summary['total_analyses']}")
    print(f"平均成功率: {summary['average_success_rate']:.2%}")
    print(f"识别模式数: {summary['patterns_identified']}")


async def example_custom_validation():
    """自定义验证示例"""
    print("\n=== 自定义验证示例 ===\n")
    
    manager = GoalManager()
    validator = GoalValidator(manager)
    
    # 创建带有特殊完成条件的目标
    goal = manager.create_goal(
        name="代码质量目标",
        description="确保代码质量达标",
        priority="high",
        metrics=[
            {"name": "测试覆盖率", "target_value": 80, "unit": "%"},
            {"name": "代码质量分数", "target_value": 90, "unit": "分"}
        ],
        completion_criteria=[
            "metric:测试覆盖率>=80",
            "metric:代码质量分数>=90",
            "custom:code_review_passed"
        ]
    )
    
    print(f"目标: {goal.name}")
    print(f"完成条件: {goal.completion_criteria}")
    
    # 注册自定义验证器
    def check_code_review(goal: Goal) -> bool:
        # 模拟代码审查检查
        return goal.metadata.get("code_review_passed", False)
    
    validator.register_validator("code_review_passed", check_code_review)
    
    # 验证目标（未通过）
    result1 = validator.validate_goal(goal.id)
    print(f"\n验证结果 (未完成):")
    print(f"  有效: {result1.is_valid}")
    print(f"  得分: {result1.score:.2f}")
    print(f"  失败条件: {result1.failed_criteria}")
    
    # 更新指标并通过代码审查
    manager.update_metric(goal.id, "测试覆盖率", 85)
    manager.update_metric(goal.id, "代码质量分数", 92)
    goal.metadata["code_review_passed"] = True
    
    # 再次验证
    result2 = validator.validate_goal(goal.id)
    print(f"\n验证结果 (已完成):")
    print(f"  有效: {result2.is_valid}")
    print(f"  得分: {result2.score:.2f}")
    print(f"  通过条件: {result2.passed_criteria}")
    
    return validator


async def main():
    """主函数"""
    print("=" * 60)
    print("AutoGPT Integration - 高级使用示例")
    print("=" * 60)
    
    # 运行高级示例
    await example_multi_goal_agent()
    await example_goal_decomposition()
    await example_reflection_cycle()
    await example_custom_validation()
    
    print("\n" + "=" * 60)
    print("高级示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
