# Erbing 统一进化系统 - 顶配版

## 🚀 概述

顶配版是企业级、生产就绪的AI进化平台，基于FastAPI微服务架构，提供完整的分布式训练、实时监控、Web界面和企业级安全。

## 🌟 核心特性

### 1. 微服务架构
- **FastAPI**: 高性能异步Web框架
- **REST API**: 完整的RESTful API接口
- **异步处理**: asyncio异步处理
- **自动文档**: Swagger/OpenAPI自动生成

### 2. 企业级存储
- **PostgreSQL**: 关系型数据库集群
- **Redis**: 高性能缓存
- **Milvus**: 向量数据库
- **MinIO**: 对象存储

### 3. 实时监控
- **Prometheus**: 指标收集
- **Grafana**: 可视化仪表板
- **健康检查**: 自动健康检查
- **日志聚合**: 结构化日志

### 4. 容器化部署
- **Docker**: 完整容器化
- **Docker Compose**: 一键部署
- **健康检查**: 自动健康检查
- **自动重启**: 故障自动恢复

### 5. 高级AI功能
- **多模型集成**: 支持多种AI模型
- **分布式训练**: 多GPU/多机训练
- **RAG系统**: 检索增强生成
- **Agent编排**: 多Agent协作

## 📦 技术栈

### 后端
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3
- SQLAlchemy 2.0.25
- Celery 5.3.6

### 数据库
- PostgreSQL 15
- Redis 7
- Milvus 2.3.3

### 监控
- Prometheus
- Grafana
- OpenTelemetry

### 容器
- Docker
- Docker Compose

## 🎯 快速开始

### 前置要求

- Docker Desktop (Windows/Mac) 或 Docker Engine (Linux)
- Docker Compose
- 8GB+ 内存
- 20GB+ 磁盘空间

### 安装步骤

#### 1. 克隆仓库
```bash
git clone <repository-url>
cd <repository-directory>
```

#### 2. 启动服务
```bash
# Windows
start_ultimate.bat

# Linux/Mac
./start_ultimate.sh
```

#### 3. 等待服务启动
服务启动需要2-5分钟，请耐心等待。

#### 4. 访问服务
- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090

## 📚 API文档

### 基础端点

#### GET /
根路径，返回系统信息

```bash
curl http://localhost:8000/
```

#### GET /health
健康检查

```bash
curl http://localhost:8000/health
```

### 状态端点

#### GET /api/v1/status
获取系统状态

```bash
curl http://localhost:8000/api/v1/status
```

#### GET /api/v1/systems
获取各子系统状态

```bash
curl http://localhost:8000/api/v1/systems
```

#### GET /api/v1/metrics
获取系统指标

```bash
curl http://localhost:8000/api/v1/metrics
```

### 进化端点

#### POST /api/v1/evolution/start
启动进化流程

```bash
curl -X POST http://localhost:8000/api/v1/evolution/start \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "erbing"}'
```

### 训练端点

#### POST /api/v1/training/run
运行训练周期

```bash
curl -X POST http://localhost:8000/api/v1/training/run \
  -H "Content-Type: application/json" \
  -d '{"cycles": 5}'
```

#### GET /api/v1/training/status
获取训练状态

```bash
curl http://localhost:8000/api/v1/training/status
```

### 状态管理端点

#### POST /api/v1/state/save
保存状态

```bash
curl -X POST http://localhost:8000/state/save
```

#### POST /api/v1/state/load
加载状态

```bash
curl -X POST http://localhost:8000/state/load
```

## 🧪 测试

### 运行API测试

```bash
python test_ultimate_api.py
```

### 测试覆盖

- [x] 根路径测试
- [x] 健康检查测试
- [x] 状态查询测试
- [x] 系统状态测试
- [x] 进化启动测试
- [x] 训练运行测试
- [x] 训练状态测试
- [x] 指标获取测试

## 📊 监控

### Grafana仪表板

访问 http://localhost:3000

默认账号: admin
默认密码: admin123

### Prometheus指标

访问 http://localhost:9090

查看系统指标和性能数据。

## 🔧 配置

### 环境变量

在 `docker-compose.ultimate.yml` 中配置：

```yaml
environment:
  - DATABASE_URL=postgresql://erbing:erbing123@postgres:5432/erbing_ultimate
  - REDIS_URL=redis://redis:6379/0
  - MILVUS_HOST=milvus
  - MILVUS_PORT=19530
  - ENVIRONMENT=development
```

