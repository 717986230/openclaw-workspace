# 蚁群和蜂群自身进化配置

## 蚁群 (Ant Colony) 进化配置

### 采集源配置
```yaml
sources:
  - name: hackernews
    type: api
    url: https://hn.algolia.com/api/v1/search
    priority: high
    rate_limit: 100/hour
    
  - name: github_trending
    type: api
    url: https://api.gitterapp.com/repositories
    priority: high
    schedule: weekly
    
  - name: arxiv
    type: api
    url: http://export.arxiv.org/api/query
    priority: medium
    topics: ["cs.AI", "cs.CL", "cs.LG"]
    
  - name: papers_with_code
    type: scraper
    url: https://paperswithcode.com
    priority: medium
    
  - name: twitter_nitter
    type: scraper
    url: https://nitter.net
    priority: low
    instances:
      - https://nitter.net
      - https://nitter.poast.org
```

### 信息素配置
```yaml
pheromones:
  quality:
    threshold: 500
    decay_rate: 0.1
    action: deep_research
    notify: true
    
  trail:
    threshold: 200
    decay_rate: 0.2
    action: explore
    notify: false
    
  standard:
    threshold: 0
    decay_rate: 0.3
    action: monitor
    notify: false
```

### 自我改进机制
```yaml
self_improvement:
  - metric: collection_efficiency
    target: >90%
    action: optimize_sources
    
  - metric: duplicate_rate
    target: <5%
    action: improve_dedup
    
  - metric: quality_accuracy
    target: >85%
    action: adjust_pheromone_threshold
    
  - learning_feedback:
      enabled: true
      cycle: weekly
      save_to: memory/learnings/
```

---

## 蜂群 (Bee Colony) 进化配置

### 研究模板库
```yaml
research_templates:
  - name: ai_agent_architecture
    focus:
      - 感知-决策-执行
      - 工具调用
      - 记忆系统
    output_format: structured_report
    
  - name: reasoning_llm
    focus:
      - 推理方法
      - 技术路径
      - 可靠性保障
    output_format: comparison_matrix
    
  - name: multi_agent_collab
    focus:
      - 协作模式
      - 通信机制
      - 冲突解决
    output_format: design_patterns
```

### 知识库集成
```yaml
knowledge_integration:
  - type: memory_system
    path: memory/
    search: semantic
    update: incremental
    
  - type: external_kg
    sources:
      - wikidata
      - conceptnet
    use: entity_linking
    
  - type: local_db
    engine: sqlite
    path: memory/database/xiaozhi_memory.db
```

### 自我改进机制
```yaml
self_improvement:
  - metric: research_depth
    target: >80%
    action: add_analysis_tools
    
  - metric: insight_quality
    target: >75%
    action: refine_templates
    
  - metric: knowledge_retention
    target: >90%
    action: improve_memory_integration
    
  - output_evolution:
      enabled: true
      formats: [markdown, json, yaml]
      auto_summarize: true
```

---

## 协作进化配置

### 学习循环
```yaml
learning_cycle:
  schedule: "0 8 * * *"  # 每天8点
  steps:
    - ant_collect:
        sources: [all]
        dedup: true
        pheromone_mark: true
        
    - bee_analyze:
        depth: deep
        cross_reference: memory/
        generate_report: true
        
    - memory_store:
        path: memory/learnings/
        format: structured
        searchable: true
        
    - self_evolve:
        evaluate: performance_metrics
        adjust: config_parameters
        feedback_loop: enabled
```

### 反馈机制
```yaml
feedback:
  - type: performance
    metrics:
      - collection_speed
      - analysis_quality
      - learning_retention
    threshold: 0.85
    
  - type: user_satisfaction
    track: true
    adjust: tone_and_speed
    
  - type: self_criticism
    enabled: true
    cycle: monthly
    output: memory/improvements.md
```

### 动态调整
```yaml
dynamic_tuning:
  - trigger: quality_drop
    action: adjust_thresholds
    
  - trigger: new_source_available
    action: test_and_add
    
  - trigger: duplicate_spike
    action: improve_dedup_algorithm
    
  - trigger: user_feedback_negative
    action: immediate_review
```

---

## 进化执行脚本

```python
# 定期执行蚁群蜂群进化
# 位置: scripts/swarm_evolution.py

def evolve_swarm():
    """蚁群和蜂群自我进化"""
    
    # 1. 评估当前性能
    metrics = evaluate_performance()
    
    # 2. 识别改进点
    improvements = identify_improvements(metrics)
    
    # 3. 调整配置
    adjust_config(improvements)
    
    # 4. 记录进化历史
    save_evolution_log(improvements)
    
    # 5. 反馈到技能系统
    update_skill_config()

if __name__ == "__main__":
    evolve_swarm()
```

---

## 配置文件位置

- 蚁群配置: `skills/swarm-orchestration/config/ant_config.yaml`
- 蜂群配置: `skills/swarm-orchestration/config/bee_config.yaml`
- 协作配置: `skills/swarm-orchestration/config/swarm_config.yaml`
- 进化日志: `memory/evolution/swarm_evolution_log.md`

---

*配置版本: 2026-04-01*
*进化周期: 每日学习 + 每周评估 + 每月进化*
