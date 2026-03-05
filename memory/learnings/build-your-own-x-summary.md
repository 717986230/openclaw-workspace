# Build Your Own X - 学习笔记

## 📚 项目核心理念
> "What I cannot create, I do not understand — Richard Feynman"
> （我不能创造的东西，我就不能理解）

## 🎯 30+ 技术领域完整列表

### 1. 3D 渲染器 (3D Renderer)
**核心技术：**
- 光线追踪 (Ray Tracing)
- 光栅化 (Rasterization)
- 物理渲染 (PBR)
- Wolfenstein 3D 射线投射

**推荐教程：**
- C++: Ray Tracing in One Weekend
- C++: How OpenGL works: software rendering in 500 lines
- JavaScript: Computer Graphics from scratch

---

### 2. AI 模型 (AI Model)
**核心技术：**
- 大语言模型 (LLM)
- 扩散模型 (Diffusion Models) - 图像生成
- RAG (Retrieval-Augmented Generation) - 文档搜索

**推荐教程：**
- Python: LLMs from Scratch (rasbt)
- Python: Diffusion Models for Image Generation (Hugging Face)
- Python: RAG from Scratch (LangChain)

---

### 3. 增强现实 (Augmented Reality)
**核心技术：**
- Unity ARCore
- Unity Vuforia
- AR 门户
- OpenCV + Python

**推荐教程：**
- C#: AR Portal Tutorial with Unity
- C#: How to create a Dragon in AR
- Python: Augmented Reality with Python and OpenCV

---

### 4. BitTorrent 客户端
**核心技术：**
- Bencode 解析
- P2P 网络
- 种子文件处理

**推荐教程：**
- Go: Building a BitTorrent client from the ground up
- Python: A BitTorrent client in Python 3.5
- Node.js: Write your own bittorrent client

---

### 5. 区块链 / 加密货币 (Blockchain / Cryptocurrency)
**核心技术：**
- 区块结构
- 工作量证明 (PoW)
- 权益证明 (PoS)
- 交易验证
- 分布式共识

**推荐教程：**
- Go: Building Blockchain in Go
- JavaScript: Naivecoin (1500 行)
- Python: Learn Blockchains by Building One
- Rust: Building A Blockchain in Rust & Substrate

**关键概念：**
- 区块链 = 不可变的链接区块列表
- 每个区块包含哈希、时间戳、交易数据
- PoW = 计算难题来验证区块
- PoS = 抵押代币来验证区块

---

### 6. 机器人 (Bot)
**核心技术：**
- IRC Bot
- Telegram Bot
- Discord Bot
- Slack Bot
- Reddit Bot
- Twitter Bot
- Facebook Messenger Bot

**推荐教程：**
- Node.js: Create a Discord bot (discordjs.guide)
- Python: How to Build Your First Slack Bot
- Python: Create a Twitter Bot in Python Using Tweepy
- Python: How To Create a Telegram Bot Using Python

---

### 7. 命令行工具 (Command-Line Tool)
**核心技术：**
- CLI 参数解析
- 终端输出格式化
- 管道和重定向

**推荐教程：**
- Go: Build a command line app with Go: lolcat
- Go: Building a cli command with Go: cowsay
- Rust: Command line apps in Rust
- Node.js: Create a CLI tool in Javascript

---

### 8. 数据库 (Database)
**核心技术：**
- B+ 树索引
- SQL 解析器
- 键值存储 (KV Store)
- 持久化存储
- 事务处理

**推荐教程：**
- C: Let's Build a Simple Database (cstack)
- Go: Build Your Own Database from Scratch (build-your-own.org)
- Python: Write your own miniature Redis
- Rust: Build your own Redis client and server (Tokio)

**关键概念：**
- 数据库 = 结构化数据存储 + 查询引擎
- B+ 树 = 高效的范围查询索引
- Redis = 内存中的键值存储，可选持久化
- WAL (Write-Ahead Log) = 崩溃恢复机制

---

### 9. Docker (容器)
**核心技术：**
- Linux 命名空间 (Namespaces)
- 控制组 (cgroups)
- 容器隔离
- 文件系统层

**推荐教程：**
- C: Linux containers in 500 lines of code
- Go: Build Your Own Container Using Less than 100 Lines
- Shell: Docker implemented in around 100 lines of bash (bocker)
- Python: A workshop on Linux containers: Rebuild Docker from Scratch

