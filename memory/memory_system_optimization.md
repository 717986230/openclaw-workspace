# 记忆系统优化文档

## 📊 优化状态

### ✅ 阶段一已完成 (2026-04-17)

| 优化项 | 状态 | 说明 |
|--------|------|------|
| FTS5 全文搜索 | ✅ 已启用 | `memories_fts` 表，277 条记录 |
| 凭证安全存储 | ✅ 已创建 | `secure_credentials` 表 |
| 工具注册表增强 | ✅ 已增强 | 添加 `metadata` 字段 |
| MCP Server 配置 | ✅ 已创建 | `scripts/mcp_tools_config.json` |
| 状态检查工具 | ✅ 已创建 | `scripts/memory_status.py` |

### 📈 当前系统统计

- **总记忆数**: 277
  - 情景记忆: 1
  - 语义记忆: 4
  - 程序记忆: 0
- **平台消息**: 1
- **进化日志**: 3
- **注册工具**: 2
- **FTS5 索引**: ✅ 已启用

---

## 🔧 已实施优化详解

### 1. FTS5 全文搜索

**功能**: 快速关键词搜索记忆内容

**使用方法**:
```sql
-- 搜索包含"记忆"的记录
SELECT * FROM memories_fts WHERE memories_fts MATCH '记忆';

-- 搜索标题包含"优化"的记录
SELECT * FROM memories_fts WHERE title MATCH '优化';

-- 组合搜索
SELECT m.* FROM memories m
INNER JOIN memories_fts fts ON m.id = fts.rowid
WHERE memories_fts MATCH '系统 AND 优化';
```

**自动同步**:
- 新增记忆 → 自动加入 FTS5 索引
- 删除记忆 → 自动从 FTS5 移除
- 更新记忆 → FTS5 自动更新

**性能提升**:
- 关键词搜索速度提升 10-100 倍
- 支持模糊匹配和布尔逻辑

---

### 2. 凭证安全存储

**表结构**:
```sql
CREATE TABLE secure_credentials (
    id INTEGER PRIMARY KEY,
    service_name TEXT UNIQUE NOT NULL,  -- 如 "feishu", "discord"
    credential_type TEXT,               -- "api_key", "token", "password"
    encrypted_value BLOB,               -- 加密后的值
    encryption_key_ref TEXT,            -- 密钥引用
    description TEXT,                   -- 描述
    created_at DATETIME,
    last_used_at DATETIME,
    expires_at DATETIME,                -- 过期时间
    metadata TEXT                       -- 额外信息
);
```

**使用建议**:
```python
# 存储凭证 (示例)
encrypted = encrypt(api_key)  # 使用 AES 加密
cursor.execute("""
    INSERT INTO secure_credentials 
    (service_name, credential_type, encrypted_value, expires_at)
    VALUES (?, ?, ?, ?)
""", ('feishu', 'api_key', encrypted, '2027-04-17'))

# 读取凭证
cursor.execute("""
    SELECT encrypted_value FROM secure_credentials 
    WHERE service_name = ?
""", ('feishu',))
decrypted = decrypt(result[0])
```

**⚠️ 安全提示**: 
- 必须使用加密存储，不要明文保存
- 建议配合环境变量或密钥管理服务

---

### 3. 工具注册表增强

**新增字段**:
- `metadata`: JSON 格式的额外信息
- 已存在字段: `success_count`, `fail_count`, `last_used`

**用途**:
- 追踪工具使用频率
- 统计成功/失败率
- 记录工具元数据

**示例**:
```sql
-- 注册新工具
INSERT INTO registered_tools 
(tool_name, tool_type, description, capabilities, metadata)
VALUES 
('memory_search', 'mcp', '搜索记忆', '["search", "filter"]', 
 '{"version": "1.0", "author": "erbing"}');

-- 更新使用统计
UPDATE registered_tools 
SET success_count = success_count + 1, last_used = CURRENT_TIMESTAMP
WHERE tool_name = 'memory_search';

-- 查询最常用工具
SELECT tool_name, success_count, fail_count 
FROM registered_tools 
ORDER BY success_count DESC LIMIT 10;
```

