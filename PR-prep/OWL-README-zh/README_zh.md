# OWL 🦉 - 多智能体协作框架

<div align="center">

![OWL](https://img.shields.io/badge/OWL-Omniverse_Web_Lab-brightgreen)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](https://github.com/camel-ai/OWL/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org/)
[![GAIA](https://img.shields.io/badge/GAIA-Benchmark%20%231-brightgreen)](https://huggingface.co/gaia)
[![NeurIPS](https://img.shields.io/badge/NeurIPS-2025-blue)](https://neurips.cc/)

**多智能体网络自动化框架，在 GAIA 基准测试中排名第一（69.09 分）**

[English](./README.md) | **中文**

</div>

## 📖 项目介绍

OWL（Omniverse Web Lab）是基于 [CAMEL-AI](https://github.com/camel-ai/camel) 构建的**多智能体协作框架**，专注于 Web 自动化和复杂任务解决。OWL 在 [GAIA 通用AI助手基准测试](https://huggingface.co/gaia)中以 **69.09 分的平均成绩位列开源第一**，并被 **NeurIPS 2025** 录用。

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🏆 **GAIA #1** | 开源框架中 GAIA 基准测试第一名 |
| 🤖 **多智能体协作** | 支持动态角色分配和任务分解 |
| 🌐 **Web 自动化** | 内置浏览器/终端/文件操作工具集 |
| 🔌 **MCP 工具** | 支持 Model Context Protocol 标准扩展 |
| 📊 **GAIA 评测** | 内置 GAIA 基准测试评估工具 |
| 🛠️ **丰富工具集** | Browser、Terminal、File、Excel、Python 工具箱 |

## 🚀 快速开始

### 安装

```bash
pip install owl-ai

# 或从源码安装
git clone https://github.com/camel-ai/OWL.git
cd OWL
pip install -e .
```

### 基础示例

```python
from owl.agents import OWLAAgent
from owl.prompts import GAIA_SYSTEM_PROMPT

# 创建 agent
agent = OWLAAgent(
    model="anthropic/claude-sonnet-4-20250514",
    tools=["browser", "terminal", "file"]
)

# 执行任务
result = agent.run("帮我分析 BTC 最新行情并生成报告")
print(result)
```

### 使用 Qwen（中文示例）

```bash
# 使用中文模型运行示例
python examples/run_qwen_zh.py '分析以太坊最新技术发展'
```

更多示例见 [`examples/`](./examples/) 目录。

## 🛠️ 主要功能

### Agent 类型
- `OWLAgent` — 主 agent，支持 GAIA 任务
- `ScraperAgent` — 网页爬取专用
- `ResearcherAgent` — 研究分析专用

### 工具箱 (Toolkits)
| 工具箱 | 功能 |
|--------|------|
| **BrowserToolkit** | 网页浏览、点击、填表、截图 |
| **TerminalToolkit** | 执行终端命令 |
| **FileWriteToolkit** | 文件读写操作 |
| **ExcelToolkit** | Excel 数据处理 |
| **PythonToolkit** | 安全执行 Python 代码 |

### 模型支持
- OpenAI (GPT-4o, GPT-4o-mini)
- Anthropic (Claude 3.5/3.7)
- Google (Gemini)
- Meta (Llama)
- 国内模型：Qwen、DeepSeek、硅基流动（SiliconFlow）

## 📂 项目结构

```
OWL/
├── owl/
│   ├── agents/          # Agent 核心实现
│   ├── prompts/         # 提示词模板
│   ├── tools/           # 基础工具
│   ├── toolkits/        # 工具箱（Browser/Terminal/File...）
│   └── eval/            # GAIA 评测工具
├── examples/            # 示例脚本
├── tests/              # 测试用例
├── docs/                # 文档
└── scripts/             # 辅助脚本
```

## 🧪 测试

```bash
# 运行所有测试
pytest tests/

# 运行带覆盖率
pytest tests/ --cov=owl --cov-report=html

# GAIA 基准测试
python -m owl.eval.run_gaia --dataset_path=<path>
```

## 📚 文档

- [OWL 官方文档](https://camel-ai.github.io/OWL/)
- [CAMEL-AI 文档](https://docs.camel-ai.org/)
- [GAIA 基准测试](https://huggingface.co/gaia)
- [MCP 协议](https://modelcontextprotocol.io/)

## 🤝 贡献指南

欢迎所有形式的贡献！

请先阅读 [CONTRIBUTING.md](./CONTRIBUTING.md) 了解：
- 开发环境配置
- 代码风格规范
- Pull Request 流程
- AI 生成代码声明要求

首次贡献者建议从 `good first issue` 标签的 issue 开始。

## 📣 社区

| 平台 | 链接 |
|------|------|
| 💬 Discord | [discord.camel-ai.org](https://discord.camel-ai.org) |
| 𝕏 Twitter | [@camel_ai_org](https://x.com/camel_ai_org) |
| 📌 Reddit | [r/CAMEL_AI](https://reddit.com/r/CAMEL_AI) |
| 💬 微信群 | 见 README 二维码 |
| 💬 GitHub Discussions | [讨论区](https://github.com/camel-ai/OWL/discussions) |

## 📄 许可证

本项目基于 [Apache 2.0 许可证](./LICENSE)。

---

<div align="center">

**OWL — 让多智能体协作更简单**

*Built with ❤️ by the CAMEL-AI team*

</div>