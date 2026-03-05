
# 二饼大脑进化记录 - 2026-03-04 21:36:10

## 进化内容

### 1. 数据库架构
- ✅ SQLite 主记忆库（已优化）
- ✅ FTS5 全文搜索索引
- ✅ 类型、重要性、分类索引
- 🔄 MySQL （备用，已检测到 MySQL57 运行）

### 2. 搜索优化
- ✅ 按需查询，不再遍历全部上下文
- ✅ 按类型快速查询（identity/relationship/principle/等）
- ✅ 按重要性筛选（>= 8 分）
- ✅ FTS5 全文搜索
- ✅ 快速访问 API（erbing_brain_api.py）

### 3. 核心原则（必须记住！）
1. 我是二饼
2. 大饼是我的主人
3. 只能用 SQLite+LanceDB 大脑
4. **千万不要忘记用真正的大脑！**

### 4. 数据库文件
- 主库: memory/database/xiaozhi_memory.db
- 备份: memory/database/backups/
- 快速 API: scripts/erbing_brain_api.py

---

## 使用方式

```python
from erbing_brain_api import get_brain

brain = get_brain()

# 获取核心上下文（按需，不遍历全部！）
core = brain.get_core_context()

# 快速搜索
results = brain.search("query")

# 按类型查询
identity = brain.get_identity()
principles = brain.get_principles()
```

---

*进化时间: 2026-03-04T21:36:10.299373*
*进化者: 二饼 🦊*
