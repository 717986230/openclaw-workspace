# 记忆数据库设计

## 选择的数据库
- SQLite（轻量级，单文件，无需服务器）

## 表结构

### memories 表 - 记忆主表
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,           -- event, learning, preference, skill, improvement
    title TEXT NOT NULL,
    content TEXT,
    category TEXT,
    tags TEXT,                    -- JSON array
    importance INTEGER DEFAULT 5,  -- 1-10
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT                 -- JSON
);
```

### memory_index 表 - 全文搜索索引
```sql
CREATE VIRTUAL TABLE memory_index USING FTS5(
    title,
    content,
    tags,
    content=memories,
    content_rowid=id
);
```

---
*设计时间：2026-03-02*
