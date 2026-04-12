@echo off
echo Stopping Erbing Continuous Training...
echo.
echo This will send a Ctrl+C signal to stop the training.
echo The training will save a checkpoint before stopping.
echo.
pause

taskkill /F /IM python.exe

echo.
echo Training stopped.
echo Check the logs directory for the latest checkpoint.
pause
