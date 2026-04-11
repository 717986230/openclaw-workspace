---
name: memory-system-complete
version: "1.2.1"
description: Complete memory system with SQLite left brain and LanceDB right brain
author: Erbing
license: MIT
keywords:
  - memory
  - sqlite
  - lancedb
  - rag
  - database
  - persistence
  - vector-search
category: productivity
requires:
  - python >= 3.7
  - sqlite3
  - lancedb >= 0.3.0 (optional, for vector search)
  - sentence-transformers >= 2.0.0 (optional, for embeddings)
install:
  post_install: |
    # Create database directory
    mkdir -p memory/database
    
    # Initialize database
    python scripts/init_database.py
    
    # Verify installation
    python scripts/verify_install.py
---

# Memory System Complete

**双脑记忆系统：SQLite左脑 + LanceDB右脑**

## 功能介绍

完整的记忆管理系统，支持：
- ✅ 结构化记忆存储（SQLite）
- ✅ 语义向量搜索（LanceDB）
- ✅ 自动清理和优化
- ✅ 完整CRUD操作
- ✅ 导入/导出功能
- ✅ 自动安装和验证
- ✅ Theory of Mind (ToM) 心智模型
- ✅ 情感分析（EQ改进）
- ✅ 增强检索系统（Memory改进）
- ✅ 相关记忆检测
- ✅ 热门记忆分析
- ✅ **Ollama本地模型嵌入**（v1.2.1新增）
- ✅ **语义搜索支持**（v1.2.1新增）

**⚠️ 重要说明**

此技能**不包含任何预置的记忆数据**。

安装后，用户将获得：
- ✅ 空的记忆系统架构
- ✅ 数据库初始化脚本
- ✅ 完整的API工具
- ✅ 使用文档和示例

用户需要根据自己的需求添加记忆数据。

---

## 安装后配置

### 1. 自动初始化
安装后运行以下命令初始化数据库：

```bash
# 初始化数据库
python scripts/init_database.py

# 或使用Python API
from memory_system import MemorySystem
memory = MemorySystem()
memory.initialize()
```

### 2. 数据库位置
数据库文件将创建在：
- SQLite: `memory/database/xiaozhi_memory.db`
- LanceDB: `memory/database/lancedb/`

### 3. 目录结构
安装后的目录结构：
```
memory-system-complete/
├── scripts/
│   ├── memory_system.py       # 核心代码
│   ├── init_database.py       # 数据库初始化
│   └── verify_install.py      # 安装验证
├── examples/
│   └── usage_demo.py          # 使用示例
├── memory/
│   └── database/              # 数据库目录（空）
│       ├── xiaozhi_memory.db  # 安装后创建
│       └── lancedb/           # 安装后创建
├── SKILL.md
└── README.md
```

---

## 安装验证

### 方法1: 自动验证脚本
```bash
python scripts/verify_install.py
```

### 方法2: 手动验证
```python
from memory_system import MemorySystem

# 初始化
memory = MemorySystem()
success = memory.initialize()

if success:
    print("✅ Installation verified!")
    
    # 保存测试记忆
    test_id = memory.save(
        type='test',
        title='Installation Test',
        content='Testing memory system installation',
        importance=5
    )
    
    # 查询测试
    result = memory.get(test_id)
    if result:
        print("✅ Memory system working!")
        memory.delete(test_id)  # 清理测试数据
    else:
        print("❌ Memory system failed!")
else:
    print("❌ Initialization failed!")
```

---

## 环境配置

### 自动配置
安装脚本会自动：
1. ✅ 检查Python版本 (>= 3.7)
2. ✅ 创建数据库目录
3. ✅ 初始化SQLite数据库
4. ✅ 创建必要的索引
5. ✅ 验证LanceDB可用性（可选）

### Ollama配置（可选，v1.2.1新增）

#### 安装Ollama
```bash
# 下载并安装Ollama
# 访问: https://ollama.com

# 拉取嵌入模型
ollama pull nomic-embed-text  # 轻量级（768维，274MB）
# 或
ollama pull mxbai-embed-large  # 高精度（1024维，669MB）
# 或
ollama pull all-minilm  # 超轻量（384维，120MB）

# 启动Ollama服务
ollama serve
```

#### 使用Ollama语义搜索
```python
from memory_system import MemorySystem

# 配置使用Ollama
config = {
    'use_ollama': True,
    'ollama_model': 'nomic-embed-text',
    'ollama_url': 'http://localhost:11434'
}

memory = MemorySystem(config=config)
memory.initialize()

# 语义搜索（使用Ollama嵌入）
results = memory.search("python best practices")
print(f"Found {len(results)} related memories")
```

