"""
AutoGPT Integration - Basic Usage Example
基础使用示例
"""

import asyncio
from integrations.autogpt.planning import TaskPlanner, PlanExecutor
from integrations.autogpt.goals import GoalManager, GoalValidator, GoalTracker
from integrations.autogpt.reflection import Reflector, ExecutionAnalyzer


async def example_task_planning():
    """任务规划示例"""
    print("\n=== 任务规划示例 ===\n")
    
    # 创建任务规划器
    planner = TaskPlanner()
    
    # 创建执行计划
    goal = "开发一个数据分析仪表板"
    plan = await planner.create_plan(goal)
    
    print(f"创建计划: {plan.id}")
    print(f"目标: {plan.goal}")
    print(f"\n任务列表:")
    
    for task_id, task in plan.tasks.items():
        print(f"  - {task.id}: {task.name}")
        print(f"    描述: {task.description}")
        print(f"    优先级: {task.priority.value}")
        print(f"    状态: {task.status.value}")
    
    # 获取进度
    progress = plan.get_progress()
    print(f"\n进度: {progress['completion_percentage']:.1f}%")
    
    return planner, plan


async def example_goal_management():
    """目标管理示例"""
    print("\n=== 目标管理示例 ===\n")
    
    # 创建目标管理器
    manager = GoalManager()
    
    # 创建主目标
    main_goal = manager.create_goal(
        name="产品发布",
        description="完成产品的开发和发布",
        priority="high",
        goal_type="milestone"
    )
    print(f"创建主目标: {main_goal.id} - {main_goal.name}")
    
    # 创建子目标
    dev_goal = manager.create_goal(
        name="开发阶段",
        description="完成产品开发",
        priority="high",
        parent_goal=main_goal.id,
        metrics=[
            {"name": "功能完成数", "target_value": 10, "unit": "个"},
            {"name": "测试覆盖率", "target_value": 80, "unit": "%"}
        ]
    )
    print(f"创建子目标: {dev_goal.id} - {dev_goal.name}")
    
    test_goal = manager.create_goal(
        name="测试阶段",
        description="完成产品测试",
        priority="high",
        parent_goal=main_goal.id,
        metrics=[
            {"name": "测试用例数", "target_value": 50, "unit": "个"},
            {"name": "Bug修复率", "target_value": 95, "unit": "%"}
        ]
    )
    print(f"创建子目标: {test_goal.id} - {test_goal.name}")
    
    # 开始目标
    manager.start_goal(main_goal.id)
    manager.start_goal(dev_goal.id)
    
    # 更新进度
    manager.update_metric(dev_goal.id, "功能完成数", 7)
    manager.update_metric(dev_goal.id, "测试覆盖率", 60)
    
    # 计算进度
    progress = dev_goal.calculate_progress()
    print(f"\n开发阶段进度: {progress:.1f}%")
    
    # 创建目标追踪器
    tracker = GoalTracker(manager)
    tracker.track_goal(dev_goal.id)
    
    # 拍摄快照
    snapshot = tracker.take_snapshot(dev_goal.id)
    print(f"拍摄进度快照: {snapshot.progress_percentage:.1f}%")
    
    # 生成进度报告
    report = tracker.get_progress_report(dev_goal.id)
    print(f"\n进度报告:")
    print(f"  状态: {report['status']}")
    print(f"  进度: {report['current_progress']:.1f}%")
    print(f"  趋势: {report.get('trend', 'N/A')}")
    
    # 创建目标验证器
    validator = GoalValidator(manager)
    
    # 验证目标
    validation = validator.validate_goal(dev_goal.id)
    print(f"\n验证结果:")
    print(f"  有效: {validation.is_valid}")
    print(f"  得分: {validation.score:.2f}")
    print(f"  通过条件: {len(validation.passed_criteria)}")
    print(f"  失败条件: {len(validation.failed_criteria)}")
    
    return manager


async def example_reflection():
    """自我反思示例"""
    print("\n=== 自我反思示例 ===\n")
    
    # 创建反思器
    reflector = Reflector()
    
    # 模拟执行结果
    class MockExecutionResult:
        def __init__(self, success, duration, error=None):
            self.task_id = "task_0001"
            self.success = success
            self.success_rate = 1.0 if success else 0.0
            self.duration_seconds = duration
            self.error = error
    
    # 分析成功的执行
    success_result = MockExecutionResult(success=True, duration=5.0)
    analysis1 = await reflector.analyze_execution(success_result)
    
    print(f"分析结果 1:")
    print(f"  任务 ID: {analysis1.task_id}")
    print(f"  成功: {analysis1.success}")
    print(f"  反思点: {len(analysis1.points)}")
    
    for point in analysis1.points:
        print(f"    - [{point.category}] {point.description}")
    
    # 分析失败的执行
    fail_result = MockExecutionResult(success=False, duration=30.0, error="Connection timeout")
    analysis2 = await reflector.analyze_execution(fail_result)
    
    print(f"\n分析结果 2:")
    print(f"  任务 ID: {analysis2.task_id}")
    print(f"  成功: {analysis2.success}")
    print(f"  反思点: {len(analysis2.points)}")
    
    for point in analysis2.points:
        print(f"    - [{point.category}] {point.description}")
        if point.suggested_action:
            print(f"      建议: {point.suggested_action}")
    
    # 生成改进建议
    suggestions = await reflector.suggest_improvements(analysis2)
    print(f"\n改进建议 ({len(suggestions)} 条):")
    
    for suggestion in suggestions[:3]:  # 显示前3条
        print(f"  - [{suggestion.priority}] {suggestion.description}")
    
    # 反思摘要
    summary = reflector.get_reflection_summary()
    print(f"\n反思摘要:")
    print(f"  总分析数: {summary['total_analyses']}")
    print(f"  平均成功率: {summary['average_success_rate']:.2f}")
    
    return reflector


