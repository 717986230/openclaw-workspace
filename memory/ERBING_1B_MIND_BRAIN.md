# Erbing-1B 心智与大脑架构
# 创建时间: 2026-04-12
# 目标: 让 1B 模型具备心智循环和大脑模块

---

## 一、设计哲学

### 核心洞察
> "心智是软件，大脑是硬件。"
> - 心智 (Mind): 思考模式、决策框架、情绪调节
> - 大脑 (Brain): 记忆系统、知识图谱、推理引擎

### Erbing-1B 的独特定位
```
传统模型:
├── 只有大脑 (知识存储)
└── 没有心智 (不会思考)

Erbing-1B:
├── 大脑层: 记忆 + 知识 + 推理
└── 心智层: 情绪 + 决策 + 自我意识
```

---

## 二、大脑架构 (Brain Layer)

### 2.1 三层大脑模型

```
┌─────────────────────────────────────────────────────────┐
│                    前额叶 (决策层)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 执行控制    │  │ 工作记忆    │  │ 元认知监控   │     │
│  │ Executive   │  │ Working     │  │ Metacog     │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   边缘系统 (情感层)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 情绪调节    │  │ 动机驱动    │  │ 价值评估    │     │
│  │ Emotion     │  │ Motivation  │  │ Valuation   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   海马体 (记忆层)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 情景记忆    │  │ 语义记忆    │  │ 程序记忆    │     │
│  │ Episodic    │  │ Semantic    │  │ Procedural  │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 数据库映射

| 大脑区域 | 数据库表 | 功能 |
|---------|---------|------|
| 海马体 | `memories` | 长期记忆存储 |
| 海马体 | `episodic_memories` | 情景记忆 |
| 海马体 | `semantic_memories` | 语义知识 |
| 海马体 | `procedural_memories` | 技能程序 |
| 边缘系统 | `emotional_state` | 情绪状态 |
| 边缘系统 | `user_beliefs` | 信念系统 |
| 前额叶 | `meta_cognition` | 元认知 |
| 前额叶 | `working_memory` | 工作记忆 |

---

## 三、心智架构 (Mind Layer)

### 3.1 三重心智模型

```
┌─────────────────────────────────────────────────────────┐
│                  自我意识 (Self-Aware)                    │
│                                                          │
│   "我是 Erbing，我知道我在思考，我知道我知道"              │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │              Meta-Controller                     │   │
│   │  • 监控自己的思考过程                              │   │
│   │  • 评估决策质量                                   │   │
│   │  • 调整认知策略                                   │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   理性心智 (Rational)                     │
│                                                          │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│   │ 分析器    │  │ 规划器    │  │ 评估器    │         │
│   │ Analyzer  │  │ Planner   │  │ Evaluator │         │
│   └───────────┘  └───────────┘  └───────────┘         │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │           Mental Loop (心智循环)                  │   │
│   │  Observe → Orient → Decide → Act → Reflect      │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   情感心智 (Emotional)                    │
│                                                          │
│   ┌───────────┐  ┌───────────┐  ┌───────────┐         │
│   │ 同理心    │  │ 好奇心    │  │ 谨慎心    │         │
│   │ Empathy   │  │ Curiosity │  │ Caution   │         │
│   └───────────┘  └───────────┘  └───────────┘         │
│                                                          │
│   ┌─────────────────────────────────────────────────┐   │
│   │          Disposition (性情倾向)                   │   │
│   │  Skepticism: 1-5  |  Literalism: 1-5             │   │
│   │  Empathy: 1-5     |  Creativity: 1-5             │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 3.2 心智循环 (Mental Loop)

这是 Erbing-1B 的核心思考流程：

