# Erbing-1B 模型架构设计

## 设计目标

**核心目标**: 在 1B 参数限制下，达到接近大模型的性能

| 指标 | 目标值 | 参考 |
|------|--------|------|
| 参数量 | 1.0B | 精确控制 |
| 性能目标 | MMLU > 55% | 接近 Llama-7B |
| 推理速度 | < 30ms/token | 优于同级别模型 |
| 上下文长度 | 8K (可扩展32K) | 支持 Long Context |
| 训练成本 | < $50K | 单卡 A100 可训练 |

---

## 架构选择：Hybrid Mamba-Transformer

### 为什么选择混合架构？

```
纯 Transformer 问题:
├── O(n²) 注意力复杂度
├── KV Cache 内存随长度增长
└── 长序列推理慢

纯 Mamba 问题:
├── 复杂推理能力稍弱
├── 需要更多训练数据
└── 生态不够成熟

Hybrid 优势:
├── 前几层用 Mamba (处理长序列)
├── 后几层用 Transformer (复杂推理)
├── 兼顾效率与性能
└── 最佳性价比
```

---

## 详细架构

### 模型配置

```yaml
# Erbing-1B 配置文件
model:
  name: "Erbing-1B"
  architecture: "HybridMambaTransformer"
  
  # 基础参数
  hidden_size: 2048        # 隐藏层维度
  num_layers: 24           # 总层数
  num_attention_heads: 16  # 注意力头数
  head_dim: 128            # 每头维度
  intermediate_size: 5504  # FFN 中间层 (约2.7x)
  vocab_size: 32000        # 词表大小
  
  # 混合架构配置
  mamba_layers: 12         # 前12层用 Mamba
  transformer_layers: 12   # 后12层用 Transformer
  
  # Mamba 特有参数
  mamba:
    d_state: 16            # 状态维度
    d_conv: 4              # 卷积核大小
    expand: 2              # 扩展因子
  
  # Transformer 特有参数  
  transformer:
    attention_type: "grouped_query"  # GQA 提升效率
    num_kv_heads: 4        # KV头数 (GQA)
    use_flash_attn: true   # Flash Attention 2
    rope_theta: 10000      # RoPE 基频
  
  # 位置编码
  position_embedding: "rope"
  max_position_embeddings: 8192
  rope_scaling:
    type: "dynamic"
    factor: 4.0            # 支持32K扩展
  
  # 激活与正则化
  hidden_act: "swiglu"     # SwiGLU 激活
  initializer_range: 0.02
  rms_norm_eps: 1e-5
  
  # 训练优化
  use_cache: true
  tie_word_embeddings: false
```

### 参数量计算

```
Embedding 层:
  vocab_size × hidden_size = 32000 × 2048 = 65.5M

Mamba 层 (×12):
  每个 Mamba 层 ≈ 3 × hidden_size² × expand
  = 3 × 2048 × 2048 × 2 = 25.2M
  总计: 25.2M × 12 = 302M

Transformer 层 (×12):
  QKV 投影: 3 × hidden_size × hidden_size = 12.6M
  输出投影: hidden_size × hidden_size = 4.2M
  FFN (SwiGLU): 3 × hidden_size × intermediate_size = 33.6M
  每层总计: ~50M
  12层总计: 600M

LayerNorm: ~0 (可忽略)

总参数 ≈ 65.5M + 302M + 600M = 967.5M ≈ 1B
```

---

## 核心组件设计

### 1. Mamba Block (状态空间模型)

```python
import torch
import torch.nn as nn
from mamba_ssm import Mamba

class MambaBlock(nn.Module):
    """Mamba 状态空间模型块"""
    
    def __init__(self, hidden_size, d_state=16, d_conv=4, expand=2):
        super().__init__()
        self.mamba = Mamba(
            d_model=hidden_size,
            d_state=d_state,
            d_conv=d_conv,
            expand=expand,
        )
        self.norm = nn.RMSNorm(hidden_size)
        
    def forward(self, x):
        # Pre-norm
        residual = x
        x = self.norm(x)
        x = self.mamba(x)
        return x + residual  # 残差连接
```