async def example_execution_analyzer():
    """执行分析器示例"""
    print("\n=== 执行分析器示例 ===\n")
    
    # 创建分析器
    analyzer = ExecutionAnalyzer()
    
    # 记录多次执行
    executions = [
        ("task_001", True, 5.2),
        ("task_001", True, 4.8),
        ("task_001", True, 6.1),
        ("task_002", True, 10.5),
        ("task_002", False, 60.0, "Timeout"),
        ("task_002", True, 12.3),
        ("task_003", False, 2.0, "Missing resource"),
        ("task_003", True, 3.5),
    ]
    
    for exec_data in executions:
        task_id = exec_data[0]
        success = exec_data[1]
        duration = exec_data[2]
        error = exec_data[3] if len(exec_data) > 3 else None
        analyzer.record_execution(task_id, success, duration, error)
    
    # 更新趋势
    analyzer.update_trends()
    
    # 获取性能报告
    report = analyzer.get_performance_report()
    print(f"性能报告:")
    print(f"  总执行数: {report['total_executions']}")
    print(f"  成功执行: {report['successful_executions']}")
    print(f"  成功率: {report['success_rate']:.2%}")
    print(f"  平均时长: {report['avg_duration']:.2f}秒")
    
    print(f"\n错误分布:")
    for error_type, count in report['error_distribution'].items():
        print(f"  - {error_type}: {count}")
    
    # 获取任务统计
    print(f"\n任务统计:")
    for task_id in ["task_001", "task_002", "task_003"]:
        stats = analyzer.get_task_stats(task_id)
        if stats:
            print(f"  {task_id}:")
            print(f"    总执行: {stats.total_executions}")
            print(f"    成功率: {stats.success_rate:.2%}")
            print(f"    平均时长: {stats.avg_duration:.2f}秒")
    
    # 获取趋势
    trends = analyzer.get_trend_report()
    print(f"\n趋势分析:")
    for metric, trend_data in trends.items():
        print(f"  {metric}: {trend_data['trend_direction']}")
    
    # 检测异常
    anomalies = analyzer.get_anomalies()
    if anomalies:
        print(f"\n检测到异常:")
        for anomaly in anomalies:
            print(f"  - 类型: {anomaly['type']}")
            print(f"    任务: {anomaly['task_id']}")
    
    return analyzer


async def example_full_workflow():
    """完整工作流示例"""
    print("\n=== 完整工作流示例 ===\n")
    
    # 1. 创建目标和计划
    planner = TaskPlanner()
    plan = await planner.create_plan("完成月度报告")
    
    print(f"步骤 1: 创建计划")
    print(f"  计划 ID: {plan.id}")
    print(f"  任务数: {len(plan.tasks)}")
    
    # 2. 设置目标追踪
    goal_manager = GoalManager()
    goal = goal_manager.create_goal(
        name="月度报告",
        description="完成月度报告的编写和提交",
        priority="high",
        metrics=[
            {"name": "完成度", "target_value": 100, "unit": "%"}
        ]
    )
    
    goal_manager.start_goal(goal.id)
    
    print(f"\n步骤 2: 创建并启动目标")
    print(f"  目标 ID: {goal.id}")
    
    # 3. 执行计划（模拟）
    executor = PlanExecutor(max_parallel_tasks=2)
    
    print(f"\n步骤 3: 准备执行")
    print(f"  最大并行任务数: {executor.max_parallel_tasks}")
    print(f"  启用重试: {executor.retry_failed_tasks}")
    
    # 4. 反思和改进
    reflector = Reflector()
    
    print(f"\n步骤 4: 反思系统已就绪")
    print(f"  反思器已创建")
    
    # 5. 执行分析
    analyzer = ExecutionAnalyzer()
    
    print(f"\n步骤 5: 执行分析器已就绪")
    print(f"  最大历史记录: {analyzer.max_history}")
    
    print(f"\n工作流准备完成，可以开始执行任务。")
    
    return {
        "planner": planner,
        "plan": plan,
        "goal_manager": goal_manager,
        "goal": goal,
        "executor": executor,
        "reflector": reflector,
        "analyzer": analyzer
    }


async def main():
    """主函数"""
    print("=" * 60)
    print("AutoGPT Integration - 使用示例")
    print("=" * 60)
    
    # 运行所有示例
    await example_task_planning()
    await example_goal_management()
    await example_reflection()
    await example_execution_analyzer()
    await example_full_workflow()
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
