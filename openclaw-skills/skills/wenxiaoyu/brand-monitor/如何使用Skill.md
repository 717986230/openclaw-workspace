# 如何使用 Brand Monitor Skill

## 前提条件

1. ✅ 已安装 OpenClaw 2026.2.9+
2. ✅ 已配置 LLM（Claude/GPT/Gemini）
3. ✅ 已设置 SERPAPI_KEY 环境变量
4. ✅ 已获取飞书 Webhook URL

## 方法 1: 在 OpenClaw 中使用 Skill（推荐）

### 步骤 1: 安装 Skill

```bash
# 进入 OpenClaw skills 目录
cd ~/.openclaw/workspace/skills/

# 复制 brand-monitor-skill 到此目录
cp -r /path/to/brand-monitor-skill ./

# 或者使用 git clone（如果是 git 仓库）
git clone <repository-url> brand-monitor-skill
```

### 步骤 2: 安装依赖

```bash
cd brand-monitor-skill
chmod +x install.sh
./install.sh
```

### 步骤 3: 配置 Skill

```bash
# 复制配置文件
cp config.example.json config.json

# 编辑配置
nano config.json
```

最小配置：
```json
{
  "brand_name": "理想汽车",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
}
```

### 步骤 4: 设置环境变量

```bash
# Linux/macOS
export SERPAPI_KEY='your_api_key_here'
export SERPAPI_ENGINE='baidu'

# Windows (PowerShell)
$env:SERPAPI_KEY='your_api_key_here'
$env:SERPAPI_ENGINE='baidu'
```

### 步骤 5: 重启 OpenClaw Gateway

```bash
openclaw gateway restart
```

### 步骤 6: 验证 Skill 已加载

```bash
openclaw skills list | grep brand-monitor
```

应该看到：
```
brand-monitor - 新能源汽车品牌舆情监控
```

### 步骤 7: 使用 Skill

在 OpenClaw 中发送消息：

```
执行品牌监控
```

或者使用命令行：

```bash
openclaw agent --message "执行品牌监控"
```

## 方法 2: 直接测试爬虫（当前窗口可用）

如果你只想测试爬虫功能，不需要完整的 OpenClaw 环境：

### 步骤 1: 进入爬虫目录

```bash
cd brand-monitor-skill/crawler
```

### 步骤 2: 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 步骤 3: 设置环境变量

```bash
# Windows (PowerShell)
$env:SERPAPI_KEY='your_api_key_here'
$env:SERPAPI_ENGINE='baidu'
```

### 步骤 4: 测试爬虫

```bash
# Mock 模式（无需 API Key）
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 5 24 --mock

# 真实搜索（需要 API Key）
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 5 24

# 包含官方账号
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 5 24 --include-official
```

### 步骤 5: 查看输出

爬虫会输出 JSON 格式的搜索结果：

```json
{
  "weibo": [
    {
      "platform": "weibo",
      "title": "李想的微博_微博",
      "content": "理想之路,不是等风来...",
      "url": "https://weibo.com/qilixiang",
      "publish_time": "2025-9-26 12:00",
      "author": "李想",
      "likes": 103629,
      "comments": 6066,
      "shares": 765,
      "is_official": false
    }
  ],
  "zhihu": [...]
}
```

## 方法 3: 手动执行监控流程

如果你想手动执行完整的监控流程（不使用 OpenClaw）：

### 步骤 1: 运行爬虫

```bash
cd brand-monitor-skill/crawler
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 10 24 > results.json
```

### 步骤 2: 分析结果

使用 Python 或其他工具分析 `results.json`：

```python
import json

# 读取结果
with open('results.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 统计
total = sum(len(r) for r in results.values())
print(f"总共找到 {total} 条结果")

# 按平台统计
for platform, mentions in results.items():
    print(f"{platform}: {len(mentions)} 条")
```

### 步骤 3: 情感分析

使用 LLM API 进行情感分析：

```python
import openai

for platform, mentions in results.items():
    for mention in mentions:
        # 调用 LLM 分析情感
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content": f"分析以下内容的情感（-1到1）：\n{mention['content']}"
            }]
        )
        sentiment = float(response.choices[0].message.content)
        mention['sentiment'] = sentiment
```

