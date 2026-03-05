#!/usr/bin/env bash
# Setup script for Aliyun Bailian TTS skill
# Run this manually to create the virtual environment and install dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/venv"

echo "🔧 Aliyun Bailian TTS Setup"
echo "==========================="
echo

# ============ Check System Dependencies ============
echo "📋 Checking system dependencies..."

# Check ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ ffmpeg not installed"
    echo "   Please install first:"
    echo "   - Mac: brew install ffmpeg"
    echo "   - Ubuntu: apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi
echo "✓ ffmpeg installed"

# Check curl
if ! command -v curl &> /dev/null; then
    echo "❌ curl not installed"
    exit 1
fi
echo "✓ curl installed"

# ============ Check Python Version ============
PYTHON_CMD=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v "$cmd" &> /dev/null; then
        VERSION=$($cmd --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        MAJOR=$(echo "$VERSION" | cut -d. -f1)
        MINOR=$(echo "$VERSION" | cut -d. -f2)
        
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
            PYTHON_CMD="$cmd"
            echo "✓ Found Python: $cmd ($VERSION)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: Python 3.10+ required"
    echo "   Current python3: $(python3 --version 2>&1)"
    exit 1
fi

# ============ Check API Key ============
if [ -z "$DASHSCOPE_API_KEY" ]; then
    echo ""
    echo "⚠️  Warning: DASHSCOPE_API_KEY not set"
    echo "   You'll need to set it before using TTS:"
    echo "   export DASHSCOPE_API_KEY=\"sk-your-api-key\""
fi

# ============ Create Virtual Environment ============
if [ -d "$VENV_DIR" ]; then
    echo ""
    echo "⚠️  Virtual environment already exists at: $VENV_DIR"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
    else
        echo "Keeping existing venv."
        exit 0
    fi
fi

echo ""
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv "$VENV_DIR"

# ============ Install Python Dependencies ============
echo "📥 Installing Python dependencies..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install required packages
echo "   Installing dashscope SDK..."
pip install dashscope

echo "   Installing websocket-client..."
pip install websocket-client

echo "   Installing soundfile (for audio processing)..."
pip install soundfile

echo ""
echo "✅ Setup complete!"
echo ""
echo "Virtual environment created at:"
echo "  $VENV_DIR"
echo ""
echo "To activate manually:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "Test with:"
echo "  $SKILL_DIR/scripts/tts.sh --mood gentle \"你好，这是测试\""
echo ""
