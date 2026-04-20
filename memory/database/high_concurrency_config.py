"""
企业级高并发配置
支持异步处理、连接池、限流、负载均衡
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable
from datetime import datetime
import time
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import multiprocessing


class HighConcurrencyConfig:
    """企业级高并发配置"""
    
    def __init__(self):
        """初始化配置"""
        # 连接池配置
        self.connection_pool_size = 100
        self.max_connections_per_host = 20
        
        # 线程池配置
        self.thread_pool_size = multiprocessing.cpu_count() * 2
        self.process_pool_size = multiprocessing.cpu_count()
        
        # 限流配置
        self.rate_limit = {
            "requests_per_second": 1000,
            "requests_per_minute": 60000,
            "concurrent_requests": 500
        }
        
        # 负载均衡配置
        self.load_balancer = LoadBalancer()
        
        # 缓存配置
        self.cache_config = {
            "enabled": True,
            "ttl": 3600,
            "max_size": 10000
        }
        
        # 重试配置
        self.retry_config = {
            "max_retries": 3,
            "retry_delay": 1,
            "backoff_factor": 2
        }
        
        # 超时配置
        self.timeout_config = {
            "connect_timeout": 10,
            "read_timeout": 30,
            "total_timeout": 60
        }
        
        # 初始化组件
        self.session = None
        self.thread_pool = None
        self.process_pool = None
        self.rate_limiter = RateLimiter(self.rate_limit)
        self.cache = Cache(self.cache_config)
    
    async def initialize(self):
        """初始化异步组件"""
        # 创建 HTTP 会话
        connector = aiohttp.TCPConnector(
            limit=self.connection_pool_size,
            limit_per_host=self.max_connections_per_host
        )
        
        timeout = aiohttp.ClientTimeout(
            connect=self.timeout_config["connect_timeout"],
            total=self.timeout_config["total_timeout"]
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        
        # 创建线程池
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.thread_pool_size
        )
        
        # 创建进程池
        self.process_pool = ProcessPoolExecutor(
            max_workers=self.process_pool_size
        )
    
    async def shutdown(self):
        """关闭所有组件"""
        if self.session:
            await self.session.close()
        
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
    
    async def execute_concurrent(self, tasks: List[Callable]) -> List[any]:
        """并发执行任务"""
        # 限流
        await self.rate_limiter.acquire()
        
        # 执行任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def execute_with_retry(self, task: Callable, *args, **kwargs) -> any:
        """带重试的执行"""
        max_retries = self.retry_config["max_retries"]
        retry_delay = self.retry_config["retry_delay"]
        backoff_factor = self.retry_config["backoff_factor"]
        
        for attempt in range(max_retries):
            try:
                result = await task(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                # 指数退避
                delay = retry_delay * (backoff_factor ** attempt)
                await asyncio.sleep(delay)
    
    async def execute_with_cache(self, key: str, task: Callable, *args, **kwargs) -> any:
        """带缓存的执行"""
        # 检查缓存
        cached_result = self.cache.get(key)
        if cached_result is not None:
            return cached_result
        
        # 执行任务
        result = await task(*args, **kwargs)
        
        # 存入缓存
        self.cache.set(key, result)
        
        return result
    
    def execute_in_thread(self, func: Callable, *args, **kwargs) -> any:
        """在线程中执行"""
        future = self.thread_pool.submit(func, *args, **kwargs)
        return future.result()
    
    def execute_in_process(self, func: Callable, *args, **kwargs) -> any:
        """在进程中执行"""
        future = self.process_pool.submit(func, *args, **kwargs)
        return future.result()
    
    async def batch_process(self, items: List[any], processor: Callable, batch_size: int = 100) -> List[any]:
        """批量处理"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # 并发处理批次
            tasks = [processor(item) for item in batch]
            batch_results = await self.execute_concurrent(tasks)
            
            results.extend(batch_results)
        
        return results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "connection_pool_size": self.connection_pool_size,
            "active_connections": len(self.session.connector._conns) if self.session and hasattr(self.session.connector, '_conns') else 0,
            "thread_pool_size": self.thread_pool_size,
            "active_threads": self.thread_pool._threads if self.thread_pool else 0,
            "process_pool_size": self.process_pool_size,
            "active_processes": len(self.process_pool._processes) if self.process_pool else 0,
            "rate_limit": self.rate_limiter.get_stats(),
            "cache": self.cache.get_stats()
        }


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self):
        """初始化负载均衡器"""
        self.servers = []
        self.current_index = 0
        self.lock = threading.Lock()
    
    def add_server(self, server: str):
        """添加服务器"""
        self.servers.append(server)
    
    def get_server(self) -> Optional[str]:
        """获取服务器（轮询）"""
        if not self.servers:
            return None
        
        with self.lock:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server
    
    def get_least_loaded_server(self) -> Optional[str]:
        """获取负载最低的服务器"""
        # 简化实现，实际应该监控服务器负载
        return self.get_server()


