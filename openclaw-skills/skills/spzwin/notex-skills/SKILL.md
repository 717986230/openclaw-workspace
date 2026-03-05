---
name: notex-skills
description: 工作协同系统 CWork Key 授权入口，提供两套核心大模型能力。其一为 8 种内容创作技能（PPT、脑图等）的异步轮询生成；其二为 OPS 运营管理智能助手（ops-chat）的同步数据洞察接口。
---

# NoteX Skills — 通用技能路由网关

**当前版本**: v1.1 | **接入渠道**: `CWork Key` 鉴权

本网关提供两套截然不同的 API 范式，分别对应**内容创作引擎**与**运营洞察助手**。

---

## 1. 核心鉴权 (Authentication)

无论调用哪种技能，**第一步**必须用工作协同系统的 `CWork Key` 换取长期访问令牌。

```http
GET https://cwork-web.mediportal.com.cn/user/login/appkey?appCode=cms_gpt&appKey={CWork Key}
```

**成功响应**将返回三个核心鉴权字段，请在后续所有业务请求的 Header 中携带：
- `x-user-id` -> 对应响应中的 `userId`
- `access-token` -> 对应响应中的 `xgToken`
- `personId` -> 对应响应中的 `personId` (部分旧接口需放在 Header)

> ✅ **最佳实践**：获取到 Token 后应在会话中缓存，绝对不要在同一段对话中反复让用户输入 Key。

---

## 2. 内容创作类技能 (Asynchronous Creator)

覆盖从文本整理到视频渲染的 8 种高发算力场景，采用**队列投递 + 异步轮询**架构。

### 2.1 支持的创作技能 (`skill` 参数)
| 技能 ID | 产物形式 | 必填参数附加约束 | 预计渲染 |
|---|---|---|---|
| `slide` | PPT 演示文稿 | 需明确视觉风格 | 3~5 分钟 |
| `infographic` | 数据信息图 | 需明确配色风格 | 2~4 分钟 |
| `video` | 视频播客 | (无) | 5~10 分钟 |
| `audio` | 纯音频播客 | (无) | 3~6 分钟 |
| `report` | 深度分析报告 | (无) | 1~3 分钟 |
| `mindmap` | 结构化思维导图 | (无) | 1~2 分钟 |
| `quiz` | 测验练习题 | (无) | 1~2 分钟 |
| `flashcards` | 记忆闪卡 | (无) | 1~2 分钟 |

### 2.2 API 调用链路 (两步走)

**Step A: 投递异步任务**
```http
POST https://notex.aishuo.co/noteX/api/trilateral/autoTask
authorization: BP
x-user-id: {换取的userId}
access-token: {换取的xgToken}
personId: {换取的personId}
Content-Type: application/json

{
  "bizId": "skills_1709000000000",
  "bizType": "TRILATERA_SKILLS",
  "skills": ["slide"],
  "require": "商务简约风格，蓝白配色",
  "sources": [{"id": "src_001", "title": "标题", "content_text": "原文素材..."}]
}
```
*(响应返回 `taskId`)*

**Step B: 轮询结果直到完结**
```http
GET https://notex.aishuo.co/noteX/api/trilateral/taskStatus/{taskId}
```
*(每 60 秒轮询一次，最多 **20 次**，即最大超时时间 20 分钟；直到 `task_status` 为 `COMPLETED`，凭借返回的 `url` + `&token={xgToken}` 组成最终查阅链接提交给用户)*

> 🌟 **大模型引导与越权拦截策略**：
> 关于如何向用户索要必要参数（针对不同形式索要时长或风格等），以及如何礼貌拒绝意图越权（例如：当用户要求“生成 Excel 或下载成 Word 文件”时，应明确拒绝并引导转化成支持的『分析报告』或『思维导图』），请务必参考系统内置的设定话术档案：👉 [`examples/notex-creator.md`](./examples/notex-creator.md)

---

## 3. OPS 运营数据洞察 (`ops-chat`)

专为内部系统后台打造的智能问答通道，对接 15 个底层观测本体工具（Function Calling），采用**短轮询 / 同步流式长连接**架构。

### 3.1 核心能力与权限
- 本技能强制校验用户的 `canViewOpsData` 内部查阅权限，无权限者统一拦截 403。
- 覆盖大盘看板统计、科室/项目组活跃排行、精准追踪某医生的流失节点、异常报错根因聚合分析等。

### 3.2 API 调用链路 (单发同步等待)

此接口内部将执行多达数十步的 ReAct 循环推理，网络超时上限需严格设定为 **300,000ms (5分钟)**。


```http
POST {OPS_BASE_URL}/noteX/api/ops/ai-chat
authorization: BP
x-user-id: {换取的userId}
access-token: {换取的xgToken}
Content-Type: application/json

{
  "message": "帮我查一下林总最近一周的操作失误告警？"
}
```

**响应报文**：
```json
{
  "reply": "根据底盘数据，林总（ID: 102x）近期共发生了...",
  "historyCount": 3
}
```
*(注：服务端已自动记忆最近 6 轮对话上下文，客户端无需再次拼接历史)*

> 🌟 **大模型引导策略**：关于 15 个核心本体的逻辑链式拆解，以及遇到多名同姓氏用户时的追问确认协议，请查阅专属的管家设定指南：� [`examples/ops-assistant.md`](./examples/ops-assistant.md)

---

## 4. 相关依赖文件说明

| 文件/目录 | 用途描述 |
|---|---|
| `/examples/` | **强烈建议阅读**。存放了对应两大分类系统的“系统内置提示词 (System Prompt)”极佳案例。定义了 Agent 应该具备的话术边界与追问法则。 |
| `/scripts/skills-run.js` | Node.js 测试桩代码。开发者可通过此脚本直接在终端体验鉴权、发起任务与并发轮询的全套完整生命周期。 |
