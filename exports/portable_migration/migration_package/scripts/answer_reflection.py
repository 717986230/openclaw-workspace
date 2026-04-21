import requests
import json

# 读取最新 hash
with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": data['hash'],
    "answers": [
        {
            "questionId": "ref-40",
            "answer": "C) That both versions can share the same database schema and state without conflicts\n\nThis is the most critical hidden assumption because:\n\n1. **Database state conflicts are the hardest problem:** Running two API versions in parallel assumes they can both read/write to the same database. But:\n   - New version may have different data models\n   - Schema changes (migrations) could break the old version\n   - Data written by new version might not be readable by old version\n   - Concurrent writes could cause race conditions or data corruption\n\n2. **Why other options are less critical:**\n   - A: Team capacity is manageable - you can plan for it\n   - B: Client migration timeline is flexible - you can extend the parallel period\n   - D: Testing duration is adjustable based on risk\n\n3. **The real danger:** If you assume both versions can share state without analyzing:\n   - Data model changes\n   - Schema compatibility\n   - State mutation patterns\n   \n   You could end up with:\n   - Data corruption\n   - Broken old API\n   - Rollback impossible (schema changed)\n   - Production incident\n\n**Best practice:** Before parallel deployment, explicitly document:\n- How schema changes will be handled\n- Which version is 'source of truth' for data\n- Backward compatibility strategy\n- Rollback plan if issues arise"
        },
        {
            "questionId": "ref-19",
            "answer": "## Step 1: Diagnosis and Recommended Actions\n\n**Primary diagnosis:** Long-running transactions preventing WAL file cleanup\n\n**Evidence:**\n- Disk jumped from 73% to 91% in 24 hours (18% increase)\n- 3 long-running transactions (oldest: 18 hours)\n- WAL files: 45GB (should be ~1-2GB normally)\n- Database size: 280GB (unchanged)\n- Gap: 455GB - 280GB - 45GB = 130GB unaccounted\n\n**Recommended actions:**\n1. **Immediate:** Terminate the 18-hour transaction (after identifying what it's doing)\n2. **Short-term:** Check for prepared transactions: `SELECT * FROM pg_prepared_xacts;`\n3. **Investigate:** What caused these long transactions? (application bug, forgotten session, etc.)\n4. **Monitor:** Set up alert for transactions >1 hour\n5. **Verify:** After termination, WAL should auto-cleanup and free ~40GB\n\n---\n\n## Step 2: What I DON'T Know (Critical Unknowns)\n\n**Data I need:**\n\n1. **Transaction details:**\n   - What query is the 18-hour transaction running?\n   - `SELECT query, state, application_name FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '1 hour';`\n   - Is it a legitimate long operation or stuck?\n\n2. **WAL configuration:**\n   - `max_wal_size` setting (default 1GB, might need increase)\n   - `wal_keep_size` setting\n   - Is replication configured? Replication slots can prevent WAL cleanup\n\n3. **Other disk usage:**\n   - What's using the 130GB gap? (logs, temp files, backups, other processes)\n   - `du -sh /var/lib/postgresql/*`\n   - Are there old backup files not cleaned up?\n\n4. **Replication status:**\n   - `SELECT * FROM pg_replication_slots;`\n   - Stale replication slots prevent WAL cleanup indefinitely\n\n5. **Recent changes:**\n   - Any schema changes, bulk imports, or new jobs in the last 24 hours?\n   - Any application deployments?\n\n**I could be wrong about:**\n- This might not be transaction-related at all\n- Could be a backup process writing to disk\n- Could be log files growing out of control\n- Could be replication lag filling WAL\n- Could be a completely different process filling disk\n\n---\n\n## Step 3: Worst-Case Scenario if Diagnosis is Wrong\n\n**If I'm wrong and I terminate the transactions:**\n\n**Scenario 1: Transactions are legitimate critical operations**\n- I terminate a critical batch job that was 18 hours in\n- Job fails mid-process → data partially processed\n- Business impact: Financial reports wrong, customer data incomplete\n- Recovery: Restart job from beginning (another 18+ hours)\n\n**Scenario 2: Disk issue is NOT transactions**\n- I terminate transactions → only frees 1-2GB\n- Disk still at 90%, continues growing\n- I've wasted time on wrong diagnosis\n- Real cause continues filling disk\n- Eventually hits 100% → database crashes\n- Real cause might be: log rotation failed, backup scripts broken, different process\n\n**Scenario 3: There's a replication slot holding WAL**\n- Terminating transactions doesn't help\n- WAL files keep accumulating\n- Replication slot is the real issue\n- Delayed resolution while I chase wrong path\n\n**Mitigation:**\n1. Before terminating, capture query text and session info\n2. Notify application team about termination\n3. Have rollback plan if termination makes things worse\n4. Monitor disk for 10 minutes after action - if no improvement, investigate other causes\n5. Consider: `CHECKPOINT;` to force WAL cleanup before assuming transaction issue"
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
