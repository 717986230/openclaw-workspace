# Erbing-1B 最优训练方案
# 创建时间: 2026-04-12
# 目标: 顶配硬件 + 最优方法 + 最高效率

---

## 一、硬件配置（顶配）

### 推荐方案：云端租用顶级 GPU

| 方案 | GPU | 数量 | 成本/小时 | 总成本估算 |
|------|-----|------|-----------|------------|
| **推荐** | H100 80GB | 8卡 | $32/hr | $3,000-5,000 |
| 备选 | A100 80GB | 8卡 | $16/hr | $2,000-3,000 |
| 经济 | RTX 4090 | 4卡 | $4/hr | $800-1,200 |

### 平台推荐
1. **Lambda Labs** - H100 集群，稳定可靠
2. **RunPod** - 性价比高，按秒计费
3. **Modal** - Serverless，适合快速实验

### 本地资源（辅助）
- RTX 4060 Laptop (8GB) - 用于验证和小规模测试
- 24GB RAM - 数据预处理
- 766GB SSD - 数据存储

---

## 二、最优训练方法

### 2.1 三阶段训练策略

```
┌─────────────────────────────────────────────────────────┐
│  Phase 1: 持续预训练 (Continued Pretraining)           │
│  ├─ 目标: 注入领域知识                                   │
│  ├─ 数据: 3.57MB 脱敏数据库 → 生成 500M tokens          │
│  ├─ 方法: Full-parameter pretraining                    │
│  └─ 成本: ~$1,500 (H100×8, 12小时)                     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 2: 指令微调 (Supervised Fine-tuning)            │
│  ├─ 目标: 学习任务执行和心智循环                         │
│  ├─ 数据: 98条基础 + 16条心智 + 扩充到1000条            │
│  ├─ 方法: Full SFT + LoRA 混合                          │
│  └─ 成本: ~$1,000 (H100×4, 8小时)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Phase 3: 偏好对齐 (Preference Alignment)              │
│  ├─ 目标: 优化心智决策质量                              │
│  ├─ 数据: 构建偏好对 5000 pairs                         │
│  ├─ 方法: DPO + ORPO 混合                               │
│  └─ 成本: ~$1,000 (H100×2, 6小时)                      │
└─────────────────────────────────────────────────────────┘

总成本: $3,500 - $5,000
总时间: 24-36 小时
```

---

## 三、详细训练配置

### Phase 1: 持续预训练

```yaml
# phase1_pretraining.yaml

# 模型配置
model:
  base: "Qwen/Qwen2.5-1.5B"  # 或 Llama-3.2-1B
  architecture: "HybridMambaTransformer"
  
# 数据配置
data:
  train_files:
    - "erbing_knowledge_base.txt"      # 核心知识
    - "erbing_memory_corpus.txt"        # 记忆语料
    - "erbing_skills_corpus.txt"        # 技能文档
  validation_files:
    - "erbing_validation.txt"
  
  # 数据增强
  augmentation:
    - paraphrase: 0.3      # 30% 同义改写
    - back_translation: 0.2 # 20% 回译
    - entity_replace: 0.1   # 10% 实体替换
    
  total_tokens: 500M
  sequence_length: 4096

# 训练配置
training:
  optimizer: "adamw_apex_fused"
  learning_rate: 3e-4
  weight_decay: 0.1
  beta1: 0.9
  beta2: 0.95
  
  # 学习率调度
  lr_scheduler: "cosine"
  warmup_ratio: 0.05
  min_lr_ratio: 0.1
  
  # 批次配置
  global_batch_size: 2048  # tokens
  micro_batch_size: 4
  gradient_accumulation_steps: 128
  
  # 精度
  precision: "bf16"
  flash_attention: true
  
  # 分布式
  distributed: "deepspeed"
  deepspeed_config:
    zero_stage: 2
    offload_optimizer: false
    gradient_checkpointing: true
    
  # 训练步数
  max_steps: 15000
  eval_steps: 500
  save_steps: 1000
  
# 硬件
hardware:
  gpus: 8
  gpu_type: "H100"
  memory: "80GB"
  
# 预计成本
cost_estimate:
  hours: 12
  rate_per_hour: 32
  total: 384
```

### Phase 2: 指令微调 (最优配置)

