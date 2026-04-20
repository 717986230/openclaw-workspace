# CrewAI Integration for OpenClaw

## 概述

CrewAI 是一个用于编排角色扮演 AI 智能体团队的框架。本集成将 CrewAI 的多智能体协作能力整合到 OpenClaw 中，实现复杂任务的智能分解和协作执行。

## 架构设计

```
integrations/crewai/
├── INTEGRATION.md          # 本文档
├── roles/                   # 角色定义
│   ├── base_role.py        # 基础角色类
│   ├── researcher.py       # 研究员角色
│   ├── writer.py           # 写作者角色
│   └── reviewer.py         # 审核者角色
├── tasks/                   # 任务管理
│   ├── task_manager.py     # 任务管理器
│   ├── task_types.py       # 任务类型定义
│   └── task_queue.py       # 任务队列
├── workflows/               # 协作流程
│   ├── base_workflow.py    # 基础工作流
│   ├── research_workflow.py # 研究工作流
│   └── content_workflow.py  # 内容创作工作流
├── examples/                # 示例代码
│   ├── basic_crew.py       # 基础示例
│   └── advanced_crew.py    # 高级示例
└── tests/                   # 测试文件
    ├── test_roles.py       # 角色测试
    ├── test_tasks.py       # 任务测试
    └── test_workflows.py   # 工作流测试
```

## 核心概念

### 1. Agents（智能体）

每个 Agent 扮演特定角色，具有：
- **Role**: 角色定义和职责
- **Goal**: 目标和动机
- **Backstory**: 背景故事
- **Tools**: 可用工具集

### 2. Tasks（任务）

任务定义工作单元：
- **Description**: 任务描述
- **Expected Output**: 预期输出
- **Agent**: 执行智能体
- **Tools**: 所需工具

### 3. Crews（团队）

团队协调智能体协作：
- **Agents**: 团队成员
- **Tasks**: 任务列表
- **Process**: 执行流程（顺序/层级）

## 安装依赖

```bash
pip install crewai crewai-tools
```

## 快速开始

```python
from integrations.crewai.roles.researcher import ResearcherAgent
from integrations.crewai.roles.writer import WriterAgent
from integrations.crewai.workflows.content_workflow import ContentWorkflow

# 创建智能体
researcher = ResearcherAgent()
writer = WriterAgent()

# 创建工作流
workflow = ContentWorkflow(agents=[researcher, writer])
result = workflow.execute("撰写关于 AI 趋势的文章")
```

## 与 OpenClaw 集成点

### 1. 工具桥接

CrewAI 智能体可以使用 OpenClaw 工具：

```python
from crewai_tools import tool

@tool
def search_memory(query: str) -> str:
    """搜索 OpenClaw 记忆系统"""
    # 调用 OpenClaw memory_search
    return memory_search(query)
```

### 2. 任务委托

将复杂任务委托给 CrewAI 团队：

```python
from integrations.crewai.tasks.task_manager import TaskManager

# 创建任务管理器
manager = TaskManager()

# 委托研究任务
result = manager.delegate_task(
    task_type="research",
    description="研究 OpenClaw 架构",
    priority="high"
)
```

### 3. 工作流触发

通过 OpenClaw 事件触发 CrewAI 工作流：

```python
# 在 OpenClaw 技能中触发
async def handle_complex_request(request):
    workflow = ResearchWorkflow()
    return await workflow.execute_async(request)
```

## 最佳实践

### 1. 角色设计

- **单一职责**: 每个角色专注一个领域
- **清晰目标**: 明确角色的主要目标
- **工具限制**: 只提供必要工具，避免权限过大

### 2. 任务分解

- **粒度适中**: 任务大小适合单个智能体完成
- **依赖明确**: 明确任务间的依赖关系
- **输出定义**: 清晰定义预期输出格式

### 3. 团队协作

- **互补角色**: 选择互补的角色组合
- **流程优化**: 根据任务类型选择合适流程
- **错误处理**: 设计重试和回退机制

## 配置选项

```yaml
# config/crewai.yaml
crewai:
  default_model: "nvidia-main/z-ai/glm5"
  max_iterations: 10
  timeout: 300
  
  agents:
    researcher:
      enabled: true
      model: "default"
    writer:
      enabled: true
      model: "default"
      
  workflows:
    research:
      max_agents: 3
      timeout: 600
```

## 监控和调试

### 日志级别

```python
import logging
logging.getLogger("crewai").setLevel(logging.DEBUG)
```

### 性能追踪

```python
from integrations.crewai.tasks.task_manager import TaskManager

manager = TaskManager(enable_tracing=True)
result = manager.delegate_task(...)
print(manager.get_trace())  # 查看执行轨迹
```

## 故障排除

### 常见问题

1. **智能体无响应**: 检查模型配置和 API 连接
2. **任务超时**: 增加超时设置或简化任务
3. **输出不符预期**: 优化任务描述和预期输出定义

## 未来扩展

- [ ] 支持更多预定义角色
- [ ] 集成 OpenClaw 记忆系统
- [ ] 添加工作流可视化
- [ ] 支持人机协作模式
- [ ] 添加成本追踪

## 参考资料

- [CrewAI 官方文档](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/joaomdmoura/crewAI)
- [OpenClaw 技能系统](../../skills/)

## 更新日志

- 2026-04-16: 初始集成版本
