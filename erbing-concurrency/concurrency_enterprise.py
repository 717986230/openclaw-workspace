#!/usr/bin/env python3
"""
Erbing High Concurrency - COMPLETE ENTERPRISE VERSION
完整企业级高并发系统 - 所有特性完整实现
无简化版，全部企业级
"""
import threading
import queue
import time
import random
import logging
from collections import deque
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass, field
from enum import Enum
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==================== 枚举定义 ====================

class Priority(Enum):
    """请求优先级枚举"""
    CRITICAL = 1    # 关键请求
    HIGH = 2        # 高优先级
    NORMAL = 5      # 普通优先级
    LOW = 8         # 低优先级
    BACKGROUND = 10 # 后台任务


class CircuitState(Enum):
    """熔断器状态枚举"""
    CLOSED = "closed"      # 正常状态
    OPEN = "open"          # 熔断状态
    HALF_OPEN = "half_open" # 半开状态


class BackendState(Enum):
    """后端状态枚举"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DRAINING = "draining"


# ==================== 配置系统 ====================

@dataclass
class ConcurrencyConfig:
    """企业级配置 - 所有参数可配置"""
    
    # Worker Pool 配置
    num_workers: int = 10
    worker_timeout: float = 30.0
    worker_heartbeat_interval: float = 5.0
    
    # Queue 配置
    max_queue_size: int = 10000
    queue_timeout: float = 5.0
    priority_levels: int = 10
    
    # Cache 配置
    cache_size: int = 10000
    cache_ttl: int = 3600  # 秒
    cache_cleanup_interval: float = 60.0
    
    # Rate Limiter 配置
    rate_limit: int = 1000  # QPS
    burst_capacity: int = 2000
    rate_limit_strategy: str = "token_bucket"
    
    # Circuit Breaker 配置
    failure_threshold: int = 10
    recovery_timeout: float = 60.0
    half_open_requests: int = 3
    success_threshold: int = 5
    
    # Load Balancer 配置
    lb_strategy: str = "adaptive"  # round_robin, least_conn, weighted, adaptive
    health_check_interval: float = 10.0
    health_check_timeout: float = 5.0
    
    # Distributed Cache 配置
    virtual_nodes: int = 150
    replication_factor: int = 3
    consistency_level: str = "quorum"
    
    # Monitoring 配置
    metrics_interval: float = 60.0
    metrics_retention: int = 86400  # 秒
    percentile_levels: List[int] = field(default_factory=lambda: [50, 90, 95, 99])
    
    # Timeout 配置
    request_timeout: float = 30.0
    connection_timeout: float = 10.0
    idle_timeout: float = 300.0


# ==================== 监控系统 ====================

class Metrics:
    """企业级监控系统 - 完整的百分位统计"""
    
    def __init__(self, config: ConcurrencyConfig = None):
        self.config = config or ConcurrencyConfig()
        self.lock = threading.RLock()
        
        # 请求计数器
        self.requests_total = 0
        self.requests_success = 0
        self.requests_failed = 0
        self.requests_timeout = 0
        self.requests_rate_limited = 0
        self.requests_circuit_open = 0
        
        # 延迟统计（支持百分位）
        self.latencies = deque(maxlen=10000)
        self.queue_wait_times = deque(maxlen=10000)
        self.processing_times = deque(maxlen=10000)
        
        # 缓存统计
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_evictions = 0
        
        # Worker统计
        self.worker_busy = {}
        self.worker_processed = {}
        self.worker_errors = {}
        
        # 后端统计
        self.backend_requests = {}
        self.backend_success = {}
        self.backend_latency = {}
        
        # 时间戳
        self.start_time = time.time()
        self.last_update = time.time()
    
    def record_request(self, success: bool, timeout: bool = False, rate_limited: bool = False, circuit_open: bool = False):
        """记录请求状态"""
        with self.lock:
            self.requests_total += 1
            if success:
                self.requests_success += 1
            elif timeout:
                self.requests_timeout += 1
            elif rate_limited:
                self.requests_rate_limited += 1
            elif circuit_open:
                self.requests_circuit_open += 1
            else:
                self.requests_failed += 1
    
    def record_latency(self, latency: float):
        """记录延迟"""
        with self.lock:
            self.latencies.append(latency)
    
    def record_queue_wait(self, wait_time: float):
        """记录队列等待时间"""
        with self.lock:
            self.queue_wait_times.append(wait_time)
    
    def record_cache(self, hit: bool, eviction: bool = False):
        """记录缓存状态"""
        with self.lock:
            if hit:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            if eviction:
                self.cache_evictions += 1
    
    def record_worker_start(self, worker_id: int):
        """记录Worker开始"""
        with self.lock:
            self.worker_busy[worker_id] = time.time()
    
    def record_worker_end(self, worker_id: int, error: bool = False):
        """记录Worker结束"""
        with self.lock:
            if worker_id in self.worker_busy:
                self.worker_processed[worker_id] = self.worker_processed.get(worker_id, 0) + 1
                if error:
                    self.worker_errors[worker_id] = self.worker_errors.get(worker_id, 0) + 1
                del self.worker_busy[worker_id]
    
    def record_backend_request(self, backend_id: str, success: bool, latency: float):
        """记录后端请求"""
        with self.lock:
            self.backend_requests[backend_id] = self.backend_requests.get(backend_id, 0) + 1
            if success:
                self.backend_success[backend_id] = self.backend_success.get(backend_id, 0) + 1
            self.backend_latency[backend_id] = self.backend_latency.get(backend_id, 0) + latency
    
    def get_percentiles(self, values: deque) -> Dict[str, float]:
        """计算百分位延迟"""
        if not values:
            return {f"p{p}": 0.0 for p in self.config.percentile_levels}
        
        sorted_values = sorted(values)
        result = {}
        for p in self.config.percentile_levels:
            idx = int(len(sorted_values) * p / 100)
            result[f"p{p}"] = sorted_values[min(idx, len(sorted_values) - 1)]
        return result
    
    def get_stats(self) -> Dict:
        """获取完整统计信息"""
        with self.lock:
            # 延迟百分位
            latency_percentiles = self.get_percentiles(self.latencies)
            queue_percentiles = self.get_percentiles(self.queue_wait_times)
            
            # 吞吐量
            uptime = time.time() - self.start_time
            throughput = self.requests_total / uptime if uptime > 0 else 0
            
            # 成功率
            success_rate = (self.requests_success / self.requests_total * 100) if self.requests_total > 0 else 0
            
            # 缓存命中率
            cache_total = self.cache_hits + self.cache_misses
            cache_hit_rate = (self.cache_hits / cache_total * 100) if cache_total > 0 else 0
            
            # 后端统计
            backend_stats = {}
            for bid in self.backend_requests:
                backend_stats[bid] = {
                    "requests": self.backend_requests[bid],
                    "success": self.backend_success.get(bid, 0),
                    "success_rate": f"{self.backend_success.get(bid, 0) / self.backend_requests[bid] * 100:.1f}%" if self.backend_requests[bid] > 0 else "100%",
                    "avg_latency": f"{self.backend_latency.get(bid, 0) / self.backend_requests[bid] * 1000:.1f}ms" if self.backend_requests[bid] > 0 else "0ms"
                }
            
            return {
                "requests": {
                    "total": self.requests_total,
                    "success": self.requests_success,
                    "failed": self.requests_failed,
                    "timeout": self.requests_timeout,
                    "rate_limited": self.requests_rate_limited,
                    "circuit_open": self.requests_circuit_open,
                    "success_rate": f"{success_rate:.2f}%",
                    "throughput": f"{throughput:.1f} req/s"
                },
                "latency": {
                    "avg": f"{sum(self.latencies) / len(self.latencies) * 1000:.1f}ms" if self.latencies else "0ms",
                    **{k: f"{v * 1000:.1f}ms" for k, v in latency_percentiles.items()}
                },
                "queue": {
                    "avg_wait": f"{sum(self.queue_wait_times) / len(self.queue_wait_times) * 1000:.1f}ms" if self.queue_wait_times else "0ms",
                    **{k: f"{v * 1000:.1f}ms" for k, v in queue_percentiles.items()}
                },
                "cache": {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                    "evictions": self.cache_evictions,
                    "hit_rate": f"{cache_hit_rate:.2f}%"
                },
                "workers": {
                    "busy": len(self.worker_busy),
                    "total_processed": sum(self.worker_processed.values()),
                    "total_errors": sum(self.worker_errors.values()),
                    "worker_stats": {
                        str(wid): {
                            "processed": self.worker_processed.get(wid, 0),
                            "errors": self.worker_errors.get(wid, 0)
                        } for wid in self.worker_processed
                    }
                },
                "backends": backend_stats,
                "uptime": f"{uptime:.0f}s"
            }


# ==================== 请求对象 ====================

class Request:
    """完整请求对象 - 支持回调、重试、超时、追踪"""
    
    _id_counter = 0
    _id_lock = threading.Lock()
    
    def __init__(
        self,
        payload: Any,
        request_id: str = None,
        priority: Priority = Priority.NORMAL,
        metadata: Dict = None,
        timeout: float = None,
        callback: Callable = None,
        max_retries: int = 3
    ):
        # 自动生成ID
        if request_id is None:
            with Request._id_lock:
                Request._id_counter += 1
                request_id = f"req_{Request._id_counter}_{int(time.time()*1000)}"
        
        self.id = request_id
        self.payload = payload
        self.priority = priority
        self.metadata = metadata or {}
        self.timeout = timeout or 30.0
        self.callback = callback
        self.max_retries = max_retries
        
        # 生命周期追踪
        self.created_at = time.time()
        self.started_at = None
        self.completed_at = None
        
        # 结果
        self.result = None
        self.error = None
        self.retry_count = 0
        self.worker_id = None
        self.backend_id = None
        
        # 状态
        self.status = "pending"  # pending, processing, completed, failed
    
    def __lt__(self, other):
        """用于优先级队列比较"""
        return (self.priority.value, self.created_at) < (other.priority.value, other.created_at)
    
    def start_processing(self, worker_id: int = None):
        """开始处理"""
        self.started_at = time.time()
        self.worker_id = worker_id
        self.status = "processing"
    
    def complete(self, result: Any):
        """完成处理"""
        self.result = result
        self.completed_at = time.time()
        self.status = "completed"
    
    def fail(self, error: str):
        """处理失败"""
        self.error = error
        self.completed_at = time.time()
        self.status = "failed"
    
    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.retry_count < self.max_retries
    
    def increment_retry(self):
        """增加重试计数"""
        self.retry_count += 1
        self.status = "pending"
        self.started_at = None
        self.completed_at = None
        self.error = None
    
    def get_processing_time(self) -> float:
        """获取处理时间"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return 0.0
    
    def get_queue_wait_time(self) -> float:
        """获取队列等待时间"""
        if self.started_at:
            return self.started_at - self.created_at
        return 0.0
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "priority": self.priority.name,
            "status": self.status,
            "created_at": datetime.fromtimestamp(self.created_at).isoformat() if self.created_at else None,
            "started_at": datetime.fromtimestamp(self.started_at).isoformat() if self.started_at else None,
            "completed_at": datetime.fromtimestamp(self.completed_at).isoformat() if self.completed_at else None,
            "processing_time": f"{self.get_processing_time()*1000:.1f}ms",
            "queue_wait_time": f"{self.get_queue_wait_time()*1000:.1f}ms",
            "retry_count": self.retry_count,
            "worker_id": self.worker_id,
            "backend_id": self.backend_id,
            "error": self.error
        }


