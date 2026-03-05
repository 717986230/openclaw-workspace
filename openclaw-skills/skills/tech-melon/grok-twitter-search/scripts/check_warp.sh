#!/bin/bash
# WARP 代理状态检查脚本

echo "🔍 WARP 代理状态检查"
echo "===================="
echo ""

# 检查 WARP 进程
echo "1. WARP 进程状态："
if pgrep -x "warp-svc" > /dev/null; then
    echo "   ✅ WARP 服务运行中"
else
    echo "   ❌ WARP 服务未运行"
    echo "   启动命令：sudo systemctl start warp-svc"
fi
echo ""

# 检查 SOCKS5 端口
echo "2. SOCKS5 代理端口 (40000)："
if netstat -tuln 2>/dev/null | grep -q ":40000" || ss -tuln 2>/dev/null | grep -q ":40000"; then
    echo "   ✅ 端口 40000 正在监听"
else
    echo "   ❌ 端口 40000 未监听"
    echo "   检查 WARP 配置：/etc/warp/config.json"
fi
echo ""

# 检查环境变量
echo "3. 环境变量配置："
if [ -n "$SOCKS5_PROXY" ]; then
    echo "   ✅ SOCKS5_PROXY=$SOCKS5_PROXY"
else
    echo "   ⚠️  SOCKS5_PROXY 未设置"
    echo "   建议：export SOCKS5_PROXY=\"socks5://127.0.0.1:40000\""
fi
echo ""

if [ -n "$GROK_API_KEY" ]; then
    echo "   ✅ GROK_API_KEY=${GROK_API_KEY:0:8}******${GROK_API_KEY: -6}"
else
    echo "   ⚠️  GROK_API_KEY 未设置"
    echo "   请运行交互式配置：uv run scripts/setup_interactive.py"
fi
echo ""

# 测试代理连接
echo "4. 代理网络连通性测试："
if command -v curl > /dev/null; then
    # 使用 curl 测试通过 WARP 代理请求 x.ai，只看 HTTP 状态码
    response=$(curl -s --socks5 127.0.0.1:40000 --connect-timeout 5 https://api.x.ai/v1 -o /dev/null -w "%{http_code}")
    if [ "$response" = "000" ]; then
        echo "   ❌ 无法通过代理连接到 api.x.ai"
        echo "   检查 WARP 配置或服务器出海网络"
    else
        echo "   ✅ 代理隧道连通正常 (HTTP Status: $response)"
    fi
else
    echo "   ⚠️  curl 未安装，跳过网络测试"
fi
echo ""

# 总结
echo "===================="
echo "💡 修复建议与常用命令："
echo "1. 启动 WARP：sudo systemctl restart warp-svc"
echo "2. 交互式配置：uv run scripts/setup_interactive.py"
echo "3. 双模态测试：bash scripts/test_search.sh"