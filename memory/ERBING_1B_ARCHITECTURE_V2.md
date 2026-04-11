# Erbing-1B 架构补充设计 (Phase 1)

基于 MEMORY.md 中的强制规则，补充以下关键设计：

## 1. 左右脑架构集成

### 设计理念
```
Erbing-1B = 左脑(结构化) + 右脑(向量) 双系统

左脑系统 (SQLite):
├── 事实记忆 (Facts)
├── 事件日志 (Events)
├── 偏好设置 (Preferences)
└── 技能笔记 (Skills)

右脑系统 (LanceDB):
├── 语义记忆 (Semantic Memory)
├── 思维链记录 (Thought Chains)
├── 关联记忆 (Associations)
└── 模式识别 (Patterns)
```

### 模型架构映射

```yaml
# Erbing-1B 双脑架构配置
architecture:
  name: "Erbing-1B-DualBrain"
  base: "HybridMambaTransformer"
  
  # 左脑模块 (结构化处理)
  left_brain:
    type: "structured_reasoning"
    layers: 6  # 前6层
    features:
      - fact_extraction      # 事实提取
      - entity_recognition   # 实体识别
      - relation_mapping     # 关系映射
      - temporal_ordering    # 时序排序
    output: "structured_state"
  
  # 右脑模块 (语义联想)
  right_brain:
    type: "semantic_association"
    layers: 6  # 后6层
    features:
      - semantic_embedding   # 语义嵌入
      - associative_recall   # 联想回忆
      - pattern_matching     # 模式匹配
      - creative_generation  # 创造性生成
    output: "semantic_state"
  
  # 中脑模块 (整合协调)
  mid_brain:
    type: "integration_layer"
    features:
      - cross_attention      # 左右脑交叉注意力
      - conflict_resolution  # 冲突解决
      - context_switching    # 上下文切换
      - goal_directed        # 目标导向
```

## 2. 四策略检索集成

### 检索策略与模型架构的结合

```python
class Erbing1BWithRetrieval(nn.Module):
    """Erbing-1B + 四策略检索系统"""
    
    def __init__(self, config):
        super().__init__()
        
        # 基础模型 (Mamba + Transformer)
        self.base_model = Erbing1BHybrid(config)
        
        # 检索适配器
        self.retrieval_adapter = RetrievalAdapter(
            strategies=["attribution", "time_decay", "importance", "semantic"]
        )
        
        # 检索-生成融合层
        self.retrieval_fusion = nn.ModuleDict({
            "left_brain_gate": nn.Linear(config.hidden_size, 4),  # 左脑门控
            "right_brain_gate": nn.Linear(config.hidden_size, 4),  # 右脑门控
            "context_encoder": nn.TransformerEncoder(...),  # 检索上下文编码
        })
    
    def forward(self, input_ids, query_context=None):
        # 1. 检索相关记忆
        if query_context:
            retrieval_results = self.retrieval_adapter.smart_retrieve(
                query_context, mode="balanced"
            )
            
            # 2. 编码检索结果
            retrieval_encoded = self.encode_retrieval(retrieval_results)
            
            # 3. 融合检索信息
            # 左脑: 结构化信息优先
            left_gate = F.softmax(self.retrieval_fusion["left_brain_gate"](retrieval_encoded), dim=-1)
            
            # 右脑: 语义信息优先
            right_gate = F.softmax(self.retrieval_fusion["right_brain_gate"](retrieval_encoded), dim=-1)
        else:
            left_gate = right_gate = None
        
        # 4. 基础模型前向传播
        hidden_states = self.base_model.forward(
            input_ids,
            left_gate=left_gate,
            right_gate=right_gate
        )
        
        return hidden_states
    
    def encode_retrieval(self, retrieval_results):
        """编码检索结果"""
        # 分离左脑和右脑记忆
        left_memories = retrieval_results["by_strategy"].get("attribution", []) + \
                       retrieval_results["by_strategy"].get("importance", [])
        
        right_memories = retrieval_results["by_strategy"].get("semantic", []) + \
                        retrieval_results["by_strategy"].get("time_decay", [])
        
        # 编码并返回
        left_encoded = self.encode_memories(left_memories)
        right_encoded = self.encode_memories(right_memories)
        
        return torch.cat([left_encoded, right_encoded], dim=-1)
```

