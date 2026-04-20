# GraphRAG 集成报告

## 集成概述

已成功将 GraphRAG（Graph Retrieval-Augmented Generation）框架集成到 OpenClaw 工作空间。

## 目录结构

```
integrations/graphrag/
├── INTEGRATION.md          # 集成文档（详细使用指南）
├── README.md               # 本报告
├── index.ts                # 主入口文件（统一 API）
├── graph/                  # 图管理模块
│   ├── types.ts            # 类型定义（Entity, Relation, Graph 等）
│   ├── manager.ts          # 图管理器（CRUD 操作）
│   └── storage.ts          # 存储适配器（支持多后端）
├── retrieval/              # 检索系统
│   ├── retriever.ts        # 图检索器（语义检索）
│   ├── indexer.ts          # 图索引器（加速查询）
│   └── ranker.ts           # 结果排序器（重排序）
├── reasoning/              # 推理引擎
│   ├── engine.ts           # 推理引擎核心
│   ├── paths.ts            # 路径推理（最短路径、路径发现）
│   └── inference.ts        # 推理策略（传递性、对称性等）
├── examples/               # 示例代码
│   ├── basic-usage.ts      # 基础用法示例
│   └── advanced-usage.ts   # 高级用法示例
└── tests/                  # 测试文件
    └── manager.test.ts     # 核心功能测试
```

## 核心组件

### 1. 图管理器 (GraphManager)

**文件**: `graph/manager.ts`

**功能**:
- 实体 CRUD 操作（添加、获取、更新、删除）
- 关系 CRUD 操作
- 批量操作支持
- 图统计信息（节点数、边数、密度、聚类系数等）
- 导入/导出功能

**关键方法**:
```typescript
addEntity(entity)           // 添加实体
addEntities(entities)       // 批量添加
getEntity(id)              // 获取实体
updateEntity(id, updates)  // 更新实体
deleteEntity(id)           // 删除实体
addRelation(relation)       // 添加关系
getRelationsForEntity(id)   // 获取实体关系
getNeighbors(id)           // 获取邻居节点
getStats()                 // 获取统计信息
```

### 2. 检索系统 (Retrieval)

**文件**: `retrieval/retriever.ts`, `indexer.ts`, `ranker.ts`

**功能**:
- 基于关键词的实体检索
- 关系检索
- 子图扩展检索
- 向量嵌入检索（如果可用）
- 结果重排序（相似度、图特征、时效性）

**关键方法**:
```typescript
retrieve(options)           // 执行检索
retrieveByEmbedding(vec, k) // 向量检索
searchByKeyword(keyword)    // 关键词搜索
rankEntities(entities)      // 实体排序
diversify(results)          // 多样性重排序
```

### 3. 推理引擎 (Reasoning)

**文件**: `reasoning/engine.ts`, `paths.ts`, `inference.ts`

**功能**:
- 路径推理（最短路径、所有路径）
- 关系推理（传递性、对称性、层次性）
- 归纳推理（模式发现）
- 自定义推理策略

**关键方法**:
```typescript
findPaths(from, to)         // 查找路径
inferRelations(params)      // 推理关系
inductPatterns(params)      // 归纳模式
findShortestPath(from, to)  // 最短路径
findCommonNeighbors(ids)    // 共同邻居
```

### 4. 统一接口 (GraphRAG)

**文件**: `index.ts`

提供简化的 API：
```typescript
const graphrag = new GraphRAG(config);

await graphrag.addKnowledge({ entities, relations });
const result = await graphrag.query('查询文本');
const path = await graphrag.findPath(from, to);
const inferred = await graphrag.reason(params);
```

## 类型定义

### 核心类型

```typescript
interface Entity {
  id: string;
  type: EntityType;
  properties: Record<string, any>;
  embedding?: number[];
  createdAt?: Date;
  updatedAt?: Date;
}

interface Relation {
  id: string;
  from: string;
  to: string;
  type: RelationType;
  properties?: Record<string, any>;
  weight?: number;
  confidence?: number;
}

interface Path {
  nodes: Node[];
  edges: Edge[];
  length: number;
  weight: number;
}

interface InferenceResult {
  inferred: Relation[];
  confidence: number;
  reasoning: string;
  evidence: Evidence[];
}
```

### 枚举类型