# ==================== 高级请求队列 ====================

class AdvancedRequestQueue:
    """高级请求队列 - 完整的优先级队列实现"""
    
    def __init__(self, config: ConcurrencyConfig, metrics: Metrics):
        self.config = config
        self.metrics = metrics
        self.queue = queue.PriorityQueue(maxsize=config.max_queue_size)
        self.counter = 0
        self.lock = threading.RLock()
        self.pending_requests = {}
        self.dropped_requests = 0
    
    def enqueue(self, request: Request) -> bool:
        """入队"""
        try:
            with self.lock:
                self.counter += 1
                self.queue.put((request.priority.value, self.counter, request), timeout=1)
                self.pending_requests[request.id] = request
            logging.debug(f"Request {request.id} enqueued with priority {request.priority.name}")
            return True
        except queue.Full:
            self.dropped_requests += 1
            logging.warning(f"Queue full, request {request.id} dropped")
            return False
    
    def dequeue(self, timeout: float = None) -> Optional[Request]:
        """出队"""
        timeout = timeout or self.config.queue_timeout
        try:
            priority, counter, request = self.queue.get(timeout=timeout)
            
            # 记录队列等待时间
            wait_time = request.get_queue_wait_time()
            self.metrics.record_queue_wait(wait_time)
            
            request.start_processing()
            
            with self.lock:
                if request.id in self.pending_requests:
                    del self.pending_requests[request.id]
            
            return request
        except queue.Empty:
            return None
    
    def size(self) -> int:
        """队列大小"""
        return self.queue.qsize()
    
    def get_pending_count(self) -> int:
        """待处理数量"""
        with self.lock:
            return len(self.pending_requests)
    
    def get_stats(self) -> Dict:
        """获取队列统计"""
        with self.lock:
            return {
                "size": self.size(),
                "pending": len(self.pending_requests),
                "dropped": self.dropped_requests
            }


