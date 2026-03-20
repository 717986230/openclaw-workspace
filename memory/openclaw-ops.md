# OpenClaw 运维约定

## 排障顺序

1. 先确认端口和渠道是否在线。
2. 再看最新日志。
3. 涉及数据库、记忆、检索时，先确认 `memory` 目录和索引状态。
4. 涉及 edict 数据同步时，确认 `.edict_repo_root` 和 `edict\data` 是否可达。

## 常用位置

- 主配置：`C:\Users\admin\.openclaw\openclaw.json`
- 活跃日志：`C:\tmp\openclaw\openclaw-2026-03-16.log`
- 工作区状态：`C:\Users\admin\.openclaw\workspace-bingbu\.openclaw\workspace-state.json`

## 当前目标

- 保持单角色模式，不再恢复三省六部目录结构。
- 优先保证 Discord / Feishu 消息可达。
- 记忆检索必须先查本地文本索引，外部 embeddings 只作为增强能力，不作为硬依赖。