### 数据库配置

PostgreSQL默认配置：
- 用户: erbing
- 密码: erbing123
- 数据库: erbing_ultimate
- 端口: 5432

### Redis配置

Redis默认配置：
- 密码: redis123
- 端口: 6379

### Milvus配置

Milvus默认配置：
- 主机: milvus
- 端口: 19530

## 🛠️ 常用命令

### Docker Compose命令

```bash
# 启动所有服务
docker-compose -f docker-compose.ultimate.yml up -d

# 停止所有服务
docker-compose -f docker-compose.ultimate.yml down

# 重启服务
docker-compose -f docker-compose.ultimate.yml restart

# 查看日志
docker-compose -f docker-compose.ultimate.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.ultimate.yml logs -f api

# 重新构建镜像
docker-compose -f docker-compose.ultimate.yml build

# 删除所有数据（危险！）
docker-compose -f docker-compose.ultimate.yml down -v
```

### 数据库操作

```bash
# 连接到PostgreSQL
docker exec -it erbing-ultimate-postgres psql -U erbing -d erbing_ultimate

# 连接到Redis
docker exec -it erbing-ultimate-redis redis-cli -a redis123

# 备份数据库
docker exec erbing-ultimate-postgres pg_dump -U erbing erbing_ultimate > backup.sql
```

## 📁 项目结构

```
.
├── ultimate_evolution_system.py    # 主应用
├── requirements-ultimate.txt       # 依赖文件
├── Dockerfile.ultimate             # Docker镜像
├── docker-compose.ultimate.yml     # Docker Compose配置
├── start_ultimate.bat              # 启动脚本
├── test_ultimate_api.py            # API测试
├── ULTIMATE_README.md              # 本文档
├── ULTIMATE_UPGRADE_PLAN.md        # 升级计划
├── erbing-evolution/               # 进化框架
├── erbing-gbrain-evolution/        # GBrain架构
└── virtual_world_advanced/          # 虚拟世界
```

## 🔒 安全

### 默认密码

生产环境请修改以下默认密码：

- PostgreSQL: erbing123
- Redis: redis123
- Grafana: admin123
- MinIO: minioadmin

### 安全建议

1. 修改所有默认密码
2. 启用HTTPS
3. 配置防火墙
4. 限制网络访问
5. 定期更新依赖

## 🚀 性能优化

### 数据库优化

- 添加适当的索引
- 配置连接池
- 优化查询语句
- 定期VACUUM

### 缓存优化

- 配置Redis缓存
- 使用多级缓存
- 设置合理的TTL
- 监控缓存命中率

### API优化

- 启用gzip压缩
- 配置CDN
- 使用异步处理
- 限制并发请求

## 📈 扩展

### 水平扩展

```bash
# 扩展API服务到3个实例
docker-compose -f docker-compose.ultimate.yml up -d --scale api=3
```

### 添加新服务

在 `docker-compose.ultimate.yml` 中添加新的服务定义。

## 🐛 故障排除

### 服务无法启动

1. 检查Docker是否运行
2. 检查端口是否被占用
3. 查看服务日志
4. 检查磁盘空间

### 数据库连接失败

1. 检查PostgreSQL是否运行
2. 检查连接字符串
3. 检查网络连接
4. 查看数据库日志

### API响应慢

1. 检查系统资源
2. 查看Prometheus指标
3. 优化数据库查询
4. 增加缓存

## 📞 支持

### 文档

- [API文档](http://localhost:8000/docs)
- [升级计划](ULTIMATE_UPGRADE_PLAN.md)
- [快速参考](QUICK_REFERENCE.md)

### 问题反馈

如有问题，请查看：
1. 日志文件
2. Grafana仪表板
3. Prometheus指标
4. API文档

## 🎉 版本历史

### 4.0.0-ultimate (当前版本)
- FastAPI微服务架构
- Docker容器化部署
- PostgreSQL + Redis + Milvus
- Prometheus + Grafana监控
- 完整的REST API
- 自动化测试

### 3.0.0-unified
- 统一进化系统
- 整合三个子系统
- 命令行界面

## 📝 许可证

MIT License

## 🙏 致谢

感谢所有贡献者和使用者！

---
**Version: 4.0.0-ultimate**
**Created: 2026-04-14**
**Status: Production Ready**
