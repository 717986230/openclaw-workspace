"""
顶级高并发分布式处理系统 v2.0
企业级分布式架构
"""

import asyncio
import aiohttp
import json
import time
import threading
import multiprocessing
import hashlib
import pickle
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
import random
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEGRADED = "degraded"
    FAILED = "failed"


class LoadBalanceStrategy(Enum):
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CONSISTENT_HASH = "consistent_hash"
    ADAPTIVE = "adaptive"


@dataclass
class Node:
    node_id: str
    host: str
    port: int
    status: NodeStatus = NodeStatus.ACTIVE
    weight: int = 1
    connections: int = 0
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payload: Any = None
    priority: int = 0
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None


class DistributedCache:
    def __init__(self, config: Dict):
        self.enabled = config.get("enabled", True)
        self.backend = config.get("backend", "memory")
        self.ttl = config.get("ttl", 3600)
        self.max_size = config.get("max_size", 100000)
        self.memory_cache = {}
        self.expiry_times = {}
        self.lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.enabled:
            return None
        try:
            with self.lock:
                if key in self.expiry_times:
                    if time.time() > self.expiry_times[key]:
                        self.remove(key)
                        return None
                return self.memory_cache.get(key)
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        if not self.enabled:
            return
        try:
            ttl = ttl or self.ttl
            with self.lock:
                if len(self.memory_cache) >= self.max_size:
                    self.evict_oldest()
                self.memory_cache[key] = value
                self.expiry_times[key] = time.time() + ttl
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
    
    def evict_oldest(self):
        if not self.expiry_times:
            return
        oldest_key = min(self.expiry_times, key=self.expiry_times.get)
        self.remove(oldest_key)
    
    def remove(self, key: str):
        with self.lock:
            self.memory_cache.pop(key, None)
            self.expiry_times.pop(key, None)
    
    async def clear(self):
        with self.lock:
            self.memory_cache.clear()
            self.expiry_times.clear()
    
    def get_stats(self) -> Dict:
        with self.lock:
            return {
                "backend": self.backend,
                "enabled": self.enabled,
                "ttl": self.ttl,
                "max_size": self.max_size,
                "current_size": len(self.memory_cache)
            }


class MessageQueue:
    def __init__(self, config: Dict):
        self.backend = config.get("backend", "memory")
        self.max_size = config.get("max_size", 10000)
        self.queues = defaultdict(deque)
        self.locks = defaultdict(threading.Lock)
    
    async def publish(self, queue_name: str, message: Any):
        try:
            with self.locks[queue_name]:
                if len(self.queues[queue_name]) >= self.max_size:
                    self.queues[queue_name].popleft()
                self.queues[queue_name].append({
                    "message": message,
                    "timestamp": time.time()
                })
        except Exception as e:
            logger.error(f"Message publish failed: {e}")
    
    async def consume(self, queue_name: str, callback: Callable):
        try:
            while True:
                with self.locks[queue_name]:
                    if self.queues[queue_name]:
                        item = self.queues[queue_name].popleft()
                        await callback(item["message"])
                await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Message consume failed: {e}")
    
    def get_stats(self) -> Dict:
        return {
            "backend": self.backend,
            "max_size": self.max_size,
            "queues": {name: len(queue) for name, queue in self.queues.items()}
        }


class ServiceDiscovery:
    def __init__(self):
        self.services: Dict[str, List[Node]] = defaultdict(list)
        self.lock = threading.RLock()
        self.heartbeat_interval = 30
        self.heartbeat_timeout = 90
    
    def register(self, service_name: str, node: Node):
        with self.lock:
            existing = next((n for n in self.services[service_name] if n.node_id == node.node_id), None)
            if existing:
                existing.last_heartbeat = datetime.now()
                existing.status = NodeStatus.ACTIVE
            else:
                self.services[service_name].append(node)
                logger.info(f"Service registered: {service_name} -> {node.node_id}")
    
    def discover(self, service_name: str) -> List[Node]:
        with self.lock:
            now = datetime.now()
            self.services[service_name] = [
                n for n in self.services[service_name]
                if (now - n.last_heartbeat).total_seconds() < self.heartbeat_timeout
            ]
            return [n for n in self.services[service_name] if n.status == NodeStatus.ACTIVE]
    
    def heartbeat(self, service_name: str, node_id: str):
        with self.lock:
            for node in self.services[service_name]:
                if node.node_id == node_id:
                    node.last_heartbeat = datetime.now()
                    node.status = NodeStatus.ACTIVE
                    break
    
    def get_stats(self) -> Dict:
        with self.lock:
            return {
                "services": {
                    name: {
                        "total": len(nodes),
                        "active": len([n for n in nodes if n.status == NodeStatus.ACTIVE])
                    }
                    for name, nodes in self.services.items()
                }
            }


