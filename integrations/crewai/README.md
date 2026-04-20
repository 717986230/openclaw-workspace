# CrewAI Integration

将 CrewAI 多智能体协作框架整合到 OpenClaw 中。

## 目录结构

```
integrations/crewai/
├── INTEGRATION.md       # 详细集成文档
├── README.md            # 本文件
├── __init__.py          # 模块入口
├── roles/               # 角色定义
│   ├── __init__.py
│   ├── base_role.py     # 基础角色类
│   ├── researcher.py    # 研究员
│   ├── writer.py        # 写作者
│   └── reviewer.py      # 审核者
├── tasks/               # 任务管理
│   ├── __init__.py
│   ├── task_types.py    # 任务类型
│   ├── task_queue.py    # 任务队列
│   └── task_manager.py  # 任务管理器
├── workflows/           # 协作流程
│   ├── __init__.py
│   ├── base_workflow.py # 基础工作流
│   ├── research_workflow.py
│   └── content_workflow.py
├── examples/            # 示例代码
│   ├── __init__.py
│   ├── basic_crew.py
│   └── advanced_crew.py
└── tests/               # 测试文件
    ├── __init__.py
    ├── test_roles.py
    ├── test_tasks.py
    └── test_workflows.py
```

## 快速开始

```python
from integrations.crewai import ResearcherAgent, ResearchWorkflow

# 创建研究工作流
workflow = ResearchWorkflow(topic="人工智能")
result = workflow.execute()

print(result.output)
```

## 安装依赖

```bash
pip install crewai crewai-tools
```

## 详细文档

参见 [INTEGRATION.md](./INTEGRATION.md)。