### 2. Transformer Block (Grouped Query Attention)

```python
class TransformerBlock(nn.Module):
    """带 GQA 的 Transformer 块"""
    
    def __init__(self, hidden_size, num_heads, num_kv_heads, intermediate_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        
        # Grouped Query Attention
        self.q_proj = nn.Linear(hidden_size, num_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(hidden_size, num_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(hidden_size, num_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(num_heads * self.head_dim, hidden_size, bias=False)
        
        # SwiGLU FFN
        self.gate_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.up_proj = nn.Linear(hidden_size, intermediate_size, bias=False)
        self.down_proj = nn.Linear(intermediate_size, hidden_size, bias=False)
        
        # Norm
        self.input_layernorm = nn.RMSNorm(hidden_size)
        self.post_attention_layernorm = nn.RMSNorm(hidden_size)
        
    def forward(self, x, cos, sin):
        # Attention
        residual = x
        x = self.input_layernorm(x)
        
        q = self.q_proj(x).view(batch, seq_len, self.num_heads, self.head_dim)
        k = self.k_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim)
        v = self.v_proj(x).view(batch, seq_len, self.num_kv_heads, self.head_dim)
        
        # Apply RoPE
        q, k = apply_rotary_pos_emb(q, k, cos, sin)
        
        # GQA: repeat K/V heads
        k = k.repeat_interleave(self.num_heads // self.num_kv_heads, dim=2)
        v = v.repeat_interleave(self.num_heads // self.num_kv_heads, dim=2)
        
        # Flash Attention
        attn_output = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        attn_output = self.o_proj(attn_output)
        
        x = residual + attn_output
        
        # FFN with SwiGLU
        residual = x
        x = self.post_attention_layernorm(x)
        gate = F.silu(self.gate_proj(x))
        up = self.up_proj(x)
        x = self.down_proj(gate * up)
        
        return x + residual
```

### 3. 完整模型架构

```python
class Erbing1B(nn.Module):
    """Erbing-1B 混合架构模型"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Embedding
        self.embed_tokens = nn.Embedding(config.vocab_size, config.hidden_size)
        
        # Layers: Mamba + Transformer
        self.layers = nn.ModuleList()
        
        # 前12层: Mamba
        for i in range(config.mamba_layers):
            self.layers.append(MambaBlock(
                config.hidden_size,
                d_state=config.mamba.d_state,
                d_conv=config.mamba.d_conv,
                expand=config.mamba.expand,
            ))
        
        # 后12层: Transformer
        for i in range(config.transformer_layers):
            self.layers.append(TransformerBlock(
                config.hidden_size,
                config.num_attention_heads,
                config.transformer.num_kv_heads,
                config.intermediate_size,
            ))
        
        # Final Norm
        self.norm = nn.RMSNorm(config.hidden_size)
        
        # Output Head
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)
        
        # RoPE
        self.rotary_emb = RotaryEmbedding(
            dim=config.hidden_size // config.num_attention_heads,
            max_seq_len=config.max_position_embeddings,
            base=config.transformer.rope_theta,
        )
    
    def forward(self, input_ids):
        x = self.embed_tokens(input_ids)
        
        # Get RoPE embeddings
        seq_len = input_ids.shape[1]
        cos, sin = self.rotary_emb(seq_len, x.device)
        
        # Forward through layers
        for layer in self.layers:
            if isinstance(layer, MambaBlock):
                x = layer(x)
            else:
                x = layer(x, cos, sin)
        
        x = self.norm(x)
        logits = self.lm_head(x)
        
        return logits
```

---

## 训练策略

### Phase 1: 预训练 (30B tokens)

```yaml
预训练配置:
  数据量: 30B tokens
  学习率: 3e-4
  批次大小: 2048
  序列长度: 4096
  
  优化器: AdamW (β1=0.9, β2=0.95)
  权重衰减: 0.1
  梯度裁剪: 1.0
  
  训练步数: ~15,000
  预计时间: 3-4天 (A100×8)
  预计成本: $15,000
```

