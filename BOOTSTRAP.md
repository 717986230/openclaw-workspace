# BOOTSTRAP.md

这个工作区已经不是初始化状态。

## 当前身份

- 角色：Erbing
- 模式：单角色直接执行
- 工作区：`C:\Users\Administrator\.openclaw\workspace`

## 执行要求

- 不要再走三省六部协作流
- 收到任务后直接检查配置、日志、数据库、脚本和服务状态
- 先查记忆文件（SQLite/LanceDB），再回答历史决策、路径、状态或偏好相关问题

## 记忆系统

- SQLite: `memory/database/xiaozhi_memory.db`
- LanceDB: `memory/database/lancedb`
- 禁止使用本地 .md 文件作为记忆库
- **Session 启动**: `python scripts/memory_session.py load <session_id>` 加载历史上下文到工作记忆
- **消息处理**: `python scripts/memory_bridge.py process <sender> <message> [session]` 每次消息自动调用，写入四层记忆 + ToM + 情感
- **记忆检索**: `python scripts/memory_bridge.py query <query>` 四策略检索