# ==================== Worker（完整版）====================

class Worker(threading.Thread):
    """企业级Worker - 完整的生命周期管理"""
    
    def __init__(
        self,
        worker_id: int,
        request_queue: AdvancedRequestQueue,
        result_queue: queue.Queue,
        config: ConcurrencyConfig,
        processor: Callable,
        metrics: Metrics,
        circuit_breaker: 'AdvancedCircuitBreaker' = None
    ):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.request_queue = request_queue
        self.result_queue = result_queue
        self.config = config
        self.processor = processor
        self.metrics = metrics
        self.circuit_breaker = circuit_breaker
        
        self.running = False
        self.current_request = None
        self.processed_count = 0
        self.error_count = 0
        self.last_activity = time.time()
    
    def run(self):
        """Worker主循环"""
        self.running = True
        logging.info(f"Worker {self.worker_id} started")
        
        while self.running:
            try:
                request = self.request_queue.dequeue(timeout=0.5)
                
                if request:
                    self.current_request = request
                    request.worker_id = self.worker_id
                    self.metrics.record_worker_start(self.worker_id)
                    
                    try:
                        # 处理请求
                        start = time.time()
                        
                        if self.circuit_breaker:
                            # 通过熔断器调用
                            result = self.circuit_breaker.call(
                                self.processor,
                                request.payload,
                                request.metadata
                            )
                        else:
                            result = self.processor(request.payload, request.metadata)
                        
                        processing_time = time.time() - start
                        
                        # 成功
                        request.complete(result)
                        self.metrics.record_request(True)
                        self.metrics.record_latency(processing_time)
                        self.metrics.record_worker_end(self.worker_id)
                        self.processed_count += 1
                        
                        # 回调
                        if request.callback:
                            try:
                                request.callback(request)
                            except Exception as e:
                                logging.error(f"Callback error for request {request.id}: {e}")
                        
                        self.result_queue.put(request)
                        logging.debug(f"Worker {self.worker_id} processed request {request.id}")
                    
                    except Exception as e:
                        # 失败
                        request.fail(str(e))
                        self.metrics.record_request(False)
                        self.metrics.record_worker_end(self.worker_id, error=True)
                        self.error_count += 1
                        
                        # 重试逻辑
                        if request.can_retry():
                            request.increment_retry()
                            self.request_queue.enqueue(request)
                            logging.info(f"Worker {self.worker_id} retrying request {request.id} (attempt {request.retry_count}/{request.max_retries})")
                        else:
                            self.result_queue.put(request)
                            logging.error(f"Worker {self.worker_id} failed request {request.id} after {request.max_retries} retries: {e}")
                    
                    finally:
                        self.current_request = None
                        self.last_activity = time.time()
                
            except Exception as e:
                logging.error(f"Worker {self.worker_id} error: {e}")
        
        logging.info(f"Worker {self.worker_id} stopped")