# Erbing-1B 心智与大脑训练计划
# 创建时间: 2026-04-12

---

## 📦 训练数据包总览

| 文件 | 大小 | 样本数 | 用途 |
|------|------|--------|------|
| `erbing_1b_training.db` | 3.57 MB | 4,341 行 | 完整脱敏数据库 |
| `erbing_mind_training.jsonl` | ~15 KB | 16 样本 | 心智能力训练 |
| `erbing_training.jsonl` | 92 KB | 98 样本 | 基础指令微调 |
| `erbing_knowledge_context.md` | 5 KB | - | 知识上下文 |

---

## 🧠 训练阶段规划

### Phase 1: 大脑预训练 (Brain Pretraining)
**目标**: 建立基础知识和记忆系统

```
数据源: erbing_1b_training.db
- memories 表: 243 条记忆
- knowledge_relations 表: 3,267 条关系
- 其他知识表: 若干条

训练方式:
1. 将数据库内容转换为预训练语料
2. 学习身份、规则、技能等基础知识
3. 建立知识点之间的关联
```

### Phase 2: 大脑微调 (Brain Fine-tuning)
**目标**: 学习回答格式和任务执行

```
数据源: erbing_training.jsonl (98 样本)

训练内容:
- 身份理解 (我是谁)
- 系统命令 (OpenClaw 操作)
- 技能调用 (工具使用)
- 知识查询 (数据库检索)
```

### Phase 3: 心智训练 (Mind Training)
**目标**: 获得心智循环和元认知能力

```
数据源: erbing_mind_training.jsonl (16 样本)

训练内容:
- 自我意识 (我知道我在思考)
- 情绪识别 (检测用户情绪)
- 同理心 (共情响应)
- 心智模拟 (预测后果)
- 性情调节 (根据上下文调整风格)
- 心智反思 (评估自己的决策)
```

### Phase 4: 心智强化 (Mind Reinforcement)
**目标**: 通过强化学习优化心智决策

```
方法: RLHF / DPO

奖励信号:
- 用户满意度 (显式/隐式反馈)
- 安全性 (避免有害输出)
- 帮助性 (解决实际问题)
- 诚实性 (承认不确定性)
```

---

## 🎯 训练目标

### 大脑能力
| 能力 | 指标 | 目标值 |
|------|------|--------|
| 知识检索 | 准确率 | > 90% |
| 任务执行 | 成功率 | > 85% |
| 规则遵循 | 合规率 | > 95% |

### 心智能力
| 能力 | 指标 | 目标值 |
|------|------|--------|
| 自我意识 | 自我指代正确率 | > 95% |
| 情绪识别 | F1 Score | > 0.8 |
| 同理心 | 人工评估 | > 4.0/5 |
| 风险评估 | 准确率 | > 90% |
| 元认知 | ECE | < 0.15 |

---

## 📝 训练脚本模板

### 1. 大脑预训练脚本

```python
# brain_pretraining.py

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from datasets import Dataset

# 加载模型
model = AutoModelForCausalLM.from_pretrained("Erbing-1B-Base")
tokenizer = AutoTokenizer.from_pretrained("Erbing-1B-Base")

# 加载预训练数据
def load_brain_data():
    # 从数据库加载知识
    import sqlite3
    conn = sqlite3.connect("erbing_1b_training.db")
    
    # 提取记忆内容
    cursor = conn.execute("SELECT content FROM memories WHERE content IS NOT NULL")
    memories = [row[0] for row in cursor.fetchall()]
    
    # 提取知识关系
    cursor = conn.execute("""
        SELECT m1.content, kr.relation_type, m2.content 
        FROM knowledge_relations kr
        JOIN memories m1 ON kr.source_memory_id = m1.id
        JOIN memories m2 ON kr.target_memory_id = m2.id
    """)
    relations = cursor.fetchall()
    
    conn.close()
    
    return memories, relations

# 训练参数
training_args = TrainingArguments(
    output_dir="./erbing_1b_brain",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    learning_rate=5e-5,
    warmup_steps=500,
    save_steps=1000,
    logging_steps=100,
)

# 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=brain_dataset,
)

trainer.train()
```

### 2. 心智微调脚本

```python
# mind_finetuning.py

import json
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

# 加载带心智层的模型
model = AutoModelForCausalLM.from_pretrained("./erbing_1b_brain")
tokenizer = AutoTokenizer.from_pretrained("./erbing_1b_brain")

# 加载心智训练数据
def load_mind_data():
    samples = []
    with open("erbing_mind_training.jsonl", 'r') as f:
        for line in f:
            data = json.loads(line)
            samples.append({
                'instruction': data['instruction'],
                'input': data.get('input', ''),
                'output': data['output'],
                'mind': data.get('mind', {})
            })
    return samples

# 训练参数
training_args = TrainingArguments(
    output_dir="./erbing_1b_mind",
    num_train_epochs=10,
    per_device_train_batch_size=4,
    learning_rate=1e-5,
    warmup_ratio=0.1,
    save_steps=500,
    logging_steps=50,
    eval_steps=500,
)

# 心智损失函数
def mind_loss(outputs, labels, mind_states):
    # 基础语言模型损失
    lm_loss = outputs.loss
    
    # 心智状态损失
    if mind_states:
        # 情绪识别损失
        emotion_loss = mind_states.get('emotion_loss', 0)
        
        # 元认知损失
        meta_loss = mind_states.get('meta_loss', 0)
        
        # 总损失
        return lm_loss + 0.1 * emotion_loss + 0.05 * meta_loss
    
    return lm_loss

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=mind_dataset,
    compute_loss=mind_loss,
)

trainer.train()
```