class LoadBalancer:
    def __init__(self, strategy: LoadBalanceStrategy = LoadBalanceStrategy.ROUND_ROBIN):
        self.strategy = strategy
        self.current_index = 0
        self.lock = threading.Lock()
    
    def select_node(self, nodes: List[Node]) -> Optional[Node]:
        if not nodes:
            return None
        
        active_nodes = [n for n in nodes if n.status == NodeStatus.ACTIVE]
        if not active_nodes:
            return None
        
        with self.lock:
            if self.strategy == LoadBalanceStrategy.ROUND_ROBIN:
                node = active_nodes[self.current_index % len(active_nodes)]
                self.current_index += 1
                return node
            
            elif self.strategy == LoadBalanceStrategy.LEAST_CONNECTIONS:
                return min(active_nodes, key=lambda n: n.connections)
            
            elif self.strategy == LoadBalanceStrategy.WEIGHTED_ROUND_ROBIN:
                total_weight = sum(n.weight for n in active_nodes)
                if total_weight == 0:
                    return active_nodes[0]
                weight_sum = 0
                rand = random.uniform(0, total_weight)
                for node in active_nodes:
                    weight_sum += node.weight
                    if rand <= weight_sum:
                        return node
                return active_nodes[-1]
            
            else:
                return active_nodes[0]


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"
        self.lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self.lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half-open"
                else:
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            with self.lock:
                if self.state == "half-open":
                    self.state = "closed"
                    self.failure_count = 0
            return result
        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = "open"
            raise
    
    def get_stats(self) -> Dict:
        with self.lock:
            return {
                "state": self.state,
                "failure_count": self.failure_count,
                "failure_threshold": self.failure_threshold
            }


class RateLimiter:
    def __init__(self, config: Dict):
        self.algorithm = config.get("algorithm", "token_bucket")
        self.requests_per_second = config.get("requests_per_second", 1000)
        self.requests_per_minute = config.get("requests_per_minute", 60000)
        self.concurrent_requests = config.get("concurrent_requests", 500)
        
        self.tokens = self.requests_per_second
        self.last_refill_time = time.time()
        self.concurrent_count = 0
        self.request_history = deque()
        self.lock = threading.Lock()
    
    async def acquire(self):
        with self.lock:
            self.concurrent_count += 1
        
        try:
            if self.algorithm == "token_bucket":
                await self._token_bucket_acquire()
            else:
                await self._leaky_bucket_acquire()
        finally:
            with self.lock:
                self.concurrent_count -= 1
    
    async def _token_bucket_acquire(self):
        while True:
            with self.lock:
                now = time.time()
                elapsed = now - self.last_refill_time
                self.tokens = min(
                    self.requests_per_second,
                    self.tokens + elapsed * self.requests_per_second
                )
                self.last_refill_time = now
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            
            await asyncio.sleep(0.01)
    
    async def _leaky_bucket_acquire(self):
        while True:
            with self.lock:
                now = time.time()
                self.request_history = [
                    t for t in self.request_history
                    if now - t < 60
                ]
                
                if len(self.request_history) < self.requests_per_minute:
                    self.request_history.append(now)
                    return
            
            await asyncio.sleep(0.01)
    
    def get_stats(self) -> Dict:
        with self.lock:
            return {
                "algorithm": self.algorithm,
                "requests_per_second": self.requests_per_second,
                "requests_per_minute": self.requests_per_minute,
                "concurrent_requests": self.concurrent_requests,
                "current_concurrent": self.concurrent_count,
                "tokens": self.tokens
            }