```typescript
type EntityType = 'Person' | 'Organization' | 'Location' | 'Event' | 
                  'Concept' | 'Document' | 'Memory' | 'Skill' | 'Task' | 'Custom';

type RelationType = 'KNOWS' | 'RELATED_TO' | 'PART_OF' | 'CAUSES' | 
                    'PRECEDES' | 'FOLLOWS' | 'DEPENDS_ON' | 'REFERENCES' | 
                    'SIMILAR_TO' | 'DERIVED_FROM' | 'USES' | 'CREATES' | 'Custom';
```

## 集成要点

### 1. 知识图谱检索

- ✅ 实体检索：支持关键词、类型、属性过滤
- ✅ 关系检索：支持实体相关关系、入边、出边
- ✅ 子图检索：支持扩展子图、限制深度

### 2. 关系推理

- ✅ 路径推理：支持 BFS、DFS、Dijkstra 算法
- ✅ 规则推理：支持传递性、对称性、层次性
- ✅ 归纳推理：支持模式发现和统计

### 3. 图结构分析

- ✅ 中心性分析：通过度中心性
- ✅ 连通性分析：连通分量计数
- ✅ 聚类分析：聚类系数计算

### 4. 知识连接

- ✅ 跨实体连接：通过关系连接
- ✅ 跨关系连接：传递性推理
- ✅ 多图谱支持：导入/导出功能

## 使用示例

### 基础用法

```typescript
import { GraphRAG } from './integrations/graphrag';

const graphrag = new GraphRAG();

// 添加知识
await graphrag.addKnowledge({
  entities: [
    { type: 'Person', properties: { name: 'Alice' } },
    { type: 'Person', properties: { name: 'Bob' } }
  ],
  relations: [
    { from: 'entity_0', to: 'entity_1', type: 'KNOWS' }
  ]
});

// 查询
const result = await graphrag.query('Alice 的朋友');
console.log(result.answer);
```

### 高级用法

```typescript
// 推理
const inferred = await graphrag.reason({
  entityId: 'entity_0',
  relationType: 'KNOWS',
  rules: ['transitive-knows']
});

// 路径查找
const path = await graphrag.findPath('entity_0', 'entity_3');

// 统计信息
const stats = await graphrag.getStats();
```

## 性能特性

1. **索引支持**: 支持关键词、类型、属性索引
2. **批量操作**: 支持批量添加实体和关系
3. **缓存**: 内置结果缓存
4. **存储抽象**: 支持内存、SQLite、Neo4j 后端（可扩展）

## 扩展性

1. **自定义实体类型**: 通过 `type: 'Custom'` 扩展
2. **自定义关系类型**: 支持任意关系类型
3. **自定义推理规则**: 实现 `InferenceStrategy` 接口
4. **自定义存储后端**: 实现 `StorageAdapter` 接口

## 与 OpenClaw 集成

### Memory 集成

```typescript
// 从 Memory 构建
const memoryEntities = memories.map(m => ({
  id: m.id,
  type: 'Memory',
  properties: { content: m.content, tags: m.tags }
}));

await graphrag.addKnowledge({ entities: memoryEntities });

// 增强检索
const enhanced = await graphrag.query('previous decisions');
```

### 技能集成

可与其他 OpenClaw 技能配合：
- `knowledge-graph`: 知识图谱管理
- `graph-analysis`: 图分析
- `relation-detection`: 关系检测

## 测试

测试文件位于 `tests/manager.test.ts`，覆盖：
- 图管理器 CRUD 操作
- 检索系统功能
- 推理引擎功能

## 未来规划

1. [ ] 完善 SQLite 存储后端
2. [ ] 完善 Neo4j 存储后端
3. [ ] 添加嵌入模型集成
4. [ ] 增强多跳推理能力
5. [ ] 支持时序图谱
6. [ ] 添加更多图算法（PageRank、社区发现）

## 总结

GraphRAG 集成已完成，提供了完整的知识图谱管理、检索和推理能力。核心功能包括：

- **图管理**: 完整的实体和关系 CRUD
- **检索系统**: 关键词、向量、子图检索
- **推理引擎**: 路径、规则、归纳推理
- **统一 API**: 简化的 GraphRAG 类

所有代码位于 `integrations/graphrag/` 目录，可直接使用或根据需求扩展。
