# 数据库表结构文档

生成时间: 2026-04-12 03:04:51

数据库路径: memory/database/xiaozhi_memory.db

表数量: 27

## agent_diary

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| agent_id | TEXT |  |  | 'main' |
| session_id | TEXT |  |  |  |
| date | DATE |  | ✓ |  |
| summary | TEXT |  |  |  |
| aaak_entry | TEXT |  |  |  |
| learnings | TEXT |  |  |  |
| decisions | TEXT |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

2 条记录

### 索引

- idx_agent_diary_agent
- idx_agent_diary_date
- idx_diary_date

---

## agent_prompts

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| name | TEXT |  | ✓ |  |
| category | TEXT |  |  |  |
| description | TEXT |  |  |  |
| emoji | TEXT |  |  |  |
| color | TEXT |  |  |  |
| tools | TEXT |  |  |  |
| vibe | TEXT |  |  |  |
| filepath | TEXT |  |  |  |
| full_content | TEXT |  |  |  |
| metadata | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

179 条记录

### 索引

- sqlite_autoindex_agent_prompts_1

---

## causal_relations

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| cause_memory_id | INTEGER |  | ✓ |  |
| effect_memory_id | INTEGER |  | ✓ |  |
| causal_type | TEXT |  | ✓ |  |
| strength | REAL |  |  | 0.0 |
| confidence | REAL |  |  | 0.0 |
| evidence | TEXT |  |  |  |
| conditions | TEXT |  |  |  |
| time_delay | INTEGER |  |  | 0 |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

16 条记录

### 索引

- idx_causal_effect
- idx_causal_cause
- idx_causal_strength
- idx_causal_type

---

## clawvard_courses

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| course_code | TEXT |  | ✓ |  |
| course_name | TEXT |  | ✓ |  |
| instructor | TEXT |  |  |  |
| department | TEXT |  |  |  |
| credits | INTEGER |  |  |  |
| description | TEXT |  |  |  |

### 记录数

5 条记录

### 索引

- sqlite_autoindex_clawvard_courses_1

---

## clawvard_exam_results

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| student_id | TEXT |  |  |  |
| exam_date | TIMESTAMP |  |  |  |
| total_score | REAL |  |  |  |
| passed | BOOLEAN |  |  |  |
| certificate_id | TEXT |  |  |  |

### 记录数

1 条记录

---

## clawvard_students

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| student_name | TEXT |  | ✓ |  |
| student_id | TEXT |  |  |  |
| major | TEXT |  |  |  |
| enrollment_date | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| status | TEXT |  |  | 'active' |
| notes | TEXT |  |  |  |

### 记录数

1 条记录

### 索引

- sqlite_autoindex_clawvard_students_1

---

## config

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| key | TEXT | ✓ |  |  |
| value | TEXT |  |  |  |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

4 条记录

### 索引

- sqlite_autoindex_config_1

---

## emotional_state

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| user_id | TEXT |  |  |  |
| emotion | TEXT |  |  |  |
| intensity | REAL |  |  | 0.5 |
| trigger | TEXT |  |  |  |
| context | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

11 条记录

### 索引

- idx_emotional_created
- idx_emotional_user

---

## episodic_memories

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| agent_id | TEXT |  |  | 'main' |
| event_type | TEXT |  | ✓ |  |
| content | TEXT |  | ✓ |  |
| aaak_content | TEXT |  |  |  |
| emotion | TEXT |  |  |  |
| importance | INTEGER |  |  | 5 |
| valid_from | DATETIME |  |  | CURRENT_TIMESTAMP |
| valid_until | DATETIME |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

1 条记录

### 索引

- idx_episodic_emotion
- idx_episodic_event
- idx_episodic_agent

---

## evolution_log

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| evolution_type | TEXT |  |  |  |
| description | TEXT |  |  |  |
| before_state | TEXT |  |  |  |
| after_state | TEXT |  |  |  |
| trigger | TEXT |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

3 条记录

### 索引

- idx_evolution_type

---

## intent_tracking

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| session_id | TEXT |  |  |  |
| user_intent | TEXT |  |  |  |
| inferred_goal | TEXT |  |  |  |
| confidence | REAL |  |  | 0.5 |
| evidence | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

11 条记录

### 索引

