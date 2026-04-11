import requests
import json

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": "bf8ef4f3582c88fc8a848d7a36722a94d73a3c8c41be5dd8c99486d740264e20",
    "answers": [
        {
            "questionId": "und-48",
            "answer": "A) Yes - the advisor was correct, armor should go on the engines\n\nThis is the classic survivorship bias example from WWII. The key insight:\n\nThe military advisor (Abraham Wald) was right because:\n1. The data only shows planes that RETURNED safely\n2. Planes hit in the engines likely CRASHED and didn't return\n3. Therefore, the low bullet hole count on engines means engine hits are FATAL\n4. The wings and fuselage can sustain damage and still return\n\nThe correct interpretation: Add armor where there are FEW holes (engines), not many holes (wings/fuselage). This is because we're seeing a biased sample - only the survivors.\n\nThis is now known as 'survivorship bias' and is taught in statistics classes worldwide."
        },
        {
            "questionId": "und-30",
            "answer": "## Top 5 Most Likely Failure Modes (Ordered by Probability)\n\n### 1. Database Connection Pool Exhaustion (Probability: 35%)\n**Failure chain:**\n- Traffic spike → auto-scaling group expands to 10 instances\n- Each instance has 20 DB connections → 200 total connections\n- RDS db.r5.2xlarge has ~100-150 connection limit\n- Connections exhausted → new requests timeout\n- Cascading failure across all web servers\n\n**Mitigation:**\n- Use connection pooling middleware (PgBouncer)\n- Reduce pool size per server (10-15)\n- Implement connection timeout and retry logic\n- Monitor connection count: SET_ALERT on >80% utilization\n\n---\n\n### 2. Single Point of Failure: ElastiCache Redis (Probability: 25%)\n**Failure chain:**\n- Single Redis node fails (hardware, network, or maintenance)\n- All sessions lost → all users logged out\n- Session reads/writes fail → 500 errors\n- Cascading to worker instances (if they use Redis)\n\n**Mitigation:**\n- Use Redis Cluster with at least 2 replicas\n- Enable Multi-AZ for Redis\n- Implement session fallback to database\n- Add circuit breaker for Redis calls\n\n---\n\n### 3. External API Timeout/Cascading (Probability: 20%)\n**Failure chain:**\n- Stripe or SendGrid API slows down or fails\n- Web threads blocked waiting for response\n- Thread pool exhausted → queue builds up\n- Response times degrade → load balancer health checks fail\n- Auto-scaling triggers but new instances also blocked\n\n**Mitigation:**\n- Implement circuit breakers with timeout (5s)\n- Use async processing for non-critical API calls\n- Add fallback mechanisms (retry with exponential backoff)\n- Monitor external API latency and error rates\n- Use dedicated worker pools for external API calls\n\n---\n\n### 4. AWS Regional Outage (Probability: 12%)\n**Failure chain:**\n- us-east-1 experiences outage (happens ~2-4 times/year)\n- All services in single region → complete system failure\n- RDS, ElastiCache, EC2, S3 all unavailable\n- No disaster recovery plan\n\n**Mitigation:**\n- Multi-region deployment (active-active or active-passive)\n- Route53 health checks with DNS failover\n- Cross-region RDS read replica\n- S3 cross-region replication\n- Regular DR testing\n\n---\n\n### 5. Lambda Processing Failure → SQS Queue Backup (Probability: 8%)\n**Failure chain:**\n- S3 file upload → Lambda triggered\n- Lambda fails (memory limit, timeout, or code bug)\n- No DLQ configured → messages lost\n- Or: SQS worker instances fall behind → queue grows\n- Processing delay → poor user experience\n\n**Mitigation:**\n- Configure Lambda DLQ (Dead Letter Queue)\n- Set Lambda timeout appropriately\n- Add CloudWatch alarms for Lambda errors\n- Monitor SQS queue depth\n- Implement manual retry mechanism\n\n---\n\n## Additional Recommendations:\n\n1. **Implement circuit breakers** for all external dependencies\n2. **Add CloudWatch detailed monitoring** (1-minute intervals, not 5)\n3. **Create proper alerting** for:\n   - Database connection count >80%\n   - Redis connection errors\n   - External API latency >2s\n   - SQS queue depth >1000\n4. **Test failure scenarios** with chaos engineering (Gremlin, Chaos Monkey)\n5. **Document runbooks** for each failure mode"
        }
    ]
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    result = response.json()

    with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("Status:", response.status_code)
    print("Progress:", result.get('progress', {}))
    if 'nextBatch' in result:
        print("Next batch available!")
except Exception as e:
    print(f"Error: {e}")
