#!/bin/bash
# OpenClaw WSL 环境配置脚本
# 版本: 1.0
# 合规版本 - 仅从官方源下载，完全隔离环境

set -e

echo "========================================
   🦞 OpenClaw WSL 环境配置
========================================
"

echo "⚠️ WSL 版本优势："
echo "  ✓ 完全隔离，不影响 Windows"
echo "  ✓ 易于卸载和重置"
echo "  ✓ 更接近生产环境"
echo "  ✓ 风险更可控"
echo ""

echo "本脚本将会："
echo "  • 安装 Node.js (via nvm)"
echo "  • 安装 Git"
echo "  • 下载 OpenClaw"
echo "  • 安装依赖"
echo ""

read -p "是否继续？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "已取消"
    exit 1
fi

# ==================== 安装依赖 ====================

echo ""
echo "[1/6] 更新系统包..."
sudo apt update && sudo apt upgrade -y

echo "[2/6] 安装基础工具..."
sudo apt install -y curl git build-essential

echo "[3/6] 安装 nvm (Node Version Manager)..."
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
else
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

echo "[4/6] 安装 Node.js..."
nvm install 20
nvm use 20
nvm alias default 20

echo "Node: $(node -v)"
echo "npm: $(npm -v)"

echo "[5/6] 克隆 OpenClaw..."
cd ~
if [ -d "openclaw" ]; then
    echo "已存在，更新中..."
    cd openclaw
    git pull
else
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
fi

echo "[6/6] 安装依赖..."
npm install

# ==================== 创建配置模板 ====================

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# OpenClaw 配置文件模板
# 
# ===== 重要说明 =====
# 修改配置后需要重启服务
# API Key 需从官方渠道获取
# ====================

# 服务端口
PORT=3000
NODE_ENV=development

# ===== API 配置 =====
# 请填入您从官方获取的 API Key
#
# 获取方式：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com
# - DeepSeek: https://platform.deepseek.com
# - Groq: https://console.groq.com
#
# 注意：API Key 需要自行申请
# 本脚本不提供任何 API Key

# Anthropic API Key（可选）
ANTHROPIC_API_KEY=

# OpenAI API Key（可选）
OPENAI_API_KEY=

# DeepSeek API Key（可选）
DEEPSEEK_API_KEY=

# Groq API Key（可选）
GROQ_API_KEY=

# ===== 高级配置 =====
MEMORY_ENABLED=true
MEMORY_PATH=./data/memory
DATABASE_PATH=./data/openclaw.db
LOG_LEVEL=info
EOF
    echo "✓ 配置文件已创建"
fi

# ==================== 创建启动脚本 ====================

cat > ~/start-openclaw.sh << 'EOF'
#!/bin/bash
cd ~/openclaw
echo "========================================"
echo "  OpenClaw 服务启动中..."
echo "========================================"
echo ""
echo "配置文件: ~/openclaw/.env"
echo "访问地址: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止"
echo "========================================"
npm start
EOF

chmod +x ~/start-openclaw.sh

# ==================== 创建数据目录 ====================

mkdir -p ~/openclaw/data/memory

# ==================== 完成 ====================

echo "
========================================
   ✅ 安装完成！
========================================

安装位置: ~/openclaw
启动命令: ~/start-openclaw.sh

下一步：
  1. 编辑配置文件:
     nano ~/openclaw/.env
     
  2. 填入 API Key（从官方获取）
  
  3. 启动服务:
     ~/start-openclaw.sh
     
  4. 访问:
     http://localhost:3000
     
========================================

⚠️ 重要合规提示：
  • 请遵守各平台服务条款
  • 不要滥用 API 或违规使用
  • 仅用于合法合规的用途
  • API Key 需自行从官方获取

========================================
"

# ==================== 验证安装 ====================

echo "验证安装..."

checks=(
    "node -v"
    "npm -v"
    "git --version"
)

all_good=true

for check in "${checks[@]}"; do
    if $check &> /dev/null; then
        echo "  ✓ $check: $($check)"
    else
        echo "  ✗ $check: 未找到"
        all_good=false
    fi
done

if [ -f "$HOME/openclaw/package.json" ]; then
    echo "  ✓ OpenClaw: 已下载"
else
    echo "  ✗ OpenClaw: 未找到"
    all_good=false
fi

if [ -f "$HOME/openclaw/.env" ]; then
    echo "  ✓ 配置文件: 已创建"
else
    echo "  ✗ 配置文件: 未找到"
    all_good=false
fi

echo ""

if $all_good; then
    echo "✅ 所有检查通过，可以开始使用！"
else
    echo "⚠️ 部分检查未通过，请查看上方提示"
fi

echo "
========================================
"
