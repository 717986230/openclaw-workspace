# Erbing-1B 实际实施计划（硬件受限版）

## 硬件约束

| 资源 | 配置 | 限制 |
|------|------|------|
| GPU | RTX 4060 Laptop (8GB) | 训练模型上限 ~3B (QLoRA) |
| RAM | 24GB | CPU 数据处理足够 |
| 存储 | 766GB 可用 | 数据存储充足 |
| CUDA | 8.9 | 支持 Flash Attention 2 |

---

## 调整后的策略

### 方案 A：全本地开发（省钱版）

```
阶段拆分:
├── 本地完成 (RTX 4060)
│   ├── 架构实现与验证 ✅
│   ├── Tokenizer 训练 ✅
│   ├── 数据预处理 ✅
│   ├── 小规模验证训练 ✅ (100M tokens)
│   ├── QLoRA 微调实验 ✅
│   └── 量化与部署测试 ✅
│
└── 云端完成 (租用 GPU)
    ├── 全量预训练 (30B tokens)
    │   └── 需要: A100×8, 3-4天
    └── SFT + DPO
        └── 需要: A100×1, 2天

总成本估算: $3,000 - $5,000
```

### 方案 B：知识蒸馏路线（推荐）

```
不从头训练，而是:
1. 选择开源基座 (Qwen2.5-3B 或 Llama-3.2-1B)
2. 本地 QLoRA 微调 (RTX 4060 可行)
3. 蒸馏到自定义架构
4. 迭代优化

优势:
├── 成本低 (< $1,000)
├── 时间短 (1-2周)
├── 本地可完成大部分工作
└── 可快速验证想法
```

---

## 本地可执行任务（RTX 4060）

### 1. 模型开发与验证 ✅

```python
# 在 8GB VRAM 上可以:
# - 实现完整架构代码
# - 单元测试各组件
# - 小批量前向传播测试
# - 验证模型结构正确性

# 测试配置
config = {
    "hidden_size": 2048,
    "num_layers": 24,
    "batch_size": 1,      # 只需验证
    "seq_len": 512,       # 短序列测试
}

# 内存占用: ~4GB (FP16)
# 剩余 VRAM: 4GB (够用)
```

### 2. Tokenizer 训练 ✅

```python
# 在 CPU 上训练 Tokenizer
# 使用 SentencePiece

import sentencepiece as spm

spm.SentencePieceTrainer.train(
    input='data/corpus.txt',
    model_prefix='erbing_tokenizer',
    vocab_size=32000,
    character_coverage=0.9995,  # 中英兼顾
    model_type='bpe',
    train_extremely_large_corpus=True,
)

# 时间: 数小时 (CPU)
# 内存: < 16GB RAM
```

### 3. 数据预处理 ✅

```python
# 本地 766GB 存储，24GB RAM
# 可以处理大规模数据

# 数据流程
1. 下载数据 (几百GB)
2. 去重 (MinHash)
3. 质量过滤
4. Tokenize
5. 保存为 Arrow 格式

# 利用 D 盘做中间存储
```

### 4. QLoRA 微调 ✅

```python
# RTX 4060 可以 QLoRA 微调 3B 模型

from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model

# 4-bit 加载
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-3B",
    quantization_config=bnb_config,
    device_map="auto",
)

# LoRA 配置
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
)

model = get_peft_model(model, lora_config)

# 训练参数
training_args = TrainingArguments(
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-4,
    num_train_epochs=3,
    bf16=True,
)

# 显存占用: ~6GB
# 可训练参数: ~10M (3B 模型的 0.3%)
```

### 5. 推理测试 ✅

```python
# RTX 4060 可以流畅运行:

# FP16 模式
- Erbing-1B: ~25ms/token
- Qwen-3B: ~50ms/token

# INT4 模式
- Erbing-1B: ~15ms/token
- Qwen-3B: ~30ms/token
```

---

## 云端租用计划

