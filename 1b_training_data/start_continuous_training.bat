@echo off
echo Starting Erbing Continuous Training...
echo.
echo This will run 24/7 continuous training.
echo Press Ctrl+C to stop and save checkpoint.
echo.
echo Log file will be created in logs directory.
echo Checkpoints will be saved every 10 episodes.
echo.
pause

cd /d "C:\Users\Administrator\.openclaw\workspace\1b_training_data"
python erbing_continuous_trainer.py

pause
