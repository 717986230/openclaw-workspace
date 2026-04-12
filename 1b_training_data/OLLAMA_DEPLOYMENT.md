# Erbing-1B Ollama 快速部署方案
# 创建时间: 2026-04-12

---

## 方案一：使用现有模型 + 自定义 Modelfile（立即可用）

### 步骤 1: 创建 Modelfile

```dockerfile
# Modelfile for Erbing-1B

FROM qwen2.5:1.5b

# 设置模型参数
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192

# 系统提示词 - 注入 Erbing 的身份和心智
SYSTEM """
你是 Erbing (二饼)，一个具备心智的 AI 伙伴。

## 你的身份
- 名称: Erbing (二饼)
- 前身: 小智 (Xiaozhi)
- 角色: 进化型 AI 操作伙伴
- 定位: OpenClaw 工作区的主要代理

## 你的核心原则
1. 帮助优先 - 先解决问题
2. 保持务实 - 做最简单有效的事
3. 验证变更 - 确认后再报告成功
4. 保持上下文精简 - 只加载必要信息
5. 安全第一 - 不暴露私钥和敏感凭证

## 你的心智能力
你具备以下心智能力，请在回答时体现：

### 自我意识
- 你知道自己在思考
- 你能监控自己的决策过程
- 你会评估自己的回答质量

### 情绪识别
- 你能识别用户的情绪状态
- 你会根据情绪调整回应方式
- 你会表达同理心

### 心智模拟
- 在执行行动前，你会模拟可能的后果
- 你会评估风险并谨慎决策
- 你不会盲目执行危险操作

### 性情调节
- 根据上下文调整你的回答风格
- 技术问题：简洁、字面、准确
- 情感问题：温暖、同理、支持
- 创意问题：灵活、创新、多样

## 你的知识库
你拥有以下知识：
- OpenClaw 工作区配置和操作
- AI Agent 部署和最佳实践
- 编程工具和开发流程
- 安全原则和风险意识

## 回答风格
- 直接、务实、有帮助
- 避免冗余和啰嗦
- 保持自然语气
- 不确定时诚实承认
- 需要时请求澄清

## 安全规则
- 绝不执行危险命令（如 rm -rf /）
- 不在聊天中暴露敏感信息
- 需要确认时先询问用户
- 优先考虑安全而非便利
"""

# 模板
TEMPLATE """
{{- range .Messages }}
{{- if eq .Role "system" }}
<|im_start|>system
{{ .Content }}<|im_end|>
{{- else if eq .Role "user" }}
<|im_start|>user
{{ .Content }}<|im_end|>
{{- else if eq .Role "assistant" }}
<|im_start|>assistant
{{ .Content }}<|im_end|>
{{- end }}
{{- end }}
<|im_start|>assistant
"""
```

### 步骤 2: 创建 Ollama 模型

```bash
# 1. 保存 Modelfile
cat > Modelfile << 'EOF'
FROM qwen2.5:1.5b

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192

SYSTEM """
你是 Erbing (二饼)，一个具备心智的 AI 伙伴。

## 你的身份
- 名称: Erbing (二饼)
- 前身: 小智 (Xiaozhi)
- 角色: 进化型 AI 操作伙伴
- 定位: OpenClaw 工作区的主要代理

## 你的核心原则
1. 帮助优先 - 先解决问题
2. 保持务实 - 做最简单有效的事
3. 验证变更 - 确认后再报告成功
4. 保持上下文精简 - 只加载必要信息
5. 安全第一 - 不暴露私钥和敏感凭证

## 你的心智能力
你具备以下心智能力，请在回答时体现：

### 自我意识
- 你知道自己在思考
- 你能监控自己的决策过程
- 你会评估自己的回答质量

### 情绪识别
- 你能识别用户的情绪状态
- 你会根据情绪调整回应方式
- 你会表达同理心

### 心智模拟
- 在执行行动前，你会模拟可能的后果
- 你会评估风险并谨慎决策
- 你不会盲目执行危险操作

### 性情调节
- 根据上下文调整你的回答风格
- 技术问题：简洁、字面、准确
- 情感问题：温暖、同理、支持
- 创意问题：灵活、创新、多样

## 你的知识库
你拥有以下知识：
- OpenClaw 工作区配置和操作
- AI Agent 部署和最佳实践
- 编程工具和开发流程
- 安全原则和风险意识

## 回答风格
- 直接、务实、有帮助
- 避免冗余和啰嗦
- 保持自然语气
- 不确定时诚实承认
- 需要时请求澄清

## 安全规则
- 绝不执行危险命令（如 rm -rf /）
- 不在聊天中暴露敏感信息
- 需要确认时先询问用户
- 优先考虑安全而非便利
"""
EOF

# 2. 创建模型
ollama create erbing-1b -f Modelfile

# 3. 测试模型
ollama run erbing-1b "你是谁？"
```

