# MetaGPT Integration for OpenClaw

## 概述

MetaGPT 是一个多智能体协作框架，通过角色扮演实现软件开发流程的完整模拟。本集成将 MetaGPT 的核心能力引入 OpenClaw，实现自动化的软件开发、代码生成和项目管理。

## 核心概念

### 1. 角色扮演系统 (Role-Playing)

MetaGPT 通过定义不同的角色来模拟真实的软件开发团队：

- **产品经理 (ProductManager)**: 分析需求，编写 PRD
- **架构师 (Architect)**: 设计系统架构，技术选型
- **工程师 (Engineer)**: 编写代码，实现功能
- **QA 工程师 (QaEngineer)**: 测试代码，质量保证
- **项目经理 (ProjectManager)**: 统筹协调，进度管理

### 2. 工作流程 (Workflow)

标准的软件开发流程：

```
需求输入 → 产品经理 → 架构师 → 工程师 → QA → 交付
```

### 3. 消息传递机制

角色之间通过标准化的消息格式进行通信：

- 需求文档 (PRD)
- 架构设计文档 (System Design)
- 代码实现 (Code Implementation)
- 测试报告 (Test Report)

## 集成架构

```
integrations/metagpt/
├── INTEGRATION.md          # 本文档
├── roles/                  # 角色定义
│   ├── product_manager.py
│   ├── architect.py
│   ├── engineer.py
│   ├── qa_engineer.py
│   └── project_manager.py
├── workflows/              # 工作流程
│   ├── software_dev.py     # 标准开发流程
│   ├── code_review.py      # 代码审查流程
│   └── agile_sprint.py     # 敏捷迭代流程
├── code_gen/               # 代码生成器
│   ├── generators.py       # 代码生成核心
│   ├── templates/          # 代码模板
│   └── validators.py       # 代码验证
├── examples/               # 示例项目
│   ├── simple_app/         # 简单应用示例
│   └── api_service/        # API 服务示例
└── tests/                  # 测试文件
    ├── test_roles.py
    └── test_workflow.py
```

## 使用方式

### 1. 快速开始

```python
from integrations.metagpt import SoftwareTeam

# 创建开发团队
team = SoftwareTeam()

# 启动开发流程
result = team.develop(
    requirement="创建一个 RESTful API 服务，提供用户管理功能",
    project_name="user_api"
)
```

### 2. 自定义角色

```python
from integrations.metagpt.roles import Engineer

class BackendEngineer(Engineer):
    """后端工程师"""
    
    def __init__(self):
        super().__init__()
        self.tech_stack = ["Python", "FastAPI", "PostgreSQL"]
    
    async def implement(self, design):
        # 实现后端逻辑
        pass
```

### 3. 工作流定制

```python
from integrations.metagpt.workflows import Workflow

class CustomWorkflow(Workflow):
    """自定义开发流程"""
    
    async def run(self, requirement):
        # 自定义流程步骤
        prd = await self.pm.analyze(requirement)
        design = await self.architect.design(prd)
        code = await self.engineer.implement(design)
        test_result = await self.qa.test(code)
        return test_result
```

## 与 OpenClaw 集成点

### 1. 工具调用

MetaGPT 角色可以调用 OpenClaw 工具：

```python
from openclaw import tools

class SmartEngineer(Engineer):
    async def implement(self, design):
        # 使用 OpenClaw 工具读取现有代码
        existing_code = await tools.read("src/main.py")
        # 生成新代码
        new_code = await self.generate(existing_code, design)
        # 写入文件
        await tools.write("src/main.py", new_code)
```

### 2. 记忆系统

角色可以使用 OpenClaw 的记忆系统：

```python
from openclaw.memory import memory_search, memory_get

class ProductManager:
    async def analyze(self, requirement):
        # 搜索相关历史项目
        similar_projects = await memory_search(requirement)
        # 基于历史经验编写 PRD
        prd = await self.write_prd(requirement, similar_projects)
        return prd
```

### 3. 技能系统

MetaGPT 工作流可以作为 OpenClaw 技能：

```yaml
# skills/software-development/SKILL.md
name: software-development
description: 使用 MetaGPT 多智能体协作进行软件开发
parameters:
  - requirement: 需求描述
  - project_name: 项目名称
  - tech_stack: 技术栈（可选）
```

## 最佳实践

### 1. 角色配置

每个角色应该有清晰的职责边界和输入输出定义：

