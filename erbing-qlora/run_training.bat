@echo off
REM Erbing QLoRA 训练启动脚本
REM 自动检查环境并开始训练

echo ============================================================
echo ERBING QLoRA Training Pipeline
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM 检查 CUDA
python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] PyTorch not found. Installing dependencies...
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
    pip install transformers datasets accelerate bitsandbytes peft sentencepiece
)

REM 检查训练数据
if not exist "data\erbing_training_data.json" (
    echo.
    echo [STEP 1] Generating training data...
    python generate_training_data.py
)

REM 开始训练
echo.
echo [STEP 2] Starting QLoRA training...
echo [INFO] Estimated time: 30-60 minutes
echo [INFO] GPU memory usage: ~6GB
echo.
pause

python train_qlora.py

echo.
echo ============================================================
echo Training Complete!
echo ============================================================
echo.
echo [NEXT] Test the model:
echo   python test_model.py
echo.
echo [OUTPUT] Checkpoint saved to: checkpoints\erbing-qlora-v1
echo.

pause
