"""
Twitter 爬取功能说明
"""

print("""
============================================================
           Twitter/X 内容爬取 - 功能说明
============================================================

[OK] 工具状态
------------------------------------------------------------
[OK] twitter-cli v0.8.5 已安装
[OK] Python 爬虫脚本已创建
[OK] 使用文档已生成

[KEY] 认证配置
------------------------------------------------------------
Twitter 需要认证才能访问内容。配置步骤：

1. 获取 Cookie
   - 在浏览器中登录 Twitter/X
   - 按 F12 打开开发者工具
   - Application -> Cookies -> https://twitter.com
   - 复制 auth_token 和 ct0 的值

2. 设置环境变量（PowerShell）
   $env:TWITTER_AUTH_TOKEN = 'your_auth_token'
   $env:TWITTER_CT0 = 'your_ct0'

3. 测试认证
   twitter feed -n 1

[LIST] 支持的功能
------------------------------------------------------------
1. 获取首页时间线（最稳定）
   twitter feed -n 20

2. 读取单条推文
   twitter tweet TWEET_ID_OR_URL

3. 读取长文 / X Article
   twitter article ARTICLE_ID_OR_URL

4. 获取用户时间线
   twitter user-posts @username -n 20

5. 获取用户资料
   twitter user @username

6. 搜索推文（可能不稳定）
   twitter search "query" -n 10

[PYTHON] Python 使用示例
------------------------------------------------------------
from twitter_crawler_demo import TwitterCrawler

# 创建爬虫
crawler = TwitterCrawler()

# 获取首页时间线
feed = crawler.get_feed(count=20)

# 获取用户资料
user_info = crawler.get_user_info('elonmusk')

# 获取用户推文
user_posts = crawler.get_user_posts('elonmusk', count=20)

# 搜索推文
search_results = crawler.search_tweets('AI', count=10)

[WARNING] 重要注意事项
------------------------------------------------------------
1. IP 风控
   - 不要在 VPS/数据中心 IP 上频繁调用
   - 建议使用住宅代理或本地环境

2. 频率限制
   - Twitter 有严格的 API 速率限制
   - 建议每次操作间隔 2-3 秒

3. 认证失效
   - Cookie 可能会过期
   - 需要定期更新认证信息

4. 搜索功能不稳定
   - Twitter 频繁修改 GraphQL API
   - search 命令可能随时返回 404

[FILES] 生成的文件
------------------------------------------------------------
1. twitter_crawler_demo.py - Python 爬虫演示
2. twitter_auth_config.py - 认证配置助手
3. TWITTER_CRAWLER_GUIDE.md - 完整使用指南

[NEXT] 下一步
------------------------------------------------------------
1. 配置 Twitter 认证（查看 TWITTER_CRAWLER_GUIDE.md）
2. 运行演示脚本: python twitter_crawler_demo.py
3. 根据需求定制爬虫功能

[INFO] 更多信息
------------------------------------------------------------
- 完整文档: TWITTER_CRAWLER_GUIDE.md
- Agent-Reach 技能: ~/.agents/skills/agent-reach/
- twitter-cli GitHub: https://github.com/andrewthad/twitter-cli

============================================================
""")

print("Twitter/X 爬取功能已准备就绪！")
print("请查看 TWITTER_CRAWLER_GUIDE.md 了解详细配置和使用方法。")
