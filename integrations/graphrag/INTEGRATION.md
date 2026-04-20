# GraphRAG Integration for OpenClaw

## 概述

GraphRAG（Graph Retrieval-Augmented Generation）是一个结合知识图谱与检索增强生成的框架，旨在提升 LLM 的推理能力和知识连接能力。

## 架构设计

```
integrations/graphrag/
├── graph/           # 图管理器
│   ├── manager.ts   # 图管理核心
│   ├── types.ts     # 图数据类型定义
│   └── storage.ts   # 图存储适配器
├── retrieval/       # 检索系统
│   ├── retriever.ts # 图检索器
│   ├── indexer.ts   # 图索引器
│   └── ranker.ts    # 结果排序器
├── reasoning/       # 推理引擎
│   ├── engine.ts    # 推理引擎核心
│   ├── paths.ts     # 路径推理
│   └── inference.ts # 推理策略
├── examples/        # 示例代码
└── tests/           # 测试文件
```

## 核心组件

### 1. 图管理器 (Graph Manager)

负责知识图谱的创建、更新、删除和查询操作。

```typescript
import { GraphManager } from './graph/manager';

const graphManager = new GraphManager({
  storage: 'memory', // 或 'neo4j', 'sqlite'
});

// 添加实体
await graphManager.addEntity({
  id: 'entity-1',
  type: 'Person',
  properties: { name: 'Alice', age: 30 }
});

// 添加关系
await graphManager.addRelation({
  from: 'entity-1',
  to: 'entity-2',
  type: 'KNOWS',
  properties: { since: '2020' }
});
```

### 2. 检索系统 (Retrieval System)

基于图结构的语义检索，支持实体检索、关系检索和子图检索。

```typescript
import { GraphRetriever } from './retriever';

const retriever = new GraphRetriever(graphManager);

// 语义检索
const results = await retriever.retrieve({
  query: 'Alice 的朋友',
  topK: 10,
  includeRelations: true
});
```

### 3. 推理引擎 (Reasoning Engine)

支持路径推理、规则推理和归纳推理。

```typescript
import { ReasoningEngine } from './reasoning/engine';

const engine = new ReasoningEngine(graphManager);

// 路径推理
const paths = await engine.findPaths({
  from: 'entity-1',
  to: 'entity-5',
  maxDepth: 3
});

// 关系推理
const inferred = await engine.inferRelations({
  entity: 'entity-1',
  relationType: 'KNOWS',
  rules: ['transitive']
});
```

## 集成要点

### 知识图谱检索

- 实体检索：基于向量相似度和图结构的混合检索
- 关系检索：检索与实体相关的所有关系
- 子图检索：检索与查询相关的子图结构

### 关系推理

- 路径推理：发现实体之间的隐含关系路径
- 规则推理：基于预定义规则的推理
- 归纳推理：从已知事实归纳新的关系

### 图结构分析

- 中心性分析：识别图中的重要节点
- 社区发现：发现图中的社群结构
- 连通性分析：分析图的连通组件

### 知识连接

- 跨实体连接：连接不同类型的实体
- 跨关系连接：发现关系的传递性
- 跨图谱连接：连接多个知识图谱

## 使用示例

### 基础用法

```typescript
import { GraphRAG } from './index';

const graphrag = new GraphRAG({
  graph: { storage: 'memory' },
  retrieval: { topK: 10 },
  reasoning: { maxDepth: 3 }
});

// 添加知识
await graphrag.addKnowledge({
  entities: [
    { id: 'e1', type: 'Person', properties: { name: 'Alice' } },
    { id: 'e2', type: 'Person', properties: { name: 'Bob' } }
  ],
  relations: [
    { from: 'e1', to: 'e2', type: 'KNOWS' }
  ]
});

// 查询
const answer = await graphrag.query('Who does Alice know?');
```

### 与 OpenClaw Memory 集成

```typescript
import { GraphRAG } from './index';
import { MemoryManager } from '../memory';

const graphrag = new GraphRAG({
  storage: 'memory',
  memoryIntegration: true
});

// 从记忆构建图谱
await graphrag.buildFromMemory(memoryManager);

// 增强检索
const enhanced = await graphrag.enhancedRetrieve({
  query: 'previous decisions about API design',
  includeMemory: true
});
```

## 配置选项

```typescript
interface GraphRAGConfig {
  graph: {
    storage: 'memory' | 'neo4j' | 'sqlite';
    indexPath?: string;
  };
  retrieval: {
    topK: number;
    similarityThreshold: number;
    includeRelations: boolean;
  };
  reasoning: {
    maxDepth: number;
    rules: string[];
    confidenceThreshold: number;
  };
  embedding: {
    model: string;
    dimensions: number;
  };
}
```

## 性能优化

1. **图索引优化**：对高频查询的实体和关系建立索引
2. **缓存策略**：缓存常用查询结果和推理路径
3. **批量操作**：支持批量添加实体和关系
4. **增量更新**：支持增量更新图谱，避免全量重建

## 扩展性

- **存储适配器**：支持多种图数据库（Neo4j、SQLite、Memory）
- **嵌入模型**：支持多种嵌入模型（OpenAI、本地模型）
- **推理规则**：支持自定义推理规则

## 未来规划

1. 支持更多图数据库后端
2. 增强多跳推理能力
3. 支持时序图谱
4. 集成更多 OpenClaw 技能（如 knowledge-graph、graph-analysis）
