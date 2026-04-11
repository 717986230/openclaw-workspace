# Part 2 of concurrency_enterprise.py - 继续实现

# 导入Part1的类型和标准库
from concurrency_enterprise import ConcurrencyConfig, Metrics, Request, Priority, CircuitState
import threading
import queue
import time
import random
import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List, Callable
from collections import deque
from enum import Enum

# 定义BackendState（如果Part1没有）
class BackendState(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"

class AdvancedWorkerPool:
    """企业级工作池 - 完整实现"""
    
    def __init__(self, config: ConcurrencyConfig, processor: Callable, metrics: Metrics):
        self.config = config
        self.processor = processor
        self.metrics = metrics
        self.request_queue = AdvancedRequestQueue(config, metrics)
        self.result_queue = queue.Queue()
        self.workers = []
        self.running = False
    
    def start(self):
        """启动所有Worker"""
        self.running = True
        for i in range(self.config.num_workers):
            worker = Worker(
                worker_id=i,
                request_queue=self.request_queue,
                result_queue=self.result_queue,
                config=self.config,
                processor=self.processor,
                metrics=self.metrics
            )
            worker.start()
            self.workers.append(worker)
        logging.info(f"WorkerPool started with {len(self.workers)} workers")
    
    def stop(self, timeout: float = 5.0):
        """优雅停止"""
        self.running = False
        for worker in self.workers:
            worker.stop()
        
        start = time.time()
        while time.time() - start < timeout:
            if all(not w.is_alive() for w in self.workers):
                break
            time.sleep(0.1)
        logging.info(f"WorkerPool stopped")
    
    def submit(self, request: Request) -> bool:
        """提交请求"""
        return self.request_queue.enqueue(request)
    
    def get_result(self, timeout: float = None) -> Optional[Request]:
        """获取结果"""
        timeout = timeout or self.config.worker_timeout
        try:
            return self.result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_workers": len(self.workers),
            "active_workers": sum(1 for w in self.workers if w.is_alive()),
            "queue_size": self.request_queue.size(),
            "pending_requests": self.request_queue.get_pending_count(),
            "worker_stats": [
                {
                    "id": w.worker_id,
                    "processed": w.processed_count,
                    "errors": w.error_count,
                    "busy": w.current_request is not None
                }
                for w in self.workers
            ]
        }


class Backend:
    """后端节点 - 完整的健康检查和统计"""
    
    def __init__(self, backend_id: str, capacity: int = 100, weight: int = 1):
        self.id = backend_id
        self.capacity = capacity
        self.weight = weight
        self.current_load = 0
        
        # 统计
        self.total_requests = 0
        self.success_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        
        # 健康
        self.state = BackendState.HEALTHY
        self.last_request_time = None
        self.last_health_check = time.time()
        self.consecutive_failures = 0
    
    def get_load_factor(self) -> float:
        """获取负载因子"""
        return self.current_load / self.capacity if self.capacity > 0 else float('inf')
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        return (self.success_requests / self.total_requests * 100) if self.total_requests > 0 else 100.0
    
    def get_avg_latency(self) -> float:
        """获取平均延迟"""
        return (self.total_latency / self.total_requests) if self.total_requests > 0 else 0.0
    
    def request_start(self):
        """请求开始"""
        self.current_load += 1
        self.total_requests += 1
        self.last_request_time = time.time()
    
    def request_end(self, success: bool, latency: float):
        """请求结束"""
        self.current_load = max(0, self.current_load - 1)
        if success:
            self.success_requests += 1
            self.consecutive_failures = 0
        else:
            self.failed_requests += 1
            self.consecutive_failures += 1
        self.total_latency += latency
    
    def mark_healthy(self):
        """标记为健康"""
        self.state = BackendState.HEALTHY
        self.consecutive_failures = 0
    
    def mark_unhealthy(self):
        """标记为不健康"""
        self.state = BackendState.UNHEALTHY
    
    def is_healthy(self) -> bool:
        """是否健康"""
        return self.state == BackendState.HEALTHY