## 3. 数据库优先训练策略

### 训练数据增强

```yaml
# 从数据库记忆生成训练数据
data_generation:
  source: "xiaozhi_memory.db"
  
  # 左脑数据 (结构化)
  left_brain_data:
    types: ["identity", "principle", "event", "preference"]
    format:
      input: "Context: {category}\nQuestion: {title}\nAnswer: {content}"
      target: "{structured_response}"
    augmentation:
      - entity_extraction    # 实体提取任务
      - fact_verification    # 事实验证任务
      - temporal_reasoning   # 时序推理任务
  
  # 右脑数据 (语义)
  right_brain_data:
    types: ["learning", "skill", "architecture"]
    format:
      input: "Topic: {tags}\nContent: {content}\nRelated:"
      target: "{semantic_expansion}"
    augmentation:
      - semantic_similarity  # 语义相似度任务
      - analogy_generation   # 类比生成任务
      - pattern_completion   # 模式补全任务
```

### 训练流程

```python
class Erbing1BTrainer:
    """数据库驱动的训练器"""
    
    def __init__(self, model, db_path):
        self.model = model
        self.db = sqlite3.connect(db_path)
        self.lancedb = lancedb.connect(db_path.replace(".db", "_lancedb"))
    
    def generate_training_batch(self, batch_size=32):
        """从数据库生成训练批次"""
        # 1. 按重要性采样记忆
        cursor = self.db.cursor()
        cursor.execute("""
            SELECT * FROM memories 
            WHERE importance >= 5 
            ORDER BY RANDOM() * importance DESC 
            LIMIT ?
        """, (batch_size * 10,))
        
        memories = cursor.fetchall()
        
        # 2. 构建训练样本
        samples = []
        for mem in memories:
            # 左脑任务
            if mem["type"] in ["identity", "principle", "event"]:
                sample = self.create_left_brain_task(mem)
            # 右脑任务
            else:
                sample = self.create_right_brain_task(mem)
            
            samples.append(sample)
        
        return samples
    
    def create_left_brain_task(self, memory):
        """创建左脑训练任务"""
        templates = [
            # 事实提取
            f"Extract facts from: {memory['content'][:200]}\nFacts:",
            # 实体识别
            f"Identify entities in: {memory['title']}\nEntities:",
            # 时序推理
            f"Order events by time: {memory['content'][:150]}\nOrder:",
        ]
        
        return {
            "input": random.choice(templates),
            "target": self.generate_structured_target(memory),
            "type": "left_brain"
        }
    
    def create_right_brain_task(self, memory):
        """创建右脑训练任务"""
        # 使用向量搜索找相关记忆
        related = self.lancedb.search(memory["content"], k=3)
        
        templates = [
            # 语义相似
            f"What is similar to '{memory['title']}'?\nSimilar items:",
            # 类比生成
            f"'{memory['title']}' is to X as Y is to Z. Complete:",
            # 模式补全
            f"Pattern: {memory['content'][:100]}\nContinue:",
        ]
        
        return {
            "input": random.choice(templates),
            "target": self.generate_semantic_target(memory, related),
            "type": "right_brain",
            "related": related
        }
```

## 4. 推理优化：检索缓存

