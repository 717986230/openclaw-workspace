# MemGPT Integration for OpenClaw

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/openclaw)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://python.org)

MemGPT 框架的 OpenClaw 集成实现，提供分层记忆管理、智能检索和上下文窗口管理能力。

## 特性

### 🧠 分层记忆管理
- **核心记忆**: 始终保持在上下文中的关键信息
- **工作记忆**: 当前会话相关的动态记忆
- **归档记忆**: 长期存储，按需检索

### 🔍 智能检索系统
- **语义检索**: 基于向量嵌入的相似度搜索
- **关键词检索**: 传统全文搜索，支持布尔查询
- **混合检索**: 多策略融合，自适应权重调整

### 📊 上下文管理
- **令牌预算**: 精确控制上下文大小
- **优先级队列**: 重要信息保持在线
- **自动压缩**: 动态总结旧消息

## 快速开始

### 安装依赖

```bash
pip install pydantic numpy tiktoken openai
```

### 基本使用

```python
from integrations.memgpt import MemGPTIntegration

# 初始化
memgpt = MemGPTIntegration(
    agent_id="erbing",
    db_path="memory/memgpt.db"
)

# 存储记忆
memgpt.remember(
    content="用户喜欢使用 Python 进行数据分析",
    category="preference",
    importance=0.8
)

# 检索记忆
results = memgpt.recall(
    query="用户的编程偏好",
    top_k=5
)

# 添加消息到上下文
memgpt.add_message(
    role="user",
    content="你好，请介绍一下你自己"
)

# 获取当前上下文
context = memgpt.get_current_context()
```

## 架构

```
integrations/memgpt/
├── INTEGRATION.md          # 集成文档
├── README.md               # 本文件
├── __init__.py             # 主入口
├── memory/                 # 记忆管理
│   ├── core_memory.py      # 核心记忆
│   ├── working_memory.py   # 工作记忆
│   ├── archival_memory.py  # 归档记忆
│   └── memory_manager.py   # 记忆管理器
├── retrieval/              # 检索系统
│   ├── semantic_retriever.py   # 语义检索
│   ├── keyword_retriever.py    # 关键词检索
│   ├── hybrid_retriever.py     # 混合检索
│   └── retrieval_manager.py    # 检索管理器
├── context/                # 上下文管理
│   ├── context_window.py       # 上下文窗口
│   ├── priority_queue.py       # 优先级队列
│   ├── compression.py          # 上下文压缩
│   └── context_manager.py      # 上下文管理器
├── examples/               # 示例代码
│   ├── basic_usage.py      # 基础示例
│   └── advanced_usage.py   # 高级示例
└── tests/                  # 测试文件
    └── test_memgpt.py      # 单元测试
```

## 详细文档

### 记忆层

#### 核心记忆 (Core Memory)

```python
from integrations.memgpt.memory import CoreMemory

core = CoreMemory(max_tokens=512)

# 添加身份信息
core.add(
    id="identity",
    content="我是 Erbing，OpenClaw 代理",
    category="identity",
    importance=1.0
)

# 转换为系统提示
prompt = core.to_prompt()
```

#### 工作记忆 (Working Memory)

```python
from integrations.memgpt.memory import WorkingMemory

working = WorkingMemory(max_tokens=2048)

# 添加会话消息
working.add(
    content="用户询问了天气",
    message_type="user",
    importance=0.6
)

# 搜索
results = working.search("天气")

# 压缩
removed = working.compress(keep_recent=20)
```

#### 归档记忆 (Archival Memory)

```python
from integrations.memgpt.memory import ArchivalMemory

archival = ArchivalMemory(
    db_path="memory/archival.db",
    agent_id="erbing"
)

# 添加长期记忆
entry_id = archival.add(
    content="用户在2026年4月进行了数据分析项目",
    summary="数据分析项目",
    category="project",
    importance=0.7,
    tags=["data", "analysis"]
)

# 搜索
results = archival.search(
    query="数据分析",
    top_k=10,
    category="project"
)
```

### 检索系统

#### 语义检索

```python
from integrations.memgpt.retrieval import SemanticRetriever

retriever = SemanticRetriever(
    similarity_threshold=0.7
)

results = retriever.search(
    query="用户的偏好",
    documents=[{"content": "..."}],
    top_k=10
)
```

#### 关键词检索

```python
from integrations.memgpt.retrieval import KeywordRetriever

retriever = KeywordRetriever()

# 索引文档
retriever.index_documents([{"content": "..."}])

# 搜索
results = retriever.search("Python AND 编程", top_k=10)

# 布尔搜索
results = retriever.search_boolean("Python NOT web")
```

#### 混合检索

```python
from integrations.memgpt.retrieval import HybridRetriever

retriever = HybridRetriever(
    semantic_weight=0.6,
    keyword_weight=0.4
)

# 自适应搜索
results = retriever.adaptive_search(
    query="用户的编程偏好",
    documents=[{"content": "..."}],
    top_k=10
)
```

### 上下文管理

#### 上下文窗口

```python
from integrations.memgpt.context import ContextWindow

window = ContextWindow(max_tokens=8192)

# 添加消息
window.add(
    role="user",
    content="你好",
    priority=2
)

# 获取令牌使用情况
usage = window.get_token_usage()
```

#### 上下文压缩

```python
from integrations.memgpt.context import ContextCompressor

compressor = ContextCompressor(
    compression_threshold=0.8,
    preserve_recent=3
)

compressed, result = compressor.compress_messages(
    messages,
    keep_full=5
)

print(f"压缩比: {result.compression_ratio}")
```

## 与 OpenClaw 集成

### 与 MEMORY.md 同步

```python
memgpt = MemGPTIntegration(agent_id="erbing")

# 从 MEMORY.md 加载
memgpt.memory.load_from_memory_md("MEMORY.md")

# 导出回 MEMORY.md
memgpt.memory.export_to_memory_md("MEMORY.md")
```

### 与知识图谱链接

```python
# 存储带标签的记忆
memgpt.remember(
    content="用户偏好 Python 数据分析",
    category="preference",
    importance=0.8,
    metadata={"tags": ["python", "data"]}
)
```

## 配置

```yaml
# config/memgpt.yaml
memgpt:
  enabled: true
  
  memory:
    core_size: 512
    working_size: 2048
    archival_enabled: true
    
  retrieval:
    default_method: hybrid
    embedding_model: text-embedding-3-small
    
  context:
    max_tokens: 8192
    auto_compress: true
    compression_threshold: 0.8
```

## 性能优化

### 索引策略

```python
# 创建向量索引
memgpt.memory.archival_memory.create_index(
    field="embedding",
    index_type="ivf_flat"
)
```

### 缓存配置

```python
# 配置嵌入缓存
retriever = SemanticRetriever()
retriever._cache_size_limit = 2000
```

## 测试

```bash
cd integrations/memgpt
python tests/test_memgpt.py
```

## 示例

```bash
# 基础示例
python examples/basic_usage.py

# 高级示例
python examples/advanced_usage.py
```

## 依赖项

- Python >= 3.10
- pydantic >= 2.0
- numpy >= 1.24
- tiktoken >= 0.5 (可选，用于精确令牌计数)
- openai >= 1.0 (可选，用于嵌入生成)

## 版本历史

- **v1.0.0** (2026-04-16)
  - 初始发布
  - 三层记忆架构
  - 混合检索系统
  - 上下文窗口管理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [MemGPT 论文](https://arxiv.org/abs/2310.08560)
- [OpenClaw 文档](https://github.com/openclaw)
- [INTEGRATION.md](./INTEGRATION.md) - 详细集成文档