### 步骤 4: 生成报告

```python
# 生成简单报告
positive = sum(1 for m in all_mentions if m.get('sentiment', 0) > 0.2)
negative = sum(1 for m in all_mentions if m.get('sentiment', 0) < -0.2)
neutral = total - positive - negative

print(f"""
📊 品牌监控报告
━━━━━━━━━━━━━━━━━━━━
总提及数: {total}
😊 正面: {positive} ({positive/total*100:.1f}%)
😐 中性: {neutral} ({neutral/total*100:.1f}%)
😞 负面: {negative} ({negative/total*100:.1f}%)
""")
```

## 方法 4: 使用 OpenClaw CLI（推荐用于自动化）

### 一次性执行

```bash
openclaw agent --message "执行品牌监控"
```

### 定时执行（cron）

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天早上 9 点）
0 9 * * * cd ~/.openclaw && openclaw agent --message "执行品牌监控" >> /var/log/brand-monitor.log 2>&1
```

### 定时执行（systemd timer）

创建服务文件 `/etc/systemd/system/brand-monitor.service`：

```ini
[Unit]
Description=Brand Monitor Service

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/home/your-username/.openclaw
Environment="SERPAPI_KEY=your_api_key"
ExecStart=/usr/local/bin/openclaw agent --message "执行品牌监控"
```

创建定时器 `/etc/systemd/system/brand-monitor.timer`：

```ini
[Unit]
Description=Brand Monitor Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl enable brand-monitor.timer
sudo systemctl start brand-monitor.timer
```

## 常见问题

### Q1: Skill 未加载

**检查**:
```bash
openclaw skills list | grep brand-monitor
```

**解决**:
```bash
# 重启 gateway
openclaw gateway restart

# 检查 SKILL.md 格式
cat brand-monitor-skill/SKILL.md
```

### Q2: 爬虫无结果

**检查**:
```bash
# 测试 API Key
echo $SERPAPI_KEY

# 测试爬虫
python search_crawler_serpapi.py "理想汽车" "weibo" 5 24
```

**解决**:
- 检查 API Key 是否正确
- 检查网络连接
- 使用 Mock 模式测试：`--mock`

### Q3: 飞书推送失败

**检查**:
```bash
# 测试 Webhook
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试消息"}}' \
  https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook
```

**解决**:
- 检查 Webhook URL 是否正确
- 检查飞书机器人是否启用
- 检查网络连接

### Q4: 数据不完整

**原因**: SerpAPI 只返回搜索结果摘要

**解决**:
- Skill 会自动使用 web_fetch 补充重要内容
- 可以手动使用 web_fetch 获取完整页面
- 考虑集成平台官方 API

## 快速测试清单

- [ ] 安装 Python 依赖
- [ ] 设置 SERPAPI_KEY
- [ ] 测试 Mock 模式
- [ ] 测试真实搜索
- [ ] 配置 config.json
- [ ] 测试飞书推送
- [ ] 安装到 OpenClaw
- [ ] 验证 Skill 加载
- [ ] 执行监控
- [ ] 检查报告

## 推荐工作流

### 开发/测试阶段

1. 使用 Mock 模式测试爬虫
2. 使用少量真实搜索验证
3. 手动分析结果
4. 调整配置

### 生产阶段

1. 配置定时任务
2. 监控 API 配额
3. 定期检查报告
4. 处理警报

## 相关文档

- [README.md](README.md) - 主文档
- [快速参考.md](快速参考.md) - 快速参考
- [使用指南-SerpAPI版.md](使用指南-SerpAPI版.md) - 详细指南
- [官方账号过滤说明.md](crawler/官方账号过滤说明.md) - 过滤功能
- [数据质量改进方案.md](数据质量改进方案.md) - 数据质量

## 获取帮助

如果遇到问题：

1. 查看文档
2. 检查日志：`~/.openclaw/logs/gateway.log`
3. 使用 Mock 模式测试
4. 检查环境变量
5. 重启 OpenClaw

---

**祝使用愉快！** 🎉

