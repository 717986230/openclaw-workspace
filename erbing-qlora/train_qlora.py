#!/usr/bin/env python3
"""
Erbing QLoRA 微调脚本
使用 Qwen2.5-3B-Instruct 作为基座模型
"""
import torch
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Transformers & PEFT
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset

# 配置
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
DATA_PATH = Path(__file__).parent / "data" / "erbing_training_data.json"
OUTPUT_DIR = Path(__file__).parent / "checkpoints" / "erbing-qlora-v1"

class ErbingQLoRATrainer:
    """Erbing QLoRA 训练器"""
    
    def __init__(self):
        self.base_model = BASE_MODEL
        self.data_path = DATA_PATH
        self.output_dir = OUTPUT_DIR
        
        print(f"[INIT] Base model: {self.base_model}")
        print(f"[INIT] Data path: {self.data_path}")
        print(f"[INIT] Output dir: {self.output_dir}")
    
    def load_training_data(self) -> List[Dict]:
        """加载训练数据"""
        print("\n[LOAD] Loading training data...")
        
        data = []
        with open(self.data_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        
        print(f"[LOAD] Loaded {len(data)} samples")
        return data
    
    def prepare_model_and_tokenizer(self):
        """准备模型和 tokenizer"""
        print("\n[MODEL] Loading base model with 4-bit quantization...")
        
        # 4-bit 量化配置
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        # 加载模型
        model = AutoModelForCausalLM.from_pretrained(
            self.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
        )
        
        # 加载 tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model,
            trust_remote_code=True,
        )
        
        # 设置 pad token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # 准备模型用于 k-bit 训练
        model = prepare_model_for_kbit_training(model)
        
        # LoRA 配置
        lora_config = LoraConfig(
            r=16,  # LoRA rank
            lora_alpha=32,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        # 应用 LoRA
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        return model, tokenizer
    
    def format_data(self, data: List[Dict], tokenizer) -> Dataset:
        """格式化数据为训练格式"""
        print("\n[FORMAT] Formatting data...")
        
        # Qwen chat template
        def format_prompt(example):
            if example["input"]:
                prompt = f"<|im_start|>user\n{example['instruction']}\n\n{example['input']}<|im_end|>\n<|im_start|>assistant\n{example['output']}<|im_end|>"
            else:
                prompt = f"<|im_start|>user\n{example['instruction']}<|im_end|>\n<|im_start|>assistant\n{example['output']}<|im_end|>"
            return prompt
        
        # 格式化所有样本
        formatted_data = []
        for item in data:
            prompt = format_prompt(item)
            formatted_data.append({"text": prompt})
        
        # 创建数据集
        dataset = Dataset.from_list(formatted_data)
        
        # Tokenize
        def tokenize_function(examples):
            return tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=2048,
                return_tensors="pt",
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])
        
        print(f"[FORMAT] Formatted {len(tokenized_dataset)} samples")
        
        return tokenized_dataset
    
    def train(self):
        """执行训练"""
        # 加载数据
        data = self.load_training_data()
        
        # 准备模型
        model, tokenizer = self.prepare_model_and_tokenizer()
        
        # 格式化数据
        train_dataset = self.format_data(data, tokenizer)
        
        # 训练参数
        training_args = TrainingArguments(
            output_dir=str(self.output_dir),
            num_train_epochs=3,
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            learning_rate=2e-4,
            weight_decay=0.01,
            logging_dir=str(self.output_dir / "logs"),
            logging_steps=10,
            save_steps=50,
            save_total_limit=3,
            bf16=True,  # 使用 BF16（RTX 4060 支持）
            gradient_checkpointing=True,
            optim="paged_adamw_8bit",
            warmup_steps=10,
            report_to="none",  # 不上传到 wandb
        )
        
        # 数据整理器
        data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
        
        # 训练器
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            data_collator=data_collator,
        )
        
        # 开始训练
        print("\n[TRAIN] Starting training...")
        print(f"[TRAIN] Epochs: {training_args.num_train_epochs}")
        print(f"[TRAIN] Batch size: {training_args.per_device_train_batch_size} x {training_args.gradient_accumulation_steps}")
        print(f"[TRAIN] Learning rate: {training_args.learning_rate}")
        
        trainer.train()
        
        # 保存模型
        print("\n[SAVE] Saving model...")
        trainer.save_model()
        tokenizer.save_pretrained(self.output_dir)
        
        print(f"\n[SUCCESS] Model saved to: {self.output_dir}")
        print(f"[INFO] Load with: model = AutoModelForCausalLM.from_pretrained('{self.output_dir}')")


def main():
    """主函数"""
    print("="*60)
    print("ERBING QLoRA Fine-tuning")
    print("="*60)
    print(f"\n[INFO] RTX 4060 (8GB) optimized")
    print(f"[INFO] Using 4-bit quantization + LoRA")
    print(f"[INFO] Base model: {BASE_MODEL}")
    
    # 检查 CUDA
    if not torch.cuda.is_available():
        print("\n[ERROR] CUDA not available!")
        return
    
    print(f"[INFO] CUDA available: {torch.cuda.get_device_name(0)}")
    print(f"[INFO] GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # 开始训练
    trainer = ErbingQLoRATrainer()
    trainer.train()


if __name__ == "__main__":
    main()