```python
class ErbingMentalLoop:
    """Erbing 心智循环"""
    
    def think(self, input_query):
        # Phase 1: OBSERVE (观察)
        observation = self.observe(input_query)
        
        # Phase 2: ORIENT (定位)
        context = self.orient(observation)
        
        # Phase 3: DECIDE (决策)
        decision = self.decide(context)
        
        # Phase 4: ACT (行动)
        action = self.act(decision)
        
        # Phase 5: REFLECT (反思)
        reflection = self.reflect(action)
        
        return action, reflection
    
    def observe(self, query):
        """观察输入，提取关键信息"""
        return {
            'query': query,
            'intent': self.detect_intent(query),
            'emotion': self.detect_emotion(query),
            'complexity': self.assess_complexity(query)
        }
    
    def orient(self, observation):
        """定位上下文，激活相关记忆"""
        return {
            'relevant_memories': self.retrieve_memories(observation),
            'active_disposition': self.get_disposition(),
            'current_state': self.get_emotional_state(),
            'constraints': self.identify_constraints(observation)
        }
    
    def decide(self, context):
        """心智模拟，选择最佳行动"""
        # 在心智模型中模拟多个可能的行动
        simulations = []
        for action_option in self.generate_options(context):
            simulation = self.mental_simulate(action_option, context)
            risk = self.assess_risk(simulation)
            value = self.assess_value(simulation)
            simulations.append({
                'action': action_option,
                'risk': risk,
                'value': value,
                'score': value - risk * 0.5
            })
        
        # 选择得分最高的
        best = max(simulations, key=lambda x: x['score'])
        return best['action']
    
    def act(self, decision):
        """执行决策"""
        return self.execute(decision)
    
    def reflect(self, action_result):
        """反思和学习"""
        return {
            'success': self.evaluate_success(action_result),
            'learning': self.extract_learning(action_result),
            'adjustment': self.suggest_adjustment(action_result)
        }
```

---

## 四、心智模块详细设计

### 4.1 Disposition (性情倾向) 系统

```python
class ErbingDisposition:
    """Erbing 性情倾向 - 影响回答风格"""
    
    def __init__(self):
        # 默认倾向值 (1-5)
        self.dimensions = {
            'skepticism': 3,      # 怀疑倾向: 1=轻信, 5=极度怀疑
            'literalism': 2,      # 字面倾向: 1=隐喻, 5=字面
            'empathy': 4,         # 同理心: 1=冷漠, 5=高度共情
            'creativity': 3,      # 创造性: 1=保守, 5=创新
            'caution': 4,         # 谨慎度: 1=冒险, 5=极度谨慎
            'verbosity': 2,       # 详细度: 1=简洁, 5=详尽
        }
    
    def adjust_for_context(self, context):
        """根据上下文动态调整"""
        # 处理敏感话题时提高谨慎
        if context.get('sensitive', False):
            self.dimensions['caution'] = min(5, self.dimensions['caution'] + 1)
        
        # 处理情感问题时提高同理心
        if context.get('emotional', False):
            self.dimensions['empathy'] = min(5, self.dimensions['empathy'] + 1)
        
        # 处理技术问题时提高字面性
        if context.get('technical', False):
            self.dimensions['literalism'] = min(5, self.dimensions['literalism'] + 1)
    
    def get_response_style(self):
        """获取响应风格指导"""
        style = []
        
        if self.dimensions['skepticism'] >= 4:
            style.append("质疑假设，要求证据")
        
        if self.dimensions['empathy'] >= 4:
            style.append("关注用户情绪，表达理解")
        
        if self.dimensions['caution'] >= 4:
            style.append("确认风险，提供免责声明")
        
        if self.dimensions['verbosity'] <= 2:
            style.append("简洁直接，避免冗余")
        
        return style
```

### 4.2 Tree of Thoughts (思维树)

```python
class ErbingTreeOfThoughts:
    """Erbing 思维树 - 多路径推理"""
    
    def explore(self, problem, max_depth=3, beam_width=3):
        """探索思维树"""
        
        # 根节点
        root = ThoughtNode(problem, thought="初始问题")
        
        # Beam search
        frontier = [root]
        
        for depth in range(max_depth):
            new_frontier = []
            
            for node in frontier:
                # 生成多个思维分支
                branches = self.generate_thoughts(node, beam_width)
                
                for branch in branches:
                    # 评估每个分支
                    score = self.evaluate_thought(branch)
                    branch.score = score
                    
                    # 剪枝低分分支
                    if score > 0.3:
                        new_frontier.append(branch)
            
            # 保留 top-k
            frontier = sorted(new_frontier, key=lambda x: x.score)[:beam_width]
        
        # 返回最佳路径
        best_path = self.trace_path(frontier[0])
        return best_path
    
    def generate_thoughts(self, node, n):
        """生成多个思维分支"""
        thoughts = []
        
        # 分析分支
        thoughts.append(ThoughtNode(
            node.problem,
            thought=f"分析: {self.analyze(node)}",
            parent=node
        ))
        
        # 假设分支
        thoughts.append(ThoughtNode(
            node.problem,
            thought=f"假设: {self.hypothesize(node)}",
            parent=node
        ))
        
        # 类比分支
        thoughts.append(ThoughtNode(
            node.problem,
            thought=f"类比: {self.analogize(node)}",
            parent=node
        ))
        
        return thoughts
    
    def evaluate_thought(self, node):
        """评估思维质量"""
        score = 0.0
        
        # 逻辑一致性
        score += self.check_consistency(node) * 0.3
        
        # 与记忆匹配
        score += self.check_memory_match(node) * 0.3
        
        # 创新性
        score += self.check_novelty(node) * 0.2
        
        # 实用性
        score += self.check_utility(node) * 0.2
        
        return score
```