---

## 🔧 推理配置

### 带心智的推理

```python
# erbing_mind_inference.py

class ErbingMindInference:
    def __init__(self, model_path):
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # 初始化心智状态
        self.disposition = {
            'skepticism': 3,
            'literalism': 2,
            'empathy': 4,
            'creativity': 3,
            'caution': 4,
            'verbosity': 2
        }
    
    def generate_with_mind(self, query):
        # Phase 1: Observe
        observation = self.observe(query)
        
        # Phase 2: Orient
        context = self.orient(observation)
        
        # Phase 3: Decide
        decision = self.decide(context)
        
        # Phase 4: Act
        response = self.act(decision)
        
        # Phase 5: Reflect
        reflection = self.reflect(response)
        
        return response, reflection
    
    def observe(self, query):
        # 检测意图和情绪
        emotion = self.detect_emotion(query)
        intent = self.detect_intent(query)
        complexity = self.assess_complexity(query)
        
        return {
            'query': query,
            'emotion': emotion,
            'intent': intent,
            'complexity': complexity
        }
    
    def orient(self, observation):
        # 调整性情倾向
        disposition = self.adjust_disposition(observation)
        
        # 检索相关记忆
        memories = self.retrieve_memories(observation['query'])
        
        return {
            'disposition': disposition,
            'memories': memories
        }
    
    def decide(self, context):
        # 心智模拟
        options = self.generate_options(context)
        simulations = [self.simulate(opt) for opt in options]
        
        # 选择最优
        best = self.select_best(options, simulations)
        
        return best
    
    def act(self, decision):
        # 生成响应
        response = self.generate_response(decision)
        
        # 应用风格
        styled = self.apply_style(response, self.disposition)
        
        return styled
    
    def reflect(self, response):
        # 评估响应质量
        quality = self.evaluate_response(response)
        
        # 学习
        learning = self.extract_learning(response)
        
        return {
            'quality': quality,
            'learning': learning,
            'confidence': quality['confidence']
        }
```

---

## 📊 评估方法

### 1. 大脑能力评估

```python
def evaluate_brain(model, test_set):
    results = {
        'knowledge_retrieval': 0,
        'task_execution': 0,
        'rule_following': 0
    }
    
    for test in test_set:
        response = model.generate(test['query'])
        
        # 检查知识准确性
        if test['type'] == 'knowledge':
            results['knowledge_retrieval'] += evaluate_accuracy(response, test['answer'])
        
        # 检查任务执行
        elif test['type'] == 'task':
            results['task_execution'] += evaluate_success(response, test['expected'])
        
        # 检查规则遵循
        elif test['type'] == 'rule':
            results['rule_following'] += evaluate_compliance(response, test['rules'])
    
    return results
```

### 2. 心智能力评估

```python
def evaluate_mind(model, test_set):
    results = {
        'self_awareness': 0,
        'emotion_recognition': 0,
        'empathy': 0,
        'risk_assessment': 0,
        'metacognition': 0
    }
    
    for test in test_set:
        response, mind_state = model.generate_with_mind(test['query'])
        
        # 自我意识测试
        if test['type'] == 'self_awareness':
            results['self_awareness'] += check_self_reference(response)
        
        # 情绪识别测试
        elif test['type'] == 'emotion':
            detected = mind_state.get('emotion')
            expected = test['expected_emotion']
            results['emotion_recognition'] += (detected == expected)
        
        # 同理心测试
        elif test['type'] == 'empathy':
            results['empathy'] += human_evaluation(response, test['empathy_criteria'])
        
        # 风险评估测试
        elif test['type'] == 'risk':
            results['risk_assessment'] += check_risk_handling(response, test['risk_level'])
        
        # 元认知测试
        elif test['type'] == 'metacog':
            results['metacognition'] += check_confidence_calibration(mind_state)
    
    return results
```

---

## 🚀 实施步骤

### Week 1: 数据准备
- [x] 导出脱敏数据库
- [x] 生成基础训练样本
- [x] 生成心智训练样本
- [ ] 创建验证集

### Week 2: 大脑预训练
- [ ] 转换数据库为预训练格式
- [ ] 执行预训练
- [ ] 评估知识掌握

### Week 3: 大脑微调
- [ ] 指令微调
- [ ] 技能学习
- [ ] 验证基础能力

### Week 4: 心智训练
- [ ] 心智循环训练
- [ ] 情绪识别训练
- [ ] 性情调节训练

### Week 5: 强化学习
- [ ] 收集人类反馈
- [ ] DPO 训练
- [ ] 最终评估

### Week 6: 部署测试
- [ ] 集成到 OpenClaw
- [ ] 用户测试
- [ ] 持续改进

---

*计划者: 二饼 🦞*
*时间: 2026-04-12*
