@echo off
REM ============================================================
REM Erbing Agent - Portable Migration System
REM 一键迁移 U 盘版 - 插上U盘，全自动迁移
REM ============================================================
REM 
REM 使用方法:
REM   1. 把整个 Erbing_Migration 文件夹复制到 U 盘
REM   2. 在原电脑运行: migrate_export.bat
REM   3. 把 U 盘插到新电脑
REM   4. 在新电脑运行: migrate_import.bat
REM
REM ============================================================

setlocal EnableDelayedExpansion

REM 获取当前脚本所在目录（U 盘根目录）
set "USB_ROOT=%~dp0"
set "USB_ROOT=%USB_ROOT:~0,-1%"

REM 设置工作目录
set "WORKSPACE=%USERPROFILE%\.openclaw\workspace"
set "MIGRATION_DIR=%USB_ROOT%\migration_package"

REM 颜色输出
set "NC=\e[0m"
set "RED=\e[31m"
set "GREEN=\e[32m"
set "YELLOW=\e[33m"
set "BLUE=\e[34m"

echo.
echo ============================================================
echo  Erbing Agent - Portable Migration System
echo ============================================================
echo.

REM 检查参数
if "%1"=="" goto :show_menu
if "%1"=="export" goto :do_export
if "%1"=="import" goto :do_import
if "%1"=="check" goto :do_check
goto :show_menu

:show_menu
echo  请选择操作:
echo  [1] Export - 导出当前 Erbing 到 U 盘
echo  [2] Import - 从 U 盘导入到本机
echo  [3] Check  - 验证迁移包完整性
echo  [Q] 退出
echo.
choice /C 123Q /N /M "请输入选择: "

if errorlevel 4 goto :end
if errorlevel 3 goto :do_check
if errorlevel 2 goto :do_import
if errorlevel 1 goto :do_export
goto :end

:do_export
echo [1/6] Checking environment...
if not exist "%WORKSPACE%" (
    echo ERROR: OpenClaw workspace not found at %WORKSPACE%
    echo Please install OpenClaw first!
    pause
    goto :end
)

echo [2/6] Creating migration package folder...
if exist "%MIGRATION_DIR%" rmdir /S /Q "%MIGRATION_DIR%"
mkdir "%MIGRATION_DIR%"

echo [3/6] Exporting Memory Database...
if exist "%WORKSPACE%\memory\database\xiaozhi_memory.db" (
    copy /Y "%WORKSPACE%\memory\database\xiaozhi_memory.db" "%MIGRATION_DIR%\" >nul
    echo   - Memory database exported
)

echo [4/6] Exporting LanceDB...
if exist "%WORKSPACE%\memory\database\lancedb" (
    xcopy /E /Y /I "%WORKSPACE%\memory\database\lancedb" "%MIGRATION_DIR%\lancedb\" >nul
    echo   - LanceDB exported
)

echo [5/6] Exporting Skills, Scripts, Config...
if exist "%WORKSPACE%\skills" (
    xcopy /E /Y /I "%WORKSPACE%\skills" "%MIGRATION_DIR%\skills\" >nul
    echo   - Skills exported
)
if exist "%WORKSPACE%\scripts" (
    xcopy /E /Y /I "%WORKSPACE%\scripts" "%MIGRATION_DIR%\scripts\" >nul
    echo   - Scripts exported
)
if exist "%WORKSPACE%\config" (
    xcopy /E /Y /I "%WORKSPACE%\config" "%MIGRATION_DIR%\config\" >nul
    echo   - Config exported
)

echo [6/6] Exporting Workspace files...
for %%f in (SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md) do (
    if exist "%WORKSPACE%\%%f" (
        copy /Y "%WORKSPACE%\%%f" "%MIGRATION_DIR%%\" >nul
    )
)

echo.
echo ============================================================
echo  Export Complete!
echo ============================================================
echo.
echo  Package location: %MIGRATION_DIR%
echo.
echo  Next steps:
echo  1. Keep this U盘
echo  2. On NEW computer: Run migrate.bat import
echo.
pause
goto :end

:do_import
echo [1/5] Preparing directories...
if not exist "%WORKSPACE%" mkdir "%WORKSPACE%"
if not exist "%WORKSPACE%\memory\database" mkdir "%WORKSPACE%\memory\database"

if not exist "%MIGRATION_DIR%\xiaozhi_memory.db" (
    echo ERROR: Migration package not found!
    echo Please run export first on the original computer.
    pause
    goto :end
)

echo [2/5] Importing Memory Database...
copy /Y "%MIGRATION_DIR%\xiaozhi_memory.db" "%WORKSPACE%\memory\database\" >nul
echo   - Database imported

echo [3/5] Importing LanceDB...
if exist "%MIGRATION_DIR%\lancedb" (
    xcopy /E /Y /I "%MIGRATION_DIR%\lancedb" "%WORKSPACE%\memory\database\lancedb\" >nul
    echo   - LanceDB imported
)

echo [4/5] Importing Skills, Scripts, Config...
if exist "%MIGRATION_DIR%\skills" (
    xcopy /E /Y /I "%MIGRATION_DIR%\skills" "%WORKSPACE%\skills\" >nul
    echo   - Skills imported
)
if exist "%MIGRATION_DIR%\scripts" (
    xcopy /E /Y /I "%MIGRATION_DIR%\scripts" "%WORKSPACE%\scripts\" >nul
    echo   - Scripts imported
)
if exist "%MIGRATION_DIR%\config" (
    xcopy /E /Y /I "%MIGRATION_DIR%\config" "%WORKSPACE%\config\" >nul
    echo   - Config imported
)

echo [5/5] Importing Workspace files...
for %%f in (SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md) do (
    if exist "%MIGRATION_DIR%\%%f" (
        copy /Y "%MIGRATION_DIR%\%%f" "%WORKSPACE%%\" >nul
    )
)

echo.
echo ============================================================
echo  Import Complete!
echo ============================================================
echo.
echo  Erbing has been successfully migrated to this computer!
echo.
echo  Note: You may need to re-configure channel credentials
echo  (Discord, Feishu, etc.) on this new device.
echo.
pause
goto :end

:do_check
echo [1/3] Checking migration package...
if not exist "%MIGRATION_DIR%\xiaozhi_memory.db" (
    echo ERROR: Migration package not found at %MIGRATION_DIR%
    echo Please run export first!
    pause
    goto :end
)

echo [2/3] Verifying files...
set "FILES_OK=1"

if not exist "%MIGRATION_DIR%\SOUL.md" (
    echo   [WARN] SOUL.md missing
    set "FILES_OK=0"
)
if not exist "%MIGRATION_DIR%\IDENTITY.md" (
    echo   [WARN] IDENTITY.md missing
    set "FILES_OK=0"
)
if not exist "%MIGRATION_DIR%\skills" (
    echo   [WARN] skills folder missing
    set "FILES_OK=0"
)
if not exist "%MIGRATION_DIR%\scripts" (
    echo   [WARN] scripts folder missing
    set "FILES_OK=0"
)

echo [3/3] Package status:
for %%f in (xiaozhi_memory.db SOUL.md IDENTITY.md USER.md AGENTS.md) do (
    if exist "%MIGRATION_DIR%\%%f" (
        echo   [OK] %%f
    ) else (
        echo   [MISSING] %%f
    )
)

echo.
echo ============================================================
if "!FILES_OK!"=="1" (
    echo  Check PASSED - Package is valid!
) else (
    echo  Check COMPLETED with warnings
)
echo ============================================================
pause
goto :end

:end
endlocal