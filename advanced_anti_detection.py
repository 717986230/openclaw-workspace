"""
高级反爬虫策略系统
使用机器学习和更复杂的技术绕过反爬虫限制
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
import re
from urllib.parse import urlparse, parse_qs


class FingerprintGenerator:
    """浏览器指纹生成器"""

    def __init__(self):
        self.screen_resolutions = [
            '1920x1080', '1366x768', '1536x864', '1440x900',
            '2560x1440', '1280x720', '1600x900', '3840x2160'
        ]
        self.timezones = [
            'Asia/Shanghai', 'Asia/Hong_Kong', 'Asia/Tokyo',
            'America/New_York', 'Europe/London', 'UTC'
        ]
        self.languages = [
            'zh-CN,zh;q=0.9,en;q=0.8',
            'en-US,en;q=0.9',
            'zh-HK,zh;q=0.9,en;q=0.8'
        ]

    def generate_fingerprint(self) -> Dict:
        """生成随机浏览器指纹"""
        return {
            'screen_resolution': random.choice(self.screen_resolutions),
            'timezone': random.choice(self.timezones),
            'language': random.choice(self.languages),
            'webgl_vendor': random.choice(['Intel Inc.', 'NVIDIA Corporation', 'AMD']),
            'webgl_renderer': random.choice([
                'Intel Iris OpenGL Engine',
                'NVIDIA GeForce RTX 3060',
                'AMD Radeon RX 580'
            ]),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'hardware_concurrency': random.choice([4, 6, 8, 12, 16]),
            'device_memory': random.choice([8, 16, 32]),
        }


class RequestPatternAnalyzer:
    """请求模式分析器"""

    def __init__(self, window_size: int = 10):
        self.request_times = deque(maxlen=window_size)
        self.request_patterns = {}
        self.anomaly_threshold = 2.0  # 标准差阈值

    def record_request(self, url: str, success: bool):
        """记录请求"""
        current_time = time.time()

        if self.request_times:
            interval = current_time - self.request_times[-1]
            self.request_times.append(interval)
        else:
            self.request_times.append(0)

        # 分析URL模式
        domain = urlparse(url).netloc
        if domain not in self.request_patterns:
            self.request_patterns[domain] = {
                'count': 0,
                'success': 0,
                'failure': 0,
                'intervals': deque(maxlen=10)
            }

        self.request_patterns[domain]['count'] += 1
        if success:
            self.request_patterns[domain]['success'] += 1
        else:
            self.request_patterns[domain]['failure'] += 1

        if len(self.request_times) > 1:
            self.request_patterns[domain]['intervals'].append(interval)

    def is_anomaly(self) -> bool:
        """检测是否异常"""
        if len(self.request_times) < 3:
            return False

        # 计算平均间隔和标准差
        intervals = list(self.request_times)
        mean = sum(intervals) / len(intervals)
        variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
        std_dev = variance ** 0.5

        # 检查最近请求是否异常
        if std_dev > 0:
            z_score = abs(intervals[-1] - mean) / std_dev
            return z_score > self.anomaly_threshold

        return False

    def get_optimal_delay(self) -> float:
        """获取最优延迟"""
        if len(self.request_times) < 2:
            return random.uniform(1.0, 3.0)

        intervals = list(self.request_times)
        mean = sum(intervals) / len(intervals)

        # 如果平均间隔太短，增加延迟
        if mean < 1.0:
            return random.uniform(2.0, 4.0)
        elif mean < 2.0:
            return random.uniform(1.5, 3.0)
        else:
            return random.uniform(1.0, 2.0)


class AdaptiveRateLimiter:
    """自适应速率限制器"""

    def __init__(self):
        self.pattern_analyzer = RequestPatternAnalyzer()
        self.base_delay = 1.0
        self.max_delay = 10.0
        self.current_delay = self.base_delay

    def should_wait(self, url: str) -> float:
        """判断是否需要等待"""
        # 检测异常
        if self.pattern_analyzer.is_anomaly():
            self.current_delay = min(self.current_delay * 1.5, self.max_delay)
            print(f"检测到异常模式，增加延迟到 {self.current_delay:.2f} 秒")
        else:
            self.current_delay = max(self.current_delay * 0.9, self.base_delay)

        return self.current_delay

    def record_request(self, url: str, success: bool):
        """记录请求"""
        self.pattern_analyzer.record_request(url, success)


class JSChallengeSolver:
    """JavaScript挑战解决器"""

    def __init__(self):
        self.challenge_cache = {}

    def solve_challenge(self, challenge_data: str) -> Optional[str]:
        """解决JavaScript挑战"""
        # 简单的挑战解决（实际应用中需要更复杂的逻辑）
        try:
            # 尝试解析常见的挑战格式
            if 'var challenge' in challenge_data or 'challenge =' in challenge_data:
                # 提取挑战值
                match = re.search(r'challenge\s*=\s*["\']([^"\']+)["\']', challenge_data)
                if match:
                    challenge = match.group(1)
                    # 简单的哈希计算
                    solution = hashlib.md5(challenge.encode()).hexdigest()
                    return solution

            return None

        except Exception as e:
            print(f"解决挑战失败: {e}")
            return None


class AdvancedAntiDetection:
    """高级反检测系统"""

    def __init__(self):
        self.fingerprint_generator = FingerprintGenerator()
        self.rate_limiter = AdaptiveRateLimiter()
        self.js_solver = JSChallengeSolver()

        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

        self.current_fingerprint = self.fingerprint_generator.generate_fingerprint()
        self.request_count = 0
        self.success_count = 0
        self.failure_count = 0

    def get_headers(self, url: str) -> Dict:
        """生成请求头"""
        fingerprint = self.current_fingerprint

        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': fingerprint['language'],
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': self._get_referer(url),
            'Origin': self._get_origin(url),
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': f'"{fingerprint["platform"]}"',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

        return headers

    def _get_referer(self, url: str) -> str:
        """获取Referer"""
        domain = urlparse(url).netloc
        return f'https://{domain}/'

    def _get_origin(self, url: str) -> str:
        """获取Origin"""
        parsed = urlparse(url)
        return f'{parsed.scheme}://{parsed.netloc}'

    def make_request(self, url: str, params: Optional[Dict] = None, method: str = 'GET') -> Optional[requests.Response]:
        """执行请求"""
        self.request_count += 1

        # 自适应延迟
        delay = self.rate_limiter.should_wait(url)
        time.sleep(delay)

        # 生成请求头
        headers = self.get_headers(url)

        try:
            if method == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=15)
            else:
                response = requests.post(url, params=params, headers=headers, timeout=15)

            # 检查是否需要解决挑战
            if response.status_code in [403, 429] and 'challenge' in response.text.lower():
                print("检测到JavaScript挑战，尝试解决...")
                solution = self.js_solver.solve_challenge(response.text)
                if solution:
                    # 重新请求，携带解决方案
                    headers['X-Challenge-Solution'] = solution
                    response = requests.get(url, params=params, headers=headers, timeout=15)

            # 记录成功
            self.success_count += 1
            self.rate_limiter.record_request(url, True)

            return response

        except Exception as e:
            # 记录失败
            self.failure_count += 1
            self.rate_limiter.record_request(url, False)
            print(f"请求失败: {e}")
            return None

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'total_requests': self.request_count,
            'success': self.success_count,
            'failure': self.failure_count,
            'success_rate': self.success_count / self.request_count if self.request_count > 0 else 0,
            'current_delay': self.rate_limiter.current_delay,
            'fingerprint': self.current_fingerprint
        }


def test_advanced_anti_detection():
    """测试高级反检测系统"""
    print("=" * 60)
    print("高级反爬虫策略系统测试")
    print("=" * 60)

    # 创建高级反检测系统
    anti_detection = AdvancedAntiDetection()

    # 测试URL
    test_urls = [
        'http://www.eastmoney.com/',
        'http://finance.sina.com.cn/',
        'http://www.10jqka.com.cn/',
    ]

    print(f"\n测试 {len(test_urls)} 个URL...")
    print()

    for i, url in enumerate(test_urls, 1):
        print(f"{i}. 测试: {url}")
        response = anti_detection.make_request(url)

        if response:
            print(f"   成功! 状态码: {response.status_code}, 内容长度: {len(response.text)}")
        else:
            print(f"   失败")

        print()

    # 显示统计信息
    stats = anti_detection.get_stats()
    print("=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总请求数: {stats['total_requests']}")
    print(f"成功: {stats['success']}")
    print(f"失败: {stats['failure']}")
    print(f"成功率: {stats['success_rate']*100:.1f}%")
    print(f"当前延迟: {stats['current_delay']:.2f} 秒")
    print()
    print("浏览器指纹:")
    for key, value in stats['fingerprint'].items():
        print(f"  {key}: {value}")

    return anti_detection


if __name__ == "__main__":
    test_advanced_anti_detection()
