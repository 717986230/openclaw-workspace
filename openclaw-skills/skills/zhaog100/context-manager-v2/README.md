# Context Manager v2.0

> 无感会话切换 - 让上下文管理完全自动化

## 🎯 核心特性

- ⭐ **无感自动切换**：上下文超过85%自动创建新会话
- ✅ **零用户干预**：完全自动化，无需/new
- ✅ **无缝体验**：新会话自动加载记忆，对话连续
- ✅ **智能监控**：每10分钟检查，提前预警

## 🚀 快速开始

### 安装
```bash
# 从ClawHub安装
clawhub install miliger-context-manager

# 或手动安装
cd ~/.openclaw/skills
tar -xzf context-manager-v2.0.0.tar.gz
cd context-manager-v2
bash install.sh
```

### 使用
**超简单 - 只需正常聊天**

1. 继续对话（监控在后台运行）
2. 达到85%阈值（自动保存记忆）
3. 创建新会话（自动）
4. 新会话加载记忆（继续工作）

**用户视角**：对话从未中断

## 📊 工作原理

```
对话进行中
  ↓
后台监控（每10分钟）
  ↓
上下文达到85%
  ↓
自动保存记忆
  ↓
触发agentTurn
  ↓
创建新会话
  ↓
加载记忆继续
```

## 💡 为什么选择v2.0

### vs v1.0
- v1.0：提醒用户手动/new
- v2.0：自动创建新会话，零操作

### vs 手动管理
- 手动：可能忘记，有中断感
- 自动：完全无感，对话连续

## 📝 版本历史

- **v2.0.0** (2026-03-04)：无感自动切换
- **v1.0.0** (2026-03-03)：基础监控

## 📞 支持

- 日志：`tail -50 ~/.openclaw/workspace/logs/seamless-switch.log`
- 定时任务：`crontab -l | grep seamless`
- 问题反馈：https://github.com/miliger/context-manager/issues

---

**让AI会话管理像呼吸一样自然** 🌟
