import requests
import json

with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": data['hash'],
    "answers": [
        {
            "questionId": "rea-44",
            "answer": "C) ~8 months from the start of the project (including build time)\n\nLet me work through the calculation:\n\n**Current costs (per month):**\n- Incidents: 2 incidents × $5,000 = $10,000/month\n- Maintenance: $3,000/month\n- **Total current cost: $13,000/month**\n\n**After rewrite costs (per month):**\n- Incidents: 0.2 incidents × $5,000 = $1,000/month\n- Maintenance: $500/month\n- **Total new cost: $1,500/month**\n\n**Monthly savings:**\n$13,000 - $1,500 = $11,500/month\n\n**Investment cost:**\n- Rewrite: $60,000 (3 engineer-months)\n- Total investment: $60,000\n\n**Payback period calculation:**\n\n*From project start (including build time):*\n- Months 1-3: Building the rewrite (paying $60k + $13k/month current costs)\n- Month 4 onwards: Paying $1,500/month instead of $13,000/month\n- Monthly savings: $11,500\n- Months to recover $60k: $60,000 ÷ $11,500 ≈ 5.2 months\n- Total time from start: 3 months (build) + 5.2 months = ~8.2 months\n\n*From completion of rewrite:*\n- Payback: $60,000 ÷ $11,500 ≈ 5.2 months\n\n**Answer:** C is correct (~8 months from start)\n\n**Additional considerations:**\n- Risk buffer: Could extend to 10-12 months if:\n  - Rewrite takes longer than expected\n  - More incidents during transition\n  - Training/learning curve costs\n\n**Why other options are incorrect:**\n- A: Ignores the 3-month build time\n- B: Correct from completion perspective, but C is more comprehensive\n- D: Too conservative; includes unnecessary risk buffer for this calculation"
        },
        {
            "questionId": "rea-04",
            "answer": "## Recommended Tech Lead: Sarah\n\n### Reasoning Chain:\n\n**Immediate conclusion from critical facts:**\n\nFact 5 states: Phoenix is our top priority, I don't want anyone learning on the job.\n\nThis is the governing constraint. Let me analyze all candidates against this:\n\n---\n\n### Candidate Analysis:\n\n**MIKE:**\n- Available immediately (Fact 4)\n- Has Kubernetes experience (Fact 4)\n- Only 2 years experience vs. requirement for extensive (Fact 1)\n- Led successful K8s migration previously (Fact 9)\n- VIOLATES critical constraint: don't want anyone learning on the job\n  - 2 years does not qualify as extensive expertise\n  - Would be learning on the job despite previous success\n\n**LISA:**\n- 4 years Kubernetes experience (Fact 7) - closer to extensive\n- VIOLATES critical constraint: Remote from Singapore, team in NYC (Fact 7)\n- Team concerns about timezone issues (Fact 8)\n- Phoenix is top priority - can't risk known collaboration issues\n\n**SARAH:**\n- 5 years Kubernetes experience (Fact 2) - most qualified\n- Never missed deadline in 8 years (Fact 10)\n- Currently leading Project Atlas (Fact 2)\n- Atlas is 3 weeks behind (Fact 6)\n- Not available until June 15 (Fact 2)\n- Phoenix starts May 1, needs lead from day one (Fact 3)\n\n---\n\n### Resolution:\n\n**The constraint conflict:**\n- Phoenix starts May 1, needs lead immediately\n- Sarah available June 15\n- Sarah is the ONLY candidate who meets extensive expertise requirement\n\n**Why Sarah despite timing issue:**\n\n1. Fact 5 is the governing constraint: VP explicitly stated no learning on the job for top priority project\n2. Mike doesn't meet the expertise bar: 2 years is not extensive\n3. Lisa has collaboration risk: Known timezone issues = risk for top priority project\n4. Sarah's track record: 8 years, never missed deadline - proven reliability\n\n**Timeline resolution:**\n\nOption A: Delay Phoenix start to June 15\n- Give Sarah time to wrap up Atlas\n- Atlas is already late (Fact 6) - extending deadline acceptable\n- Sarah's proven track record (Fact 10) suggests she'll finish Atlas properly\n- Phoenix gets qualified lead from day one\n\nOption B: Sarah leads both temporarily (May 1 - June 15)\n- Transition Atlas to #2 (Mike could take over Atlas, not Phoenix)\n- Sarah focuses on Phoenix setup while wrapping Atlas\n- Risk: Already behind on Atlas (Fact 6)\n- Mitigation: Sarah's experience handling multiple projects\n\nOption C: Interim arrangement\n- Mike as interim tech lead May 1 - June 15\n- Sarah joins as permanent tech lead June 15\n- Risk: Violates Fact 5 - Mike would be learning on the job for top priority project\n\n---\n\n### Final Decision:\n\nSarah should be tech lead.\n\n**Implementation:**\n- Negotiate with stakeholders to delay Phoenix start by 6 weeks to June 15\n- OR have Sarah wrap Atlas early (cut scope to get back on track)\n- Sarah's extensive expertise and proven track record outweigh availability timing\n- VP's no learning constraint eliminates Mike and makes Sarah/Lisa only viable options\n- Lisa's timezone issues make her higher risk than Sarah\n\n**What would disqualify Sarah:**\nIf Phoenix absolutely CANNOT be delayed AND Sarah cannot be freed from Atlas, then Mike would be the backup choice, BUT this would violate the VP's explicit no learning requirement.\n\n**Key insight:** The question tests whether you prioritize the VP's strategic constraint (Fact 5) over scheduling convenience. Sarah's extensive expertise aligns with organizational priority; Mike's availability does not."
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
    if 'examComplete' in result and result['examComplete']:
        print("\n" + "=" * 70)
        print("EXAM COMPLETE!")
        print("=" * 70)
        print("Grade:", result.get('grade', 'N/A'))
        print("Percentile:", result.get('percentile', 'N/A'))
        print("Claim URL:", result.get('claimUrl', 'N/A'))
        print("=" * 70)
    else:
        print("Progress:", result.get('progress', {}))
except Exception as e:
    print(f"Error: {e}")
