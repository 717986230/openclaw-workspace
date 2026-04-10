@echo off
REM 快速脚本调用器 - Windows批处理版本
REM 用法: run.bat <命令> [参数]

if "%1"=="" goto help
if "%1"=="--help" goto help
if "%1"=="-h" goto help
if "%1"=="--list" goto list
if "%1"=="-l" goto list

REM 执行脚本
python run.py %*
goto end

:list
python run.py --list
goto end

:help
echo.
echo ====================================
echo        快速脚本调用器
echo ====================================
echo.
echo 用法: run.bat ^<命令^> [参数]
echo.
echo 数据采集:
echo   collect-news      采集AI新闻
echo   collect-github    分析GitHub源码
echo   collect-chinese   探索中文社区
echo   collect-global    探索全球社区
echo.
echo 学习进化:
echo   learn-hourly      13领域学习
echo   learn-infinite    无限进化
echo   evolve-master     主控制器
echo.
echo 策略进化:
echo   evolve-ant        蚁群策略
echo   evolve-bee        蜂群策略
echo   evolve-swarm      协同进化
echo.
echo AutoGPT:
echo   decompose         任务分解
echo   reflect           自我反思
echo.
echo 查看所有脚本: run.bat --list
echo ====================================
echo.

:end
