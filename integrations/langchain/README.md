# LangChain Integration for OpenClaw

## 快速开始

本集成模块提供 OpenClaw 与 LangChain 框架的无缝连接，支持工具链管理、链式执行、记忆系统集成和上下文管理。

### 安装依赖

```bash
npm install @langchain/core langchain zod
```

### 基本使用

#### 1. 工具包装

```typescript
import { createOpenClawTool } from '@openclaw/langchain-integration';
import { z } from 'zod';

const myTool = createOpenClawTool(
  'my_tool',
  'A simple tool',
  z.object({ input: z.string() }),
  async (input) => ({ result: input.input.toUpperCase() })
);
```

#### 2. 链式执行

```typescript
import { createChainBuilder } from '@openclaw/langchain-integration';

const chain = createChainBuilder()
  .addStep('step1', tool1)
  .addStep('step2', tool2)
  .build();

const result = await chain.execute({ input: 'test' });
```

#### 3. 记忆系统集成

```typescript
import { createOpenClawMemory, createContextManager } from '@openclaw/langchain-integration';

const memory = createOpenClawMemory({
  sessionId: 'user-session',
  maxTokens: 4000,
});

await memory.saveContext(
  { input: 'Hello' },
  { output: 'Hi there!' }
);
```

## 目录结构

```
integrations/langchain/
├── INTEGRATION.md          # 详细集成文档
├── tools/                  # 工具包装器
│   ├── openclaw-tool.ts    # OpenClaw 工具包装
│   └── tool-adapter.ts     # LangChain 工具适配器
├── chains/                 # 链管理
│   ├── chain-manager.ts    # 链执行管理器
│   └── chain-builder.ts    # 链构建器
├── memory/                 # 记忆系统
│   ├── openclaw-memory.ts  # OpenClaw 记忆适配器
│   └── context-manager.ts  # 上下文管理器
├── examples/               # 示例代码
│   ├── basic-chain.ts      # 基础链示例
│   ├── tool-chain.ts       # 工具链示例
│   └── memory-chain.ts     # 记忆链示例
└── tests/                  # 测试文件
    ├── tools.test.ts
    ├── chains.test.ts
    └── memory.test.ts
```

## 核心功能

### 工具链管理

- ✅ 工具包装和注册
- ✅ LangChain 工具适配
- ✅ 批量工具调用
- ✅ 错误处理和重试

### 链式执行

- ✅ 顺序链执行
- ✅ 并行执行
- ✅ 条件分支
- ✅ 输入转换
- ✅ 重试配置

### 记忆系统集成

- ✅ 会话级记忆隔离
- ✅ 上下文管理
- ✅ 令牌限制和修剪
- ✅ 系统消息支持

### 上下文管理

- ✅ 请求级上下文
- ✅ 用户身份传播
- ✅ 会话跟踪
- ✅ 上下文清理

## 运行测试

```bash
npm test
```

## 运行示例

```bash
npx ts-node examples/basic-chain.ts
npx ts-node examples/tool-chain.ts
npx ts-node examples/memory-chain.ts
```

## 文档

详细文档请参考 [INTEGRATION.md](./INTEGRATION.md)

## 版本历史

- v1.0.0 - 初始集成，提供基础工具和记忆支持
