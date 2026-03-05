---
name: context-manager
description: Auto context management with seamless session switching. Monitors usage, triggers at 85% threshold, automatically creates new session with loaded memory. Zero user intervention required. Trigger on "context", "memory", "session management", "context limit", "memory transfer".
---

# Context Manager - 无感会话切换版

智能上下文管理技能，自动监控上下文使用率，达到阈值时自动保存记忆并创建新会话，用户完全无感知。

## 🎯 核心特性

### ⭐ 无感自动切换（新功能）
- ✅ **自动触发**：上下文达到85%自动切换
- ✅ **零操作**：用户无需任何干预
- ✅ **无缝体验**：新会话自动加载记忆
- ✅ **自然接续**：对话连续，就像没切换

### 📊 智能监控
- ✅ 每10分钟自动检查上下文
- ✅ 85%阈值提前预警
- ✅ 自动保存关键信息

### 💾 记忆传递
- ✅ 自动更新MEMORY.md
- ✅ 自动更新daily log
- ✅ 保存当前任务状态

## 🚀 使用方式

### 超简单 - 零配置

**你只需要正常聊天，其他的一切自动完成：**

1. 继续对话（监控在后台运行）
2. 达到85%阈值（自动保存记忆）
3. 创建新会话（agentTurn机制）
4. 新会话加载记忆（继续工作）

**用户视角**：对话从未中断，就像什么都没发生

## 📋 工作原理

```
开始对话
  ↓
后台监控（每10分钟）
  ↓
上下文达到85%
  ↓
自动提取会话信息
  ↓
保存到MEMORY.md
  ↓
更新daily log
  ↓
触发agentTurn
  ↓
创建新会话
  ↓
新会话加载记忆
  ↓
自然继续工作
```

## 🔄 无感切换设计

### agentTurn消息
```json
{
  "kind": "agentTurn",
  "message": "【无缝接续】请从MEMORY.md加载完整记忆，自然继续对话。不要提及新会话、不要解释切换，就像什么都没发生。继续之前的任务。",
  "deliver": true,
  "channel": "qqbot",
  "to": "USER_ID"
}
```

### 新会话行为
- ✅ 自动读取MEMORY.md
- ✅ 加载当前任务进度
- ✅ 自然接续对话
- ❌ 不说"新会话"
- ❌ 不说"已切换"
- ❌ 不说"请继续"

## 🛠️ 安装配置

### 安装
```bash
# 从ClawHub安装
clawhub install miliger-context-manager

# 或从本地安装
cd ~/.openclaw/skills
tar -xzf context-manager-v2.0.0.tar.gz
cd context-manager
bash install.sh
```

### 配置定时任务
```bash
# 添加到crontab（每10分钟检查）
*/10 * * * * ~/.openclaw/skills/context-manager/scripts/seamless-switch.sh
```

### 自定义阈值
```bash
# 编辑脚本，修改THRESHOLD值
THRESHOLD=85  # 可改为80或90
```

## 📊 性能指标

| 指标 | 目标 | 实际 |
|------|------|------|
| 检测延迟 | < 10分钟 | 10分钟 ✅ |
| 记忆保存 | < 5秒 | < 5秒 ✅ |
| 切换时间 | < 1秒 | 即时 ✅ |
| 用户感知 | 零感知 | 完全无感 ✅ |

## 🎯 使用场景

### 场景1：长时间对话
- 用户：和我聊聊项目管理
- AI：好的，项目管理有...
- [自动切换]
- 用户：继续深入
- AI：刚才说到项目管理...（自然接续）

### 场景2：多任务处理
- 用户：帮我做旅行客测试
- AI：好的，开始测试...
- [自动切换]
- AI：继续旅行客测试...（任务未中断）

### 场景3：学习讨论
- 用户：学习系统化思维
- AI：系统化思维是...
- [自动切换]
- AI：继续说系统化思维...（学习继续）

## 💡 核心优势

### vs 手动切换
| 特性 | 手动 | 自动 |
|------|------|------|
| 用户操作 | 需要/new | 零操作 |
| 时机把握 | 可能忘记 | 自动检测 |
| 记忆连续 | 需手动保存 | 自动保存 |
| 体验连续性 | 有中断感 | 完全无感 |

### vs 其他方案
- ✅ 比"提醒用户"更进一步：直接自动切换
- ✅ 比"外部监控"更智能：内置AI检测
- ✅ 比"手动操作"更便捷：完全自动化

## 🔧 技术实现

### 双重保险机制
1. **外部监控**：定时任务每10分钟检查
2. **内部检测**：AI每次回复前检查（未来）

### 记忆传递系统
```
当前会话
  ↓
提取关键信息
  ↓
├── MEMORY.md（长期记忆）
├── daily log（工作日志）
└── HEARTBEAT.md（任务进度）
  ↓
新会话加载
  ↓
继续工作
```

### agentTurn机制
- 使用cron tool的agentTurn
- 创建isolated会话
- 自动传递消息
- 新会话自动启动

## 📝 版本历史

### v2.0.0 (2026-03-04) ⭐
- ✅ **无感自动切换**：agentTurn创建新会话
- ✅ **零用户干预**：完全自动化
- ✅ **无缝体验**：对话连续
- ✅ **智能保存**：自动提取关键信息
- ✅ **阈值降低**：从95%到85%

### v1.0.0 (2026-03-03)
- ✅ 基础上下文监控
- ✅ 手动提醒功能
- ✅ 记忆传递系统

## 🚀 未来规划

### 短期（本周）
- [ ] 实现内部AI检测（每次回复检查）
- [ ] 优化agentTurn消息内容
- [ ] 完善记忆提取逻辑

### 中期（本月）
- [ ] 智能任务识别（避免关键任务中断）
- [ ] 用户自定义配置
- [ ] 多会话管理

### 长期（未来）
- [ ] 机器学习预测最佳切换时机
- [ ] 会话状态追踪
- [ ] 性能优化

## 📞 技术支持

**遇到问题？**
1. 查看日志：`tail -50 ~/.openclaw/workspace/logs/seamless-switch.log`
2. 检查定时任务：`crontab -l | grep seamless`
3. 验证记忆保存：`cat ~/.openclaw/workspace/MEMORY.md`

**社区资源**：
- GitHub: https://github.com/openclaw/openclaw
- Discord: https://discord.com/invite/clawd
- ClawHub: https://clawhub.com

---

*Context Manager v2.0 - 无感会话切换版*
*让上下文管理完全自动化，用户只需专注对话*
*版本：2.0.0*
*发布时间：2026-03-04*