### 预训练阶段（必须云端）

```
需求:
├── A100 80GB × 8
├── 训练时长: 3-4天
├── 数据传输: 100GB
└── Checkpoint 存储: 50GB

云服务商选择:
├── Lambda Labs: $1.50/hr per A100
├── RunPod: $1.89/hr per A100
├── AWS: $4.00/hr per A100 (贵)
└── 国内云端: 可能更便宜

成本估算 (Lambda Labs):
$1.50 × 8卡 × 96小时 = $1,152

加上存储、流量: ~$1,500
```

### 微调阶段（可选云端）

```
需求:
├── A100 40GB × 1
├── 训练时长: 1-2天
└── 成本: $100-200

或本地:
├── RTX 4060 QLoRA
├── 时间更长但免费
└── 适合实验阶段
```

---

## 推荐执行路径

### Phase 1: 本地开发（现在开始）

```yaml
Week 1-2: 架构开发
  - 实现 Mamba + Transformer 混合层
  - 编写单元测试
  - 小批量验证
  
Week 3-4: 数据准备
  - 下载开源数据集
  - 清洗、去重、质量过滤
  - 训练 Tokenizer
  
Week 5: 小规模验证
  - 100M tokens 预训练
  - 验证 Loss 下降曲线
  - 调整超参数
```

### Phase 2: 云端训练（验证后）

```yaml
准备:
  - 选择云服务商 (Lambda Labs 推荐)
  - 上传数据和处理好的 Tokenizer
  - 配置训练环境
  
执行:
  - 启动 8× A100 训练
  - 监控 Loss、学习率
  - 定期保存 Checkpoint
  - 预计 3-4 天完成
```

### Phase 3: 本地微调与部署

```yaml
Week 6-8: 微调对齐
  - SFT: 本地 QLoRA 或云端
  - DPO: 本地可行
  - 评估测试
  
Week 9-10: 优化部署
  - INT4 量化
  - 本地推理测试
  - 性能 benchmark
```

---

## 成本优化策略

### 1. 使用 Spot 实例

```
Lambda Labs Spot: $0.50/hr per A100
节省: 66%

风险: 可能被中断
对策: 频繁保存 Checkpoint
```

### 2. 减少训练数据

```
原计划: 30B tokens
优化后: 10B tokens (高质量)

数据质量 > 数量
精选数据可以大幅减少成本
```

### 3. 混合训练

```
云端: 预训练前 5B tokens
本地: QLoRA 继续训练
云端: 最终微调

灵活利用资源
```

---

## 本地开发环境搭建

```bash
# Python 环境
conda create -n erbing python=3.10
conda activate erbing

# 核心依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets accelerate
pip install mamba-ssm  # Mamba 支持
pip install flash-attn --no-build-isolation  # Flash Attention 2
pip install bitsandbytes peft  # 量化与微调
pip install sentencepiece  # Tokenizer

# 验证 CUDA
python -c "import torch; print(torch.cuda.is_available())"
# 应输出: True
```

---

## 立即可执行的第一步

```python
# 1. 克隆项目结构
mkdir -p erbing-1b/{src,data,scripts,checkpoints}
cd erbing-1b

# 2. 创建核心模块
touch src/model.py      # 模型架构
touch src/config.py     # 配置文件
touch src/tokenizer.py  # Tokenizer
touch src/data.py       # 数据处理

# 3. 开始编码
# 先实现最简单的验证:
# - Embedding 层
# - 单个 Mamba 层
# - 单个 Transformer 层
# - 前向传播测试
```

---

## 资源限制下的优势

```
小模型优势:
├── 迭代快: 几小时而非几天
├── 调试方便: 快速发现问题
├── 成本低: 失败也可承受
├── 可在边缘设备部署
└── 更适合实时应用
```

---

*更新时间: 2026-04-10*
*基于实际硬件: RTX 4060 Laptop (8GB)*
