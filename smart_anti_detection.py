"""
智能反爬虫策略系统
使用多种算法和技术绕过反爬虫限制
"""

import random
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
import hashlib
import threading
import queue


class AntiDetectionStrategy:
    """反检测策略基类"""

    def __init__(self):
        self.enabled = True
        self.success_count = 0
        self.failure_count = 0

    def apply(self, request_params: Dict) -> Dict:
        """应用策略到请求参数"""
        return request_params

    def record_success(self):
        """记录成功"""
        self.success_count += 1

    def record_failure(self):
        """记录失败"""
        self.failure_count += 1

    def get_success_rate(self) -> float:
        """获取成功率"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0


class UserAgentRotator(AntiDetectionStrategy):
    """User-Agent 轮换策略"""

    def __init__(self):
        super().__init__()
        self.user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
        ]
        self.current_index = 0

    def apply(self, request_params: Dict) -> Dict:
        """轮换User-Agent"""
        if 'headers' not in request_params:
            request_params['headers'] = {}

        # 随机选择或轮换
        if random.random() < 0.3:  # 30%概率随机选择
            user_agent = random.choice(self.user_agents)
        else:  # 70%概率轮换
            user_agent = self.user_agents[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.user_agents)

        request_params['headers']['User-Agent'] = user_agent
        return request_params


class RequestRateLimiter(AntiDetectionStrategy):
    """请求速率限制策略"""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        super().__init__()
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.request_times = deque(maxlen=10)  # 保存最近10次请求时间

    def apply(self, request_params: Dict) -> Dict:
        """应用速率限制"""
        current_time = time.time()

        # 计算需要等待的时间
        if self.last_request_time > 0:
            elapsed = current_time - self.last_request_time

            # 基于历史请求动态调整延迟
            if len(self.request_times) > 1:
                avg_interval = sum(self.request_times) / len(self.request_times)
                # 如果平均间隔太短，增加延迟
                if avg_interval < self.min_delay:
                    delay = random.uniform(self.min_delay, self.max_delay)
                    time.sleep(delay)

            # 确保最小延迟
            if elapsed < self.min_delay:
                delay = self.min_delay - elapsed
                time.sleep(delay)

        # 记录请求时间
        if self.last_request_time > 0:
            self.request_times.append(current_time - self.last_request_time)

        self.last_request_time = time.time()
        return request_params


class HeaderManager(AntiDetectionStrategy):
    """请求头管理策略"""

    def __init__(self):
        super().__init__()
        self.base_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

    def apply(self, request_params: Dict) -> Dict:
        """添加完整的请求头"""
        if 'headers' not in request_params:
            request_params['headers'] = {}

        # 合并基础请求头
        for key, value in self.base_headers.items():
            if key not in request_params['headers']:
                request_params['headers'][key] = value

        # 添加随机Referer
        referers = [
            'https://www.eastmoney.com/',
            'https://finance.sina.com.cn/',
            'https://www.10jqka.com.cn/',
            'https://www.baidu.com/',
        ]
        if 'Referer' not in request_params['headers']:
            request_params['headers']['Referer'] = random.choice(referers)

        return request_params


class ProxyRotator(AntiDetectionStrategy):
    """代理IP轮换策略"""

    def __init__(self, proxy_list: Optional[List[str]] = None):
        super().__init__()
        self.proxy_list = proxy_list or []
        self.current_index = 0
        self.proxy_stats = {}  # 记录每个代理的统计信息

    def add_proxy(self, proxy: str):
        """添加代理"""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
            self.proxy_stats[proxy] = {'success': 0, 'failure': 0}

    def apply(self, request_params: Dict) -> Dict:
        """轮换代理"""
        if not self.proxy_list:
            return request_params

        # 选择成功率最高的代理
        best_proxy = None
        best_rate = 0

        for proxy in self.proxy_list:
            stats = self.proxy_stats.get(proxy, {'success': 0, 'failure': 0})
            total = stats['success'] + stats['failure']
            if total > 0:
                rate = stats['success'] / total
                if rate > best_rate:
                    best_rate = rate
                    best_proxy = proxy

        # 如果没有统计数据，随机选择
        if best_proxy is None:
            best_proxy = random.choice(self.proxy_list)

        # 设置代理
        request_params['proxies'] = {
            'http': best_proxy,
            'https': best_proxy
        }

        return request_params

    def record_success(self):
        """记录成功"""
        super().record_success()
        # 记录当前代理的成功
        if self.proxy_list:
            proxy = self.proxy_list[self.current_index]
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]['success'] += 1

    def record_failure(self):
        """记录失败"""
        super().record_failure()
        # 记录当前代理的失败
        if self.proxy_list:
            proxy = self.proxy_list[self.current_index]
            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]['failure'] += 1
                # 切换到下一个代理
                self.current_index = (self.current_index + 1) % len(self.proxy_list)


class CookieManager(AntiDetectionStrategy):
    """Cookie管理策略"""

    def __init__(self):
        super().__init__()
        self.cookies = {}
        self.cookie_jar = {}

    def apply(self, request_params: Dict) -> Dict:
        """添加Cookie"""
        if self.cookies:
            if 'cookies' not in request_params:
                request_params['cookies'] = {}
            request_params['cookies'].update(self.cookies)

        return request_params

    def update_cookies(self, response):
        """更新Cookie"""
        if hasattr(response, 'cookies'):
            self.cookies.update(response.cookies)


class BehaviorSimulator(AntiDetectionStrategy):
    """人类行为模拟策略"""

    def __init__(self):
        super().__init__()
        self.mouse_movements = []
        self.scroll_events = []

    def apply(self, request_params: Dict) -> Dict:
        """模拟人类行为"""
        # 添加随机延迟，模拟人类思考时间
        think_time = random.uniform(0.5, 2.0)
        time.sleep(think_time)

        # 模拟鼠标移动（通过请求间隔）
        if random.random() < 0.2:  # 20%概率模拟鼠标移动
            time.sleep(random.uniform(0.1, 0.3))

        return request_params


class AdaptiveRetryStrategy(AntiDetectionStrategy):
    """自适应重试策略"""

    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries
        self.retry_delays = [1, 2, 4, 8]  # 指数退避

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False

        # 根据错误类型决定是否重试
        error_str = str(error).lower()
        if any(code in error_str for code in ['502', '503', '504', '429', 'timeout']):
            return True

        return False

    def get_retry_delay(self, attempt: int) -> float:
        """获取重试延迟"""
        if attempt < len(self.retry_delays):
            return self.retry_delays[attempt]
        return self.retry_delays[-1]


class SmartCrawler:
    """智能爬虫"""

    def __init__(self):
        self.strategies = [
            UserAgentRotator(),
            RequestRateLimiter(min_delay=1.0, max_delay=3.0),
            HeaderManager(),
            BehaviorSimulator(),
            AdaptiveRetryStrategy(max_retries=3),
        ]

        # 可选策略
        self.proxy_rotator = None
        self.cookie_manager = None

    def add_proxy_rotator(self, proxy_list: List[str]):
        """添加代理轮换"""
        self.proxy_rotator = ProxyRotator(proxy_list)
        self.strategies.insert(2, self.proxy_rotator)  # 在请求头管理之后添加

    def add_cookie_manager(self):
        """添加Cookie管理"""
        self.cookie_manager = CookieManager()
        self.strategies.insert(3, self.cookie_manager)

    def apply_strategies(self, request_params: Dict) -> Dict:
        """应用所有策略"""
        for strategy in self.strategies:
            if strategy.enabled:
                request_params = strategy.apply(request_params)
        return request_params

    def record_success(self):
        """记录成功"""
        for strategy in self.strategies:
            strategy.record_success()

    def record_failure(self):
        """记录失败"""
        for strategy in self.strategies:
            strategy.record_failure()

    def get_request(self, url: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """执行GET请求"""
        request_params = {
            'url': url,
            'params': params,
            'timeout': 15,
            **kwargs
        }

        # 应用所有策略
        request_params = self.apply_strategies(request_params)

        # 执行请求（带重试）
        retry_strategy = next((s for s in self.strategies if isinstance(s, AdaptiveRetryStrategy)), None)

        for attempt in range(retry_strategy.max_retries if retry_strategy else 1):
            try:
                response = requests.get(**request_params)

                # 更新Cookie
                if self.cookie_manager:
                    self.cookie_manager.update_cookies(response)

                # 记录成功
                self.record_success()

                return response

            except Exception as e:
                # 记录失败
                self.record_failure()

                # 判断是否重试
                if retry_strategy and retry_strategy.should_retry(attempt, e):
                    delay = retry_strategy.get_retry_delay(attempt)
                    print(f"请求失败，{delay}秒后重试... (尝试 {attempt + 1}/{retry_strategy.max_retries})")
                    time.sleep(delay)
                else:
                    raise

    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            'total_requests': 0,
            'total_success': 0,
            'total_failure': 0,
            'strategies': {}
        }

        for strategy in self.strategies:
            stats['strategies'][strategy.__class__.__name__] = {
                'success': strategy.success_count,
                'failure': strategy.failure_count,
                'success_rate': strategy.get_success_rate()
            }
            stats['total_success'] += strategy.success_count
            stats['total_failure'] += strategy.failure_count

        stats['total_requests'] = stats['total_success'] + stats['total_failure']

        return stats


def test_smart_crawler():
    """测试智能爬虫"""
    print("=" * 60)
    print("智能反爬虫策略系统测试")
    print("=" * 60)

    # 创建智能爬虫
    crawler = SmartCrawler()

    # 测试URL列表
    test_urls = [
        'http://www.eastmoney.com/',
        'http://finance.sina.com.cn/',
        'http://www.10jqka.com.cn/',
    ]

    print(f"\n测试 {len(test_urls)} 个URL...")
    print()

    for i, url in enumerate(test_urls, 1):
        print(f"{i}. 测试: {url}")
        try:
            response = crawler.get_request(url)
            print(f"   成功! 状态码: {response.status_code}, 内容长度: {len(response.text)}")
        except Exception as e:
            print(f"   失败: {e}")
        print()

    # 显示统计信息
    stats = crawler.get_stats()
    print("=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功: {stats['total_success']}")
    print(f"失败: {stats['total_failure']}")
    print(f"成功率: {stats['total_success']/stats['total_requests']*100:.1f}%")
    print()

    print("各策略统计:")
    for strategy_name, strategy_stats in stats['strategies'].items():
        print(f"  {strategy_name}:")
        print(f"    成功: {strategy_stats['success']}")
        print(f"    失败: {strategy_stats['failure']}")
        print(f"    成功率: {strategy_stats['success_rate']*100:.1f}%")

    return crawler


if __name__ == "__main__":
    test_smart_crawler()
