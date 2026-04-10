# 快速脚本调用指南

## 基本用法

```bash
# Windows
run.bat <命令> [参数]

# Linux/Mac
python run.py <命令> [参数]

# 查看所有脚本
run.bat --list
```

---

## 常用命令

### 📊 数据采集

| 命令 | 说明 | 示例 |
|------|------|------|
| `collect-news` | AI新闻采集 | `run.bat collect-news --topic ai --limit 10` |
| `collect-github` | GitHub源码分析 | `run.bat collect-github` |
| `collect-chinese` | 中文社区探索 | `run.bat collect-chinese` |
| `collect-global` | 全球社区探索 | `run.bat collect-global` |

### 🧠 学习进化

| 命令 | 说明 | 示例 |
|------|------|------|
| `learn-hourly` | 13领域学习 | `run.bat learn-hourly --now` |
| `learn-infinite` | 无限进化 | `run.bat learn-infinite --once` |
| `evolve-master` | 主控制器 | `run.bat evolve-master --once` |

### 🐜 策略进化

| 命令 | 说明 | 示例 |
|------|------|------|
| `evolve-ant` | 蚁群策略 | `run.bat evolve-ant` |
| `evolve-bee` | 蜂群策略 | `run.bat evolve-bee` |
| `evolve-swarm` | 协同进化 | `run.bat evolve-swarm --once` |

### 🤖 AutoGPT风格

| 命令 | 说明 | 示例 |
|------|------|------|
| `decompose` | 任务分解 | `run.bat decompose "构建系统"` |
| `reflect` | 自我反思 | `run.bat reflect` |

---

## 示例

### 1. 采集AI新闻
```bash
run.bat collect-news --topic ai --limit 10
run.bat collect-news --topic reasoning --limit 10
run.bat collect-news --topic agent --limit 10
```

### 2. 启动学习
```bash
run.bat learn-hourly --now
run.bat evolve-master --once
```

### 3. 任务分解
```bash
run.bat decompose "优化蚁群蜂群协作系统"
```

### 4. 自我反思
```bash
run.bat reflect
```

---

## 快速参考

```bash
# 查看帮助
run.bat --help

# 查看所有脚本
run.bat --list

# 执行任意脚本
run.bat <脚本名> [参数]
```

---

*创建时间: 2026-04-01*
