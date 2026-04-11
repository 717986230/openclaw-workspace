# Agent Calling System - Skill

## 描述
从数据库中按需调用179个专业Agent，支持搜索、分类浏览、随机获取等功能。

## 数据库位置
`C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db`

## 表名
`agent_prompts` (179条记录)

---

## 使用方式

### 1. 导入AgentCaller
```python
from scripts.agent_caller import AgentCaller

caller = AgentCaller()
```

### 2. 基本操作

#### 列出所有Agent (前20个)
```python
agents = caller.list_all_agents(limit=20)
for agent in agents:
    print(f"{agent['name']} ({agent['category']})")
```

#### 搜索Agent
```python
# 搜索关键词
agents = caller.search_agents('data')
print(f"找到 {len(agents)} 个相关Agent")

for agent in agents:
    print(f"- {agent['name']}: {agent['description']}")
```

#### 按分类获取
```python
# 获取engineering类别的Agent
engineering_agents = caller.get_agents_by_category('engineering')
print(f"Engineering类别有 {len(engineering_agents)} 个Agent")
```

#### 随机获取
```python
# 随机获取一个Agent
random_agent = caller.get_random_agent()
print(f"随机Agent: {random_agent['name']}")
print(f"描述: {random_agent['description']}")
```

### 3. 获取完整Prompt

#### 根据名称获取
```python
agent = caller.get_agent_by_name('Backend Architect')
if agent:
    full_prompt = agent['full_content']
    # 使用prompt...
```

#### 根据ID获取
```python
prompt = caller.get_agent_full_prompt(agent_id=14)
```

---

## CLI命令行工具

### 查看所有分类
```bash
python scripts/agent_caller.py --categories
```

输出:
```
academic: 5 agents
design: 8 agents
engineering: 26 agents
game-development: 20 agents
marketing: 29 agents
paid-media: 7 agents
product: 5 agents
project-management: 6 agents
sales: 8 agents
spatial-computing: 6 agents
specialized: 28 agents
strategy: 16 agents
support: 6 agents
testing: 8 agents
```

### 搜索Agent
```bash
python scripts/agent_caller.py "data"
```

### 随机获取
```bash
python scripts/agent_caller.py --random
```

---

## Agent分类

### 技术类 (74个)
- **engineering** (26): Backend Architect, AI Engineer, Database Optimizer, etc.
- **specialized** (28): Agents Orchestrator, Code Generator, etc.
- **testing** (8): QA Engineer, Test Automation, etc.
- **spatial-computing** (6): AR/VR Specialist, etc.
- **integrations** (1): Integration Specialist

### 商业类 (77个)
- **marketing** (29): Growth Hacker, SEO Specialist, Content Creator, etc.
- **strategy** (16): Business Strategist, Product Manager, etc.
- **sales** (8): Sales Manager, Account Executive, etc.
- **paid-media** (7): Ads Specialist, Media Buyer, etc.
- **product** (5): Product Manager, Designer, etc.
- **project-management** (6): PM, Scrum Master, etc.
- **support** (6): Customer Success, Technical Support, etc.

### 创意类 (28个)
- **design** (8): UI/UX Designer, Brand Guardian, etc.
- **game-development** (20): Game Designer, Level Designer, etc.

### 学术类 (5个)
- **academic** (5): Historian, Psychologist, Narratologist, etc.

---

## 应用场景

### 场景1: 代码审查
```python
caller = AgentCaller()
agent = caller.get_agent_by_name('Code Reviewer')

# 使用agent['full_content']作为系统提示
system_prompt = agent['full_content']
user_message = "请审查这段代码..."

# 发送给LLM...
```

### 场景2: 架构设计
```python
agent = caller.get_agent_by_name('Backend Architect')
# 使用Backend Architect的专业知识设计系统架构
```

### 场景3: 营销策划
```python
marketing_agents = caller.get_agents_by_category('marketing')
# 选择合适的营销Agent进行协作
```

### 场景4: 多Agent协作
```python
# 组建Agent团队
backend = caller.get_agent_by_name('Backend Architect')
frontend = caller.get_agent_by_name('Frontend Developer')
designer = caller.get_agent_by_name('UI Designer')

# 协作完成任务...
```

---

## 数据库Schema

```sql
CREATE TABLE agent_prompts (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    description TEXT,
    emoji TEXT,
    color TEXT,
    tools TEXT,
    vibe TEXT,
    filepath TEXT,
    full_content TEXT,
    metadata TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 文件位置
- **Agent Caller**: `scripts/agent_caller.py`
- **使用示例**: `scripts/agent_usage_demo.py`
- **数据库**: `memory/database/xiaozhi_memory.db`

---

## 快速测试

```bash
# 查看统计
python scripts/agent_caller.py

# 按分类查看
python scripts/agent_caller.py --categories

# 搜索特定功能
python scripts/agent_caller.py "backend"

# 随机获取
python scripts/agent_caller.py --random
```

---

*创建时间: 2026-04-11*
*Agent总数: 179个*
*分类数: 15个*
