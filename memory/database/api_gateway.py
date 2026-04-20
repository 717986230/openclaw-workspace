"""
API网关系统
企业级API网关，支持路由、认证、限流、熔断
"""

import asyncio
import json
import time
import hashlib
import hmac
import jwt
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
from aiohttp import web, ClientSession
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class Route:
    path: str
    service: str
    methods: List[str]
    rate_limit: int
    timeout: int
    auth_required: bool = True


@dataclass
class RequestLog:
    request_id: str
    path: str
    method: str
    status_code: int
    latency: float
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    error: Optional[str] = None


class APIGateway:
    def __init__(self, config: Dict):
        self.config = config
        self.gateway_config = config.get('api_gateway', {})
        self.enabled = self.gateway_config.get('enabled', True)
        self.host = self.gateway_config.get('host', '0.0.0.0')
        self.port = self.gateway_config.get('port', 8080)
        
        # 认证配置
        self.auth_config = self.gateway_config.get('authentication', {})
        self.auth_enabled = self.auth_config.get('enabled', True)
        self.jwt_secret = self.auth_config.get('secret_key', 'default-secret')
        self.jwt_algorithm = self.auth_config.get('algorithm', 'HS256')
        
        # 限流配置
        self.rate_limit_config = self.gateway_config.get('rate_limiting', {})
        self.rate_limit_enabled = self.rate_limit_config.get('enabled', True)
        self.default_limit = self.rate_limit_config.get('default_limit', 1000)
        self.burst = self.rate_limit_config.get('burst', 100)
        
        # 熔断配置
        self.circuit_breaker_config = self.gateway_config.get('circuit_breaker', {})
        self.circuit_breaker_enabled = self.circuit_breaker_config.get('enabled', True)
        self.failure_threshold = self.circuit_breaker_config.get('failure_threshold', 5)
        self.circuit_timeout = self.circuit_breaker_config.get('timeout', 60)
        
        # 负载均衡
        self.load_balancing_config = self.gateway_config.get('load_balancing', {})
        self.load_balancing_strategy = self.load_balancing_config.get('strategy', 'round_robin')
        
        # 日志
        self.logging_config = self.gateway_config.get('logging', {})
        self.logging_enabled = self.logging_config.get('enabled', True)
        self.log_level = self.logging_config.get('level', 'INFO')
        
        # 统计
        self.request_logs: List[RequestLog] = []
        self.request_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        
        # 限流存储
        self.rate_limit_store: Dict[str, Dict] = {}
        
        # 熔断状态
        self.circuit_states: Dict[str, Dict] = {}
        
        # HTTP会话
        self.session: Optional[ClientSession] = None
        
        # 服务发现
        self.service_nodes: Dict[str, List[Dict]] = {}
        
        # 路由配置（必须在其他配置之后初始化）
        self.routes: Dict[str, Route] = {}
        self._init_routes()
        
        logger.info(f"API Gateway initialized on {self.host}:{self.port}")
    
    def _init_routes(self):
        """初始化路由"""
        for route_config in self.gateway_config.get('routes', []):
            route = Route(
                path=route_config['path'],
                service=route_config['service'],
                methods=route_config['methods'],
                rate_limit=route_config.get('rate_limit', self.default_limit),
                timeout=route_config.get('timeout', 30),
                auth_required=route_config.get('auth_required', True)
            )
            self.routes[route.path] = route
            logger.info(f"Route registered: {route.path} -> {route.service}")
    
    async def initialize(self):
        """初始化"""
        self.session = ClientSession()
        logger.info("API Gateway initialized")
    
    async def shutdown(self):
        """关闭"""
        if self.session:
            await self.session.close()
        logger.info("API Gateway shutdown")
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        return hashlib.md5(f"{time.time()}_{self.request_count}".encode()).hexdigest()
    
    def _match_route(self, path: str) -> Optional[Route]:
        """匹配路由"""
        for route_path, route in self.routes.items():
            if path.startswith(route_path.rstrip('*')):
                return route
        return None
    
    def _check_rate_limit(self, client_id: str, route: Route) -> bool:
        """检查限流"""
        if not self.rate_limit_enabled:
            return True
        
        now = time.time()
        key = f"{client_id}:{route.path}"
        
        if key not in self.rate_limit_store:
            self.rate_limit_store[key] = {
                'tokens': route.rate_limit,
                'last_update': now
            }
        
        store = self.rate_limit_store[key]
        elapsed = now - store['last_update']
        
        # 令牌桶算法
        store['tokens'] = min(
            route.rate_limit,
            store['tokens'] + elapsed * route.rate_limit
        )
        store['last_update'] = now
        
        if store['tokens'] >= 1:
            store['tokens'] -= 1
            return True
        
        return False
    
    def _check_circuit_breaker(self, service: str) -> bool:
        """检查熔断器"""
        if not self.circuit_breaker_enabled:
            return True
        
        if service not in self.circuit_states:
            self.circuit_states[service] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'
            }
        
        state = self.circuit_states[service]
        
        if state['state'] == 'open':
            if time.time() - state['last_failure'] > self.circuit_timeout:
                state['state'] = 'half_open'
            else:
                return False
        
        return True
    
    def _record_failure(self, service: str):
        """记录失败"""
        if service not in self.circuit_states:
            self.circuit_states[service] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'
            }
        
        state = self.circuit_states[service]
        state['failures'] += 1
        state['last_failure'] = time.time()
        
        if state['failures'] >= self.failure_threshold:
            state['state'] = 'open'
            logger.warning(f"Circuit breaker opened for service: {service}")
    
    def _record_success(self, service: str):
        """记录成功"""
        if service not in self.circuit_states:
            return
        
        state = self.circuit_states[service]
        if state['state'] == 'half_open':
            state['state'] = 'closed'
            state['failures'] = 0
            logger.info(f"Circuit breaker closed for service: {service}")
    
    def _verify_jwt(self, token: str) -> Optional[Dict]:
        """验证JWT"""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def _get_client_id(self, request: web.Request) -> str:
        """获取客户端ID"""
        # 优先使用X-Client-ID头
        client_id = request.headers.get('X-Client-ID')
        if client_id:
            return client_id
        
        # 使用IP地址
        peername = request.transport.get_extra_info('peername')
        if peername:
            return peername[0]
        
        return 'unknown'
    
    async def _log_request(self, log: RequestLog):
        """记录请求日志"""
        if self.logging_enabled:
            self.request_logs.append(log)
            # 只保留最近1000条日志
            if len(self.request_logs) > 1000:
                self.request_logs.pop(0)
    
    async def _proxy_request(self, request: web.Request, route: Route) -> web.Response:
        """代理请求到后端服务"""
        start_time = time.time()
        request_id = self._generate_request_id()
        client_id = self._get_client_id(request)
        
        # 检查限流
        if not self._check_rate_limit(client_id, route):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return web.json_response(
                {'error': 'Rate limit exceeded', 'request_id': request_id},
                status=429
            )
        
        # 检查认证
        if route.auth_required and self.auth_enabled:
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                logger.warning(f"Missing authorization header: {request_id}")
                return web.json_response(
                    {'error': 'Unauthorized', 'request_id': request_id},
                    status=401
                )
            
            token = auth_header[7:]
            payload = self._verify_jwt(token)
            if not payload:
                logger.warning(f"Invalid token: {request_id}")
                return web.json_response(
                    {'error': 'Invalid token', 'request_id': request_id},
                    status=401
                )
        
        # 检查熔断器
        if not self._check_circuit_breaker(route.service):
            logger.warning(f"Circuit breaker open for service: {route.service}")
            return web.json_response(
                {'error': 'Service unavailable', 'request_id': request_id},
                status=503
            )
        
        # 代理请求
        try:
            # 获取服务节点
            nodes = self.service_nodes.get(route.service, [])
            if not nodes:
                logger.error(f"No nodes available for service: {route.service}")
                return web.json_response(
                    {'error': 'Service unavailable', 'request_id': request_id},
                    status=503
                )
            
            # 选择节点（简化版，轮询）
            node = nodes[0]
            target_url = f"http://{node['host']}:{node['port']}{request.path}"
            
            # 转发请求
            headers = {k: v for k, v in request.headers.items() 
                      if k.lower() not in ['host', 'content-length']}
            
            async with self.session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=await request.read(),
                timeout=route.timeout
            ) as response:
                body = await response.read()
                status = response.status
                
                # 记录成功
                self._record_success(route.service)
                
                # 记录日志
                latency = time.time() - start_time
                log = RequestLog(
                    request_id=request_id,
                    path=request.path,
                    method=request.method,
                    status_code=status,
                    latency=latency
                )
                await self._log_request(log)
                
                # 更新统计
                self.request_count += 1
                self.total_latency += latency
                
                return web.Response(
                    body=body,
                    status=status,
                    headers=dict(response.headers)
                )
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {request_id}")
            self._record_failure(route.service)
            return web.json_response(
                {'error': 'Request timeout', 'request_id': request_id},
                status=504
            )
        except Exception as e:
            logger.error(f"Request failed: {request_id}, error: {e}")
            self._record_failure(route.service)
            return web.json_response(
                {'error': 'Internal server error', 'request_id': request_id},
                status=500
            )
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """处理请求"""
        # 匹配路由
        route = self._match_route(request.path)
        if not route:
            return web.json_response(
                {'error': 'Not found'},
                status=404
            )
        
        # 检查方法
        if request.method not in route.methods:
            return web.json_response(
                {'error': 'Method not allowed'},
                status=405
            )
        
        # 代理请求
        return await self._proxy_request(request, route)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """健康检查"""
        return web.json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'request_count': self.request_count,
            'error_count': self.error_count,
            'avg_latency': self.total_latency / self.request_count if self.request_count > 0 else 0
        })
    
    async def metrics(self, request: web.Request) -> web.Response:
        """指标"""
        return web.json_response({
            'request_count': self.request_count,
            'error_count': self.error_count,
            'avg_latency': self.total_latency / self.request_count if self.request_count > 0 else 0,
            'routes': {path: {'rate_limit': route.rate_limit} for path, route in self.routes.items()},
            'circuit_breakers': self.circuit_states
        })
    
    def create_app(self) -> web.Application:
        """创建应用"""
        app = web.Application()
        
        # 注册路由
        app.router.add_route('*', '/{path:.*}', self.handle_request)
        app.router.add_get('/health', self.health_check)
        app.router.add_get('/metrics', self.metrics)
        
        return app
    
    async def start(self):
        """启动网关"""
        app = self.create_app()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"API Gateway started on {self.host}:{self.port}")
        
        # 保持运行
        try:
            while True:
                await asyncio.sleep(60)
                logger.info(f"API Gateway running - requests: {self.request_count}, errors: {self.error_count}")
        except asyncio.CancelledError:
            logger.info("API Gateway stopping")
            await runner.cleanup()


if __name__ == "__main__":
    async def main():
        config = {
            'api_gateway': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 8080,
                'routes': [
                    {
                        'path': '/api/v1/',
                        'service': 'main_service',
                        'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                        'rate_limit': 1000,
                        'timeout': 30
                    }
                ],
                'authentication': {
                    'enabled': True,
                    'type': 'jwt',
                    'secret_key': 'test-secret-key',
                    'algorithm': 'HS256'
                },
                'rate_limiting': {
                    'enabled': True,
                    'default_limit': 1000,
                    'burst': 100
                },
                'circuit_breaker': {
                    'enabled': True,
                    'failure_threshold': 5,
                    'timeout': 60
                },
                'load_balancing': {
                    'strategy': 'round_robin'
                },
                'logging': {
                    'enabled': True,
                    'level': 'INFO',
                    'format': 'json'
                }
            }
        }
        
        gateway = APIGateway(config)
        await gateway.initialize()
        
        # 添加测试服务节点
        gateway.service_nodes['main_service'] = [
            {'host': 'localhost', 'port': 8001}
        ]
        
        await gateway.start()
    
    asyncio.run(main())
