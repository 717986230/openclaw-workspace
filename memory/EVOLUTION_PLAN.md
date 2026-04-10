# AI 记忆系统进化 - 综合整合

整合自：OpenViking、MemPalace、Engram、Memoh、Phantom、Agent-Reach

## 一、项目精华提炼

### 1. OpenViking (21.5k stars)
**核心设计**: 专为 AI Agent 设计的上下文数据库
- **统一管理**: 记忆、资源、技能
- **分层上下文**: 多层级传递
- **自进化**: 持续学习改进

### 2. MemPalace (已整合)
**核心设计**: 四层记忆架构 + AAAK 压缩方言
- 工作记忆、情景记忆、语义记忆、程序记忆
- Agent 日记系统

### 3. Engram (2.3k stars)
**核心设计**: AI 编码 Agent 的持久化记忆
- SQLite + FTS5 全文搜索
- MCP Server 支持
- HTTP API + CLI + TUI 多接口

### 4. Memoh (1.4k stars)
**核心设计**: 自托管多平台 AI Agent 平台
- 支持 Telegram、Discord、Feishu、Matrix
- 长期记忆存储
- Docker 容器化部署

### 5. Phantom (1.2k stars)
**核心设计**: 拥有自己电脑的 AI 同事
- 自进化能力
- 持久化记忆 (Qdrant)
- MCP Server
- 安全凭证收集
- 自建基础设施能力

### 6. Agent-Reach (已安装)
**核心设计**: 互联网眼睛
- 11+ 平台数据获取
- 统一 API

---

## 二、统一架构设计

