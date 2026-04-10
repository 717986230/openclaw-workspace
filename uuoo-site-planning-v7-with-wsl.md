# uuoo.site 完整策划 - 含风险提示和 WSL

## ⚠️ 风险提示（必须显示）

### 脚本开始前显示：
```
========================================
   ⚠️ 重要风险提示
========================================

本脚本将会：
  • 安装 Node.js（官方版本）
  • 安装 Git（官方版本）
  • 下载 OpenClaw 项目
  • 安装项目依赖

潜在风险：
  ⚠️ 将修改系统环境变量
  ⚠️ 需要管理员权限运行
  ⚠️ 需要稳定的网络连接
  ⚠️ 可能与其他软件冲突
  ⚠️ 建议在虚拟机或 WSL 中运行

建议：
  ✓ 先备份重要数据
  ✓ 在虚拟机中测试
  ✓ 使用系统还原点
  ✓ 遇到问题可卸载重装

是否继续？(Y/N):
========================================
```

---

## 🐧 WSL 版本支持

### 为什么推荐 WSL？
- ✅ 隔离环境，不影响主系统
- ✅ 易于卸载和重置
- ✅ 更接近生产环境
- ✅ 风险更可控

---

## 💻 Windows 原生版脚本（带风险提示）

```powershell
# OpenClaw Windows 环境配置脚本
# 版本: 1.0
# 包含完整风险提示

#Requires -RunAsAdministrator

param(
    [switch]$Force,
    [switch]$SkipWarnings
)

# ==================== 风险提示 ====================

if (!$SkipWarnings) {
    Write-Host "
========================================
   ⚠️ 重要风险提示
========================================
" -ForegroundColor Yellow

Write-Host "本脚本将会：" -ForegroundColor White
Write-Host "  • 安装 Node.js（官方版本）" -ForegroundColor Gray
Write-Host "  • 安装 Git（官方版本）" -ForegroundColor Gray
Write-Host "  • 下载 OpenClaw 项目" -ForegroundColor Gray
Write-Host "  • 安装项目依赖" -ForegroundColor Gray

Write-Host ""
Write-Host "潜在风险：" -ForegroundColor Red
Write-Host "  ⚠️ 将修改系统环境变量" -ForegroundColor Yellow
Write-Host "  ⚠️ 需要管理员权限运行" -ForegroundColor Yellow
Write-Host "  ⚠️ 需要稳定的网络连接" -ForegroundColor Yellow
Write-Host "  ⚠️ 可能与其他软件冲突" -ForegroundColor Yellow
Write-Host "  ⚠️ 建议在虚拟机或 WSL 中运行" -ForegroundColor Yellow

Write-Host ""
Write-Host "建议：" -ForegroundColor Cyan
Write-Host "  ✓ 先备份重要数据" -ForegroundColor White
Write-Host "  ✓ 在虚拟机中测试" -ForegroundColor White
Write-Host "  ✓ 使用系统还原点" -ForegroundColor White
Write-Host "  ✓ 遇到问题可卸载重装" -ForegroundColor White

Write-Host "
========================================
" -ForegroundColor Yellow

if (!$Force) {
    $confirm = Read-Host "是否继续？(Y/N)"
    if ($confirm -ne 'Y' -and $confirm -ne 'y') {
        Write-Host "已取消安装" -ForegroundColor Yellow
        exit
    }
}

Write-Host "
推荐使用 WSL 获得更好的隔离性：" -ForegroundColor Cyan
Write-Host "  WSL 安装命令: wsl --install" -ForegroundColor White
Write-Host "  或运行 WSL 版本脚本: .\setup-openclaw-wsl.sh" -ForegroundColor White
Write-Host ""
}

# ==================== 安装流程 ====================

Write-Host "
========================================
   🦞 OpenClaw 环境配置
========================================
" -ForegroundColor Cyan

# ... 后续安装步骤 ...
```

---

## 🐧 WSL 版脚本（推荐）

```bash
#!/bin/bash
# OpenClaw WSL 环境配置脚本
# 推荐：在 WSL 中运行，完全隔离，零风险

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

echo "[1/6] 更新系统包..."
sudo apt update && sudo apt upgrade -y

echo "[2/6] 安装基础工具..."
sudo apt install -y curl git build-essential

echo "[3/6] 安装 nvm (Node Version Manager)..."
if [ ! -d "$HOME/.nvm" ]; then
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
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
# 请填入您从官方获取的 API Key
# 
# 获取方式：
# - Claude: https://console.anthropic.com
# - OpenAI: https://platform.openai.com
#
# 注意：API Key 需要自行申请，本脚本不提供

ANTHROPIC_API_KEY=
OPENAI_API_KEY=
PORT=3000
NODE_ENV=development
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
"
```

---

## 📋 完整功能对比

| 功能 | Windows 版 | WSL 版 |
|------|-----------|--------|
| **风险提示** | ✅ | ✅ |
| **环境隔离** | ❌ | ✅ |
| **易于卸载** | ⚠️ 需手动 | ✅ 一键卸载 |
| **系统影响** | ⚠️ 可能影响 | ✅ 完全隔离 |
| **推荐程度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## 🔒 风险等级说明

### 🟢 低风险（WSL）
- ✅ 完全隔离
- ✅ 不影响 Windows
- ✅ 易于恢复

### 🟡 中风险（Windows 虚拟机）
- ⚠️ 需要虚拟化软件
- ⚠️ 占用资源较多
- ✅ 可快照恢复

### 🔴 高风险（Windows 原生）
- ⚠️ 直接修改系统
- ⚠️ 可能与其他软件冲突
- ⚠️ 需要系统还原点

---

## 📝 用户选择界面

### 脚本启动时显示：
```
========================================
   选择安装方式
========================================

推荐程度从高到低：

[1] WSL (推荐) ⭐⭐⭐⭐⭐
    • 完全隔离，零风险
    • 易于卸载和重置
    • 不影响 Windows
    
[2] Windows 原生 ⭐⭐⭐
    • 直接运行
    • 需管理员权限
    • 有一定风险
    
[3] 查看风险说明
    • 了解详细风险
    
[4] 退出

请选择 (1-4):
========================================
```

---

## 🎯 最终推荐流程

### 推荐方案（WSL）：
```
1. 安装 WSL: wsl --install
2. 进入 WSL: wsl
3. 运行脚本: ./setup-openclaw-wsl.sh
4. 配置 API Key
5. 启动服务
```

### 备选方案（Windows）：
```
1. 创建系统还原点
2. 以管理员运行脚本
3. 确认风险提示
4. 等待安装完成
5. 配置 API Key
```

---

## ✅ 完整执行清单

### 立即实现
1. [ ] Windows 脚本（含风险提示）
2. [ ] WSL 脚本
3. [ ] 风险提示模块
4. [ ] 用户选择界面

### 本周实现
5. [ ] 网站界面展示两种方案
6. [ ] 详细的风险说明页面
7. [ ] WSL 安装教程页面

---

*版本: V7 完整版*
*核心: 风险提示 + WSL 支持*
*目标: 安全第一，用户自主选择*