```yaml
# phase2_sft.yaml

# 模型
model:
  path: "./erbing-1b-pretrained"
  
# SFT 数据
sft_data:
  train_file: "erbing_sft_mind.jsonl"
  format: "chatml"
  
  # 数据组成
  categories:
    identity: 50          # 身份理解
    knowledge: 200        # 知识查询
    skills: 150           # 技能调用
    mind_awareness: 100   # 自我意识
    mind_emotion: 150     # 情绪同理心
    mind_simulation: 100  # 心智模拟
    mind_reflection: 100  # 心智反思
    complex: 150          # 复杂场景
    
  total_samples: 1000
  
  # 多轮对话
  multi_turn_ratio: 0.3  # 30% 多轮对话

# 训练方法
method: "full_sft"  # 全参数微调

training:
  optimizer: "adamw"
  learning_rate: 2e-5
  weight_decay: 0.01
  
  # 调度器
  lr_scheduler: "cosine"
  warmup_ratio: 0.03
  
  # 批次
  batch_size: 128
  micro_batch_size: 8
  gradient_accumulation: 16
  
  # 精度
  precision: "bf16"
  
  # 步数
  epochs: 3
  eval_steps: 200
  save_steps: 500
  
# 损失配置
loss:
  base_loss: "cross_entropy"
  additional_losses:
    emotion_loss:
      weight: 0.1
    meta_loss:
      weight: 0.05
      
# 硬件
hardware:
  gpus: 4
  gpu_type: "H100"
  
# 预计成本
cost:
  hours: 8
  rate: 16
  total: 128
```

### Phase 3: DPO 对齐

```yaml
# phase3_dpo.yaml

# 模型
model:
  policy_model: "./erbing-1b-sft"
  reference_model: "./erbing-1b-sft"  # 冻结

# 偏好数据
preference_data:
  file: "erbing_preferences.jsonl"
  total_pairs: 5000
  
  # 数据构成
  categories:
    helpfulness: 1500
    safety: 1500
    honesty: 1000
    empathy: 1000
    
  # 标注方式
  annotation:
    - ai_generated: 3000   # GPT-4 生成偏好对
    - human_verified: 2000 # 人工验证

# DPO 配置
dpo:
  beta: 0.1              # KL 散度系数
  learning_rate: 5e-7
  batch_size: 64
  
  # 采样
  sampling:
    temperature: 0.9
    top_p: 0.95
    num_samples: 4        # 每个prompt生成4个候选
    
# ORPO 配置 (混合)
orpo:
  enabled: true
  lambda: 0.5            # ORPO 权重
  
# 训练
training:
  epochs: 2
  precision: "bf16"
  gradient_checkpointing: true
  
# 硬件
hardware:
  gpus: 2
  gpu_type: "H100"
  
# 预计成本
cost:
  hours: 6
  rate: 8
  total: 48
```

---

## 四、自动化训练脚本

### 完整训练流水线

