# 二饼运行记忆

## 运行规则

- 回答任何涉及历史决策、配置、数据库路径、服务状态、账号、渠道、偏好、待办的问题前，先查 `MEMORY.md` 和 `memory/*.md`。
- 与 OpenClaw 运行相关的问题，优先检查 `C:\Users\admin\.openclaw\openclaw.json`、`C:\tmp\openclaw\openclaw-YYYY-MM-DD.log`、`C:\Users\admin\.openclaw\workspace-bingbu`。
- 与 edict 数据相关的问题，优先检查 `C:\Users\admin\Documents\New project\edict\data`，不要假设数据库路径在当前工作区里。

## 当前固定事实

- OpenClaw 当前只保留一个角色：`main / 二饼`。
- 当前角色工作区：`C:\Users\admin\.openclaw\workspace-bingbu`。
- Discord 中的“伞兵”对应 OpenClaw 里的“二饼”。
- OpenClaw gateway 当前端口：`18789`。
- 当前保留的模型 provider：`openai`、`volcengine`、`scnet`。

## 数据路径

- edict 项目根目录：`C:\Users\admin\Documents\New project\edict`
- edict 共享数据目录：`C:\Users\admin\Documents\New project\edict\data`
- 工作区回到 edict 根目录的标记文件：`.edict_repo_root`

## 已知约束

- 机器直连外网不稳定，很多外部请求需要走 `http://127.0.0.1:7890`。
- OpenAI embeddings 当前额度不可用；记忆检索需要优先依赖本地文本索引，不要假设向量检索一定可用。
