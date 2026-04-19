@echo off
chcp 65001 >nul
echo ========================================
echo MT5 顶配盯盘系统 v2
echo ========================================
echo.

echo [1/2] 运行测试...
python mt5_system\test_all.py
echo.

echo [2/2] 启动系统...
python mt5_system\run.py
echo.

pause