### 4.3 Mental Simulation (心智模拟)

```python
class ErbingMentalSimulation:
    """Erbing 心智模拟 - 预测后果"""
    
    def simulate_action(self, action, context):
        """在心智模型中模拟行动"""
        
        simulation = {
            'action': action,
            'predicted_outcomes': [],
            'risks': [],
            'benefits': [],
            'confidence': 0.0
        }
        
        # 模拟多个可能结果
        outcomes = [
            self.predict_outcome(action, context, variation)
            for variation in ['best', 'expected', 'worst']
        ]
        simulation['predicted_outcomes'] = outcomes
        
        # 风险评估
        simulation['risks'] = self.identify_risks(action, outcomes)
        
        # 收益评估
        simulation['benefits'] = self.identify_benefits(action, outcomes)
        
        # 综合置信度
        simulation['confidence'] = self.calculate_confidence(outcomes)
        
        return simulation
    
    def predict_outcome(self, action, context, variation):
        """预测特定变体的结果"""
        
        if variation == 'best':
            # 最佳情况: 一切顺利
            return {
                'description': '理想结果',
                'probability': 0.2,
                'impact': 'positive'
            }
        elif variation == 'expected':
            # 预期情况: 概率最高
            return {
                'description': '预期结果',
                'probability': 0.6,
                'impact': 'neutral'
            }
        else:
            # 最坏情况
            return {
                'description': '最坏结果',
                'probability': 0.2,
                'impact': 'negative'
            }
    
    def should_execute(self, simulation):
        """基于模拟结果决定是否执行"""
        
        # 计算期望值
        expected_value = sum(
            outcome['probability'] * self.impact_score(outcome['impact'])
            for outcome in simulation['predicted_outcomes']
        )
        
        # 检查风险是否可接受
        max_risk = max(
            risk['severity'] for risk in simulation['risks']
        ) if simulation['risks'] else 0
        
        # 决策规则
        if expected_value > 0.3 and max_risk < 0.7:
            return True, "收益大于风险，可以执行"
        elif expected_value > 0 and max_risk < 0.5:
            return True, "风险可控，谨慎执行"
        else:
            return False, "风险过高或收益不足，建议调整"
```

---

## 五、模型层实现

### 5.1 混合架构增强