class RateLimiter:
    """限流器"""
    
    def __init__(self, config: Dict):
        """初始化限流器"""
        self.requests_per_second = config["requests_per_second"]
        self.requests_per_minute = config["requests_per_minute"]
        self.concurrent_requests = config["concurrent_requests"]
        
        self.request_times = []
        self.concurrent_count = 0
        self.lock = threading.Lock()
    
    async def acquire(self):
        """获取许可"""
        with self.lock:
            # 检查并发限制
            if self.concurrent_count >= self.concurrent_requests:
                await asyncio.sleep(0.1)
                await self.acquire()
                return
            
            self.concurrent_count += 1
        
        try:
            # 检查速率限制
            now = time.time()
            
            with self.lock:
                # 清理过期的请求时间
                self.request_times = [t for t in self.request_times if now - t < 60]
                
                # 检查每分钟限制
                if len(self.request_times) >= self.requests_per_minute:
                    await asyncio.sleep(1)
                    await self.acquire()
                    return
                
                # 检查每秒限制
                recent_requests = [t for t in self.request_times if now - t < 1]
                if len(recent_requests) >= self.requests_per_second:
                    await asyncio.sleep(0.1)
                    await self.acquire()
                    return
                
                # 记录请求时间
                self.request_times.append(now)
        finally:
            with self.lock:
                self.concurrent_count -= 1
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            return {
                "requests_per_second": self.requests_per_second,
                "requests_per_minute": self.requests_per_minute,
                "concurrent_requests": self.concurrent_requests,
                "current_concurrent": self.concurrent_count,
                "recent_requests": len([t for t in self.request_times if time.time() - t < 60])
            }


class Cache:
    """缓存"""
    
    def __init__(self, config: Dict):
        """初始化缓存"""
        self.enabled = config["enabled"]
        self.ttl = config["ttl"]
        self.max_size = config["max_size"]
        
        self.cache = {}
        self.expiry_times = {}
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[any]:
        """获取缓存"""
        if not self.enabled:
            return None
        
        with self.lock:
            # 检查是否过期
            if key in self.expiry_times:
                if time.time() > self.expiry_times[key]:
                    self.remove(key)
                    return None
            
            return self.cache.get(key)
    
    def set(self, key: str, value: any):
        """设置缓存"""
        if not self.enabled:
            return
        
        with self.lock:
            # 检查大小限制
            if len(self.cache) >= self.max_size:
                self.evict_oldest()
            
            self.cache[key] = value
            self.expiry_times[key] = time.time() + self.ttl
    
    def remove(self, key: str):
        """删除缓存"""
        with self.lock:
            self.cache.pop(key, None)
            self.expiry_times.pop(key, None)
    
    def evict_oldest(self):
        """淘汰最旧的缓存"""
        if not self.expiry_times:
            return
        
        oldest_key = min(self.expiry_times, key=self.expiry_times.get)
        self.remove(oldest_key)
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.expiry_times.clear()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self.lock:
            return {
                "enabled": self.enabled,
                "ttl": self.ttl,
                "max_size": self.max_size,
                "current_size": len(self.cache),
                "hit_rate": self.calculate_hit_rate()
            }
    
    def calculate_hit_rate(self) -> float:
        """计算命中率"""
        # 简化实现，实际应该跟踪命中和未命中
        return 0.0


# 使用示例
if __name__ == "__main__":
    async def main():
        # 初始化
        config = HighConcurrencyConfig()
        await config.initialize()
        
        # 示例任务
        async def sample_task(item):
            await asyncio.sleep(0.1)
            return f"Processed: {item}"
        
        # 批量处理
        items = [f"item_{i}" for i in range(100)]
        results = await config.batch_process(items, sample_task, batch_size=10)
        
        print(f"Processed {len(results)} items")
        
        # 获取统计信息
        stats = config.get_stats()
        print(f"Stats: {stats}")
        
        # 关闭
        await config.shutdown()
    
    asyncio.run(main())