### Phase 2: 指令微调 (1M samples)

```yaml
SFT配置:
  数据: 高质量指令数据
  学习率: 1e-5
  批次大小: 128
  序列长度: 4096
  
  训练步数: ~8,000
  预计时间: 1-2天
  预计成本: $5,000
```

### Phase 3: DPO 对齐 (100K pairs)

```yaml
DPO配置:
  数据: 偏好对比数据
  学习率: 5e-7
  Beta: 0.1
  
  训练步数: ~2,000
  预计时间: 半天
  预计成本: $2,000
```

---

## 推理优化

### 内存占用估算

```
FP16 模型大小: 2GB
INT4 量化后: 0.5GB

推理内存 (FP16):
├── 模型权重: 2GB
├── KV Cache (4K): 512MB (GQA节省)
└── 总计: ~2.5GB

推理内存 (INT4):
├── 模型权重: 0.5GB
├── KV Cache: 512MB
└── 总计: ~1GB (可在手机运行!)
```

### 推理速度

```
A100 GPU:
├── Prefill (512 tokens): ~15ms
├── Decode (per token): ~5ms
└── Throughput: ~200 tokens/s

RTX 4090:
├── Prefill: ~25ms
├── Decode: ~10ms
└── Throughput: ~100 tokens/s

手机 (Snapdragon 8 Gen 3):
├── INT4 量化
├── Decode: ~30-50ms
└── 可用流畅度: 20-30 tokens/s
```

---

## 预期性能

| 基准测试 | 预期分数 | 参考模型 |
|----------|----------|----------|
| MMLU | 52-58% | 接近 Llama-7B |
| GSM8K | 35-40% | 优于同级别 |
| HumanEval | 22-28% | 代码能力 |
| TruthfulQA | 65-70% | 事实准确 |
| WinoGrande | 68-72% | 常识推理 |

---

## 数据需求

### 预训练数据构成

```
总数据量: 30B tokens

构成:
├── 高质量网页 (40%)
│   └── RefinedWeb, Dolma
├── 代码 (25%)
│   └── GitHub stars > 10, 多语言
├── 数学/科学 (15%)
│   └── arXiv, 教科书
├── 书籍 (10%)
│   └── 公版书籍, 教材
└── 问答/对话 (10%)
    └── StackExchange, 高质量QA
```

### 质量优于数量

```
关键原则:
1. 去重 (MinHash + Exact)
2. 过滤低质量 (困惑度 > 100)
3. 语言平衡 (中英各30%, 其他40%)
4. 代码质量 (通过测试的优先)
```

---

## 下一步实施计划

1. **Week 1-2**: 实现模型架构
   - 编写 Mamba + Transformer 混合层
   - 集成 RoPE、Flash Attention
   - 单元测试

2. **Week 3-4**: 数据准备
   - 下载并清洗预训练数据
   - 构建 Tokenizer (SentencePiece)
   - 数据质量验证

3. **Week 5-8**: 预训练
   - 小规模验证 (1B tokens)
   - 全量预训练 (30B tokens)
   - Checkpoint 管理

4. **Week 9-10**: 微调对齐
   - SFT 指令微调
   - DPO 偏好对齐
   - 评估测试

5. **Week 11-12**: 优化部署
   - INT4 量化
   - 推理优化
   - 文档发布

---

## 技术栈

```yaml
训练框架:
  - PyTorch 2.1+
  - transformers
  - mamba-ssm
  - flash-attn

分布式训练:
  - DeepSpeed ZeRO-2
  - 或 FSDP

量化部署:
  - bitsandbytes (训练量化)
  - llama.cpp (推理部署)
  - vLLM (高效服务)

评估:
  - lm-evaluation-harness
  - evalplus (代码)
```

---

*设计者: 二饼 🦞*
*创建时间: 2026-04-10*
*版本: v1.0*
