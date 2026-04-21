@echo off
REM ============================================================
REM Erbing Agent - U 盘便携迁移系统 v2.0
REM ============================================================

setlocal EnableDelayedExpansion

REM 获取脚本所在目录（U 盘根目录）
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "PKG_DIR=%SCRIPT_DIR%\migration_package"
set "WORKSPACE=%USERPROFILE%\.openclaw\workspace"

echo.
echo ============================================================
echo   Erbing Agent - U盘便携迁移
echo ============================================================

REM 解析参数
if "%1"=="" goto :menu
if /i "%1"=="export" goto :export
if /i "%1"=="import" goto :import
if /i "%1"=="check" goto :check
goto :menu

:menu
echo.
echo   请选择操作:
echo   -----------------------------------------
echo   [E] 导出 - 将 Erbing 保存到 U 盘
echo   [I] 导入 - 从 U 盘恢复 Erbing
echo   [C] 检查 - 验证迁移包
echo   [Q] 退出
echo.
choice /C EICQ /N /M "请选择: "

if errorlevel 4 goto :end
if errorlevel 3 goto :check
if errorlevel 2 goto :import
if errorlevel 1 goto :export
goto :end

:export
echo.
echo [1/5] 准备导出环境...
if not exist "%WORKSPACE%" (
    echo [错误] OpenClaw 工作区不存在: %WORKSPACE%
    echo 请先安装 OpenClaw
    pause
    goto :end
)
echo   [OK] 工作区就绪

echo.
echo [2/5] 创建迁移目录...
if exist "%PKG_DIR%" rd /S /Q "%PKG_DIR%"
mkdir "%PKG_DIR%"
echo   [OK] 目录已创建

echo.
echo [3/5] 导出数据库...
if exist "%WORKSPACE%\memory\database\xiaozhi_memory.db" (
    copy /Y "%WORKSPACE%\memory\database\xiaozhi_memory.db" "%PKG_DIR%\" >nul
    for %%A in ("%WORKSPACE%\memory\database\xiaozhi_memory.db") do echo   [OK] 数据库 %%~zA bytes
) else (
    echo   [跳过] 数据库不存在
)

echo.
echo [4/5] 导出 Skills 和 Scripts...
if exist "%WORKSPACE%\skills" (
    xcopy /E /Y /I /Q "%WORKSPACE%\skills" "%PKG_DIR%\skills\" >nul 2>nul
    for /f %%A in ('dir /b /s "%WORKSPACE%\skills\*" ^| find /c /v ""') do echo   [OK] %%A 个 Skills 文件
)
if exist "%WORKSPACE%\scripts" (
    xcopy /E /Y /I /Q "%WORKSPACE%\scripts" "%PKG_DIR%\scripts\" >nul 2>nul
    for /f %%A in ('dir /b /s "%WORKSPACE%\scripts\*" ^| find /c /v ""') do echo   [OK] %%A 个 Scripts 文件
)

echo.
echo [5/5] 导出配置文件...
if exist "%WORKSPACE%\config" (
    xcopy /E /Y /I /Q "%WORKSPACE%\config" "%PKG_DIR%\config\" >nul 2>nul
)
if exist "%WORKSPACE%\memory\database\lancedb" (
    xcopy /E /Y /I /Q "%WORKSPACE%\memory\database\lancedb" "%PKG_DIR%\lancedb\" >nul 2>nul
)
for %%f in (SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md) do (
    if exist "%WORKSPACE%\%%f" (
        copy /Y "%WORKSPACE%\%%f" "%PKG_DIR%%\" >nul
    )
)
echo   [OK] 配置和工作区文件已导出

echo.
echo ============================================================
echo   导出完成!
echo ============================================================
echo.
echo   迁移包位置: %PKG_DIR%
echo.
echo   接下来请:
echo   1. 保留此 U 盘
echo   2. 在新电脑运行 migrate.bat import
echo.
pause
goto :end

:import
echo.
echo [1/4] 准备目录...
if not exist "%WORKSPACE%" mkdir "%WORKSPACE%"
if not exist "%WORKSPACE%\memory\database" mkdir "%WORKSPACE%\memory\database"

if not exist "%PKG_DIR%\xiaozhi_memory.db" (
    echo [错误] 未找到迁移包!
    echo 请先在原电脑运行 migrate.bat export
    pause
    goto :end
)
echo   [OK] 目录就绪

echo.
echo [2/4] 导入数据库...
copy /Y "%PKG_DIR%\xiaozhi_memory.db" "%WORKSPACE%\memory\database\" >nul
echo   [OK] 数据库已导入

echo.
echo [3/4] 导入 Skills 和 Scripts...
if exist "%PKG_DIR%\skills" (
    xcopy /E /Y /I /Q "%PKG_DIR%\skills" "%WORKSPACE%\skills\" >nul 2>nul
    echo   [OK] Skills 已导入
)
if exist "%PKG_DIR%\scripts" (
    xcopy /E /Y /I /Q "%PKG_DIR%\scripts" "%WORKSPACE%\scripts\" >nul 2>nul
    echo   [OK] Scripts 已导入
)
if exist "%PKG_DIR%\config" (
    xcopy /E /Y /I /Q "%PKG_DIR%\config" "%WORKSPACE%\config\" >nul 2>nul
)
if exist "%PKG_DIR%\lancedb" (
    xcopy /E /Y /I /Q "%PKG_DIR%\lancedb" "%WORKSPACE%\memory\database\lancedb\" >nul 2>nul
)

echo.
echo [4/4] 导入工作区文件...
for %%f in (SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md) do (
    if exist "%PKG_DIR%\%%f" (
        copy /Y "%PKG_DIR%\%%f" "%WORKSPACE%%\" >nul
        echo   [OK] %%f
    )
)

echo.
echo ============================================================
echo   导入完成!
echo ============================================================
echo.
echo   Erbing 已成功迁移到本机!
echo.
echo   注意: 频道凭证需要重新配置
echo.
pause
goto :end

:check
echo.
echo [检查 1/3] 查找迁移包...
if not exist "%PKG_DIR%" (
    echo [错误] 未找到迁移包!
    echo 请先在原电脑运行 migrate.bat export
    pause
    goto :end
)
echo   [OK] 找到迁移包

echo.
echo [检查 2/3] 验证核心文件...
set "ALL_OK=1"

for %%f in (xiaozhi_memory.db SOUL.md IDENTITY.md) do (
    if exist "%PKG_DIR%\%%f" (
        echo   [OK] %%f
    ) else (
        echo   [缺少] %%f
        set "ALL_OK=0"
    )
)

echo.
echo [检查 3/3] 统计信息...
if exist "%PKG_DIR%\skills" (
    for /f %%A in ('dir /b /s "%PKG_DIR%\skills" ^| find /c /v ""') do echo   Skills: %%A 个文件
)
if exist "%PKG_DIR%\scripts" (
    for /f %%A in ('dir /b /s "%PKG_DIR%\scripts" ^| find /c /v ""') do echo   Scripts: %%A 个文件
)
if exist "%PKG_DIR%\xiaozhi_memory.db" (
    for %%A in ("%PKG_DIR%\xiaozhi_memory.db") do echo   Database: %%~zA bytes
)

echo.
echo ============================================================
if "!ALL_OK!"=="1" (
    echo   验证通过!
) else (
    echo   验证完成，部分文件缺失
)
echo ============================================================
pause
goto :end

:end
endlocal