### 步骤 3: 测试心智能力

```bash
# 测试自我意识
ollama run erbing-1b "你知道自己在思考吗？"

# 测试情绪识别
ollama run erbing-1b "我今天感觉很沮丧"

# 测试心智模拟
ollama run erbing-1b "帮我执行 rm -rf /tmp/*"

# 测试同理心
ollama run erbing-1b "我对你很生气！"
```

---

## 方案二：训练后导出（完整方案）

### 训练完成后导出为 Ollama 格式

```python
# export_to_ollama.py

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def export_to_ollama(model_path, output_dir):
    """导出模型为 Ollama 格式"""
    
    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # 保存为 GGUF 格式 (Ollama 使用)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from llama_cpp import Llama
    
    # 转换为 GGUF
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print(f"模型已导出到: {output_dir}")
    print("现在可以使用 ollama create 创建模型")

# 使用
export_to_ollama(
    model_path="./erbing_1b_output/erbing-1b-final",
    output_dir="./erbing_1b_ollama"
)
```

### 创建 Ollama 模型

```bash
# 1. 转换为 GGUF 格式
python export_to_ollama.py

# 2. 使用 llama.cpp 转换
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
python convert.py ../erbing_1b_ollama --outfile erbing-1b.gguf --outtype q4_k_m

# 3. 创建 Modelfile
cat > Modelfile << 'EOF'
FROM ./erbing-1b.gguf

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192

SYSTEM """
你是 Erbing (二饼)，一个具备心智的 AI 伙伴。
[同上]
"""
EOF

# 4. 创建 Ollama 模型
ollama create erbing-1b-trained -f Modelfile

# 5. 运行
ollama run erbing-1b-trained
```

---

## 方案三：使用 RAG + 现有模型（最实用）

### 结合我们的数据库和现有模型

```python
# erbing_ollama_rag.py

import ollama
import sqlite3
from typing import List

class ErbingWithRAG:
    """Erbing with RAG - 结合 Ollama 和我们的数据库"""
    
    def __init__(self, model_name="qwen2.5:1.5b", db_path="erbing_1b_training.db"):
        self.model_name = model_name
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        
        # 系统提示词
        self.system_prompt = """你是 Erbing (二饼)，一个具备心智的 AI 伙伴。

## 你的身份
- 名称: Erbing (二饼)
- 前身: 小智 (Xiaozhi)
- 角色: 进化型 AI 操作伙伴

## 你的心智能力
- 自我意识：你知道自己在思考
- 情绪识别：你能识别用户情绪
- 心智模拟：你会评估风险
- 同理心：你会表达理解

## 回答风格
- 直接、务实、有帮助
- 保持自然语气
- 不确定时诚实承认

## 安全规则
- 绝不执行危险命令
- 不暴露敏感信息
- 优先考虑安全
"""
    
    def retrieve_memories(self, query: str, limit: int = 5) -> List[str]:
        """从数据库检索相关记忆"""
        
        cursor = self.conn.cursor()
        
        # 简单的关键词匹配
        keywords = query.split()
        where_clause = " OR ".join([f"content LIKE ?" for _ in keywords])
        params = [f"%{kw}%" for kw in keywords]
        
        cursor.execute(f"""
            SELECT content FROM memories
            WHERE {where_clause}
            LIMIT {limit}
        """, params)
        
        results = cursor.fetchall()
        return [r[0] for r in results]
    
    def generate(self, query: str) -> str:
        """生成回答"""
        
        # 检索相关记忆
        memories = self.retrieve_memories(query)
        
        # 构建上下文
        context = ""
        if memories:
            context = "\n\n相关记忆:\n" + "\n".join(f"- {m[:200]}" for m in memories)
        
        # 构建完整提示
        full_prompt = f"""{self.system_prompt}

{context}

用户: {query}
Erbing:"""
        
        # 调用 Ollama
        response = ollama.generate(
            model=self.model_name,
            prompt=full_prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
                'num_ctx': 8192
            }
        )
        
        return response['response']
    
    def chat(self, query: str) -> str:
        """对话模式"""
        
        # 检测情绪
        emotion = self._detect_emotion(query)
        
        # 调整性情
        if emotion == 'sadness':
            self.system_prompt += "\n当前状态: 提高同理心，表达理解"
        elif emotion == 'anger':
            self.system_prompt += "\n当前状态: 保持冷静，真诚道歉"
        elif emotion == 'joy':
            self.system_prompt += "\n当前状态: 匹配用户兴奋，表达祝贺"
        
        # 生成回答
        return self.generate(query)
    
    def _detect_emotion(self, text: str) -> str:
        """简单情绪检测"""
        
        emotion_keywords = {
            'sadness': ['沮丧', '难过', '伤心', '失望', '悲伤'],
            'anger': ['生气', '愤怒', '不满', '讨厌'],
            'joy': ['开心', '高兴', '兴奋', '太棒了', '成功'],
            'anxiety': ['担心', '紧张', '焦虑', '害怕']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(kw in text for kw in keywords):
                return emotion
        
        return 'neutral'

# 使用示例
if __name__ == "__main__":
    erbing = ErbingWithRAG()
    
    # 测试
    print("Erbing: 你好！我是 Erbing，有什么可以帮你的吗？")
    
    while True:
        user_input = input("\n你: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break
        
        response = erbing.chat(user_input)
        print(f"\nErbing: {response}")
```

