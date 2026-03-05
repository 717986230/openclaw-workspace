# 🐦 Grok Twitter Search

使用 xAI Grok 模型的 `x_search` 工具智能搜索 Twitter 内容。

## ✨ 核心特性

- **🚀 双引擎动态路由**: Fast 极速检索 / Reasoning 深度分析
- **💰 超低成本**: 相比 X API ($100/月)，实测约 $2.8/千次
- **🔍 智能语义**: 自然语言查询，自带 LLM 降噪
- **🌐 WARP 代理**: 自动检测并分流被禁 IP
- **📊 纯净输出**: 原生 Tool Call 数据，无渲染噪音

## 🚀 快速开始

```bash
# 交互式配置（推荐）
uv run scripts/setup_interactive.py

# 直接搜索
uv run scripts/search_twitter.py --query "Bitcoin latest news" --max-results 10
```

## 📋 系统要求

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Python 包管理器)
- curl
- Grok API Key ([获取](https://x.ai/api))
- WARP (可选，中国大陆必需)

## 🔧 代理配置

支持三种方式，优先级从高到低：

1. **显式配置** - 在 `~/.openclaw/openclaw.json` 中设置
2. **环境变量** - `export SOCKS5_PROXY="socks5://127.0.0.1:40000"`
3. **自动检测** - 脚本自动检测 WARP 并启用

## 💡 使用示例

### OpenClaw 中使用

直接对智能体说：
> "搜索推特上关于 Ethereum 的最新讨论"

### CLI 使用

```bash
# 极速检索（默认，最低成本）
uv run scripts/search_twitter.py --query "Solana ecosystem" --max-results 10

# 深度分析（带推理总结）
uv run scripts/search_twitter.py --query "AI crypto trends" --analyze
```

## 📊 成本对比

| 方案 | 计费方式 | 千次调用成本 |
|------|----------|--------------|
| **Grok x_search** | Token 计费 | **~$2.8** |
| X API Basic | 固定月租 | $100/月 |

## 🔗 链接

- [详细配置文档](./references/CONFIG.md)
- [ClawHub](https://clawhub.com)

## 📄 License

MIT
