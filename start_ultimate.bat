@echo off
echo ============================================
echo   Erbing 统一进化系统 - 顶配版
echo   Ultimate Edition
echo ============================================
echo.
echo 版本: 4.0.0-ultimate
echo 架构: FastAPI微服务 + Docker
echo.
echo 正在启动...
echo.

cd /d C:\Users\Administrator\.openclaw\workspace

REM 检查Docker是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose是否可用
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Compose未安装，请先安装Docker Compose
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
echo       Docker: 已安装
echo       Docker Compose: 已安装
echo.

echo [2/3] 构建镜像...
docker-compose -f docker-compose.ultimate.yml build
if %errorlevel% neq 0 (
    echo [ERROR] 镜像构建失败
    pause
    exit /b 1
)
echo       镜像构建完成
echo.

echo [3/3] 启动服务...
docker-compose -f docker-compose.ultimate.yml up -d
if %errorlevel% neq 0 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)
echo       服务启动完成
echo.

echo ============================================
echo   顶配版启动成功!
echo ============================================
echo.
echo 服务地址:
echo   - API服务: http://localhost:8000
echo   - API文档: http://localhost:8000/docs
echo   - Grafana: http://localhost:3000 (admin/admin123)
echo   - Prometheus: http://localhost:9090
echo.
echo 数据库:
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
echo   - Milvus: localhost:19530
echo.
echo 常用命令:
echo   - 查看日志: docker-compose -f docker-compose.ultimate.yml logs -f
echo   - 停止服务: docker-compose -f docker-compose.ultimate.yml down
echo   - 重启服务: docker-compose -f docker-compose.ultimate.yml restart
echo.
echo ============================================
pause