```
┌──────────────────────────────────────────────────────────────┐
│                    统一记忆系统 v2.0                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              多平台接入层 (Memoh 风格)               │   │
│  │  Feishu | Telegram | Discord | Matrix | Email | Web  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              四层记忆栈 (MemPalace 架构)             │   │
│  │                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────┐│   │
│  │  │ 工作记忆 │  │ 情景记忆 │  │ 语义记忆 │  │程序  ││   │
│  │  │ Working  │  │ Episodic │  │ Semantic │  │Proc. ││   │
│  │  │ TTL缓存  │  │ 事件经历 │  │ 知识图谱 │  │技能  ││   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────┘│   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────────┐│   │
│  │  │           Agent 日记 (AAAK 压缩格式)            ││   │
│  │  └─────────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              持久化存储层 (混合方案)                 │   │
│  │                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ SQLite     │  │ LanceDB    │  │ Qdrant     │    │   │
│  │  │ 结构化存储 │  │ 本地向量   │  │ 云端向量   │    │   │
│  │  │ (左脑)     │  │ (右脑本地) │  │ (可选)     │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                      │   │
│  │  ┌────────────┐  ┌────────────┐                    │   │
│  │  │ FTS5       │  │ ChromaDB   │ (备选)             │   │
│  │  │ 全文搜索   │  │ 向量备选   │                    │   │
│  │  └────────────┘  └────────────┘                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              服务接口层 (多协议支持)                 │   │
│  │                                                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ MCP Server │  │ HTTP API   │  │ CLI        │    │   │
│  │  │ (Engram)   │  │ (Phantom)  │  │ (Engram)   │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              互联网获取层 (Agent-Reach)              │   │
│  │                                                      │   │
│  │  GitHub | Web | YouTube | B站 | 微博 | 小红书 | ...  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 三、核心表结构升级

### 1. 多平台消息表 (Memoh 风格)
```sql
CREATE TABLE platform_messages (
    id INTEGER PRIMARY KEY,
    platform TEXT NOT NULL,  -- feishu, telegram, discord, matrix
    channel_id TEXT NOT NULL,
    sender_id TEXT,
    message_type TEXT,
    content TEXT,
    metadata JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_platform_channel (platform, channel_id)
);
```

### 2. 自进化记录表 (Phantom 风格)
```sql
CREATE TABLE evolution_log (
    id INTEGER PRIMARY KEY,
    evolution_type TEXT,  -- skill_gained, tool_created, capability_extended
    description TEXT,
    before_state JSON,
    after_state JSON,
    trigger TEXT,  -- user_request, self_discovered, scheduled
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3. 凭证安全表 (Phantom 风格)
```sql
CREATE TABLE secure_credentials (
    id INTEGER PRIMARY KEY,
    service_name TEXT UNIQUE NOT NULL,
    credential_type TEXT,  -- api_key, token, password
    encrypted_value BLOB,
    encryption_key_ref TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used_at DATETIME,
    expires_at DATETIME
);
```

### 4. 工具注册表 (OpenViking 风格)
```sql
CREATE TABLE registered_tools (
    id INTEGER PRIMARY KEY,
    tool_name TEXT UNIQUE NOT NULL,
    tool_type TEXT,  -- mcp, http, cli, builtin
    endpoint TEXT,
    description TEXT,
    capabilities JSON,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    last_used DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5. 分层上下文表 (OpenViking 风格)
```sql
CREATE TABLE layered_context (
    id INTEGER PRIMARY KEY,
    layer_level INTEGER,  -- 1=session, 2=task, 3=project, 4=global
    context_key TEXT NOT NULL,
    context_value JSON,
    parent_context_id INTEGER,
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 四、关键特性整合

### 1. 自进化能力 (来自 Phantom)
```python
async def evolve_self(self):
    """自我进化循环"""
    # 1. 检测自身能力缺口
    gaps = await self.detect_capability_gaps()
    
    # 2. 搜索解决方案
    for gap in gaps:
        solution = await self.search_solution(gap)
        
    # 3. 实施改进
        if solution:
            await self.implement_solution(solution)
            await self.log_evolution(gap, solution)
    
    # 4. 注册新能力
    await self.register_new_capabilities()
```

### 2. 多平台消息处理 (来自 Memoh)
```python
async def handle_platform_message(self, platform, message):
    """统一平台消息处理"""
    # 存储到统一消息表
    msg_id = await self.store_message(platform, message)
    
    # 根据平台类型处理
    handler = self.get_platform_handler(platform)
    response = await handler.process(message)
    
    # 记录到情景记忆
    await self.add_episodic(
        event_type=f'{platform}_message',
        content=message.content,
        metadata={'msg_id': msg_id}
    )
    
    return response
```

### 3. 分层上下文传递 (来自 OpenViking)
```python
def get_context_for_layer(self, layer_level):
    """获取指定层级的上下文"""
    contexts = []
    current_layer = layer_level
    
    while current_layer >= 1:
        ctx = self.query(
            "SELECT * FROM layered_context WHERE layer_level = ?",
            current_layer
        )
        contexts.extend(ctx)
        current_layer -= 1
    
    return self.merge_contexts(contexts)
```

### 4. MCP Server 工具集 (来自 Engram)
```python
# MCP 工具定义
MCP_TOOLS = {
    # 读工具
    'memory_status': '获取记忆系统状态',
    'memory_search': '搜索记忆内容',
    'memory_get': '获取指定记忆',
    'kg_query': '查询知识图谱',
    
    # 写工具
    'memory_add': '添加新记忆',
    'diary_write': '写 Agent 日记',
    'kg_add_relation': '添加知识关系',
    
    # 进化工具
    'evolution_log': '查看进化日志',
    'tool_register': '注册新工具',
}
```

---

## 五、部署方案

### 方案 A: 轻量级 (保持现状)
- SQLite + LanceDB
- 无需额外服务
- 适合个人使用

### 方案 B: 中量级 (推荐)
- SQLite + LanceDB + Qdrant (可选)
- MCP Server
- HTTP API
- 适合小团队

### 方案 C: 完整版 (企业级)
- SQLite + Qdrant (云端)
- 多平台接入
- 自进化能力
- 完整监控
- Docker 部署
- 适合团队协作

---

## 六、下一步行动

1. **立即可做**:
   - 创建新数据库表
   - 添加多平台消息处理
   - 实现 MCP Server 工具

2. **短期优化**:
   - 添加自进化循环
   - 实现分层上下文
   - 凭证加密存储

3. **长期目标**:
   - Qdrant 云端向量支持
   - Docker 容器化
   - 多 Agent 协作

---

整合时间: 2026-04-08
来源项目: OpenViking, MemPalace, Engram, Memoh, Phantom, Agent-Reach