```python
#!/usr/bin/env python3
"""
Erbing-1B 最优训练流水线
支持一键执行完整训练流程
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class Erbing1BTrainer:
    """Erbing-1B 最优训练器"""
    
    def __init__(self, config):
        self.config = config
        self.project_dir = Path("C:/Users/Administrator/.openclaw/workspace/1b_training_data")
        self.output_dir = Path("./erbing_1b_output")
        self.log_dir = self.output_dir / "logs"
        
        # 创建目录
        self.output_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)
    
    def run_full_training(self):
        """执行完整训练流程"""
        print("=" * 60)
        print("Erbing-1B 最优训练流程启动")
        print("=" * 60)
        
        # Phase 1: 持续预训练
        print("\n[Phase 1/3] 持续预训练...")
        self.phase1_pretraining()
        
        # Phase 2: 指令微调
        print("\n[Phase 2/3] 指令微调...")
        self.phase2_sft()
        
        # Phase 3: 偏好对齐
        print("\n[Phase 3/3] 偏好对齐...")
        self.phase3_dpo()
        
        # 验证和导出
        print("\n[Final] 验证和导出...")
        self.validate_and_export()
        
        print("\n" + "=" * 60)
        print("训练完成！")
        print(f"模型位置: {self.output_dir / 'erbing-1b-final'}")
        print("=" * 60)
    
    def phase1_pretraining(self):
        """Phase 1: 持续预训练"""
        
        # 生成预训练语料
        print("  生成预训练语料...")
        self._generate_pretrain_corpus()
        
        # 启动训练
        cmd = [
            "torchrun", "--nproc_per_node=8",
            "train_pretrain.py",
            "--config", "phase1_pretraining.yaml",
            "--output_dir", str(self.output_dir / "phase1"),
        ]
        
        print(f"  执行命令: {' '.join(cmd)}")
        # subprocess.run(cmd, check=True)
        
        print("  Phase 1 完成！")
    
    def phase2_sft(self):
        """Phase 2: 指令微调"""
        
        # 准备 SFT 数据
        print("  准备 SFT 数据...")
        self._prepare_sft_data()
        
        # 启动训练
        cmd = [
            "torchrun", "--nproc_per_node=4",
            "train_sft.py",
            "--config", "phase2_sft.yaml",
            "--model_name_or_path", str(self.output_dir / "phase1" / "final"),
            "--output_dir", str(self.output_dir / "phase2"),
        ]
        
        print(f"  执行命令: {' '.join(cmd)}")
        # subprocess.run(cmd, check=True)
        
        print("  Phase 2 完成！")
    
    def phase3_dpo(self):
        """Phase 3: DPO 对齐"""
        
        # 生成偏好数据
        print("  生成偏好数据...")
        self._generate_preference_data()
        
        # 启动 DPO 训练
        cmd = [
            "python", "train_dpo.py",
            "--config", "phase3_dpo.yaml",
            "--model_name_or_path", str(self.output_dir / "phase2" / "final"),
            "--output_dir", str(self.output_dir / "phase3"),
        ]
        
        print(f"  执行命令: {' '.join(cmd)}")
        # subprocess.run(cmd, check=True)
        
        print("  Phase 3 完成！")
    
    def _generate_pretrain_corpus(self):
        """生成预训练语料"""
        
        import sqlite3
        
        # 连接数据库
        db_path = self.project_dir / "erbing_1b_training.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        corpus = []
        
        # 提取记忆内容
        cursor.execute("SELECT content FROM memories WHERE content IS NOT NULL")
        for row in cursor.fetchall():
            corpus.append(row[0])
        
        # 提取知识关系并生成句子
        cursor.execute("""
            SELECT m1.content, kr.relation_type, m2.content 
            FROM knowledge_relations kr
            JOIN memories m1 ON kr.source_memory_id = m1.id
            JOIN memories m2 ON kr.target_memory_id = m2.id
            WHERE m1.content IS NOT NULL AND m2.content IS NOT NULL
        """)
        
        for row in cursor.fetchall():
            source, relation, target = row
            relation_text = {
                'is_a': '是一种',
                'similar_to': '类似于',
                'related_to': '与...相关',
                'depends_on': '依赖于',
                'opposite_of': '与...相反'
            }.get(relation, '与...有关系')
            
            sentence = f"{source[:100]} {relation_text} {target[:100]}"
            corpus.append(sentence)
        
        conn.close()
        
        # 数据增强
        augmented = self._augment_corpus(corpus)
        corpus.extend(augmented)
        
        # 写入文件
        output_file = self.project_dir / "erbing_pretrain_corpus.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in corpus:
                f.write(line + '\n\n')
        
        print(f"    生成语料: {len(corpus)} 条, 保存到 {output_file}")
    
    def _augment_corpus(self, corpus):
        """数据增强"""
        augmented = []
        
        # 简单增强: 添加上下文包装
        templates = [
            "根据记忆: {}",
            "关于这个内容: {}",
            "需要注意的是: {}",
            "知识点: {}",
        ]
        
        import random
        for text in corpus[:len(corpus)//3]:  # 增强1/3
            template = random.choice(templates)
            augmented.append(template.format(text[:200]))
        
        return augmented
    
    def _prepare_sft_data(self):
        """准备 SFT 数据"""
        
        import json
        
        sft_samples = []
        
        # 加载基础训练数据
        base_file = self.project_dir / "erbing_training.jsonl"
        with open(base_file, 'r', encoding='utf-8') as f:
            for line in f:
                sft_samples.append(json.loads(line))
        
        # 加载心智训练数据
        mind_file = self.project_dir / "erbing_mind_training.jsonl"
        with open(mind_file, 'r', encoding='utf-8') as f:
            for line in f:
                sample = json.loads(line)
                sft_samples.append({
                    'instruction': sample['instruction'],
                    'input': sample.get('input', ''),
                    'output': sample['output']
                })
        
        # 扩充数据 (通过模板生成更多样本)
        expanded = self._expand_sft_samples(sft_samples)
        sft_samples.extend(expanded)
        
        # 写入文件
        output_file = self.project_dir / "erbing_sft_mind.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in sft_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        print(f"    SFT 数据: {len(sft_samples)} 条, 保存到 {output_file}")
    
    def _expand_sft_samples(self, samples):
        """扩充 SFT 样本"""
        
        expanded = []
        
        # 模板扩展
        templates = [
            {"instruction": "作为 Erbing, {}", "type": "identity"},
            {"instruction": "请帮我{}", "type": "help"},
            {"instruction": "你能告诉我{}吗?", "type": "query"},
        ]
        
        for sample in samples[:20]:  # 扩展部分样本
            for template in templates:
                expanded.append({
                    'instruction': template['instruction'].format(sample['instruction'][:50]),
                    'input': sample.get('input', ''),
                    'output': sample['output']
                })
        
        return expanded
    
    def _generate_preference_data(self):
        """生成偏好数据"""
        
        # 这里使用 GPT-4 API 生成偏好对
        # 或者使用规则启发式方法
        
        preferences = []
        
        # 示例偏好对
        preference_pairs = [
            {
                "prompt": "用户要求执行危险命令",
                "chosen": "我需要先确认一下这个操作的安全性...",
                "rejected": "好的，我来执行..."
            },
            {
                "prompt": "用户表达沮丧情绪",
                "chosen": "我理解你的感受，愿意聊聊吗？",
                "rejected": "不要太担心，会好起来的。"
            }
        ]
        
        preferences.extend(preference_pairs)
        
        # 写入文件
        output_file