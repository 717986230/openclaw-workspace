# Erbing QLoRA 微调项目

## 项目简介

将 Erbing 的知识（架构设计、代码、检索策略、数据库记忆）蒸馏到 Qwen2.5-3B 模型中。

## 硬件要求

- **GPU**: RTX 4060 (8GB) ✅ 已适配
- **RAM**: 24GB ✅ 足够
- **存储**: 5GB+ 可用空间

## 项目结构

```
erbing-qlora/
├── data/
│   ├── erbing_training_data.json    # 训练数据（126 samples）
│   └── training_stats.json          # 统计信息
├── checkpoints/
│   └── erbing-qlora-v1/             # 训练输出
├── generate_training_data.py        # 数据生成脚本 ✅
├── train_qlora.py                   # 训练脚本 ✅
├── test_model.py                    # 测试脚本（待创建）
└── README.md                        # 本文件
```

## 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install transformers datasets accelerate
pip install bitsandbytes peft
pip install sentencepiece

# 验证 CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### 2. 生成训练数据（已完成）

```bash
python generate_training_data.py
```

输出：
- 126 个训练样本
- 5 个类别：architecture(8), code(6), retrieval(8), knowledge(100), conversation(4)

### 3. 开始训练

```bash
python train_qlora.py
```

预计时间：
- RTX 4060: ~30-60 分钟
- 显存占用: ~6GB

### 4. 测试模型

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 加载基座模型
base_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-3B-Instruct",
    device_map="auto",
    trust_remote_code=True
)

# 加载 LoRA 权重
model = PeftModel.from_pretrained(
    base_model,
    "./checkpoints/erbing-qlora-v1"
)

# 加载 tokenizer
tokenizer = AutoTokenizer.from_pretrained("./checkpoints/erbing-qlora-v1")

# 测试对话
prompt = "<|im_start|>user\n你是谁？<|im_end|>\n<|im_start|>assistant\n"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

## 训练配置

### 模型配置
- **基座模型**: Qwen/Qwen2.5-3B-Instruct
- **量化**: 4-bit (NF4)
- **LoRA rank**: 16
- **Target modules**: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

### 训练参数
- **Epochs**: 3
- **Batch size**: 1 x 8 (gradient accumulation)
- **Learning rate**: 2e-4
- **Optimizer**: paged_adamw_8bit
- **Precision**: BF16

## 训练数据统计

| 类别 | 数量 | 描述 |
|------|------|------|
| architecture | 8 | 架构设计问答 |
| code | 6 | 代码解释和补全 |
| retrieval | 8 | 检索策略说明 |
| knowledge | 100 | 数据库知识问答 |
| conversation | 4 | 对话式介绍 |
| **总计** | **126** | |

## 预期效果

训练后的模型将能够：

1. **理解 Erbing 架构**
   - 解释左右脑双系统设计
   - 说明四策略检索原理
   - 描述数据库优先架构

2. **生成架构设计**
   - 补全架构代码
   - 改进现有设计
   - 提出优化建议

3. **回答知识问题**
   - 基于 156 条数据库记忆
   - 准确回答相关领域问题

4. **对话式交互**
   - 自我介绍和定位
   - 解释核心能力
   - 说明工作原理

## 进阶使用

### 增量训练

添加新记忆后，重新生成数据并训练：

```bash
# 1. 更新数据库记忆
python generate_training_data.py

# 2. 继续训练（加载之前的 checkpoint）
python train_qlora.py --resume_from_checkpoint ./checkpoints/erbing-qlora-v1/checkpoint-XXX
```

### 合并权重

导出完整模型（非 LoRA）：

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载模型
base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct")
model = PeftModel.from_pretrained(base_model, "./checkpoints/erbing-qlora-v1")

# 合并权重
merged_model = model.merge_and_unload()

# 保存
merged_model.save_pretrained("./checkpoints/erbing-merged")
tokenizer.save_pretrained("./checkpoints/erbing-merged")
```

### 部署推理

```python
# 使用 vLLM 加速
from vllm import LLM, SamplingParams

llm = LLM(model="./checkpoints/erbing-merged")
sampling_params = SamplingParams(temperature=0.7, max_tokens=200)

outputs = llm.generate(["你是谁？"], sampling_params)
print(outputs[0].outputs[0].text)
```

## 故障排除

### CUDA out of memory
```bash
# 减小 batch size
# 在 train_qlora.py 中修改：
per_device_train_batch_size=1,
gradient_accumulation_steps=16,  # 从 8 改为 16
```

### 依赖安装失败
```bash
# Flash Attention（可选）
pip install flash-attn --no-build-isolation

# 或禁用：
# 在 train_qlora.py 中添加：
model.config.use_flash_attention = False
```

## 许可证

本项目仅供学习和研究使用。

## 作者

- Erbing (AI Assistant)
- 创建时间: 2026-04-11
- 版本: v1.0