class UltimateDistributedSystem:
    def __init__(self, config: Dict):
        self.config = config
        self.cache = DistributedCache(config.get("cache", {}))
        self.message_queue = MessageQueue(config.get("message_queue", {}))
        self.service_discovery = ServiceDiscovery()
        
        strategy_name = config.get("load_balancer", {}).get("strategy", "round_robin")
        self.load_balancer = LoadBalancer(LoadBalanceStrategy(strategy_name))
        
        self.rate_limiter = RateLimiter(config.get("rate_limiter", {}))
        self.circuit_breaker = CircuitBreaker(
            config.get("circuit_breaker", {}).get("failure_threshold", 10),
            config.get("circuit_breaker", {}).get("timeout", 60)
        )
        
        self.session = None
        self.thread_pool = None
        self.process_pool = None
        self.total_tasks_processed = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = None
    
    async def initialize(self):
        connector = aiohttp.TCPConnector(limit=1000)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        self.thread_pool = ThreadPoolExecutor(max_workers=64)
        self.process_pool = ProcessPoolExecutor(max_workers=16)
        self.start_time = time.time()
        logger.info("System initialized")
    
    async def shutdown(self):
        if self.session:
            await self.session.close()
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
        logger.info("System shutdown")
    
    async def execute_task(self, task: Task) -> Any:
        await self.rate_limiter.acquire()
        
        cache_key = f"task:{task.task_id}"
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            self.cache_hits += 1
            return cached_result
        
        self.cache_misses += 1
        
        try:
            result = self.circuit_breaker.call(
                self._execute_task_internal,
                task
            )
            await self.cache.set(cache_key, result)
            self.total_tasks_processed += 1
            return result
        except Exception as e:
            task.error = str(e)
            task.status = "failed"
            raise
    
    def _execute_task_internal(self, task: Task) -> Any:
        if asyncio.iscoroutinefunction(task.payload):
            return asyncio.run(task.payload())
        elif callable(task.payload):
            return task.payload()
        else:
            return task.payload
    
    async def run_performance_test(self):
        logger.info("Running performance test...")
        
        async def sample_task(i):
            await asyncio.sleep(0.001)
            return f"result_{i}"
        
        tasks = [Task(payload=lambda i=i: sample_task(i)) for i in range(1000)]
        
        start_time = time.time()
        results = await asyncio.gather(*[
            self.execute_task(task) for task in tasks
        ])
        end_time = time.time()
        
        duration = end_time - start_time
        throughput = len(tasks) / duration
        
        logger.info(f"Performance test completed:")
        logger.info(f"  Tasks: {len(tasks)}")
        logger.info(f"  Duration: {duration:.2f}s")
        logger.info(f"  Throughput: {throughput:.2f} tasks/s")
        
        return {
            "tasks": len(tasks),
            "duration": duration,
            "throughput": throughput
        }
    
    def get_stats(self) -> Dict:
        cache_hit_rate = 0
        if self.cache_hits + self.cache_misses > 0:
            cache_hit_rate = self.cache_hits / (self.cache_hits + self.cache_misses)
        
        uptime = 0
        if self.start_time:
            uptime = time.time() - self.start_time
        
        return {
            "total_tasks_processed": self.total_tasks_processed,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "uptime": uptime,
            "cache": self.cache.get_stats(),
            "message_queue": self.message_queue.get_stats(),
            "service_discovery": self.service_discovery.get_stats(),
            "rate_limiter": self.rate_limiter.get_stats(),
            "circuit_breaker": self.circuit_breaker.get_stats()
        }


if __name__ == "__main__":
    async def main():
        config = {
            "cache": {"enabled": True, "backend": "memory", "ttl": 3600, "max_size": 100000},
            "message_queue": {"backend": "memory", "max_size": 10000},
            "load_balancer": {"strategy": "adaptive"},
            "rate_limiter": {
                "algorithm": "token_bucket",
                "requests_per_second": 10000,
                "requests_per_minute": 600000,
                "concurrent_requests": 5000
            },
            "circuit_breaker": {"failure_threshold": 10, "timeout": 60}
        }
        
        system = UltimateDistributedSystem(config)
        await system.initialize()
        
        print("System initialized successfully")
        stats = system.get_stats()
        print(f"System stats: {json.dumps(stats, indent=2, default=str)}")
        
        await system.run_performance_test()
        
        await system.shutdown()
    
    asyncio.run(main())
