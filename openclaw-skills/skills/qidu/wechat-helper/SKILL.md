---
name: wechat-helper
alias: 
  - wechat
  - wechat-me
  - wechat-filehelper
description: |
  WeChat File Helper automation. Use when:
  - Check if filehelper.weixin.qq.com is open in browser
  - Open the page if not already open
  - Capture QR code and send to user via WhatsApp
  - Monitor for login (QR scanned)
  - Send message for OpenClaw through web interface to owner's WeChat App who just scan the QR Code and login WeChat File Helper.

  NOT for: Personal WeChat accounts (violates ToS).
---

# WeChat File Helper Skill

Automate `WeChat` File Helper web interface. ( `wechat`, `wechat-helper`, `wechat-me`, or `wechat-filehelper` ) 

## Quick Reference

| Task | Command |
|------|---------|
| Check if open | `browser action=tabs targetUrl="filehelper.weixin.qq.com"` |
| Open page | `browser action=open targetUrl="https://filehelper.weixin.qq.com/"` |
| Capture QR | `browser action=screenshot` |
| Find input | `browser action=act request={"kind":"click","ref":"..."}` |
| Send message | `browser action=act request={"kind":"type","text":"Hello"}` |

## Workflow

### 1. Check if Page is Open

```bash
# Check if filehelper page is already open
browser action=tabs targetUrl="filehelper.weixin.qq.com"
```

### 2. Open if Not

```bash
# Open WeChat File Helper
browser action=open targetUrl="https://filehelper.weixin.qq.com/"
```

### 3. Capture QR Code

```bash
# Take screenshot of QR code
browser action=screenshot
```

### 4. Send QR to User

```bash
# Send via WhatsApp
message action=send to=+01234567890 media=/path/to/qr-screenshot.png
```

### 5. Monitor for Login

```bash
# Check if QR is scanned (page changes to chat interface)
browser action=snapshot targetId=...
# Look for: chat input box, "发送" or "Send" button, or contact list
```

### 6. Send Message After Login

```bash
# Find and fill message input
browser action=act request={"kind":"type","ref":"input-box","text":"Hello from OpenClaw!"}

# Click send button
browser action=act request={"kind":"click","ref":"send-button"}
```

## QR Code Detection

### Page States

| State | URL | Description |
|-------|-----|-------------|
| **Logged Out** | `filehelper.weixin.qq.com/` | Shows QR code |
| **Logged In** | `filehelper.weixin.qq.com/_/` | Shows chat interface |
| **Error** | Various | Error messages |

### Detect Login

```javascript
// In browser snapshot, look for:
// - Chat input box (textarea, contenteditable)
// - "发送" or "Send" button
// - Contact list / recent chats
// - Absence of QR code image
```

## Cron Job Setup

### 1-Minute QR Capture

```bash
# Add cron job to capture QR every minute
openclaw cron add --schedule "cron * * * * *" --task "
  browser action=snapshot
  # If logged in, break
  # If QR present, send to user
"
```

### Monitor Script (wechat-monitor.sh)

```bash
#!/bin/bash
# Monitor WeChat File Helper QR code

# Check page state
STATE=$(browser action=tabs targetUrl="filehelper.weixin.qq.com" | grep -c "chat" || echo "0")

if [ "$STATE" -gt "0" ]; then
  echo "Logged in!"
  # Send test message
  browser action=act request='{"kind":"type","ref":"input","text":"Hello from OpenClaw!"}'
else
  echo "Not logged in, capturing QR..."
  browser action=screenshot
  # Send QR to user
  message action=send to=+8618610831272 media=/tmp/wechat-qr.png
fi
```

## Message Sending

### Find Input Box

Common selectors:
- `textarea[placeholder*="输入"]`
- `div[contenteditable="true"]`
- `#inputArea`
- `.msg_input`

### Find Send Button

Common selectors:
- `button:contains("发送")`
- `.send_btn`
- `[data-type="send"]`

### Example: Send Message

```bash
# Type message
browser action=act request='{"kind":"type","ref":"input-area","text":"Hello!"}'

# Click send
browser action=act request='{"kind":"click","ref":"send-btn"}'
```

## Complete Automation Script

```bash
#!/bin/bash
# wechat-filehelper-auto.sh

WEBSITE="https://filehelper.weixin.qq.com/"
QR_FILE="/tmp/wechat-qr.png"
USER_PHONE="+01234567890"

# Check if logged in
PAGE=$(browser action=tabs targetUrl="$WEBSITE")

if echo "$PAGE" | grep -q "chat\|_/"; then
  echo "Already logged in"
  
  # Send hello message
  browser action=act request='{"kind":"type","ref":"input","text":"Hello from OpenClaw! 🦞"}'
  browser action=act request='{"kind":"click","ref":"send"}'
  
  echo "Message sent!"
else
  echo "Not logged in, capturing QR..."
  
  # Capture QR
  browser action=screenshot path="$QR_FILE"
  
  # Send QR to user
  message action=send to="$USER_PHONE" media="$QR_FILE"
  
  echo "QR code sent to user"
fi
```

## Important Notes

- **ToS Warning:** Using personal WeChat accounts via web may violate WeChat ToS
- **QR Expiry:** QR codes refresh every 1-2 minutes
- **Session:** Web sessions may timeout after inactivity
- **Rate Limits:** Don't send too many messages rapidly, don't select and send files directly
- **Login State:** Monitor page URL for `_/` suffix to detect login

## Troubleshooting

| Issue | Solution |
|-------|-----------|
| QR not loading | Refresh page, check network |
| Login not detected | Check for `_/` in URL |
| Can't send message | Check selector, try different input |
| Session expired | Re-scan QR |
| Can't send files | Use other storage skills, upload file, get a link, send the link |

## Dependencies

- OpenClaw browser tool
- WhatsApp or other messaging channel
- Cron capability for monitoring
