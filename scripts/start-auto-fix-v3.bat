@echo off
REM 自动化代码审查修复流水线启动脚本 v3

echo ========================================
echo 自动化代码审查修复流水线 v3
echo ========================================
echo.
echo 监控的PR:
echo   - PR #65669: Custom Cron Job IDs
echo   - PR #65675: Avatar 2MB Limit
echo.
echo 检查间隔: 5分钟
echo 日志文件: auto-fix-log.txt
echo 自动创建PR: 是
echo.
echo 按 Ctrl+C 停止
echo ========================================
echo.

node scripts\auto-fix-code-review-v3.js

pause
