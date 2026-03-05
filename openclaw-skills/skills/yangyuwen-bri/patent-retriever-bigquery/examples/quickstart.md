# Quickstart

```bash
python3 -m pip install -r requirements.txt

python3 scripts/patent_search.py \
  --keywords "ai sentiment analysis" \
  --limit 80 \
  --output results/seed_raw.json

python3 scripts/build_query_plan.py \
  --topic "舆情+AI" \
  --keywords "public opinion ai sentiment" \
  --task-id "demo_001" \
  --seed-raw results/seed_raw.json \
  --concept-output results/concept_scan.json \
  --plan-output results/query_plan.json

python3 scripts/patent_search_plan.py \
  --plan results/query_plan.json \
  --output-raw results/retriever_raw.json \
  --output-retriever results/retriever_result.json \
  --min-results 20
```