**关键概念：**
- Namespaces = 隔离 PID、网络、文件系统等
- cgroups = 限制资源使用（CPU、内存）
- Chroot = 改变根目录
- UnionFS = 分层文件系统

---

### 10. 模拟器 / 虚拟机 (Emulator / Virtual Machine)
**核心技术：**
- 字节码解释器
- CPU 指令集模拟
- 内存管理
- 外设模拟

**推荐教程：**
- C: Write your Own Virtual Machine (LC-3)
- C++: How to write an emulator (CHIP-8 interpreter)
- JavaScript: GameBoy Emulation in JavaScript
- Rust: Learning Rust by building a partial Game Boy emulator

**经典模拟器项目：**
- CHIP-8 (简单，80's 游戏)
- Game Boy (任天堂)
- NES (任天堂娱乐系统)

---

### 11. 前端框架 / 库 (Front-end Framework / Library)
**核心技术：**
- Virtual DOM (虚拟 DOM)
- 组件化
- 状态管理
- JSX 渲染
- Reconciliation (协调算法)

**推荐教程：**
- JavaScript: A DIY guide to build your own React (didact)
- JavaScript: Gooact: React in 160 lines
- JavaScript: Build Yourself a Redux
- JavaScript: Build your own React (pomb.us)

**关键概念：**
- Virtual DOM = 内存中的 DOM 表示
- Diff 算法 = 比较新旧 VDOM 差异
- 组件 = 可复用的 UI 单元
- 状态 = 组件的内部数据

---

### 12. 游戏 (Game)
**核心技术：**
- 游戏循环 (Game Loop)
- 碰撞检测
- 精灵渲染
- 输入处理
- 物理引擎
- 声音系统

**推荐教程：**
- C: Handmade Hero (从头制作游戏)
- C++: Breakout (Learn OpenGL)
- Python: Developing Games With PyGame
- JavaScript: How to Make Flappy Bird in HTML5 With Phaser
- Rust: Adventures in Rust: A Basic 2D Game

**经典游戏项目：**
- 俄罗斯方块 (Tetris)
- 打砖块 (Breakout)
- 贪吃蛇 (Snake)
- 太空侵略者 (Space Invaders)
- Roguelike (地牢探险)

---

### 13. Git (版本控制)
**核心技术：**
- 对象存储 (blob, tree, commit)
- SHA-1 哈希
- 分支管理
- 暂存区 (Staging Area)
- 远程同步

**推荐教程：**
- Python: Write yourself a Git! (wyag.thb.lt)
- Python: ugit: Learn Git Internals by Building Git Yourself
- JavaScript: Gitlet
- Ruby: Rebuilding Git in Ruby

**关键概念：**
- .git 目录 = Git 仓库的元数据
- Blob = 文件内容
- Tree = 目录结构
- Commit = 快照 + 父引用
- HEAD = 当前分支指针

---

### 14. 内存分配器 (Memory Allocator)
**核心技术：**
- malloc/free 实现
- 内存池
- 碎片整理
- 边界标记

**推荐教程：**
- C: Malloc is not magic -- Implementing your own memory allocator

---

### 15. 网络栈 (Network Stack)
**核心技术：**
- TCP/IP 协议
- 以太网帧
- ARP 地址解析
- IP 路由
- TCP 可靠传输

**推荐教程：**
- C: Let's code a TCP/IP stack
- C: Beej's Guide to Network Programming

---

### 16. 神经网络 (Neural Network)
**核心技术：**
- 神经元 (Neuron)
- 激活函数 (Activation)
- 前馈传播 (Feedforward)
- 反向传播 (Backpropagation)
- 梯度下降 (Gradient Descent)
- 损失函数 (Loss Function)

**推荐教程：**
- Python: A Neural Network in 11 lines of Python (iamtrask)
- Python: Implement a Neural Network from Scratch (victorzhou)
- Python: Neural Networks: Zero to Hero (Andrej Karpathy)
- Go: How to build a simple artificial neural network with Go

**关键概念：**
- 神经元 = 输入 × 权重 + 偏置 → 激活函数
- Sigmoid = 把任意值压缩到 (0,1)
- ReLU = max(0, x)，现代首选
- MSE = 均方误差损失
- SGD = 随机梯度下降优化
- 学习率 = 控制更新步长

**架构类型：**
- MLP (多层感知机) = 全连接层
- CNN (卷积神经网络) = 计算机视觉
- RNN (循环神经网络) = 序列数据
- LSTM = 长短期记忆，解决梯度消失
- Transformer = 注意力机制，LLM 基础

---

### 17. 操作系统 (Operating System)
**核心技术：**
- 引导加载器 (Bootloader)
- 内核 (Kernel)
- 内存管理
- 进程调度
- 系统调用
- 文件系统

**推荐教程：**
- C: The little book about OS development
- C: How to create an OS from scratch (cfenollosa)
- Rust: Writing an OS in Rust (os.phil-opp.com)
- Assembly: Baking Pi – Operating Systems Development

**关键概念：**
- BIOS/UEFI = 固件，初始化硬件
- Bootloader = 加载内核
- 实模式 → 保护模式 → 长模式
- 分页 = 虚拟内存管理
- 上下文切换 = 切换进程

---

### 18. 物理引擎 (Physics Engine)
**核心技术：**
- 刚体动力学
- 碰撞检测
- 约束求解
- 积分器

**推荐教程：**
- C++: How to Create a Custom Physics Engine
- JavaScript: Build a simple 2D physics engine

---

### 19. 处理器 (Processor)
**核心技术：**
- FPGA 编程
- RISC-V 指令集
- Verilog/VHDL

**推荐教程：**
- Verilog: From Blinker to RISC-V

---

### 20. 编程语言 (Programming Language)
**核心技术：**
- 词法分析 (Lexing)
- 语法分析 (Parsing)
- 抽象语法树 (AST)
- 解释器 (Interpreter)
- 编译器 (Compiler)
- 垃圾回收 (GC)

**推荐教程：**
- C: Build Your Own Lisp (buildyourownlisp.com)
- Python: A Python Interpreter Written in Python
- Java: Crafting interpreters (craftinginterpreters.com)
- (any): mal - Make a Lisp (kanaka/mal)

**关键概念：**
- Lexer = 源码 → Token 流
- Parser = Token → AST
- Interpreter = 直接执行 AST
- Compiler = AST → 机器码/字节码
- GC = 自动内存管理

---

### 21. 正则表达式引擎 (Regex Engine)
**核心技术：**
- NFA (非确定有限自动机)
- DFA (确定有限自动机)
- 回溯算法
- Thompson 构造法

**推荐教程：**
- C: A Regular Expression Matcher (Rob Pike)
- Python: Build Your Own Regular Expression Engines
- JavaScript: Build a Regex Engine in Less than 40 Lines

---

### 22. 搜索引擎 (Search Engine)
**核心技术：**
- 倒排索引 (Inverted Index)
- TF-IDF (词频-逆文档频率)
- 向量空间模型
- 排名算法

**推荐教程：**
- Python: Building a Vector Space Indexing Engine
- Python: Finding Important Words in Text Using TF-IDF

---

### 23. Shell (命令行解释器)
**核心技术：**
- 命令解析
- 管道 (Pipe)
- 重定向
- 环境变量
- 进程管理

**推荐教程：**
- C: Tutorial - Write a Shell in C (brennan.io)
- Go: Writing a simple shell in Go
- Rust: Build Your Own Shell using Rust

---

### 24. 模板引擎 (Template Engine)
**核心技术：**
- 变量替换
- 控制结构 (if/for)
- 模板继承
- 转义处理

**推荐教程：**
- JavaScript: JavaScript template engine in just 20 lines
- Python: Approach: Building a toy template engine

---

### 25. 文本编辑器 (Text Editor)
**核心技术：**
- 缓冲区管理
- 光标移动
- 语法高亮
- 文件 I/O

**推荐教程：**
- C: Build Your Own Text Editor (viewsourcecode.org/snaptoken/kilo)
- Rust: Hecto: Build your own text editor in Rust
- Python: Python Tutorial: Make Your Own Text Editor

---

### 26. 视觉识别系统 (Visual Recognition System)
**核心技术：**
- 人脸识别
- 车牌识别
- 卷积神经网络 (CNN)

**推荐教程：**
- Python: Developing a License Plate Recognition System
- Python: Building a Facial Recognition Pipeline

---

### 27. 体素引擎 (Voxel Engine)
**核心技术：**
- 体素 (Voxel) = 3D 像素
- 网格渲染
- 地形生成

**推荐教程：**
- C++: Let's Make a Voxel Engine

---

### 28. Web 浏览器 (Web Browser)
**核心技术：**
- HTML 解析
- CSS 布局
- JavaScript 引擎
- 渲染引擎

**推荐教程：**
- Rust: Let's build a browser engine (limpet.net/mbrubeck)
- Python: Browser Engineering (browser.engineering)

---

### 29. Web 服务器 (Web Server)
**核心技术：**
- Socket 编程
- TCP 连接
- HTTP 协议
- 请求解析
- 响应生成
- 并发处理

**推荐教程：**
- Python: Let’s Build A Web Server (ruslanspivak.com) - 3 部分系列
- Node.js: Build Your Own Web Server From Scratch
- Python: A Simple Web Server (AOSA)

**最简实现（20 行 Python）：**
```python
import socket

HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)

while True:
    client_connection, client_address = listen_socket.accept()
    request_data = client_connection.recv(1024)
    
    http_response = b"""HTTP/1.1 200 OK

Hello, World!"""
    client_connection.sendall(http_response)
    client_connection.close()
```

**HTTP 协议基础：**
- 请求格式：`METHOD PATH HTTP/VERSION\r\nHeaders\r\n\r\nBody`
- 响应格式：`HTTP/VERSION STATUS MESSAGE\r\nHeaders\r\n\r\nBody`
- 常用方法：GET, POST, PUT, DELETE
- 常用状态码：200 OK, 404 Not Found, 500 Internal Server Error

---

### 30. 未分类 (Uncategorized)
**其他有趣项目：**
- 从 NAND 到 Tetris (nand2tetris.org)
- 哈希表 (Hash Table)
- 终端模拟器 (Terminal Emulator)
- DNS 服务器
- 负载均衡器
- 视频编码器
- MQTT broker
- Linux 调试器
- VR 头戴设备
- X Window Manager
- CDN
- 模块打包器
- Promise 实现
- 缓存系统
- 推荐系统
- 垃圾邮件检测器
- GAN (生成对抗网络)
- 文档扫描器
- 移动应用

---

## 💡 学习路径建议

### 初学者（1-3 个月）
1. **命令行工具** - Go/Rust 写 CLI
2. **文本编辑器** - kilo tutorial
3. **Web 服务器** - 20 行 Python
4. **神经网络** - 11 行 Python
5. **Shell** - C 写简单 shell

### 中级（3-6 个月）
1. **Git** - 理解 Git 内部
2. **数据库** - SQLite 克隆
3. **前端框架** - React 克隆
4. **游戏** - 2D 游戏引擎
5. **区块链** - 简单加密货币

### 高级（6+ 个月）
1. **操作系统** - 写内核
2. **编程语言** - 编译器/解释器
3. **Docker** - 容器运行时
4. **Web 浏览器** - 渲染引擎
5. **神经网络** - 深度学习框架

---

## 🔧 常用语言推荐

| 任务 | 推荐语言 | 理由 |
|------|---------|------|
| 系统编程 | C, Rust | 性能、内存控制 |
| Web 开发 | Python, Node.js | 快速原型、生态好 |
| 系统工具 | Go | 并发、跨平台 |
| 学习概念 | Python | 简单易读 |
| 现代项目 | Rust | 安全、性能 |

---

## 📖 推荐书籍

1. **系统编程**
   - Unix Network Programming, Volume 1
   - Advanced Programming in the UNIX Environment
   - The Linux Programming Interface

2. **编译器**
   - Crafting Interpreters
   - Compilers: Principles, Techniques, and Tools (龙书)

3. **操作系统**
   - Operating Systems: Three Easy Pieces
   - The little book about OS development

4. **深度学习**
   - Neural Networks and Deep Learning
   - Deep Learning (Goodfellow et al.)

---

## 🎯 核心原则

1. **从简单开始** - 不要一开始就做复杂项目
2. **迭代改进** - 先让它工作，再让它更好
3. **阅读源码** - 学习现有项目的实现
4. **写测试** - 确保你的代码正确
5. **文档化** - 记录你的学习过程

---

*学习日期：2026-03-04*
*记录者：二饼 🦊*
