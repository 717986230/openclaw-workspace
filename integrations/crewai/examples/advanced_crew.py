"""
CrewAI 高级示例

展示更复杂的多智能体协作场景。
"""

# 示例 1: 层级式协作流程
def example_hierarchical_process():
    """层级式协作示例"""
    try:
        from crewai import Crew, Process
        
        from integrations.crewai.roles import (
            ResearcherAgent,
            WriterAgent,
            ReviewerAgent,
            AgentConfig,
            AgentRole
        )
        
        # 创建管理者配置
        manager_config = AgentConfig(
            role=AgentRole.COORDINATOR,
            goal="协调团队完成复杂研究任务",
            backstory="你是一个经验丰富的项目经理，擅长分配任务和协调资源。",
            allow_delegation=True
        )
        
        # 创建团队成员
        researcher = ResearcherAgent()
        writer = WriterAgent()
        reviewer = ReviewerAgent()
        
        # 创建层级式 Crew
        crew = Crew(
            agents=[researcher.get_agent(), writer.get_agent(), reviewer.get_agent()],
            process=Process.hierarchical,
            manager_llm="gpt-4",
            verbose=True
        )
        
        print("创建了层级式团队")
        
    except ImportError:
        print("需要安装 CrewAI: pip install crewai")


# 示例 2: 任务依赖管理
def example_task_dependencies():
    """任务依赖示例"""
    from integrations.crewai.tasks import (
        TaskManager,
        TaskType,
        TaskPriority
    )
    
    manager = TaskManager(enable_tracing=True)
    
    # 创建有依赖关系的任务
    task1 = manager.create_task(
        task_type=TaskType.RESEARCH,
        description="收集项目需求",
        expected_output="需求文档",
        priority=TaskPriority.HIGH
    )
    
    task2 = manager.create_task(
        task_type=TaskType.ANALYSIS,
        description="分析需求可行性",
        expected_output="可行性分析报告",
        priority=TaskPriority.HIGH,
        dependencies=[task1.task_id]  # 依赖 task1
    )
    
    task3 = manager.create_task(
        task_type=TaskType.WRITING,
        description="撰写项目计划",
        expected_output="项目计划文档",
        priority=TaskPriority.MEDIUM,
        dependencies=[task2.task_id]  # 依赖 task2
    )
    
    # 提交所有任务
    manager.submit_task(task1)
    manager.submit_task(task2)
    manager.submit_task(task3)
    
    print("任务依赖关系:")
    print(f"  {task1.task_id[:8]} (需求收集)")
    print(f"    └─ {task2.task_id[:8]} (可行性分析)")
    print(f"        └─ {task3.task_id[:8]} (项目计划)")
    
    return manager


# 示例 3: 动态任务分配
def example_dynamic_allocation():
    """动态任务分配示例"""
    from integrations.crewai.tasks import TaskManager, TaskPriority
    from integrations.crewai.roles import AgentFactory, AgentRole
    
    manager = TaskManager()
    
    # 根据任务类型动态分配智能体
    tasks = [
        ("研究 AI 趋势", "research"),
        ("撰写技术报告", "writing"),
        ("审核代码质量", "review"),
        ("分析用户数据", "analysis")
    ]
    
    results = []
    
    for desc, task_type in tasks:
        # 动态创建智能体
        role_map = {
            'research': AgentRole.RESEARCHER,
            'writing': AgentRole.WRITER,
            'review': AgentRole.REVIEWER,
            'analysis': AgentRole.ANALYZER
        }
        
        role = role_map.get(task_type, AgentRole.EXECUTOR)
        
        try:
            agent = AgentFactory.create(role)
            print(f"为任务 '{desc}' 分配智能体: {agent}")
        except ValueError:
            print(f"角色 {role} 未注册")
            
        # 委托任务
        result = manager.delegate_task(
            task_type=task_type,
            description=desc,
            priority="medium"
        )
        results.append(result)
        
    return results


# 示例 4: 工作流编排
def example_workflow_orchestration():
    """工作流编排示例"""
    from integrations.crewai.workflows import (
        ResearchWorkflow,
        ContentWorkflow,
        WorkflowRegistry
    )
    
    # 查看可用工作流
    print("可用工作流:", WorkflowRegistry.list_workflows())
    
    # 研究工作流
    research_wf = ResearchWorkflow(topic="微服务架构")
    research_result = research_wf.execute()
    
    # 基于研究结果创建内容
    content_wf = ContentWorkflow(style="technical")
    content_result = content_wf.execute({
        'topic': "微服务架构分析",
        'research_data': research_result.output
    })
    
    print(f"研究完成: {research_result.status.value}")
    print(f"内容创作完成: {content_result.status.value}")
    
    return {
        'research': research_result,
        'content': content_result
    }


# 示例 5: 错误处理和重试
def example_error_handling():
    """错误处理示例"""
    from integrations.crewai.tasks import (
        TaskManager,
        TaskType,
        TaskPriority,
        TaskStatus
    )
    
    manager = TaskManager()
    
    # 创建高优先级任务
    task = manager.create_task(
        task_type=TaskType.RESEARCH,
        description="复杂研究任务",
        expected_output="研究报告",
        priority=TaskPriority.URGENT,
        max_retries=5,
        timeout=60
    )
    
    manager.submit_task(task)
    result = manager._execute_task(task)
    
    # 检查结果并重试
    if result.status == TaskStatus.FAILED:
        print(f"任务失败: {result.error}")
        print("执行重试逻辑...")
    else:
        print(f"任务成功: {result.output}")
        
    return result


# 示例 6: 多工作流并行执行
async def example_parallel_workflows():
    """并行工作流示例"""
    import asyncio
    from integrations.crewai.workflows import ResearchWorkflow
    
    # 创建多个工作流
    workflows = [
        ResearchWorkflow(topic="机器学习"),
        ResearchWorkflow(topic="自然语言处理"),
        ResearchWorkflow(topic="计算机视觉")
    ]
    
    # 并行执行
    tasks = [wf.execute_async() for wf in workflows]
    results = await asyncio.gather(*tasks)
    
    for i, result in enumerate(results):
        print(f"工作流 {i+1}: {result.status.value}")
        
    return results


if __name__ == "__main__":
    print("=== 示例 1: 层级式协作 ===")
    example_hierarchical_process()
    
    print("\n=== 示例 2: 任务依赖管理 ===")
    example_task_dependencies()
    
    print("\n=== 示例 3: 动态任务分配 ===")
    example_dynamic_allocation()
    
    print("\n=== 示例 4: 工作流编排 ===")
    example_workflow_orchestration()
    
    print("\n=== 示例 5: 错误处理 ===")
    example_error_handling()
    
    print("\n=== 示例 6: 并行工作流 ===")
    import asyncio
    asyncio.run(example_parallel_workflows())