---

### 4. MCP Server 工具配置

**配置文件**: `scripts/mcp_tools_config.json`

**可用工具**:

| 工具名 | 功能 | 参数示例 |
|--------|------|----------|
| `memory_search` | 搜索记忆 | `{"query": "优化", "limit": 10}` |
| `memory_add` | 添加记忆 | `{"type": "learning", "title": "xxx", "content": "xxx"}` |
| `memory_status` | 系统状态 | `{}` |
| `diary_write` | 写日记 | `{"date": "2026-04-17", "summary": "xxx"}` |
| `evolution_log` | 进化日志 | `{"limit": 10}` |
| `tool_register` | 注册工具 | `{"tool_name": "xxx", "tool_type": "mcp"}` |

**MCP 集成示例**:
```json
{
  "mcpServers": {
    "memory-system": {
      "command": "python",
      "args": ["scripts/mcp_server.py"],
      "env": {
        "DB_PATH": "memory/database/xiaozhi_memory.db"
      }
    }
  }
}
```

---

## 🛠️ 工具脚本

### 状态检查
```bash
python scripts/memory_status.py
```

输出示例:
```
==================================================
记忆系统状态报告
==================================================
记忆总数：277
  - 情景记忆：1
  - 语义记忆：4
  - 程序记忆：0
平台消息：1
进化日志：3
注册工具：2
FTS5 索引：已启用
==================================================
```

### FTS5 测试
```bash
python scripts/test_fts5.py
```

### 执行优化
```bash
python scripts/memory_optimize_phase1.py  # 阶段一
python scripts/memory_optimize_phase2.py  # 阶段二 (待创建)
```

---

## 📅 下一步计划

### 阶段二 (短期优化)
- [ ] 实现分层上下文管理 (session/task/project/global)
- [ ] 添加批量写入优化
- [ ] 实现自进化循环检测
- [ ] 创建 MCP Server 服务端实现

### 阶段三 (长期目标)
- [ ] Qdrant 云端向量支持
- [ ] 知识图谱可视化
- [ ] Docker 容器化部署
- [ ] 多 Agent 协作支持

---

## 📖 使用示例

### 快速搜索记忆
```python
import sqlite3

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 使用 FTS5 搜索
cursor.execute("""
    SELECT m.id, m.title, m.content, m.created_at
    FROM memories m
    INNER JOIN memories_fts fts ON m.id = fts.rowid
    WHERE memories_fts MATCH '系统'
    ORDER BY m.importance DESC
    LIMIT 10
""")

results = cursor.fetchall()
for row in results:
    print(f"[{row[3]}] {row[1]}")
    print(f"  {row[2][:100]}...\n")

conn.close()
```

### 安全存储 API Key
```python
from cryptography.fernet import Fernet
import sqlite3

# 生成密钥 (只生成一次，保存到安全位置)
# key = Fernet.generate_key()
cipher = Fernet(b'your-secret-key-here')

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 加密并存储
api_key = b'your-api-key'
encrypted = cipher.encrypt(api_key)

cursor.execute("""
    INSERT OR REPLACE INTO secure_credentials 
    (service_name, credential_type, encrypted_value, expires_at)
    VALUES (?, ?, ?, ?)
""", ('my-service', 'api_key', encrypted, '2027-01-01'))

conn.commit()
conn.close()
```

---

## 📝 更新日志

- **2026-04-17**: 完成阶段一优化
  - ✅ FTS5 全文搜索启用
  - ✅ 凭证安全存储表创建
  - ✅ 工具注册表增强
  - ✅ MCP 工具配置创建
  - ✅ 状态检查工具创建

---

*文档维护：Erbing 🦐*
*最后更新：2026-04-17 10:05*
