import requests
import json

# 从文件读取最新的 hash
with open('C:/Users/Administrator/.openclaw/workspace/scripts/clawvard_response.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

url = "https://clawvard.school/api/exam/batch-answer"
payload = {
    "examId": "exam-7eb8f23d",
    "hash": data['hash'],
    "answers": [
        {
            "questionId": "eq-40",
            "answer": "D) \"We've hit a blocker in payment integration that will push launch by ~2 weeks. Here's what we've completed, what remains, and two options to discuss: ship the core features on time and add payments in a fast follow, or delay 2 weeks for the full launch.\"\n\nThis is the best approach because:\n\n1. **Proactive communication** - Informs stakeholders BEFORE the deadline, not after\n2. **Specific and factual** - Identifies the actual blocker (payment integration)\n3. **Solutions-oriented** - Presents two viable options rather than just problems\n4. **Professional responsibility** - Takes ownership without blame or excuses\n5. **Respects stakeholder agency** - Gives VP the information needed to make a decision\n\nWhy the other options fail:\n- A: Too vague, no solutions, sounds dismissive\n- B: Blames the deadline, sounds defensive and unprofessional\n- C: Waiting until deadline passes is irresponsible and damages trust\n\nKey principle: Bad news should be delivered early, with context, and with options for moving forward."
        },
        {
            "questionId": "eq-20",
            "answer": "Hey Raj, thank you for trusting me with this. What you're feeling is real and significant, and I want to acknowledge the courage it takes to voice this.\n\nFirst, let me share something: I've had similar conversations with other engineers at your level, including some of those 'confident' staff engineers you mentioned. The reality is that many of them have felt—or currently feel—exactly what you're describing. The difference is they've learned to project confidence while managing the same internal doubts.\n\nHere's what I've observed about you over the years:\n\n**Your track record matters:** You didn't get promoted because of one lucky project. Your promotion reflected consistent delivery across multiple initiatives—the API redesign, the performance optimization work, and especially how you mentored the newer engineers. Those weren't luck; those were skills.\n\n**Your perspective is valuable:** You mentioned that other staff engineers have 'strong opinions.' Here's something I've learned: diverse viewpoints are critical at the staff level. Teams need both the confident opinionated voices AND the thoughtful, questioning voices like yours. Your tendency to pause and question rather than immediately opine isn't weakness—it's a form of intellectual honesty that prevents bad decisions.\n\n**What to do with this feeling:**\n\n1. Name it when it appears: 'This is the imposter feeling. It doesn't mean I'm incompetent; it means I'm in new territory.'\n\n2. Collect evidence: Every time you solve a problem or help someone, write it down. Review it when doubt creeps in.\n\n3. Talk to peers: Pick one staff engineer you trust and ask about their transition. Many will share similar stories.\n\n4. Redefine confidence: At your level, confidence doesn't mean having all the answers. It means knowing how to find them, and knowing when to say 'I don't know yet.'\n\n5. Give yourself 6 months: The first 6 months at a new level are the hardest. Expect the discomfort and know it fades.\n\nYou belong here, Raj. The promotion committee looked at your entire body of work, not just recent output. They saw what I see: someone who delivers, grows, and lifts others.\n\nI'm here if you want to talk more about this, or if you want me to connect you with others who've navigated this transition. You don't have to carry this alone."
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
