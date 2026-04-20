"""
Twitter/X 内容爬取演示
使用 twitter-cli 爬取 Twitter/X 平台内容
"""

import subprocess
import json
import re
from datetime import datetime
from typing import Dict, List, Optional


class TwitterCrawler:
    """Twitter/X 内容爬虫"""

    def __init__(self):
        """初始化爬虫"""
        self.version = self._get_version()

    def _get_version(self) -> str:
        """获取 twitter-cli 版本"""
        try:
            result = subprocess.run(['twitter', '--version'],
                                  capture_output=True, text=True, timeout=10)
            return result.stdout.strip()
        except Exception as e:
            return f"Error: {e}"

    def _run_command(self, command: List[str]) -> Optional[str]:
        """执行命令"""
        try:
            result = subprocess.run(command,
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout
            else:
                print(f"命令执行失败: {result.stderr}")
                return None
        except Exception as e:
            print(f"执行命令时出错: {e}")
            return None

    def get_feed(self, count: int = 20) -> Optional[List[Dict]]:
        """获取首页时间线"""
        print(f"获取首页时间线 (最近 {count} 条推文)...")

        output = self._run_command(['twitter', 'feed', '-n', str(count)])

        if output:
            # 尝试解析JSON输出
            try:
                tweets = json.loads(output)
                print(f"成功获取 {len(tweets)} 条推文")
                return tweets
            except json.JSONDecodeError:
                # 如果不是JSON，返回原始文本
                print("获取到文本格式数据")
                return [{'raw_text': output}]

        return None

    def get_tweet(self, tweet_id_or_url: str) -> Optional[Dict]:
        """读取单条推文"""
        print(f"读取推文: {tweet_id_or_url}")

        output = self._run_command(['twitter', 'tweet', tweet_id_or_url])

        if output:
            try:
                tweet = json.loads(output)
                print("成功获取推文详情")
                return tweet
            except json.JSONDecodeError:
                return {'raw_text': output}

        return None

    def get_article(self, article_id_or_url: str) -> Optional[Dict]:
        """读取长文 / X Article"""
        print(f"读取长文: {article_id_or_url}")

        output = self._run_command(['twitter', 'article', article_id_or_url])

        if output:
            try:
                article = json.loads(output)
                print("成功获取长文详情")
                return article
            except json.JSONDecodeError:
                return {'raw_text': output}

        return None

    def get_user_posts(self, username: str, count: int = 20) -> Optional[List[Dict]]:
        """获取用户时间线"""
        print(f"获取用户 @{username} 的推文 (最近 {count} 条)...")

        output = self._run_command(['twitter', 'user-posts', f'@{username}', '-n', str(count)])

        if output:
            try:
                tweets = json.loads(output)
                print(f"成功获取 {len(tweets)} 条推文")
                return tweets
            except json.JSONDecodeError:
                return [{'raw_text': output}]

        return None

    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户资料"""
        print(f"获取用户 @{username} 的资料...")

        output = self._run_command(['twitter', 'user', f'@{username}'])

        if output:
            try:
                user_info = json.loads(output)
                print("成功获取用户资料")
                return user_info
            except json.JSONDecodeError:
                return {'raw_text': output}

        return None

    def search_tweets(self, query: str, count: int = 10) -> Optional[List[Dict]]:
        """搜索推文（可能不稳定）"""
        print(f"搜索推文: {query} (最近 {count} 条)...")

        output = self._run_command(['twitter', 'search', query, '-n', str(count)])

        if output:
            try:
                tweets = json.loads(output)
                print(f"成功搜索到 {len(tweets)} 条推文")
                return tweets
            except json.JSONDecodeError:
                return [{'raw_text': output}]

        return None

    def format_tweet(self, tweet: Dict) -> str:
        """格式化推文显示"""
        if 'raw_text' in tweet:
            return tweet['raw_text']

        lines = []
        lines.append(f"ID: {tweet.get('id', 'N/A')}")
        lines.append(f"作者: @{tweet.get('username', 'N/A')}")
        lines.append(f"内容: {tweet.get('text', 'N/A')}")
        lines.append(f"时间: {tweet.get('created_at', 'N/A')}")
        lines.append(f"点赞: {tweet.get('favorite_count', 0)}")
        lines.append(f"转发: {tweet.get('retweet_count', 0)}")
        lines.append(f"回复: {tweet.get('reply_count', 0)}")

        return '\n'.join(lines)


def main():
    """主函数"""
    print("=" * 60)
    print("Twitter/X 内容爬取演示")
    print("=" * 60)
    print(f"twitter-cli 版本: {TwitterCrawler()._get_version()}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 创建爬虫
    crawler = TwitterCrawler()

    # 演示功能
    print("1. 获取首页时间线")
    print("-" * 60)
    feed = crawler.get_feed(count=5)
    if feed:
        for i, tweet in enumerate(feed[:3], 1):
            print(f"\n推文 {i}:")
            print(crawler.format_tweet(tweet))

    print("\n" + "=" * 60)
    print("2. 获取用户资料")
    print("-" * 60)
    # 示例用户（可以替换为实际用户名）
    user_info = crawler.get_user_info('elonmusk')
    if user_info:
        print(json.dumps(user_info, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("3. 搜索推文")
    print("-" * 60)
    # 示例搜索（可以替换为实际搜索词）
    search_results = crawler.search_tweets('AI', count=3)
    if search_results:
        for i, tweet in enumerate(search_results[:3], 1):
            print(f"\n搜索结果 {i}:")
            print(crawler.format_tweet(tweet))

    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
