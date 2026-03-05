
# M5Stack Assistant Skill - 使用说明

## 📦 包含内容

```
skills/m5stack-arduino-programmer/
├── SKILL.md                          # 核心skill指令
├── README.md                         # 本文件
├── references/
│   └── quick-reference.md           # M5Stack快速参考
└── scripts/
    └── mcp.js                       # 简单好用的MCP客户端
```

## ✅ 测试状态
- ✅ MCP 服务器连接成功
- ✅ JSON-RPC 调用成功
- ✅ knowledge_search 工具可用

## 🚀 功能范围

这个 skill 可以解决以下类型的问题：

### 📋 产品咨询
- 产品功能、特性、应用场景
- 产品对比、选型建议
- 包装内容、配件信息

### 📊 规格参数
- 技术规格、电气特性
- 尺寸、重量、SKU
- 功耗、热设计、工作温度
- 芯片型号、内存配置、接口定义

### 💻 编程开发
- Arduino / UIFlow / ESP-IDF 编程
- API使用、示例代码
- 库依赖、配置要求
- 引脚定义、硬件连接

### 🔧 技术支持
- 设备无法正常工作
- 连接问题、通信错误
- 常见问题解答 (FAQ)
- 固件更新、恢复出厂设置

## 🚀 快速开始

### 1. 使用 mcp.js 查询知识库

```javascript
const { mcpSearch } = require('./scripts/mcp.js');

// 查询 M5Stack CoreS3 产品信息
const result = await mcpSearch('M5Stack CoreS3 规格参数', { 
  filter_type: 'product',
  num: 2 
});

// 查询 Arduino 开发相关
const result = await mcpSearch('M5Stack Core2 Arduino', { 
  filter_type: 'arduino',
  num: 2 
});

// 查询 LLM-8850 加速卡功耗
const result = await mcpSearch('LLM-8850 功耗 热设计', { 
  filter_type: 'product',
  num: 2 
});
```

### 2. 运行演示
```bash
cd skills/m5stack-arduino-programmer/scripts
node mcp.js
```

## 📝 MCP 协议说明

### 连接流程
1. **SSE 连接**: GET `https://mcp.m5stack.com/sse`
2. **获取 endpoint**: 接收 `event: endpoint` 事件
3. **保持 SSE 连接**: 持续监听响应
4. **发送 JSON-RPC**: POST 到 `/messages?session_id=xxx`
5. **接收响应**: 通过 SSE 接收 `event: message`

### 支持的 JSON-RPC 方法
- `initialize` - 初始化会话
- `tools/list` - 列出可用工具
- `tools/call` - 调用工具
- `resources/list` - 列出资源
- `ping` - 心跳检测

## 🔧 可用工具

### knowledge_search
从 M5Stack 产品知识库中检索相关信息。

**参数：**
- `query` (必填): 查询文本
- `num`: 实体数量 (1-3, 默认 1)
- `is_chip`: 是否查询芯片手册 (true/false)
- `filter_type`: 文档类型过滤
  - `product` - 产品文档（推荐用于产品咨询、规格查询）
  - `arduino` - Arduino 开发
  - `uiflow` - UiFlow 开发
  - `esp-idf` - ESP-IDF 开发
  - `program` - 全品类编程文档
  - 等等...

## 💡 使用建议

### 根据问题类型选择 filter_type

| 问题类型 | 推荐 filter_type | 示例 |
|---------|-----------------|------|
| 产品规格、功耗、尺寸 | `product` | "CoreS3 规格参数" |
| Arduino 代码、API | `arduino` | "CoreS3 Arduino 示例" |
| UIFlow 开发 | `uiflow` | "UIFlow CoreS3 使用" |
| ESP-IDF 开发 | `esp-idf` | "ESP-IDF CoreS3" |
| 故障排除、FAQ | `product` 或 `program` | "CoreS3 无法启动" |

### 查询数量 num 建议

| 场景 | num 值 |
|-----|--------|
| 单个产品简单查询 | 1 |
| 产品详细规格查询 | 2 |
| 产品对比、复杂问题 | 3 |

### 备用方案
- 如果 MCP 服务有问题，直接访问 https://docs.m5stack.com
- 查看 `references/quick-reference.md` 了解常用信息
