# Erbing-1B 项目实施计划

## 项目概览

**目标**: 构建一个 1B 参数的混合架构模型，集成左脑(结构化) + 右脑(语义) 双系统，支持四策略检索增强生成。

**状态**: Phase 1 设计完成 ✅

---

## 已完成的工作

### 1. 核心架构设计 ✅

- `memory/ERBING_1B_ARCHITECTURE.md` - 基础架构设计
  - Hybrid Mamba-Transformer 混合架构
  - 24层配置（12层 Mamba + 12层 Transformer）
  - 参数量精确控制在 1B
  
- `memory/ERBING_1B_ARCHITECTURE_V2.md` - 数据库集成设计 ✅ NEW
  - 左右脑架构映射
  - 四策略检索集成
  - 数据库优先训练策略
  - 评估指标体系

### 2. 实施方案 ✅

- `memory/ERBING_1B_IMPLEMENTATION.md` - 硬件适配方案
  - RTX 4060 (8GB) 本地开发策略
  - 云端训练成本估算
  - QLoRA 微调方案
  - 推理优化计划

### 3. 记忆系统迁移 ✅ NEW

- `memory/database/retrieval_strategies.py` - 四策略检索系统
  - 策略 1: 按需归因检索
  - 策略 2: 时间衰减检索
  - 策略 3: 重要性优先检索
  - 策略 4: 向量语义检索
  - 智能组合检索
  
- `memory/database/migration_plan_v2.py` - 数据库迁移方案
  - 源文件分析
  - 自动类型推断
  - 重要性评估
  - 迁移验证

---

## 项目结构

```
erbing-1b/
├── memory/
│   ├── database/
│   │   ├── xiaozhi_memory.db          # SQLite (左脑)
│   │   ├── lancedb/                    # LanceDB (右脑)
│   │   ├── hybrid_memory.py            # 混合记忆接口
│   │   ├── retrieval_strategies.py     # 四策略检索 ✅ NEW
│   │   └── migration_plan_v2.py        # 迁移方案 ✅ NEW
│   │
│   ├── ERBING_1B_ARCHITECTURE.md       # 基础架构
│   ├── ERBING_1B_ARCHITECTURE_V2.md    # 数据库架构 ✅ NEW
│   └── ERBING_1B_IMPLEMENTATION.md      # 实施方案
│
├── src/
│   ├── model/
│   │   ├── __init__.py
│   │   ├── config.py                   # 模型配置
│   │   ├── mamba_block.py              # Mamba 层
│   │   ├── transformer_block.py        # Transformer 层
│   │   ├── dual_brain.py               # 左右脑整合 ✅ NEW
│   │   └── erbing_1b.py                # 完整模型
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── adapter.py                  # 检索适配器
│   │   ├── cache.py                    # 检索缓存
│   │   └── fusion.py                   # 检索-生成融合
│   │
│   ├── training/
│   │   ├── __init__.py
│   │   ├── data_generator.py           # 数据库驱动数据生成
│   │   ├── trainer.py                  # 训练器
│   │   └── evaluator.py                # 评估器
│   │
│   └── api/
│       ├── __init__.py
│       ├── server.py                   # FastAPI 服务
│       └── client.py                   # 客户端
│
├── scripts/
│   ├── train_tokenizer.py              # 训练 Tokenizer
│   ├── prepare_data.py                 # 数据准备
│   ├── train.py                        # 训练脚本
│   ├── evaluate.py                     # 评估脚本
│   └── export.py                       # 模型导出
│
├── tests/
│   ├── test_model.py
│   ├── test_retrieval.py
│   └── test_training.py
│
├── configs/
│   ├── model_config.yaml               # 模型配置
│   ├── training_config.yaml            # 训练配置
│   └── deployment_config.yaml          # 部署配置
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_prototype.ipynb
│   └── 03_retrieval_integration.ipynb
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── TRAINING.md
│   └── DEPLOYMENT.md
│
├── checkpoints/
│   └── .gitkeep
│
├── data/
│   ├── raw/                            # 原始数据
│   ├── processed/                      # 处理后数据
│   └── tokenizer/                      # Tokenizer 文件
│
├── requirements.txt
├── setup.py
└── README.md
```

---

## Phase 1 检查清单

### ✅ 已完成
- [x] Hybrid Mamba-Transformer 架构设计
- [x] 左右脑双系统架构设计
- [x] 四策略检索系统实现
- [x] 数据库迁移方案设计
- [x] 训练成本估算和硬件适配
- [x] 评估指标体系设计

### 🚧 进行中
- [ ] 项目结构初始化
- [ ] 基础模型代码实现
- [ ] 检索系统集成测试

### 📋 待办
- [ ] Tokenizer 训练
- [ ] 数据收集和预处理
- [ ] 小规模训练验证
- [ ] 评估基准测试
- [ ] API 服务开发
- [ ] 文档完善

---

## 下一步行动

### 本周任务 (Week 1)

1. **项目初始化**
   ```bash
   mkdir -p erbing-1b/{src/model,src/retrieval,src/training,src/api}
   mkdir -p erbing-1b/{scripts,tests,configs,notebooks,docs}
   mkdir -p erbing-1b/{checkpoints,data/raw,data/processed,data/tokenizer}
   ```

2. **核心代码框架**
   - 实现 `config.py` - 模型配置
   - 实现 `mamba_block.py` - Mamba 层
   - 实现 `transformer_block.py` - Transformer 层

3. **检索系统测试**
   - 运行 `retrieval_strategies.py` 测试
   - 验证四种策略效果
   - 优化检索性能

### 下周任务 (Week 2)

1. **左右脑整合**
   - 实现 `dual_brain.py`
   - 添加门控机制
   - 测试左右脑交互

2. **训练数据生成**
   - 从数据库生成训练样本
   - 创建任务模板
   - 数据质量验证

---

## 技术债务

- [ ] 解决 Windows 控制台 UTF-8 编码问题（emoji 显示）
- [ ] 优化数据库查询性能
- [ ] 添加单元测试
- [ ] 完善文档

---

## 参考资料

### 架构设计
- [Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752)
- [FlashAttention-2](https://arxiv.org/abs/2307.08691)
- [Grouped Query Attention](https://arxiv.org/abs/2305.13245)

### 记忆系统
- [MemGPT](https://arxiv.org/abs/2310.08560)
- [Memori: Memory System for LLM Agents](https://github.com/your-repo/memori)

### 检索增强
- [RAG: Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [Dense Passage Retrieval](https://arxiv.org/abs/2007.00808)

---

*项目负责人: Erbing*
*创建时间: 2026-04-11*
*最后更新: 2026-04-11*
*版本: v1.0*
