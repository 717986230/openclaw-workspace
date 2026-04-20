# Twitter/X 内容爬取指南

## ✅ 工具已安装

- **工具**: twitter-cli v0.8.5
- **状态**: 已安装，需要配置认证

## 🔑 认证配置

Twitter/X 需要认证才能访问内容。有两种配置方式：

### 方法1: 使用 Cookie-Editor（推荐）

1. **安装 Cookie-Editor 浏览器扩展**
   - Chrome: https://chrome.google.com/webstore/detail/cookie-editor
   - Firefox: https://addons.mozilla.org/firefox/addon/cookie-editor

2. **导出 Twitter Cookie**
   - 登录 Twitter/X
   - 点击 Cookie-Editor 图标
   - 选择导出为 JSON 格式
   - 保存到文件

3. **设置环境变量**
   ```powershell
   # 从导出的 JSON 中提取 auth_token 和 ct0
   $env:TWITTER_AUTH_TOKEN = "your_auth_token_here"
   $env:TWITTER_CT0 = "your_ct0_here"
   ```

### 方法2: 手动提取 Cookie

1. **登录 Twitter/X**
   - 在浏览器中登录 https://twitter.com

2. **打开开发者工具**
   - 按 F12 或右键 -> 检查
   - 切换到 "Application" 或 "存储" 标签

3. **找到 Cookie**
   - 左侧菜单 -> Cookies -> https://twitter.com
   - 找到以下两个 Cookie:
     - `auth_token`
     - `ct0`

4. **复制 Cookie 值**
   - 双击对应的值进行复制

5. **设置环境变量**
   ```powershell
   $env:TWITTER_AUTH_TOKEN = "复制的auth_token值"
   $env:TWITTER_CT0 = "复制的ct0值"
   ```

## 📋 支持的功能

### 1. 获取首页时间线（最稳定）
```bash
twitter feed -n 20
```

### 2. 读取单条推文
```bash
twitter tweet TWEET_ID_OR_URL
```

### 3. 读取长文 / X Article
```bash
twitter article ARTICLE_ID_OR_URL
```

### 4. 获取用户时间线
```bash
twitter user-posts @username -n 20
```

### 5. 获取用户资料
```bash
twitter user @username
```

### 6. 搜索推文（可能不稳定）
```bash
twitter search "query" -n 10
```

## 🐍 Python 使用示例

### 基础使用

```python
from twitter_crawler_demo import TwitterCrawler

# 创建爬虫
crawler = TwitterCrawler()

# 获取首页时间线
feed = crawler.get_feed(count=20)
if feed:
    for tweet in feed:
        print(crawler.format_tweet(tweet))

# 获取用户资料
user_info = crawler.get_user_info('elonmusk')
if user_info:
    print(json.dumps(user_info, indent=2, ensure_ascii=False))

# 获取用户推文
user_posts = crawler.get_user_posts('elonmusk', count=20)
if user_posts:
    for tweet in user_posts:
        print(crawler.format_tweet(tweet))

# 搜索推文
search_results = crawler.search_tweets('AI', count=10)
if search_results:
    for tweet in search_results:
        print(crawler.format_tweet(tweet))
```

### 高级使用

```python
import subprocess
import json

# 使用 YAML 格式输出（更易读）
result = subprocess.run(
    ['twitter', 'feed', '-n', '10', '--yaml'],
    capture_output=True,
    text=True
)
print(result.stdout)

# 使用 JSON 格式输出（程序化处理）
result = subprocess.run(
    ['twitter', 'feed', '-n', '10', '--json'],
    capture_output=True,
    text=True
)
tweets = json.loads(result.stdout)
for tweet in tweets:
    print(f"@{tweet['username']}: {tweet['text']}")
```

## ⚠️ 重要注意事项

### 1. IP 风控
- 不要在 VPS/数据中心 IP 上频繁调用
- 尤其是 followers/following 功能，有封号风险
- 建议使用住宅代理或本地环境

### 2. 频率限制
- Twitter 有严格的 API 速率限制
- 建议每次操作间隔 2-3 秒
- 避免批量操作

### 3. 认证失效
- Cookie 可能会过期
- 如果遇到认证错误，需要重新提取 Cookie
- 建议定期更新认证信息

### 4. 搜索功能不稳定
- Twitter 频繁修改 GraphQL API
- search 命令可能随时返回 404
- 如遇到问题，升级 twitter-cli: `pipx upgrade twitter-cli`

### 5. 功能限制
- likes 功能在 2024 年后只能看自己的
- followers/following 有严格的限制
- 某些功能可能需要特定的权限

## 🔧 故障排除

### 问题1: 认证失败
```
WARNING twitter_cli.auth: Twitter cookie extraction failed
```

**解决方案**:
- 检查环境变量是否正确设置
- 重新提取 Cookie
- 确保 Cookie 没有过期

### 问题2: 搜索返回 404
```
Error: 404 Not Found
```

**解决方案**:
- 升级 twitter-cli: `pipx upgrade twitter-cli`
- 如果最新版仍不行，说明上游还没跟上 Twitter 的改动
- 使用 `twitter feed` 替代

### 问题3: 速率限制
```
Error: 429 Too Many Requests
```

**解决方案**:
- 减少请求频率
- 等待一段时间后重试
- 考虑使用代理 IP

### 问题4: IP 被封
```
Error: Account suspended
```

**解决方案**:
- 更换 IP 地址
- 使用住宅代理
- 避免在数据中心 IP 上操作

## 📊 数据存储

### 保存到数据库

```python
import sys
sys.path.insert(0, 'skills/smart-crawler')
from scripts.database_storage import DatabaseStorage

# 连接数据库
db = DatabaseStorage(
    db_type='mysql',
    host='localhost',
    port=3306,
    user='root',
    password='root123',
    database='crawler_db'
)

# 保存推文数据
task_id = db.create_task(
    title="Twitter 推文数据",
    url="twitter_feed",
    description="获取 Twitter 首页时间线"
)

for tweet in feed:
    db.create_result(
        task_id=task_id,
        url="twitter_feed",
        title=f"推文 {tweet['id']}",
        extracted_data=tweet,
        media_files=None
    )

db.close()
```

### 保存到文件

```python
import json

# 保存为 JSON
with open('twitter_feed.json', 'w', encoding='utf-8') as f:
    json.dump(feed, f, ensure_ascii=False, indent=2)

# 保存为 CSV
import pandas as pd
df = pd.DataFrame(feed)
df.to_csv('twitter_feed.csv', index=False, encoding='utf-8')
```

## 🎯 使用场景

### 1. 舆情监控
- 监控特定关键词
- 跟踪品牌提及
- 分析用户情绪

### 2. 内容分析
- 分析热门话题
- 研究用户行为
- 挖掘趋势数据

### 3. 竞品分析
- 监控竞争对手
- 分析营销策略
- 跟踪产品发布

### 4. 学术研究
- 社交媒体研究
- 网络分析
- 数据挖掘

## 📚 相关资源

- **twitter-cli GitHub**: https://github.com/andrewthad/twitter-cli
- **Twitter API 文档**: https://developer.twitter.com/en/docs
- **Agent-Reach 文档**: ~/.agents/skills/agent-reach/

## 🆘 获取帮助

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查 twitter-cli 的 GitHub Issues
3. 查看 Agent-Reach 的文档

---

**版本**: 1.0.0
**更新时间**: 2026-04-16
**作者**: Erbing
