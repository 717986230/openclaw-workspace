# OpenClaw Trinity

**OpenClaw + Hermes + Claude Code in one operator workflow.**

OpenClaw Trinity 是这个 workspace 当前最重要的整合方向。

它不是简单把三个名字摆在一起，而是明确三者的角色分工：

- **OpenClaw** = control plane / 会话与渠道控制层
- **Hermes** = runtime path / ACP 风格运行时能力路径
- **Claude Code** = coding engine / 仓库分析与代码执行引擎
- **memory/** = long-term context / 长期记忆与经验沉淀层

---

## 一句话定位

**一个把聊天入口、任务路由、代码执行、长期记忆整合到一起的 AI 工作台。**

---

## 为什么要这样整合

很多 AI 项目只强在一个层面：

- 有的擅长聊天入口
- 有的擅长 agent runtime
- 有的擅长代码执行
- 但很少有项目能把“入口、路由、执行、记忆”放在一个连续工作流里

OpenClaw Trinity 的目标，就是把这些层连接起来。

---

## 系统分层

### 1. OpenClaw
负责：
- 控制平面
- 渠道接入
- 会话与路由
- 审批与反馈
- 长驻助手体验

### 2. Hermes
负责：
- 运行时路径
- ACP 风格能力接入
- 非 coding-first 的 runtime 扩展能力

### 3. Claude Code
负责：
- 仓库分析
- 代码修改
- 调试与实现任务
- PR / 代码工作流

### 4. memory/
负责：
- 长期知识
- 个人偏好
- 项目经验
- 架构决策与演进记录

---

## 最强使用场景

### 从聊天发起代码任务

一个理想流程应该是：

1. 用户从聊天入口发起任务
2. OpenClaw 接收并判断任务类型
3. coding 类任务交给 Claude Code
4. runtime / ACP 类任务可交给 Hermes
5. 结果再回到 OpenClaw 的统一会话界面
6. 经验与偏好进入 memory/，供后续持续复用

---

## 与普通“项目集合”有什么不同

OpenClaw Trinity 不是：
- 一堆独立工具仓库
- 一堆零散 README
- 一个只强调技术名词的概念页

它应该是：
- 有明确角色分工
- 有连续工作流
- 有长期记忆沉淀
- 有可演示、可迭代、可对外传播的产品叙事

---

## 当前仓库里的定位

在这个 `openclaw-workspace` 里：

- `projects/openclaw-trinity/` 负责产品层
- `skills/` 负责能力层
- `memory/` 负责长期记忆层
- `docs/` 负责对外材料与计划

这意味着 Trinity 不是外置于你的记忆系统之外，而是建立在它之上。

---

## 下一步

- 补 setup 文档
- 补 routing workflow 文档
- 补 demo 场景
- 补对外展示素材

---

## 推荐标语

- Route smarter. Code faster. Stay in control.
- From chat to code delivery in one operator workflow.
- 项目负责运行，记忆负责延续。
