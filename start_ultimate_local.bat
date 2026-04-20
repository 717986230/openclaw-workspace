@echo off
echo ============================================
echo   Erbing 统一进化系统 - 顶配版 (本地运行)
echo   Ultimate Edition (Local Run)
echo ============================================
echo.
echo 版本: 4.0.0-ultimate
echo 架构: FastAPI微服务
echo.

cd /d C:\Users\Administrator\.openclaw\workspace

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python未安装，请先安装Python 3.11+
    pause
    exit /b 1
)

echo [1/4] 检查Python环境...
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo       Python: %PYTHON_VERSION%
echo.

echo [2/4] 检查依赖...
pip show fastapi >nul 2>&1
if %errorlevel% neq 0 (
    echo       安装FastAPI...
    pip install fastapi uvicorn pydantic
)
echo       FastAPI: 已安装
echo.

echo [3/4] 启动API服务...
echo       服务地址: http://localhost:8000
echo       API文档: http://localhost:8000/docs
echo.
echo       按 Ctrl+C 停止服务
echo.

python ultimate_evolution_system.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] 服务启动失败
    echo.
    echo 可能的原因:
    echo   1. 端口8000被占用
    echo   2. 依赖未正确安装
    echo   3. Python版本不兼容
    echo.
    echo 解决方案:
    echo   1. 检查端口占用: netstat -ano | findstr :8000
    echo   2. 安装依赖: pip install -r requirements-ultimate.txt
    echo   3. 升级Python: 下载Python 3.11+
    echo.
)

pause