class AdvancedLoadBalancer:
    """企业级负载均衡 - 4种策略完整实现"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.backends = {}
        self.sorted_backends = []
        self.current_index = 0
        self.lock = threading.RLock()
    
    def add_backend(self, backend_id: str, capacity: int = 100, weight: int = 1):
        """添加后端"""
        with self.lock:
            self.backends[backend_id] = Backend(backend_id, capacity, weight)
            self.sorted_backends = list(self.backends.keys())
            logging.info(f"Backend {backend_id} added with capacity {capacity}")
    
    def remove_backend(self, backend_id: str):
        """移除后端"""
        with self.lock:
            if backend_id in self.backends:
                del self.backends[backend_id]
                self.sorted_backends = list(self.backends.keys())
                logging.info(f"Backend {backend_id} removed")
    
    def select_backend(self) -> Optional[str]:
        """选择后端"""
        with self.lock:
            if not self.backends:
                return None
            
            if self.config.lb_strategy == "round_robin":
                return self._round_robin()
            elif self.config.lb_strategy == "least_conn":
                return self._least_connections()
            elif self.config.lb_strategy == "weighted":
                return self._weighted_random()
            elif self.config.lb_strategy == "adaptive":
                return self._adaptive()
            else:
                return self.sorted_backends[0]
    
    def _round_robin(self) -> str:
        """轮询"""
        healthy = [b for b in self.sorted_backends if self.backends[b].is_healthy()]
        if not healthy:
            return None
        backend_id = healthy[self.current_index % len(healthy)]
        self.current_index = (self.current_index + 1) % len(healthy)
        return backend_id
    
    def _least_connections(self) -> str:
        """最少连接"""
        healthy = [b for b in self.backends.values() if b.is_healthy()]
        if not healthy:
            return None
        return min(healthy, key=lambda b: b.current_load).id
    
    def _weighted_random(self) -> str:
        """加权随机"""
        healthy = [b for b in self.backends.values() if b.is_healthy()]
        if not healthy:
            return None
        weights = [b.weight * (b.capacity - b.current_load) for b in healthy]
        total = sum(weights)
        if total <= 0:
            return healthy[0].id
        r = random.uniform(0, total)
        current = 0
        for backend, weight in zip(healthy, weights):
            current += weight
            if r <= current:
                return backend.id
        return healthy[0].id
    
    def _adaptive(self) -> str:
        """自适应负载均衡 - 综合评分"""
        healthy = [b for b in self.backends.values() if b.is_healthy()]
        if not healthy:
            return None
        
        def score(b):
            remaining = b.capacity - b.current_load
            success_rate = b.get_success_rate() / 100
            avg_latency = b.get_avg_latency() + 1
            weight = b.weight
            return (remaining * success_rate * weight) / avg_latency
        
        return max(healthy, key=score).id
    
    def request_start(self, backend_id: str):
        """请求开始"""
        with self.lock:
            if backend_id in self.backends:
                self.backends[backend_id].request_start()
    
    def request_end(self, backend_id: str, success: bool, latency: float):
        """请求结束"""
        with self.lock:
            if backend_id in self.backends:
                self.backends[backend_id].request_end(success, latency)
                self.metrics.record_backend_request(backend_id, success, latency)
    
    def health_check(self):
        """健康检查"""
        with self.lock:
            for backend in self.backends.values():
                if backend.last_request_time:
                    if time.time() - backend.last_request_time < 60:
                        if backend.consecutive_failures < 5:
                            backend.mark_healthy()
                        else:
                            backend.mark_unhealthy()
                    else:
                        if backend.get_success_rate() > 50:
                            backend.mark_healthy()
                        else:
                            backend.mark_unhealthy()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "backends": {
                    bid: {
                        "load": b.current_load,
                        "capacity": b.capacity,
                        "weight": b.weight,
                        "success_rate": f"{b.get_success_rate():.1f}%",
                        "avg_latency": f"{b.get_avg_latency()*1000:.1f}ms",
                        "healthy": b.is_healthy(),
                        "state": b.state.value
                    }
                    for bid, b in self.backends.items()
                },
                "strategy": self.config.lb_strategy
            }


class AdvancedCache:
    """企业级缓存 - LRU + TTL + 监控"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.cache = {}
        self.access_order = deque()
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                # 检查TTL
                if time.time() - entry["created_at"] < self.config.cache_ttl:
                    self.metrics.record_cache(True)
                    self.access_order.remove(key)
                    self.access_order.append(key)
                    return entry["value"]
                else:
                    # 过期删除
                    del self.cache[key]
                    self.access_order.remove(key)
                    self.metrics.record_cache(False, eviction=True)
            else:
                self.metrics.record_cache(False)
            return None
    
    def set(self, key: str, value: Any):
        """设置缓存"""
        with self.lock:
            if key in self.cache:
                self.access_order.remove(key)
            elif len(self.cache) >= self.config.cache_size:
                # LRU淘汰
                oldest = self.access_order.popleft()
                del self.cache[oldest]
                self.metrics.record_cache(False, eviction=True)
            
            self.cache[key] = {"value": value, "created_at": time.time()}
            self.access_order.append(key)
    
    def delete(self, key: str):
        """删除缓存"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.access_order.remove(key)
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "size": len(self.cache),
                "max_size": self.config.cache_size,
                "ttl": self.config.cache_ttl
            }


class AdvancedRateLimiter:
    """令牌桶限流器 - 完整实现"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.rate = config.rate_limit
        self.capacity = config.burst_capacity
        self.tokens = config.burst_capacity
        self.last_update = time.time()
        self.lock = threading.RLock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """获取令牌"""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            
            # 补充令牌
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            # 检查是否足够
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            self.metrics.requests_rate_limited += 1
            return False
    
    def wait_for_token(self, tokens: int = 1, timeout: float = 5.0) -> bool:
        """等待令牌"""
        start = time.time()
        while time.time() - start < timeout:
            if self.acquire(tokens):
                return True
            time.sleep(0.01)
        return False
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "rate": self.rate,
                "capacity": self.capacity,
                "current_tokens": self.tokens
            }


