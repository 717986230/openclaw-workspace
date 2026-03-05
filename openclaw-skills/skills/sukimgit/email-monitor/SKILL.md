# Email Monitor - 邮件自动监控

自动监控 Gmail/163 邮箱，发现商机邮件后自动回复 + 通知。

## 配置 Configuration

编辑 `email_config.json`：

```json
{
  "email": {
    "address": "1776480440@qq.com",
    "imap": {
      "host": "imap.qq.com",
      "port": 993,
      "auth": {
        "user": "1776480440@qq.com",
        "pass": "你的 QQ 邮箱授权码"
      }
    },
    "smtp": {
      "host": "smtp.qq.com",
      "port": 465,
      "auth": {
        "user": "1776480440@qq.com",
        "pass": "你的 QQ 邮箱授权码"
      }
    }
  }
}
```

## 使用方法

```bash
# 检查新邮件
python check_emails.py

# 发送测试邮件
python send_email.py --to "test@example.com" --subject "测试" --body "你好"
```

## 自动回复模板 Auto-Reply Template

当邮件包含关键词（定制、开发、技能）时，自动回复：

```
【中文】
您好！感谢联系 OpenClaw 技能开发服务。

【服务内容】
- 技能定制开发：5000-20000 元
- AI 自动化集成：10000-50000 元
- 企业培训：20000 元/场

【已发布技能】
- Weekly Digest: https://clawhub.ai/sukimgit/weekly-digest
- Email Monitor: https://clawhub.ai/sukimgit/email-monitor

【联系方式】
📧 邮箱：1776480440@qq.com
💬 微信：私信获取

【English】
Hello! Thank you for contacting OpenClaw skill development.

【Services】
- Custom Skill: $700-3000 USD
- AI Automation: $1500-7000 USD  
- Training: $3000/session

【Contact】
📧 Email: 1776480440@qq.com
💬 WeChat: DM for details

Best regards,
老高 | OpenClaw Team
```

## 心跳配置

在 `HEARTBEAT.md` 添加：

```markdown
## 邮件检查
- [ ] 检查 sukim_sy@163.com 新邮件
- [ ] 自动回复商机邮件
- [ ] 飞书通知老高
```

## 依赖

- himalaya CLI（已安装）
- Python 3.8+
- 飞书 API（通知用）
