# MemGPT Integration for OpenClaw

## 概述

MemGPT 是一个分层记忆管理框架，为 AI 代理提供长期记忆、上下文窗口管理和智能检索能力。本集成将其能力引入 OpenClaw 平台。

## 核心组件

### 1. 分层记忆管理 (Memory/)

MemGPT 采用三层记忆架构：

- **核心记忆 (Core Memory)**: 系统提示和身份信息，始终在上下文中
- **工作记忆 (Working Memory)**: 当前会话相关，动态加载
- **归档记忆 (Archival Memory)**: 长期存储，按需检索

```
+-------------------+     +-------------------+     +-------------------+
|   Core Memory     | --> |  Working Memory   | --> | Archival Memory   |
| (Always Active)   |     | (Session-based)   |     | (On-demand Load)  |
+-------------------+     +-------------------+     +-------------------+
```

### 2. 记忆检索系统 (Retrieval/)

支持多种检索策略：

- **语义检索**: 基于向量嵌入的相似度搜索
- **关键词检索**: 传统全文搜索
- **时间范围检索**: 按时间窗口过滤
- **混合检索**: 多策略融合

### 3. 上下文管理器 (Context/)

智能上下文窗口管理：

- **动态压缩**: 自动总结旧消息
- **优先级队列**: 重要信息保持在线
- **令牌预算**: 精确控制上下文大小
- **滑动窗口**: 保持最新交互历史

## 集成架构

```
OpenClaw Agent
      |
      v
+------------------------------------------+
|         MemGPT Memory Manager            |
+------------------------------------------+
|                                          |
|  +------------+  +------------+  +------------+
|  |   Memory   |  |  Retrieval |  |  Context   |
|  |   Layer    |  |   System   |  |  Manager   |
|  +------------+  +------------+  +------------+
|                                          |
+------------------------------------------+
      |
      v
+------------------------------------------+
|         Storage Backend                  |
+------------------------------------------+
|  SQLite | LanceDB | Qdrant | Redis      |
+------------------------------------------+
```

## 使用方式

### Python API

```python
from integrations.memgpt import MemGPTIntegration

# 初始化
memgpt = MemGPTIntegration(
    agent_id="erbing",
    storage_backend="sqlite",
    db_path="memory/erbing_memgpt.db"
)

# 存储记忆
memgpt.remember(
    content="用户喜欢使用 Python 进行数据分析",
    metadata={"category": "preference", "importance": "high"}
)

# 检索记忆
results = memgpt.recall(
    query="用户的编程偏好",
    top_k=5,
    filters={"category": "preference"}
)

# 上下文管理
context = memgpt.get_context_window(
    max_tokens=4096,
    include_core=True,
    include_working=True
)
```

### 配置文件

```yaml
# config/memgpt.yaml
memgpt:
  enabled: true
  
  memory:
    core_size: 512      # 核心记忆令牌数
    working_size: 2048  # 工作记忆令牌数
    archival_enabled: true
    
  retrieval:
    default_method: semantic
    embedding_model: text-embedding-3-small
    top_k_default: 10
    
  context:
    max_tokens: 8192
    compression_threshold: 0.8
    priority_levels: 3
```

## 与 OpenClaw 现有系统集成

### 与 MEMORY.md 集成

MemGPT 作为 MEMORY.md 的增强后端：

```python
# 读取 MEMORY.md 到核心记忆
memgpt.load_core_from_file("MEMORY.md")

# 同步更新
memgpt.sync_to_memory_md()
```

### 与 memory/ 目录集成

```python
# 导入现有记忆文件
for file in glob.glob("memory/*.md"):
    memgpt.import_memories(file)
```

### 与知识图谱集成

```python
# 将记忆链接到知识图谱
memgpt.link_to_knowledge_graph(
    memory_id="mem_001",
    graph_node="user_preferences"
)
```

## 高级特性

### 1. 自动记忆迁移

当工作记忆溢出时，自动迁移到归档：

```python
# 配置自动迁移阈值
memgpt.config.auto_archive_threshold = 0.9

# 迁移时会自动总结
archived = memgpt.auto_archive_working_memory()
```

### 2. 记忆重要性评分

基于访问频率和时效性的自动评分：

```python
score = memgpt.calculate_importance(memory_id="mem_001")
# 返回: {"score": 0.85, "factors": {"recency": 0.9, "frequency": 0.8}}
```

### 3. 跨会话持久化

```python
# 保存会话状态
memgpt.save_session_state(session_id="sess_001")

# 恢复会话
memgpt.restore_session_state(session_id="sess_001")
```

## 性能优化

### 索引策略

```python
# 创建向量索引
memgpt.create_index(
    field="embedding",
    index_type="ivf_flat",
    n_lists=100
)

# 创建时间索引
memgpt.create_index(
    field="timestamp",
    index_type="btree"
)
```

### 缓存配置

```yaml
cache:
  enabled: true
  hot_memories: 50      # 热点记忆缓存数量
  embedding_cache: 1000 # 嵌入向量缓存
  ttl_seconds: 3600     # 缓存过期时间
```

## 监控与调试

### 记忆统计

```python
stats = memgpt.get_stats()
# {
#   "total_memories": 1234,
#   "core_count": 10,
#   "working_count": 45,
#   "archival_count": 1179,
#   "avg_importance": 0.72
# }
```

### 检索质量分析

```python
quality = memgpt.analyze_retrieval_quality()
# {
#   "precision": 0.89,
#   "recall": 0.82,
#   "avg_latency_ms": 12.5
# }
```

## 安全考虑

- 记忆数据加密存储
- 访问控制基于 agent_id
- 敏感信息自动脱敏
- 审计日志记录所有操作

## 依赖项

```
sqlite3>=3.40
numpy>=1.24
pydantic>=2.0
openai>=1.0  # 用于嵌入
lancedb>=0.3  # 可选向量存储
```

## 版本历史

- v1.0.0 (2026-04-16): 初始集成，支持核心三层记忆架构