class AdvancedCircuitBreaker:
    """熔断器 - 完整的三状态实现"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.failure_threshold = config.failure_threshold
        self.timeout = config.recovery_timeout
        self.success_threshold = config.success_threshold
        
        self.failures = 0
        self.successes = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.half_open_requests = 0
        self.lock = threading.RLock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """通过熔断器调用"""
        with self.lock:
            if self.state == CircuitState.OPEN:
                # 检查是否可以尝试恢复
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_requests = 0
                    self.successes = 0
                    logging.info("Circuit breaker entering HALF_OPEN state")
                else:
                    self.metrics.requests_circuit_open += 1
                    raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """成功回调"""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.successes += 1
                if self.successes >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failures = 0
                    logging.info("Circuit breaker recovered to CLOSED state")
            else:
                self.failures = 0
    
    def _on_failure(self):
        """失败回调"""
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.half_open_requests += 1
                if self.half_open_requests >= self.config.half_open_requests:
                    self.state = CircuitState.OPEN
                    logging.warning("Circuit breaker reopened due to failures in HALF_OPEN")
            elif self.failures >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logging.warning(f"Circuit breaker opened after {self.failures} failures")
    
    def get_state(self) -> CircuitState:
        """获取状态"""
        return self.state
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "state": self.state.value,
                "failures": self.failures,
                "successes": self.successes,
                "threshold": self.failure_threshold
            }


class DistributedCache:
    """分布式缓存 - 一致性哈希"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.nodes = []
        self.ring = {}
        self.sorted_keys = []
        self.lock = threading.RLock()
    
    def add_node(self, node_id: str):
        """添加节点"""
        with self.lock:
            self.nodes.append(node_id)
            for i in range(self.config.virtual_nodes):
                virtual_key = f"{node_id}#{i}"
                hash_key = self._hash(virtual_key)
                self.ring[hash_key] = node_id
            self.sorted_keys = sorted(self.ring.keys())
            logging.info(f"Node {node_id} added with {self.config.virtual_nodes} virtual nodes")
    
    def remove_node(self, node_id: str):
        """移除节点"""
        with self.lock:
            self.nodes.remove(node_id)
            keys_to_remove = [k for k, v in self.ring.items() if v == node_id]
            for k in keys_to_remove:
                del self.ring[k]
            self.sorted_keys = sorted(self.ring.keys())
            logging.info(f"Node {node_id} removed")
    
    def get_node(self, key: str) -> str:
        """根据key获取节点"""
        with self.lock:
            if not self.ring:
                return None
            hash_key = self._hash(key)
            for node_hash in self.sorted_keys:
                if node_hash >= hash_key:
                    return self.ring[node_hash]
            return self.ring[self.sorted_keys[0]]
    
    def _hash(self, key: str) -> int:
        """计算哈希"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % (2**32)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        with self.lock:
            return {
                "nodes": len(self.nodes),
                "virtual_nodes": self.config.virtual_nodes,
                "ring_size": len(self.ring)
            }


# 导入需要的模块
import hashlib
from datetime import datetime