```python
class Role:
    name: str           # 角色名称
    profile: str        # 角色描述
    goal: str          # 角色目标
    constraints: list  # 约束条件
    actions: list      # 可执行动作
```

### 2. 消息格式

使用标准化的消息格式确保角色间通信的可靠性：

```python
class Message:
    role: str           # 发送者角色
    content: str        # 消息内容
    cause_by: str       # 触发原因
    send_to: str        # 接收者
    state: str          # 消息状态
```

### 3. 错误处理

```python
class Workflow:
    async def run(self, requirement):
        try:
            result = await self.execute(requirement)
            return result
        except RoleExecutionError as e:
            # 记录错误
            await self.log_error(e)
            # 回滚操作
            await self.rollback()
            # 重试或报告
            raise
```

## 配置选项

### 环境变量

```bash
# MetaGPT 配置
METAGPT_LLM_PROVIDER=openai  # 或 local
METAGPT_MODEL=gpt-4          # 使用的模型
METAGPT_MAX_TOKENS=4096      # 最大 token 数
METAGPT_TEMPERATURE=0.7      # 温度参数
```

### 配置文件

```yaml
# integrations/metagpt/config.yaml
roles:
  product_manager:
    model: gpt-4
    max_retries: 3
  architect:
    model: gpt-4
    max_retries: 3
  engineer:
    model: gpt-4
    max_retries: 5

workflow:
  max_iterations: 10
  timeout: 3600  # 秒
  
code_generation:
  style: google  # 代码风格
  test_coverage: true
```

## 性能优化

### 1. 并行执行

```python
# 架构师和产品经理可以并行工作
async def parallel_workflow(requirement):
    prd_task = asyncio.create_task(pm.analyze(requirement))
    research_task = asyncio.create_task(architect.research())
    
    prd, research = await asyncio.gather(prd_task, research_task)
    design = await architect.design(prd, research)
```

### 2. 缓存机制

```python
from functools import lru_cache

class Architect:
    @lru_cache(maxsize=100)
    async def get_architecture_pattern(self, pattern_name):
        # 缓存架构模式
        return await self.load_pattern(pattern_name)
```

### 3. 流式输出

```python
class Engineer:
    async def implement_stream(self, design):
        async for chunk in self.generate_stream(design):
            yield chunk
```

## 监控和日志

### 日志级别

```python
import logging

# MetaGPT 使用 OpenClaw 的日志系统
logger = logging.getLogger("metagpt")

# 不同级别的日志
logger.debug("角色执行细节")
logger.info("工作流进度")
logger.warning("潜在问题")
logger.error("执行错误")
```

### 性能指标

```python
from openclaw.metrics import track_metrics

@track_metrics
async def execute_workflow(requirement):
    # 自动收集执行时间、成功率等指标
    pass
```

## 故障排查

### 常见问题

1. **角色通信失败**
   - 检查消息格式是否正确
   - 确认角色名称和地址匹配

2. **代码生成质量低**
   - 调整 temperature 参数
   - 增加上下文信息
   - 使用更强的模型

3. **工作流超时**
   - 增加 timeout 配置
   - 优化步骤复杂度
   - 使用并行执行

## 扩展开发

### 添加新角色

```python
from integrations.metagpt.roles import Role

class DevOpsEngineer(Role):
    """DevOps 工程师"""
    
    name = "DevOps Engineer"
    profile = "负责 CI/CD 和基础设施"
    goal = "自动化部署和运维"
    
    async def setup_ci(self, project):
        # 设置 CI/CD
        pass
```

### 添加新工作流

```python
from integrations.metagpt.workflows import Workflow

class MicroserviceWorkflow(Workflow):
    """微服务开发流程"""
    
    async def run(self, requirement):
        # 服务拆分
        services = await self.architect.split_services(requirement)
        
        # 并行开发各个服务
        tasks = [
            self.develop_service(svc) 
            for svc in services
        ]
        results = await asyncio.gather(*tasks)
        
        # 集成测试
        return await self.integrate_test(results)
```

## 参考资料

- [MetaGPT 官方文档](https://github.com/geekan/MetaGPT)
- [OpenClaw 技能开发指南](../../../docs/skill-development.md)
- [多智能体协作最佳实践](../../../docs/multi-agent.md)

## 版本历史

- v1.0.0 (2026-04-16): 初始集成版本
  - 实现核心角色定义
  - 实现标准开发流程
  - 实现代码生成器
  - 添加示例和测试

## 贡献者

- OpenClaw Team

## 许可证

本集成遵循 OpenClaw 主项目许可证。
