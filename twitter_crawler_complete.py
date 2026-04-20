"""
Twitter爬虫 - 完整版本
支持数据存储到MySQL数据库
"""

import os
import json
import sqlite3
import mysql.connector
from datetime import datetime
from typing import List, Dict, Optional
import subprocess


class TwitterCrawler:
    """Twitter爬虫类"""

    def __init__(self, auth_token: str, ct0: str, mysql_config: Optional[Dict] = None):
        """
        初始化Twitter爬虫

        Args:
            auth_token: Twitter认证token
            ct0: Twitter CSRF token
            mysql_config: MySQL配置(可选)
        """
        self.auth_token = auth_token
        self.ct0 = ct0
        self.mysql_config = mysql_config

    def set_environment(self):
        """设置环境变量"""
        os.environ['TWITTER_AUTH_TOKEN'] = self.auth_token
        os.environ['TWITTER_CT0'] = self.ct0

    def get_feed(self, count: int = 10) -> List[Dict]:
        """
        获取首页时间线

        Args:
            count: 获取的推文数量

        Returns:
            推文列表
        """
        self.set_environment()

        try:
            result = subprocess.run(
                ['twitter', 'feed', '-n', str(count)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            if result.returncode == 0:
                # 解析输出
                output = result.stdout
                tweets = self._parse_twitter_output(output)
                return tweets
            else:
                print(f"错误: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            print("请求超时")
            return []
        except Exception as e:
            print(f"获取推文失败: {e}")
            return []

    def get_user_posts(self, username: str, count: int = 10) -> List[Dict]:
        """
        获取用户推文

        Args:
            username: 用户名(如 @elonmusk)
            count: 获取的推文数量

        Returns:
            推文列表
        """
        self.set_environment()

        try:
            result = subprocess.run(
                ['twitter', 'user-posts', username, '-n', str(count)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                tweets = self._parse_twitter_output(output)
                return tweets
            else:
                print(f"错误: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            print("请求超时")
            return []
        except Exception as e:
            print(f"获取用户推文失败: {e}")
            return []

    def get_tweet(self, tweet_id: str) -> Optional[Dict]:
        """
        获取单条推文

        Args:
            tweet_id: 推文ID或URL

        Returns:
            推文信息
        """
        self.set_environment()

        try:
            result = subprocess.run(
                ['twitter', 'tweet', tweet_id],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            if result.returncode == 0:
                output = result.stdout
                tweets = self._parse_twitter_output(output)
                return tweets[0] if tweets else None
            else:
                print(f"错误: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print("请求超时")
            return None
        except Exception as e:
            print(f"获取推文失败: {e}")
            return None

    def _parse_twitter_output(self, output: str) -> List[Dict]:
        """
        解析twitter-cli输出

        Args:
            output: twitter-cli的输出

        Returns:
            推文列表
        """
        tweets = []
        current_tweet = {}
        current_section = None
        current_list = []

        try:
            lines = output.strip().split('\n')

            for line in lines:
                if line is None:
                    continue
                line = line.rstrip()

                if not line:
                    continue

                # 检查是否是新的推文开始
                if line.startswith('- id:'):
                    # 保存上一条推文
                    if current_tweet:
                        tweets.append(current_tweet)
                    # 开始新推文
                    current_tweet = {'id': line.split(':', 1)[1].strip().strip("'")}
                    current_section = None
                    current_list = []

                # 检查是否是新的section
                elif line.startswith('  ') and not line.startswith('    '):
                    # 顶级缩进，可能是新的section
                    if ':' in line:
                        key = line.strip().split(':', 1)[0].strip()
                        value = line.strip().split(':', 1)[1].strip()

                        # 处理特殊section
                        if key in ['author', 'metrics', 'media', 'urls']:
                            current_section = key
                            current_list = []
                            # 如果有值，添加到列表
                            if value and value != '[]':
                                current_list.append(value)
                        else:
                            current_section = None
                            current_tweet[key] = value

                # 检查是否是列表项
                elif line.startswith('    -'):
                    if current_section:
                        item = line[4:].strip()
                        if ':' in item:
                            item_key = item.split(':', 1)[0].strip()
                            item_value = item.split(':', 1)[1].strip()
                            # 添加到当前列表
                            if not current_list:
                                current_list = {}
                            if isinstance(current_list, dict):
                                current_list[item_key] = item_value
                            else:
                                # 转换为字典
                                new_dict = {}
                                for existing_item in current_list:
                                    if ':' in existing_item:
                                        k, v = existing_item.split(':', 1)
                                        new_dict[k.strip()] = v.strip()
                                new_dict[item_key] = item_value
                                current_list = new_dict
                        else:
                            if not isinstance(current_list, list):
                                current_list = []
                            current_list.append(item)

                # 检查section结束
                elif line.startswith('  ') and ':' in line and current_section:
                    # 可能是section的结束
                    if current_list:
                        current_tweet[current_section] = current_list
                    current_section = None
                    current_list = []

            # 保存最后一条推文
            if current_tweet:
                # 确保section被保存
                if current_section and current_list:
                    current_tweet[current_section] = current_list
                tweets.append(current_tweet)

        except Exception as e:
            print(f"解析输出失败: {e}")
            import traceback
            traceback.print_exc()

        return tweets

    def _parse_nested_structure(self, value: str) -> Dict:
        """
        解析嵌套结构

        Args:
            value: 嵌套结构的字符串

        Returns:
            解析后的字典
        """
        result = {}

        try:
            # 简单的解析逻辑
            if value.startswith('{') and value.endswith('}'):
                return json.loads(value)
            else:
                # 处理简单的键值对
                for item in value.split(','):
                    if ':' in item:
                        k, v = item.split(':', 1)
                        result[k.strip()] = v.strip()
        except Exception as e:
            print(f"解析嵌套结构失败: {e}")

        return result

    def _parse_datetime(self, date_str: str) -> Optional[str]:
        """
        解析日期时间字符串

        Args:
            date_str: 日期时间字符串

        Returns:
            格式化后的日期时间字符串
        """
        if not date_str:
            return None

        try:
            # 尝试解析各种日期格式
            formats = [
                '%a %b %d %H:%M:%S %z %Y',  # Wed Apr 15 03:17:50 +0000 2026
                '%Y-%m-%d %H:%M:%S',  # 2026-04-15 11:17
                '%Y-%m-%dT%H:%M:%S%z',  # 2026-04-15T03:17:50+00:00
                '%Y-%m-%dT%H:%M:%S.%f%z',  # 2026-04-15T03:17:50.000+00:00
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue

            # 如果所有格式都失败，返回原始字符串
            return date_str

        except Exception as e:
            print(f"解析日期失败: {e}")
            return date_str

    def save_to_mysql(self, tweets: List[Dict]) -> bool:
        """
        保存推文到MySQL数据库

        Args:
            tweets: 推文列表

        Returns:
            是否成功
        """
        if not self.mysql_config:
            print("未配置MySQL")
            return False

        try:
            conn = mysql.connector.connect(**self.mysql_config)
            cursor = conn.cursor()

            # 创建表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS twitter_tweets (
                    id VARCHAR(50) PRIMARY KEY,
                    text TEXT,
                    author_id VARCHAR(50),
                    author_name VARCHAR(255),
                    author_screen_name VARCHAR(255),
                    author_verified BOOLEAN,
                    likes INT,
                    retweets INT,
                    replies INT,
                    quotes INT,
                    views INT,
                    bookmarks INT,
                    created_at DATETIME,
                    created_at_local DATETIME,
                    created_at_iso VARCHAR(50),
                    is_retweet BOOLEAN,
                    lang VARCHAR(10),
                    media_urls TEXT,
                    external_urls TEXT,
                    crawled_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入数据
            for tweet in tweets:
                try:
                    # 提取媒体URL
                    media_urls = []
                    if 'media' in tweet and tweet['media']:
                        for media in tweet['media']:
                            if isinstance(media, dict) and 'url' in media:
                                media_urls.append(media['url'])

                    # 提取外部URL
                    external_urls = []
                    if 'urls' in tweet and tweet['urls']:
                        for url in tweet['urls']:
                            if isinstance(url, str):
                                external_urls.append(url)

                    # 提取作者信息
                    author_id = None
                    author_name = None
                    author_screen_name = None
                    author_verified = False

                    if 'author' in tweet and tweet['author']:
                        author = tweet['author']
                        if isinstance(author, dict):
                            author_id = author.get('id')
                            author_name = author.get('name')
                            author_screen_name = author.get('screenName')
                            author_verified = author.get('verified', False)

                    # 提取指标
                    metrics = tweet.get('metrics', {})
                    if isinstance(metrics, dict):
                        likes = metrics.get('likes', 0)
                        retweets = metrics.get('retweets', 0)
                        replies = metrics.get('replies', 0)
                        quotes = metrics.get('quotes', 0)
                        views = metrics.get('views', 0)
                        bookmarks = metrics.get('bookmarks', 0)
                    else:
                        likes = retweets = replies = quotes = views = bookmarks = 0

                    # 插入数据
                    cursor.execute("""
                        INSERT INTO twitter_tweets
                        (id, text, author_id, author_name, author_screen_name, author_verified,
                         likes, retweets, replies, quotes, views, bookmarks,
                         created_at, created_at_local, created_at_iso, is_retweet, lang,
                         media_urls, external_urls)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        text = VALUES(text),
                        likes = VALUES(likes),
                        retweets = VALUES(retweets),
                        replies = VALUES(replies),
                        quotes = VALUES(quotes),
                        views = VALUES(views),
                        bookmarks = VALUES(bookmarks)
                    """, (
                        tweet.get('id') or '',
                        tweet.get('text') or '',
                        author_id or '',
                        author_name or '',
                        author_screen_name or '',
                        author_verified,
                        likes,
                        retweets,
                        replies,
                        quotes,
                        views,
                        bookmarks,
                        self._parse_datetime(tweet.get('createdAt')),
                        self._parse_datetime(tweet.get('createdAtLocal')),
                        tweet.get('createdAtISO') or '',
                        tweet.get('isRetweet', False),
                        tweet.get('lang') or '',
                        json.dumps(media_urls),
                        json.dumps(external_urls)
                    ))

                except Exception as e:
                    print(f"插入推文失败: {e}")
                    continue

            conn.commit()
            cursor.close()
            conn.close()

            print(f"成功保存 {len(tweets)} 条推文到MySQL")
            return True

        except Exception as e:
            print(f"保存到MySQL失败: {e}")
            return False

    def save_to_sqlite(self, tweets: List[Dict], db_path: str = 'twitter_crawler.db') -> bool:
        """
        保存推文到SQLite数据库

        Args:
            tweets: 推文列表
            db_path: 数据库路径

        Returns:
            是否成功
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 创建表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS twitter_tweets (
                    id TEXT PRIMARY KEY,
                    text TEXT,
                    author_id TEXT,
                    author_name TEXT,
                    author_screen_name TEXT,
                    author_verified INTEGER,
                    likes INTEGER,
                    retweets INTEGER,
                    replies INTEGER,
                    quotes INTEGER,
                    views INTEGER,
                    bookmarks INTEGER,
                    created_at TEXT,
                    created_at_local TEXT,
                    created_at_iso TEXT,
                    is_retweet INTEGER,
                    lang TEXT,
                    media_urls TEXT,
                    external_urls TEXT,
                    crawled_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 插入数据
            for tweet in tweets:
                try:
                    # 提取媒体URL
                    media_urls = []
                    if 'media' in tweet and tweet['media']:
                        for media in tweet['media']:
                            if isinstance(media, dict) and 'url' in media:
                                media_urls.append(media['url'])

                    # 提取外部URL
                    external_urls = []
                    if 'urls' in tweet and tweet['urls']:
                        for url in tweet['urls']:
                            if isinstance(url, str):
                                external_urls.append(url)

                    # 提取作者信息
                    author_id = None
                    author_name = None
                    author_screen_name = None
                    author_verified = False

                    if 'author' in tweet and tweet['author']:
                        author = tweet['author']
                        if isinstance(author, dict):
                            author_id = author.get('id')
                            author_name = author.get('name')
                            author_screen_name = author.get('screenName')
                            author_verified = author.get('verified', False)

                    # 提取指标
                    metrics = tweet.get('metrics', {})
                    if isinstance(metrics, dict):
                        likes = metrics.get('likes', 0)
                        retweets = metrics.get('retweets', 0)
                        replies = metrics.get('replies', 0)
                        quotes = metrics.get('quotes', 0)
                        views = metrics.get('views', 0)
                        bookmarks = metrics.get('bookmarks', 0)
                    else:
                        likes = retweets = replies = quotes = views = bookmarks = 0

                    # 插入数据
                    cursor.execute("""
                        INSERT OR REPLACE INTO twitter_tweets
                        (id, text, author_id, author_name, author_screen_name, author_verified,
                         likes, retweets, replies, quotes, views, bookmarks,
                         created_at, created_at_local, created_at_iso, is_retweet, lang,
                         media_urls, external_urls)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tweet.get('id') or '',
                        tweet.get('text') or '',
                        author_id or '',
                        author_name or '',
                        author_screen_name or '',
                        1 if author_verified else 0,
                        likes,
                        retweets,
                        replies,
                        quotes,
                        views,
                        bookmarks,
                        self._parse_datetime(tweet.get('createdAt')) or '',
                        self._parse_datetime(tweet.get('createdAtLocal')) or '',
                        tweet.get('createdAtISO') or '',
                        1 if tweet.get('isRetweet', False) else 0,
                        tweet.get('lang') or '',
                        json.dumps(media_urls),
                        json.dumps(external_urls)
                    ))

                except Exception as e:
                    print(f"插入推文失败: {e}")
                    continue

            conn.commit()
            cursor.close()
            conn.close()

            print(f"成功保存 {len(tweets)} 条推文到SQLite")
            return True

        except Exception as e:
            print(f"保存到SQLite失败: {e}")
            return False


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("Twitter 爬虫 - 完整版本")
    print("=" * 60)
    print()

    # 从文件读取认证信息
    try:
        with open('twitter_auth.json', 'r', encoding='utf-8') as f:
            auth_data = json.load(f)

        auth_token = auth_data.get('auth_token')
        ct0 = auth_data.get('ct0')

        if not auth_token or not ct0:
            print("错误: 认证信息不完整")
            return

        print(f"认证信息已加载")
        print(f"auth_token: {auth_token[:20]}...{auth_token[-10:]}")
        print(f"ct0: {ct0[:20]}...{ct0[-10:]}")
        print()

    except Exception as e:
        print(f"读取认证信息失败: {e}")
        return

    # MySQL配置
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root123',
        'database': 'crawler_db',
        'charset': 'utf8mb4'
    }

    # 创建爬虫实例
    crawler = TwitterCrawler(auth_token, ct0, mysql_config)

    # 获取首页时间线
    print("获取首页时间线...")
    print("-" * 60)
    tweets = crawler.get_feed(count=10)

    if tweets:
        print(f"成功获取 {len(tweets)} 条推文")
        print()

        # 显示推文摘要
        print("推文摘要:")
        print("-" * 60)
        for i, tweet in enumerate(tweets, 1):
            author = tweet.get('author', {})
            author_name = author.get('name', 'Unknown') if isinstance(author, dict) else 'Unknown'
            text = tweet.get('text', '')[:50] + '...' if len(tweet.get('text', '')) > 50 else tweet.get('text', '')

            print(f"{i}. {author_name}: {text}")

        print()

        # 保存到MySQL
        print("保存到MySQL数据库...")
        print("-" * 60)
        if crawler.save_to_mysql(tweets):
            print("[OK] MySQL保存成功")
        else:
            print("[X] MySQL保存失败")

        print()

        # 保存到SQLite
        print("保存到SQLite数据库...")
        print("-" * 60)
        if crawler.save_to_sqlite(tweets):
            print("[OK] SQLite保存成功")
        else:
            print("[X] SQLite保存失败")

        print()
        print("=" * 60)
        print("[OK] 完成！")
        print()
        print("数据库信息:")
        print(f"  MySQL: crawler_db.twitter_tweets")
        print(f"  SQLite: twitter_crawler.db")

    else:
        print("未获取到推文")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