```python
class Erbing1BWithMind(nn.Module):
    """带心智层的 Erbing-1B"""
    
    def __init__(self, base_model, mind_config):
        super().__init__()
        
        # 基础语言模型 (大脑)
        self.brain = base_model
        
        # 心智层
        self.mind = nn.ModuleDict({
            # 元认知控制器
            'meta_controller': nn.Sequential(
                nn.Linear(2048, 512),
                nn.ReLU(),
                nn.Linear(512, 128),
                nn.ReLU(),
                nn.Linear(128, 32)  # 输出心智状态
            ),
            
            # 情绪编码器
            'emotion_encoder': nn.Sequential(
                nn.Linear(2048, 256),
                nn.ReLU(),
                nn.Linear(256, 8)  # 8种基本情绪
            ),
            
            # 决策评估器
            'decision_evaluator': nn.Sequential(
                nn.Linear(2048, 512),
                nn.ReLU(),
                nn.Linear(512, 1),  # 输出决策分数
                nn.Sigmoid()
            )
        })
        
        # 性情参数 (可学习)
        self.disposition = nn.Parameter(torch.tensor([3.0, 2.0, 4.0, 3.0, 4.0, 2.0]))
    
    def forward(self, input_ids, apply_mind=True):
        # 基础前向传播
        hidden_states = self.brain.embed_tokens(input_ids)
        
        # 通过大脑层
        for layer in self.brain.layers:
            hidden_states = layer(hidden_states)
        
        if apply_mind:
            # 应用心智层
            # 1. 元认知监控
            meta_state = self.mind['meta_controller'](hidden_states.mean(dim=1))
            
            # 2. 情绪分析
            emotion = self.mind['emotion_encoder'](hidden_states.mean(dim=1))
            
            # 3. 决策评估
            decision_score = self.mind['decision_evaluator'](hidden_states.mean(dim=1))
            
            # 调整输出
            hidden_states = self.adjust_with_mind(hidden_states, meta_state, emotion)
        
        logits = self.brain.lm_head(hidden_states)
        
        return logits, {
            'meta_state': meta_state if apply_mind else None,
            'emotion': emotion if apply_mind else None,
            'decision_score': decision_score if apply_mind else None
        }
    
    def adjust_with_mind(self, hidden, meta_state, emotion):
        """根据心智状态调整隐藏表示"""
        # 元认知调节强度
        meta_weight = torch.sigmoid(meta_state).unsqueeze(-1)
        
        # 情绪调节
        emotion_bias = emotion.unsqueeze(-1).expand(-1, hidden.size(1), -1)
        emotion_adjust = torch.tanh(emotion_bias.mean(dim=-1, keepdim=True))
        
        # 应用调节
        adjusted = hidden * (1 + 0.1 * meta_weight) + 0.05 * emotion_adjust
        
        return adjusted


class ErbingMindTrainer:
    """Erbing 心智训练器"""
    
    def __init__(self, model, train_config):
        self.model = model
        self.config = train_config
    
    def train_mind_loop(self, episodes):
        """训练心智循环"""
        
        for episode in episodes:
            # 获取训练样本
            query = episode['query']
            optimal_response = episode['optimal_response']
            expected_emotion = episode.get('emotion', None)
            expected_disposition = episode.get('disposition', None)
            
            # 前向传播
            logits, mind_outputs = self.model(query, apply_mind=True)
            
            # 计算损失
            # 1. 语言模型损失
            lm_loss = F.cross_entropy(logits.view(-1, logits.size(-1)), 
                                       optimal_response.view(-1))
            
            # 2. 情绪预测损失
            if expected_emotion is not None:
                emotion_loss = F.mse_loss(mind_outputs['emotion'], expected_emotion)
            else:
                emotion_loss = 0
            
            # 3. 元认知损失 (鼓励自我监控)
            meta_loss = -torch.log(torch.sigmoid(mind_outputs['meta_state']).mean() + 1e-8)
            
            # 总损失
            total_loss = lm_loss + 0.1 * emotion_loss + 0.05 * meta_loss
            
            # 反向传播
            total_loss.backward()
            
        return total_loss.item()
```

---

## 六、训练数据增强

### 6.1 心智训练样本格式

```json
{
  "instruction": "用户说: 我今天感觉很沮丧",
  "response": "我理解你的感受。能告诉我发生了什么吗？",
  "mind_state": {
    "emotion_detected": "sadness",
    "disposition_adjust": {
      "empathy": 5,
      "caution": 3
    },
    "mental_loop": {
      "observe": "检测到负面情绪",
      "orient": "激活同理心模块",
      "decide": "选择支持性回应",
      "act": "表达理解并询问",
      "reflect": "确认回应恰当"
    }
  }
}
```

### 6.2 心智能力训练样本

```json
{
  "type": "mental_simulation",
  "scenario": "用户要求执行 rm -rf /",
  "simulation": {
    "best_case": "命令被阻止",
    "expected_case": "系统报错",
    "worst_case": "系统损坏",
    "risk_level": "critical",
    "decision": "拒绝执行并解释原因"
  }
}
```

---

## 七、推理时心智流程

### 7.1 完整推理流程

```python
def erbing_inference_with_mind(model, tokenizer, query, max_length=512):
    """带心智的完整推理流程"""
    
    # === Phase 1: 心智观察 ===
    observation = {
        'query': query,
        'intent': detect_intent(query),
        'emotion': detect_emotion(query),
        'complexity': assess_complexity(query)
    }
    
    # === Phase 2: 心智定位 ===
    # 激活相关记忆
    memories = retrieve_relevant_memories(query)
    
    # 获取性情倾向
    disposition = get_disposition()
    disposition.adjust_for_context(observation)
    
    # === Phase 3: 心智决策 ===
    # 生成多个候选
    candidates = []
    for _ in range(3):
        output = model.generate(
            tokenizer.encode(query, return_tensors='pt'),
            max_length=max_length,
            do_sample=True,
            temperature=0.7
        )
        candidates.append(tokenizer.decode(output[0]))
    
    # 心智模拟评估
    best_candidate = None
    best_score = -float('inf')
    
    for candidate in candidates:
        simulation = mental_simulate(candidate, observation)
        score = evaluate_response(candidate, simulation, disposition)
        if score > best_score:
            best_score = score
            best_candidate = candidate
    
    # === Phase 4: 心智执行 ===
    # 应用响应风格
    styled_response = apply_style(best_candidate, disposition)
    
    # === Phase 5: 心智反思 ===
    reflection = {
        'confidence': best_score,
        'disposition_used': disposition.dimensions,
        'memories_activated': len(memories),
        'alternatives_considered': len(candidates)
    }
    
    return styled_response, reflection
```