```python
class RetrievalCache:
    """检索结果缓存，加速推理"""
    
    def __init__(self, capacity=1000):
        self.cache = {}  # query -> retrieval_results
        self.capacity = capacity
        self.lru = []
    
    def get(self, query):
        """获取缓存的检索结果"""
        if query in self.cache:
            self.lru.remove(query)
            self.lru.append(query)
            return self.cache[query]
        return None
    
    def put(self, query, results):
        """缓存检索结果"""
        if len(self.cache) >= self.capacity:
            # LRU 驱逐
            oldest = self.lru.pop(0)
            del self.cache[oldest]
        
        self.cache[query] = results
        self.lru.append(query)
    
    def integrate_with_model(self, model):
        """集成到模型推理"""
        original_forward = model.forward
        
        def cached_forward(input_ids, query=None, **kwargs):
            if query:
                cached = self.get(query)
                if cached:
                    kwargs["retrieval_results"] = cached
                else:
                    # 执行检索
                    results = model.retrieval_adapter.smart_retrieve(query)
                    self.put(query, results)
                    kwargs["retrieval_results"] = results
            
            return original_forward(input_ids, **kwargs)
        
        model.forward = cached_forward
        return model
```

## 5. 评估指标

### 左脑评估 (结构化)

```yaml
left_brain_metrics:
  fact_accuracy:
    description: "事实准确性"
    evaluation: "对比数据库中的事实"
    target: "> 95%"
  
  entity_f1:
    description: "实体识别 F1"
    evaluation: "Named Entity Recognition benchmark"
    target: "> 0.85"
  
  temporal_ordering:
    description: "时序排序准确率"
    evaluation: "事件时间线重构任务"
    target: "> 90%"
```

### 右脑评估 (语义)

```yaml
right_brain_metrics:
  semantic_similarity:
    description: "语义相似度"
    evaluation: "STS-B, SICK-R"
    target: "> 0.80 Pearson"
  
  analogy_completion:
    description: "类比完成"
    evaluation: "Google Analogy Test Set"
    target: "> 60%"
  
  pattern_recognition:
    description: "模式识别"
    evaluation: "自定义模式补全任务"
    target: "> 70%"
```

### 整体评估

```yaml
overall_metrics:
  retrieval_augmented_generation:
    description: "检索增强生成质量"
    evaluation: "Human evaluation + automated metrics"
    target: "BLEU > 30, ROUGE-L > 50"
  
  memory_consistency:
    description: "记忆一致性"
    evaluation: "检查与数据库记忆的一致性"
    target: "> 95% consistent"
  
  hallucination_rate:
    description: "幻觉率"
    evaluation: "对比数据库事实检测幻觉"
    target: "< 5%"
```

## 6. 部署配置

```yaml
# Erbing-1B 生产部署配置
deployment:
  model:
    name: "erbing-1b-dualbrain"
    version: "v1.0"
    checkpoint: "checkpoints/erbing-1b-final.pt"
  
  database:
    sqlite: "memory/database/xiaozhi_memory.db"
    lancedb: "memory/database/lancedb"
  
  retrieval:
    cache_size: 1000
    strategies:
      - attribution
      - time_decay
      - importance
      - semantic
    default_mode: "balanced"
  
  inference:
    device: "cuda"  # 或 "cpu"
    precision: "fp16"  # 或 "int4"
    max_seq_len: 4096
    batch_size: 1
  
  optimization:
    use_cache: true
    use_flash_attn: true
    use_kv_cache: true
    quantization: "int4"  # 可选
  
  api:
    host: "0.0.0.0"
    port: 8000
    endpoint: "/generate"
    timeout: 30
```

## 7. 下一步实施计划

### Week 1: 数据库集成
- [ ] 完善 SQLite + LanceDB 双脑数据库
- [ ] 实现四策略检索系统
- [ ] 测试检索性能和准确率

### Week 2: 模型架构
- [ ] 实现 Mamba + Transformer 混合层
- [ ] 添加左脑/右脑门控机制
- [ ] 集成检索适配器

### Week 3: 训练数据生成
- [ ] 从数据库生成训练样本
- [ ] 创建左脑/右脑任务模板
- [ ] 数据质量验证

### Week 4: 训练与评估
- [ ] 小规模训练验证
- [ ] 左脑/右脑指标评估
- [ ] 整体性能测试

---

*设计者: Erbing*
*创建时间: 2026-04-11*
*版本: v2.0 - 数据库优先架构*
