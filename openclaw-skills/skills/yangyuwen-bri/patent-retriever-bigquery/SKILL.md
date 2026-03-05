---
name: patent-retriever-bigquery
description: |
  基于 Google Patent BigQuery 的专利检索技能。用于按主题/关键词构建检索计划并拉取专利结果（默认不少于20条），输出结构化 JSON 供后续分析使用。
  触发词：专利检索、patent search、prior art、google patents、bigquery patent。
homepage: https://github.com/yangyuwen-bri/patent-retriever-bigquery
user-invocable: true
emoji: 🔎
tags:
  - patent
  - patent-search
  - prior-art
  - bigquery
  - google-patents
  - openclaw
metadata:
  openclaw:
    homepage: https://github.com/yangyuwen-bri/patent-retriever-bigquery
    requires:
      bins:
        - python3
      env:
        - GOOGLE_APPLICATION_CREDENTIALS
        - GOOGLE_CLOUD_PROJECT
---

# Patent Retriever (BigQuery)

仅做专利检索与结构化结果输出，不做法律结论。

## Preconditions

需要用户自行配置 Google 环境变量（必需）：

- `GOOGLE_APPLICATION_CREDENTIALS`：service account JSON 的绝对路径
- `GOOGLE_CLOUD_PROJECT`：GCP project id

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

## Workflow

1. Seed 检索（先拿一批种子样本）
2. 生成 `concept_scan.json` 与 `query_plan.json`
3. 按 query plan 执行多轮检索，输出 `retriever_result.json`
4. 用 schema 校验输出合法性

## Commands

### 1) Seed retrieval

```bash
python3 scripts/patent_search.py \
  --keywords "ai sentiment analysis" \
  --limit 80 \
  --output results/seed_raw.json
```

### 2) Build plan

```bash
python3 scripts/build_query_plan.py \
  --topic "舆情+AI" \
  --keywords "public opinion ai sentiment" \
  --task-id "run_001" \
  --seed-raw results/seed_raw.json \
  --concept-output results/concept_scan.json \
  --plan-output results/query_plan.json
```

### 3) Execute planned retrieval

```bash
python3 scripts/patent_search_plan.py \
  --plan results/query_plan.json \
  --output-raw results/retriever_raw.json \
  --output-retriever results/retriever_result.json \
  --min-results 20
```

### 4) Validate outputs

```bash
python3 scripts/schema_check.py --input results/concept_scan.json --schema schemas/concept_scan.schema.json
python3 scripts/schema_check.py --input results/query_plan.json --schema schemas/query_plan.schema.json
python3 scripts/schema_check.py --input results/retriever_result.json --schema schemas/retriever_result.schema.json
```

## Output contract

- `results/concept_scan.json`
- `results/query_plan.json`
- `results/retriever_raw.json`
- `results/retriever_result.json`

其中 `retriever_result.json` 默认要求：

- `patents` 数量 `>= 20`
- 每条至少包含 `publication_number` 与 `title`

## References

需要方法论细节时再读取：`references/methodology.md`
