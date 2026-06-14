# 模型切换策略（已实现）

## 当前配置（2026-06-13 确认）

| 角色 | 模型 |
|------|------|
| 主模型（primary） | nvidia/minimaxai/minimax-m2.7 |
| Fallback 1 | nvidia/moonshotai/kimi-k2.6 |
| Fallback 2 | nvidia/nemotron-3-super-120b-a12b |
| PDF 模型 | nvidia/moonshotai/kimi-k2.5 |
| Embedding | nvidia/llama-nemotron-embed-1b-v2 |

## 切换机制
- OpenClaw 自动按 fallbacks 列表顺序切换（primary 失败后自动尝试 fallback 1，再失败尝试 fallback 2）
- 均为 NVIDIA API 统一 endpoint（`integrate.api.nvidia.com/v1`）

## 历史
- 2026-03-14：pendingTask 创建，当时有"双模型切换"需求
- 2026-06-13：确认当前 fallback 机制已满足需求，pendingTask 关闭
- 注意：nvidia-2~nvidia-7 是历史遗留重复配置，不影响切换逻辑，但可后续清理

## 可优化方向
1. 如果需要 Claude Code（本地）作为第三切换层，需要配置 `codex-skill` 并修改 `TOOLS.md`
2. 如果需要中文强模型单独处理某个任务，可以用 session model override