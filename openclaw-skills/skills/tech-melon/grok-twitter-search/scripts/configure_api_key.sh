#!/bin/bash
# Grok API Key 快捷配置脚本 (OpenClaw Gateway 适配版)

echo "🔐 Grok API Key 环境变量注入向导"
echo "=================================="
echo "提示：独立测试推荐使用 uv run scripts/setup_interactive.py 自动生成 .env"
echo "此脚本主要用于将 Key 注入到系统或 OpenClaw 生产环境中。"
echo ""

# 检查是否已有配置
if [ -n "$GROK_API_KEY" ]; then
    echo "⚠️  检测到当前会话中已有 GROK_API_KEY"
    echo "   当前值：${GROK_API_KEY:0:8}******${GROK_API_KEY: -6}"
    echo ""
    read -p "是否需要重新配置？(y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "已取消配置，退出。"
        exit 0
    fi
fi

echo ""
echo "📝 请选择注入目标："
echo "1. 写入 OpenClaw Gateway 环境 (推荐：作为技能常驻运行)"
echo "2. 写入 ~/.bashrc (当前用户全局生效)"
echo "3. 仅当前终端会话临时生效"
echo "0. 退出"
echo ""
read -p "请输入数字选择 (0-3): " choice

case $choice in
    1)
        echo ""
        read -p "请输入你的 GROK_API_KEY: " api_key
        if [ -z "$api_key" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        GATEWAY_ENV="$HOME/.openclaw/gateway.env"
        mkdir -p "$(dirname "$GATEWAY_ENV")"
        
        # 追加配置
        cat >> "$GATEWAY_ENV" << EOF

# Grok Twitter Search Skill Config
GROK_API_KEY=$api_key
GROK_API_BASE=https://api.x.ai/v1
SOCKS5_PROXY=socks5://127.0.0.1:40000
EOF
        
        echo ""
        echo "✅ 配置已成功追加至 $GATEWAY_ENV"
        echo "⚠️  注意：必须重启 OpenClaw Gateway 才能让 Agent 技能读取到新配置！"
        echo "👉 执行命令: openclaw gateway restart"
        ;;
        
    2)
        echo ""
        read -p "请输入你的 GROK_API_KEY: " api_key
        if [ -z "$api_key" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d%H%M%S)
        
        cat >> ~/.bashrc << EOF

# Grok Twitter Search
export GROK_API_KEY="$api_key"
export GROK_API_BASE="https://api.x.ai/v1"
export SOCKS5_PROXY="socks5://127.0.0.1:40000"
EOF
        
        echo ""
        echo "✅ 配置已写入 ~/.bashrc (已备份原文件)"
        echo "👉 请执行 source ~/.bashrc 立即生效。"
        ;;
        
    3)
        echo ""
        read -p "请输入你的 GROK_API_KEY: " api_key
        if [ -z "$api_key" ]; then
            echo "❌ API Key 不能为空"
            exit 1
        fi
        
        export GROK_API_KEY="$api_key"
        export SOCKS5_PROXY="socks5://127.0.0.1:40000"
        
        echo ""
        echo "✅ 配置已注入当前会话。(关闭终端后失效)"
        echo "👉 你现在可以直接运行: bash scripts/test_search.sh"
        ;;
        
    0)
        echo "已退出"
        exit 0
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac