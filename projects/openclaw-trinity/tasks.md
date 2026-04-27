# OpenClaw Trinity Tasks

## 目标

把 OpenClaw Trinity 从“概念整合”推进到“可演示、可迭代、可上线”的状态。

---

## P0：最优先任务

### 1. 固定主叙事
- [ ] 统一对外名称
- [ ] 统一一句话定位
- [ ] 统一三层角色描述：OpenClaw / Hermes / Claude Code
- [ ] 把 memory/ 明确为长期上下文层

### 2. 固定主链路
- [ ] 聊天入口 → OpenClaw 接收任务
- [ ] coding 任务 → Claude Code
- [ ] 结果回传 → OpenClaw 统一入口
- [ ] 长期价值信息 → memory/

### 3. 固定主 demo
- [ ] 选择一个真实 demo 场景
- [ ] 输出 demo 讲解脚本
- [ ] 输出 demo 截图 / 录屏清单

---

## P1：产品层任务

### 4. 完善项目文档
- [ ] README 持续收敛
- [ ] workflow.md 完善为更细的执行流程
- [ ] routing-rules.md 增加更多真实判断例子
- [ ] demo.md 增加视频 / 截图建议

### 5. 完善站点内容
- [ ] 在 uuoo.site 增加 Trinity 区块
- [ ] 在 uuoo.site 增加 Token Optimizer 区块
- [ ] 增加最近更新区
- [ ] 增加演示展示区

### 6. 完善宣传材料
- [ ] GitHub Release 文案
- [ ] 中文宣传文案
- [ ] 英文宣传文案
- [ ] 官网展示图 / 封面图

---

## P2：整合层任务

### 7. 明确路由规则
- [ ] 定义普通任务与 coding 任务边界
- [ ] 定义 Hermes 进入条件
- [ ] 定义什么内容需要沉淀到 memory/

### 8. 明确执行路径
- [ ] OpenClaw 作为统一入口
- [ ] Claude Code 作为高价值 coding 路径
- [ ] Hermes 作为第二执行路径
- [ ] 结果统一回流到会话入口

### 9. 明确记忆沉淀方式
- [ ] 什么进入 events/
- [ ] 什么进入 learnings/
- [ ] 什么进入 preferences/
- [ ] 什么进入 skills/
- [ ] 什么进入 improvements.md

---

## P3：后续增强

### 10. 面向真实使用的增强
- [ ] 更具体的 setup 指南
- [ ] 更具体的 repo-task 模板
- [ ] 更具体的工作流模板
- [ ] 更具体的错误恢复 / 回退说明

### 11. 面向演示的增强
- [ ] 终端录屏
- [ ] Before / After 图
- [ ] 单页产品图
- [ ] 社媒封面图

### 12. 面向长期维护的增强
- [ ] 定期更新最近进展
- [ ] 让站点与仓库内容保持同步
- [ ] 把每次关键经验沉淀进 memory/

---

## 当前建议

第一优先级只做一件事：

> **把“聊天入口 → coding 路由 → 结果回传 → 记忆沉淀”这条主链稳定下来。**

这条链一旦稳定，后面所有扩展都会顺很多。