#### Ollama模型对比
| 模型 | 维度 | 大小 | 特点 | 适用场景 |
|------|------|------|------|----------|
| nomic-embed-text | 768 | 274MB | 轻量级，速度快 | 通用场景 |
| mxbai-embed-large | 1024 | 669MB | 高精度，效果好 | 精确匹配 |
| all-minilm | 384 | 120MB | 超轻量 | 资源受限 |

#### Ollama故障排除
```bash
# 检查Ollama服务状态
curl http://localhost:11434/api/tags

# 查看已安装模型
ollama list

# 重新拉取模型
ollama pull nomic-embed-text

# 重启Ollama服务
ollama serve
```

### 手动配置（如需）

#### 依赖安装
```bash
# 基础依赖（SQLite已包含在Python中）
# 无需额外安装

# 可选依赖（用于向量搜索）
pip install lancedb>=0.3.0
pip install sentence-transformers>=2.0.0
```

#### 数据库配置
```python
# 自定义数据库路径
from memory_system import MemorySystem

config = {
    'db_path': '/custom/path/memory.db',
    'vector_db': '/custom/path/lancedb',
    'min_confidence': 0.3,
    'cleanup_interval_days': 90
}

memory = MemorySystem(config)
memory.initialize()
```

---

## 数据库自动创建

### ✅ 会被自动创建
- `memory/database/xiaozhi_memory.db` - SQLite数据库文件
- `memory/database/lancedb/` - LanceDB向量数据库
- `memory/database/backups/` - 备份目录

### ❌ 不会被创建
- 预置的记忆数据
- 测试数据
- 示例数据

---

## 首次使用流程

### 1. 安装技能
```bash
clawhub install memory-system-complete
```

### 2. 初始化数据库
```bash
cd ~/.openclaw/skills/memory-system-complete
python scripts/init_database.py
```

### 3. 验证安装
```bash
python scripts/verify_install.py
```

### 4. 开始使用
```python
from memory_system import MemorySystem

memory = MemorySystem()
memory.initialize()

# 保存第一条记忆
memory.save(
    type='learning',
    title='My First Memory',
    content='This is my first memory in the system',
    importance=7
)

print("Memory system ready!")
```

---

## 环境要求

### 必需
- Python 3.7+
- SQLite3（Python标准库）

### 可选（用于向量搜索）
- LanceDB >= 0.3.0
- sentence-transformers >= 2.0.0
- numpy >= 1.20.0

---

## 故障排除

### 问题1: 数据库初始化失败
```bash
# 检查权限
chmod +w memory/database

# 重新初始化
python scripts/init_database.py --force
```

### 问题2: LanceDB不可用
```bash
# 安装LanceDB
pip install lancedb

# 或使用纯SQLite模式
# 系统会自动降级到文本搜索
```

### 问题3: Python版本不兼容
```bash
# 检查Python版本
python --version

# 需要 >= 3.7
```

---

## 重要提醒

### ✅ 此技能提供
- 完整的内存管理架构
- 数据库初始化工具
- CRUD操作API
- 自动清理机制
- 安装验证脚本

### ❌ 此技能不提供
- 预置的记忆数据
- 示例数据库内容
- 用户数据迁移
- 云端同步功能

---

## 数据隐私

- 所有记忆数据存储在用户本地
- 不上传到云端
- 不共享给第三方
- 用户完全控制数据

---

*更新时间: 2026-04-11*
*版本: 1.1.0*

---

## Changelog

### v1.2.1 (2026-04-11)
- Added Ollama local model embedding support
- Added semantic search with Ollama embeddings
- Added Ollama configuration documentation
- Added Ollama model comparison table
- Improved search method with Ollama fallback
- Added Ollama troubleshooting guide

### v1.2.0 (2026-04-11)
- Added Theory of Mind (ToM) engine for cognitive modeling
- Added Emotional Analyzer for EQ improvement (Clawvard)
- Added Enhanced Retrieval system for Memory improvement (Clawvard)
- Added semantic search capabilities
- Added related memory detection
- Added trending memory analysis
- Added comprehensive statistics

### v1.1.1 (2026-04-11)
- Added Chinese language documentation
- Improved bilingual support for Chinese users
- Added Chinese feature descriptions

### v1.1.0 (2026-04-11)
- Added automatic database initialization script (`init_database.py`)
- Added installation verification script (`verify_install.py`)
- Improved installation documentation with step-by-step guide
- Added automatic directory structure creation
- Added LanceDB availability check
- Added sample data creation for first-time users
- Fixed Windows encoding issues (GBK compatibility)

### v1.0.0 (2026-04-11)
- Initial release
- SQLite + LanceDB dual-brain architecture
- Full CRUD operations
- Semantic search with embeddings
- Automatic cleanup and optimization
- Import/export functionality