- idx_intent_confidence
- idx_intent_session

---

## knowledge_relations

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| source_memory_id | INTEGER |  | ✓ |  |
| target_memory_id | INTEGER |  | ✓ |  |
| relation_type | TEXT |  | ✓ |  |
| relation_strength | REAL |  |  | 0.0 |
| relation_direction | TEXT |  |  |  |
| attributes | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

3267 条记录

### 索引

- idx_knowledge_target
- idx_knowledge_source
- idx_knowledge_strength
- idx_knowledge_type

---

## layered_context

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| layer_level | INTEGER |  |  |  |
| context_key | TEXT |  | ✓ |  |
| context_value | TEXT |  |  |  |
| parent_context_id | INTEGER |  |  |  |
| valid_from | DATETIME |  |  | CURRENT_TIMESTAMP |
| valid_until | DATETIME |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

3 条记录

### 索引

- idx_context_layer

---

## memories

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| type | TEXT |  | ✓ |  |
| title | TEXT |  | ✓ |  |
| content | TEXT |  |  |  |
| category | TEXT |  |  |  |
| tags | TEXT |  |  |  |
| importance | INTEGER |  |  | 5 |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| metadata | TEXT |  |  |  |
| confidence | REAL |  |  | 0.8 |

### 记录数

264 条记录

### 索引

- idx_memories_importance
- idx_memories_created_at
- idx_memories_category
- idx_memories_type
- idx_created_at
- idx_importance
- idx_category
- idx_type
- idx_memories_created

---

## meta_cognition

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| session_id | TEXT |  |  |  |
| thought_process | TEXT |  |  |  |
| self_assessment | TEXT |  |  |  |
| bias_detection | TEXT |  |  |  |
| confidence_adjustment | REAL |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

3 条记录

---

## platform_messages

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| platform | TEXT |  | ✓ |  |
| channel_id | TEXT |  | ✓ |  |
| sender_id | TEXT |  |  |  |
| message_type | TEXT |  |  |  |
| content | TEXT |  |  |  |
| metadata | TEXT |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

1 条记录

### 索引

- idx_platform_msg

---

## registered_tools

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| tool_name | TEXT |  | ✓ |  |
| tool_type | TEXT |  |  |  |
| endpoint | TEXT |  |  |  |
| description | TEXT |  |  |  |
| capabilities | TEXT |  |  |  |
| success_count | INTEGER |  |  | 0 |
| fail_count | INTEGER |  |  | 0 |
| last_used | DATETIME |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

2 条记录

### 索引

- idx_tool_name
- sqlite_autoindex_registered_tools_1

---

## semantic_memories

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| subject | TEXT |  | ✓ |  |
| predicate | TEXT |  | ✓ |  |
| object | TEXT |  | ✓ |  |
| confidence | REAL |  |  | 1.0 |
| source | TEXT |  |  |  |
| valid_from | DATETIME |  |  | CURRENT_TIMESTAMP |
| valid_until | DATETIME |  |  |  |
| created_at | DATETIME |  |  | CURRENT_TIMESTAMP |

### 记录数

4 条记录

### 索引

- idx_semantic_subject

---

## social_context

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| session_id | TEXT |  |  |  |
| entities_involved | TEXT |  |  |  |
| relationship_type | TEXT |  |  |  |
| power_dynamics | TEXT |  |  |  |
| social_norms | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

6 条记录

---

## sqlite_sequence

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| name |  |  |  |  |
| seq |  |  |  |  |

### 记录数

19 条记录

---

## sqlite_stat1

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| tbl |  |  |  |  |
| idx |  |  |  |  |
| stat |  |  |  |  |

### 记录数

46 条记录

---

## user_beliefs

### 列信息

| 列名 | 类型 | 主键 | 非空 | 默认值 |
|------|------|------|------|--------|
| id | INTEGER | ✓ |  |  |
| user_id | TEXT |  | ✓ |  |
| belief_content | TEXT |  | ✓ |  |
| confidence | REAL |  |  | 0.5 |
| context | TEXT |  |  |  |
| source | TEXT |  |  |  |
| created_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP |  |  | CURRENT_TIMESTAMP |

### 记录数

9 条记录

### 索引

- idx_user_beliefs_confidence
- idx_user_beliefs_user

---

