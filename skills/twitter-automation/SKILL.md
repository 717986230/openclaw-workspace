
---
name: twitter-automation
description: Twitter/X 自动化技能 - 使用 tweepy（官方 Twitter API）搜索、阅读、发帖。需要开发者账号和 API keys。
homepage: https://github.com/openclaw/skills/tree/main/skills/iqbalnaveliano/bird-su
metadata: { "openclaw": { "emoji": "🐦", "requires": { "bins": ["python"] } } }
---

# Twitter Automation with Tweepy 🐦

使用 tweepy（官方 Twitter API）搜索、阅读、发帖。

## 功能

- 🔍 搜索 Twitter/X 内容（官方 API）
- 📖 阅读推文和时间线
- 📝 发帖和回复
- 🔑 使用官方 API keys
- ✅ 稳定可靠

## 前置准备

### 第一步：创建 Twitter 开发者账号

1. 访问 https://developer.twitter.com/
2. 注册/登录开发者账号
3. 创建一个新项目和应用
4. 获取以下 API keys：

```
API Key (Consumer Key)
API Secret (Consumer Secret)
Bearer Token
Access Token
Access Token Secret
```

### 第二步：保存 API keys

创建一个配置文件 `twitter-config.json`：

```json
{
  "bearer_token": "YOUR_BEARER_TOKEN",
  "consumer_key": "YOUR_CONSUMER_KEY",
  "consumer_secret": "YOUR_CONSUMER_SECRET",
  "access_token": "YOUR_ACCESS_TOKEN",
  "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET"
}
```

## 安装 tweepy

```bash
pip install tweepy
```

## 使用方式

### 搜索推文

```python
import tweepy
import json

# 加载配置
with open('twitter-config.json', 'r') as f:
    config = json.load(f)

# 初始化客户端（只需要 Bearer Token 用于搜索）
client = tweepy.Client(bearer_token=config['bearer_token'])

# 搜索最新推文
query = "war conflict latest -is:retweet"
tweets = client.search_recent_tweets(
    query=query,
    max_results=20,
    tweet_fields=["created_at", "public_metrics"],
    user_fields=["username", "name"],
    expansions=["author_id"]
)

# 处理结果
users = {u.id: u for u in tweets.includes['users']} if tweets.includes else {}

print(f"\n🔥 搜索结果: {query}\n")
print("="*60)

if tweets.data:
    for i, tweet in enumerate(tweets.data, 1):
        user = users.get(tweet.author_id)
        print(f"\n{i}. @{user.username if user else 'Unknown'}")
        print(f"   {tweet.text[:200]}...")
        print(f"   👍 {tweet.public_metrics['like_count']} | 🔄 {tweet.public_metrics['retweet_count']}")
        print(f"   🕐 {tweet.created_at}")
else:
    print("❌ 没有找到结果")

print("\n" + "="*60)
```

### 完整搜索脚本

```python
import tweepy
import json
from datetime import datetime

class TwitterSearch:
    def __init__(self, config_file='twitter-config.json'):
        with open(config_file, 'r') as f:
            config = json.load(f)
        self.client = tweepy.Client(bearer_token=config['bearer_token'])
    
    def search(self, query, max_results=20):
        """搜索推文"""
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=["created_at", "public_metrics", "lang"],
                user_fields=["username", "name"],
                expansions=["author_id"]
            )
            return tweets
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            return None
    
    def print_results(self, tweets, title="搜索结果"):
        """打印搜索结果"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}\n")
        
        if not tweets or not tweets.data:
            print("❌ 没有找到结果\n")
            return
        
        users = {u.id: u for u in tweets.includes['users']} if tweets.includes else {}
        
        for i, tweet in enumerate(tweets.data, 1):
            user = users.get(tweet.author_id)
            print(f"{i}. @{user.username if user else 'Unknown'}")
            print(f"   {tweet.text}")
            print(f"   👍 {tweet.public_metrics['like_count']} | 🔄 {tweet.public_metrics['retweet_count']} | 💬 {tweet.public_metrics['reply_count']}")
            print(f"   🕐 {tweet.created_at}")
            print()
        
        print(f"{'='*60}\n")

# 使用示例
if __name__ == "__main__":
    twitter = TwitterSearch()
    
    # 搜索战火消息
    war_results = twitter.search("war conflict military attack -is:retweet", max_results=15)
    twitter.print_results(war_results, "🔥 战火消息")
    
    # 搜索原油市场
    oil_results = twitter.search("oil crude prices OPEC market -is:retweet", max_results=15)
    twitter.print_results(oil_results, "🛢️ 原油市场动态")
```

## 快速搜索查询

| 场景 | 查询字符串 |
|------|-----------|
| 战火消息 | `"war conflict military attack -is:retweet"` |
| 原油价格 | `"oil crude prices OPEC market -is:retweet"` |
| 中东局势 | `"Middle East tension conflict -is:retweet"` |
| 乌克兰局势 | `"Ukraine Russia war -is:retweet"` |
| 全球市场 | `"global economy markets finance -is:retweet"` |

## 查询运算符

- `-is:retweet` - 排除转发
- `is:verified` - 只看认证用户
- `has:media` - 只看有媒体的
- `has:images` - 只看有图片的
- `lang:en` - 只看英文
- `lang:zh` - 只看中文

## 安全提示

⚠️ **重要提示：**
- 妥善保管 API keys，不要提交到代码仓库
- 遵守 Twitter 开发者服务条款
- 注意速率限制（免费账号：500,000  tweets/月）
- 仅供个人学习和研究使用

---

*使用官方 API，搜索更稳定* 🐦
