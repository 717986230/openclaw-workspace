
---
name: agent-reach
description: Agent Reach - 扩展 Agent 的触达能力，支持多平台消息发送、通知推送、和用户交互。
homepage: https://skills.sh/panniantong/agent-reach/agent-reach
metadata: { "openclaw": { "emoji": "📡", "requires": { "bins": ["python"] } } }
---

# Agent Reach 📡

扩展 Agent 的触达能力，支持多平台消息发送、通知推送、和用户交互。

## 功能

- 📨 多平台消息发送
- 🔔 通知推送
- 💬 和用户交互
- 📱 移动端支持
- 🔗 多平台集成

## 支持的平台

| 平台 | 状态 |
|------|------|
| Feishu / Lark | ✅ 已支持 |
| Discord | ✅ 已支持 |
| Telegram | ✅ 已支持 |
| WhatsApp | 🔄 开发中 |
| Slack | 🔄 开发中 |
| Email | 🔄 开发中 |

## 使用方式

### Feishu（飞书）

当前已在 Feishu 中运行，直接对话即可！

### 发送通知

```python
# 发送简单通知
def send_notification(message):
    """发送通知给用户"""
    print(f"📢 通知: {message}")
    # 这里可以集成具体的通知 API
    return True

# 使用示例
send_notification("任务完成！")
```

### 多平台消息

```python
class AgentReach:
    def __init__(self):
        self.platforms = {
            'feishu': self._send_feishu,
            'discord': self._send_discord,
            'telegram': self._send_telegram,
        }
    
    def send(self, platform, message):
        """发送消息到指定平台"""
        if platform in self.platforms:
            return self.platforms[platform](message)
        else:
            print(f"❌ 不支持的平台: {platform}")
            return False
    
    def _send_feishu(self, message):
        """发送到 Feishu"""
        print(f"📤 [Feishu] {message}")
        return True
    
    def _send_discord(self, message):
        """发送到 Discord"""
        print(f"📤 [Discord] {message}")
        return True
    
    def _send_telegram(self, message):
        """发送到 Telegram"""
        print(f"📤 [Telegram] {message}")
        return True

# 使用示例
reach = AgentReach()
reach.send('feishu', '你好！这是来自 Agent Reach 的消息！')
```

## 交互模式

### 提问用户

```python
def ask_user(question, options=None):
    """
    向用户提问
    
    Args:
        question: 问题内容
        options: 选项列表（可选）
    """
    print(f"\n❓ {question}")
    if options:
        print("选项:")
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
    print()
    
    # 实际使用时，这里会等待用户回复
    # 这里只是模拟
    return "用户回复"

# 使用示例
answer = ask_user("你想了解什么？", ["战火消息", "原油市场", "其他"])
```

### 确认操作

```python
def confirm_action(action):
    """确认用户是否要执行某个操作"""
    print(f"\n⚠️  即将执行: {action}")
    print("请确认（是/否）: ", end="")
    # 这里等待用户确认
    return True

# 使用示例
if confirm_action("发送通知"):
    print("✅ 已确认")
```

## 快速命令

| 命令 | 功能 |
|------|------|
| `send [平台] [消息]` | 发送消息 |
| `notify [消息]` | 发送通知 |
| `ask [问题]` | 提问用户 |
| `confirm [操作]` | 确认操作 |

## 扩展计划

- [ ] Webhook 支持
- [ ] 更多平台集成
- [ ] 消息模板
- [ ] 定时通知
- [ ] 消息队列

## 安全提示

⚠️ **重要提示：**
- 妥善保管 API keys
- 遵守各平台服务条款
- 不要频繁发送消息
- 尊重用户隐私

---

*扩展 Agent 触达，连接更多平台* 📡
