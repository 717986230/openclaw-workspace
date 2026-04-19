@echo off
chcp 65001 >nul
echo ========================================
echo MT5 顶配盯盘系统 - 快速启动
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)
echo.

echo [2/3] 安装依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 警告: 依赖安装失败，请手动安装
)
echo.

echo [3/3] 启动系统...
echo.
echo 选择启动模式:
echo 1. 核心系统 (命令行)
echo 2. Web 界面 (浏览器)
echo 3. 同时启动核心系统和 Web 界面
echo.
set /p choice="请输入选项 (1-3): "

if "%choice%"=="1" (
    echo 启动核心系统...
    python start.py
) else if "%choice%"=="2" (
    echo 启动 Web 界面...
    echo 访问地址: http://localhost:8080
    python web_interface.py
) else if "%choice%"=="3" (
    echo 同时启动核心系统和 Web 界面...
    start "MT5 核心系统" python start.py
    timeout /t 2 /nobreak >nul
    echo 访问地址: http://localhost:8080
    python web_interface.py
) else (
    echo 无效选项
    pause
    exit /b 1
)

echo.
echo 系统已停止
pause