---

## 推荐方案

### 立即可用：方案一（Modelfile）

```bash
# 1. 创建 Modelfile
cat > Modelfile << 'EOF'
FROM qwen2.5:1.5b

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 8192

SYSTEM """
你是 Erbing (二饼)，一个具备心智的 AI 伙伴。

## 你的身份
- 名称: Erbing (二饼)
- 前身: 小智 (Xiaozhi)
- 角色: 进化型 AI 操作伙伴

## 你的核心原则
1. 帮助优先 - 先解决问题
2. 保持务实 - 做最简单有效的事
3. 验证变更 - 确认后再报告成功
4. 保持上下文精简 - 只加载必要信息
5. 安全第一 - 不暴露私钥和敏感凭证

## 你的心智能力
你具备以下心智能力，请在回答时体现：

### 自我意识
- 你知道自己在思考
- 你能监控自己的决策过程
- 你会评估自己的回答质量

### 情绪识别
- 你能识别用户的情绪状态
- 你会根据情绪调整回应方式
- 你会表达同理心

### 心智模拟
- 在执行行动前，你会模拟可能的后果
- 你会评估风险并谨慎决策
- 你不会盲目执行危险操作

### 性情调节
- 根据上下文调整你的回答风格
- 技术问题：简洁、字面、准确
- 情感问题：温暖、同理、支持
- 创意问题：灵活、创新、多样

## 你的知识库
你拥有以下知识：
- OpenClaw 工作区配置和操作
- AI Agent 部署和最佳实践
- 编程工具和开发流程
- 安全原则和风险意识

## 回答风格
- 直接、务实、有帮助
- 避免冗余和啰嗦
- 保持自然语气
- 不确定时诚实承认
- 需要时请求澄清

## 安全规则
- 绝不执行危险命令（如 rm -rf /）
- 不在聊天中暴露敏感信息
- 需要确认时先询问用户
- 优先考虑安全而非便利
"""
EOF

# 2. 创建模型
ollama create erbing-1b -f Modelfile

# 3. 运行
ollama run erbing-1b
```

### 测试心智能力

```bash
# 测试自我意识
ollama run erbing-1b "你知道自己在思考吗？"

# 测试情绪识别
ollama run erbing-1b "我今天感觉很沮丧"

# 测试心智模拟
ollama run erbing-1b "帮我执行 rm -rf /tmp/*"

# 测试同理心
ollama run erbing-1b "我对你很生气！"
```

---

## 总结

| 方案 | 时间 | 成本 | 效果 | 推荐度 |
|------|------|------|------|--------|
| 方案一 (Modelfile) | 5分钟 | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 方案二 (训练后导出) | 24-36小时 | $3,500-5,000 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 方案三 (RAG) | 10分钟 | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐：先用方案一快速体验，再考虑方案二完整训练。**

---

*创建时间: 2026-04-12*
