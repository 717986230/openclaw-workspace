"""
CrewAI 基础示例

展示如何创建和运行一个简单的 CrewAI 团队。
"""

# 示例 1: 使用预定义角色创建团队
def example_basic_research():
    """基础研究示例"""
    from integrations.crewai.roles import ResearcherAgent, WriterAgent
    from integrations.crewai.workflows import ResearchWorkflow
    
    # 创建工作流
    workflow = ResearchWorkflow(topic="人工智能发展趋势")
    
    # 执行
    result = workflow.execute()
    
    print(f"状态: {result.status.value}")
    print(f"输出: {result.output}")
    print(f"耗时: {result.execution_time:.2f}秒")
    
    return result


# 示例 2: 使用任务管理器
def example_task_manager():
    """任务管理器示例"""
    from integrations.crewai.tasks import TaskManager, TaskType
    
    # 创建任务管理器
    manager = TaskManager(enable_tracing=True)
    
    # 创建任务
    task = manager.create_task(
        task_type=TaskType.RESEARCH,
        description="研究 OpenClaw 架构设计",
        expected_output="架构分析报告",
        agent_role="researcher"
    )
    
    # 提交任务
    manager.submit_task(task)
    
    # 执行任务
    result = manager.delegate_task(
        task_type="research",
        description="分析系统性能",
        priority="high"
    )
    
    print(f"任务状态: {result.status.value}")
    print(f"结果: {result.output}")
    
    # 查看执行轨迹
    trace = manager.get_trace()
    for record in trace:
        print(f"[{record['timestamp']}] {record['action']}: {record['task_id']}")
    
    return result


# 示例 3: 使用任务模板
def example_task_template():
    """任务模板示例"""
    from integrations.crewai.tasks import TaskManager
    
    manager = TaskManager()
    
    # 从模板创建任务
    task = manager.create_from_template(
        'research_topic',
        topic='量子计算应用'
    )
    
    print(f"任务ID: {task.task_id}")
    print(f"类型: {task.task_type.value}")
    print(f"描述: {task.description}")
    
    return task


# 示例 4: 简单的内容创作流程
def example_content_creation():
    """内容创作示例"""
    from integrations.crewai.roles import ResearcherAgent, WriterAgent, ReviewerAgent
    from integrations.crewai.workflows import ContentWorkflow
    
    # 创建智能体
    researcher = ResearcherAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    
    # 创建工作流
    workflow = ContentWorkflow(
        agents=[researcher, writer, reviewer],
        style="professional"
    )
    
    # 执行创作
    result = workflow.write(
        topic="OpenClaw 技术架构",
        length="medium"
    )
    
    print(f"创作结果: {result}")
    
    return result


# 示例 5: 自定义智能体配置
def example_custom_agent():
    """自定义智能体示例"""
    from integrations.crewai.roles import (
        ResearcherAgent,
        AgentConfig,
        AgentRole
    )
    
    # 自定义配置
    config = AgentConfig(
        role=AgentRole.RESEARCHER,
        goal="专注于技术深度研究，提供专业技术分析",
        backstory="""你是一个资深技术研究员，擅长深入分析技术架构和系统设计。
        你具有丰富的软件开发经验，能够快速理解复杂系统的工作原理。""",
        verbose=True,
        max_iter=20
    )
    
    # 使用自定义配置创建智能体
    researcher = ResearcherAgent(config=config)
    
    # 获取 Agent 实例
    agent = researcher.get_agent()
    
    print(f"角色: {agent['role']}")
    print(f"目标: {agent['goal']}")
    
    return researcher


if __name__ == "__main__":
    print("=== 示例 1: 基础研究 ===")
    example_basic_research()
    
    print("\n=== 示例 2: 任务管理器 ===")
    example_task_manager()
    
    print("\n=== 示例 3: 任务模板 ===")
    example_task_template()
    
    print("\n=== 示例 4: 内容创作 ===")
    example_content_creation()
    
    print("\n=== 示例 5: 自定义智能体 ===")
    example_custom_agent()