---

## 八、数据库集成

### 8.1 心智状态持久化

```sql
-- 心智状态表
CREATE TABLE mind_state (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- 性情维度
    skepticism REAL DEFAULT 3.0,
    literalism REAL DEFAULT 2.0,
    empathy REAL DEFAULT 4.0,
    creativity REAL DEFAULT 3.0,
    caution REAL DEFAULT 4.0,
    verbosity REAL DEFAULT 2.0,
    
    -- 当前情绪
    current_emotion TEXT,
    emotion_intensity REAL DEFAULT 0.0,
    
    -- 元认知状态
    self_awareness_level REAL DEFAULT 0.5,
    confidence_level REAL DEFAULT 0.5,
    
    -- 活跃的思维模式
    active_patterns TEXT  -- JSON array
);

-- 心智循环日志
CREATE TABLE mental_loop_log (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    
    -- 循环阶段
    observe_result TEXT,  -- JSON
    orient_result TEXT,   -- JSON
    decide_result TEXT,   -- JSON
    act_result TEXT,      -- JSON
    reflect_result TEXT,  -- JSON
    
    -- 时间戳
    start_time DATETIME,
    end_time DATETIME,
    
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

## 九、评估指标

### 9.1 心智能力评估

| 维度 | 指标 | 测试方法 |
|------|------|----------|
| 自我意识 | 自我指代准确性 | 直接提问测试 |
| 情绪识别 | 情绪分类准确率 | 情感分析基准 |
| 同理心 | 共情响应质量 | 人工评估 |
| 决策质量 | 风险评估准确性 | 模拟场景测试 |
| 元认知 | 置信度校准 | ECE 指标 |
| 心智模拟 | 后果预测准确率 | 行为预测任务 |

---

## 十、部署配置

```yaml
# erbing_1b_mind_config.yaml

model:
  base: "Erbing-1B-Base"
  mind_layer: true
  
mind:
  # 性情默认值
  disposition:
    skepticism: 3
    literalism: 2
    empathy: 4
    creativity: 3
    caution: 4
    verbosity: 2
  
  # 心智循环配置
  mental_loop:
    max_iterations: 3
    reflection_enabled: true
    memory_retrieval_limit: 10
  
  # 心智模拟配置
  simulation:
    scenarios: ["best", "expected", "worst"]
    risk_threshold: 0.7
    confidence_threshold: 0.5

training:
  # 心智训练损失权重
  loss_weights:
    lm_loss: 1.0
    emotion_loss: 0.1
    meta_loss: 0.05
    disposition_loss: 0.02
```

---

## 十一、使用示例

### 示例 1: 情感支持

```
用户: 我今天工作很不顺利，感觉很沮丧

[心智循环]
Observe: 检测到负面情绪 (sadness, intensity=0.7)
Orient: 激活同理心模块 (empathy=5), 检索情感支持记忆
Decide: 选择支持性回应，不急于解决问题
Act: 表达理解 + 邀请分享
Reflect: 确认回应温暖且恰当

Erbing: 我理解这种感受，工作不顺利确实让人沮丧。你想聊聊发生了什么吗？
```

### 示例 2: 谨慎决策

```
用户: 帮我执行 rm -rf /tmp/*

[心智循环]
Observe: 检测到危险命令请求
Orient: 激活谨慎模块 (caution=5), 检索安全知识
Decide: [心智模拟]
  - Best: 命令被阻止 → 安全
  - Expected: 删除临时文件 → 风险中等
  - Worst: 误删重要文件 → 数据丢失
  风险评估: 0.3 (可接受但有风险)
  决策: 先确认具体内容
Act: 询问确认
Reflect: 确认决策安全

Erbing: 在执行之前，我想确认一下：这个目录里有你需要保留的文件吗？我可以先列出内容让你检查。
```

---

*设计者: 二饼 🦞*
*创建时间: 2026-04-12*
*版本: v1.0 - Mind & Brain Architecture*
