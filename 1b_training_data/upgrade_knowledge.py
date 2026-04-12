import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

# 顶级大模型知识
llm_knowledge = [
    ('LLM Architecture', 'Transformer Architecture', 'Self-attention mechanism allows the model to weigh the importance of different parts of the input when making predictions. Key components: Query, Key, Value matrices, Multi-head attention, Position encoding'),
    ('LLM Architecture', 'GPT Series', 'GPT-4: 1.8 trillion parameters, multimodal capabilities, 128K context window. GPT-4 Turbo: Faster, cheaper, better performance. GPT-4o: Omni model with real-time voice and vision'),
    ('LLM Architecture', 'Claude Series', 'Claude 3.5 Sonnet: 200K context, 2-hour conversations, tool use, vision capabilities. Claude 3 Opus: Most powerful, complex reasoning, nuanced content. Claude 3 Haiku: Fast and efficient'),
    ('LLM Architecture', 'Gemini Series', 'Gemini 1.5 Pro: 1M token context window, multimodal native, long-context reasoning. Gemini Ultra: State-of-the-art performance, complex tasks. Gemini Nano: On-device AI'),
    ('LLM Architecture', 'Llama Series', 'Llama 3.1 405B: Largest open model, matches GPT-4 performance. Llama 3.1 70B: Best cost-performance ratio. Llama 3.1 8B: Lightweight, fast inference'),
    ('LLM Architecture', 'Mistral Series', 'Mistral Large: Multilingual, reasoning, coding. Mistral Medium: Balanced performance. Mistral Small: Efficient, cost-effective. Mixtral 8x7B: Mixture of experts'),
    ('LLM Architecture', 'Qwen Series', 'Qwen2.5-Max: 72B parameters, coding, math, reasoning. Qwen2.5-Plus: Multimodal, long context. Qwen2.5-Turbo: Fast, affordable. Qwen-VL: Vision-language model'),
    ('LLM Architecture', 'DeepSeek Series', 'DeepSeek V3: 67B parameters, MoE architecture, coding specialist. DeepSeek Coder: Code generation, multiple languages. DeepSeek Math: Mathematical reasoning'),
    ('LLM Training', 'Pre-training', 'Massive text corpus (trillions of tokens), next token prediction objective, self-supervised learning, scaling laws, compute-optimal training'),
    ('LLM Training', 'Fine-tuning', 'Supervised fine-tuning (SFT), instruction tuning, RLHF (Reinforcement Learning from Human Feedback), DPO (Direct Preference Optimization), safety alignment'),
    ('LLM Training', 'Constitutional AI', 'Self-critique and revision, constitutional principles, harmlessness training, helpfulness training, red teaming, adversarial training'),
    ('LLM Training', 'Efficient Training', 'LoRA (Low-Rank Adaptation), QLoRA, gradient checkpointing, mixed precision training, distributed training, pipeline parallelism'),
    ('LLM Inference', 'Quantization', 'INT8, INT4, FP8 quantization, GPTQ, AWQ, GGUF format, vLLM optimization, tensor parallelism'),
    ('LLM Inference', 'Speculative Decoding', 'Draft model generates candidates, target model verifies, reduces latency, improves throughput, tree-based speculation'),
    ('LLM Inference', 'KV Cache Optimization', 'Paged attention, KV cache compression, sliding window attention, long-context optimization, memory-efficient inference'),
    ('LLM Capabilities', 'Chain-of-Thought', 'Step-by-step reasoning, self-consistency, program-of-thoughts, tree-of-thought, graph-of-thought'),
    ('LLM Capabilities', 'Tool Use', 'Function calling, code execution, web search, API integration, agentic workflows, tool learning'),
    ('LLM Capabilities', 'RAG', 'Retrieval-Augmented Generation, vector databases, semantic search, hybrid search, reranking, chunking strategies'),
    ('LLM Capabilities', 'Multimodal', 'Vision-language models, speech recognition, video understanding, image generation, cross-modal reasoning'),
    ('LLM Applications', 'Coding Assistants', 'GitHub Copilot, Cursor, Claude Code, Code generation, debugging, code review, documentation'),
    ('LLM Applications', 'Research Assistants', 'Literature review, hypothesis generation, experiment design, data analysis, paper writing'),
    ('LLM Applications', 'Creative Writing', 'Story generation, scriptwriting, poetry, content creation, style transfer, collaborative writing'),
]

# 顶级黑客知识
hacker_knowledge = [
    ('Hacking Methodology', 'Reconnaissance', 'OSINT (Open Source Intelligence), social engineering, network scanning, port scanning, service enumeration, DNS reconnaissance, WHOIS lookup, Google dorking'),
    ('Hacking Methodology', 'Vulnerability Assessment', 'CVE databases, NVD (National Vulnerability Database), vulnerability scanners (Nessus, OpenVAS), penetration testing frameworks, threat modeling'),
    ('Hacking Methodology', 'Exploitation', 'Buffer overflow, SQL injection, XSS (Cross-Site Scripting), CSRF (Cross-Site Request Forgery), SSRF (Server-Side Request Forgery), XXE (XML External Entity)'),
    ('Hacking Methodology', 'Post-Exploitation', 'Privilege escalation, lateral movement, persistence mechanisms, data exfiltration, covering tracks, anti-forensics'),
    ('Web Security', 'OWASP Top 10', 'Injection, broken authentication, sensitive data exposure, XML external entities, broken access control, security misconfiguration, XSS, insecure deserialization, using components with known vulnerabilities, insufficient logging'),
    ('Web Security', 'Advanced Web Attacks', 'Business logic flaws, IDOR (Insecure Direct Object Reference), HTTP request smuggling, cache poisoning, CRLF injection, template injection, deserialization attacks'),
    ('Web Security', 'API Security', 'API authentication bypass, rate limiting bypass, mass assignment, improper assets management, injection in APIs, GraphQL vulnerabilities'),
    ('Network Security', 'Network Attacks', 'Man-in-the-middle, ARP spoofing, DNS cache poisoning, packet sniffing, session hijacking, SSL stripping, evil twin attack'),
    ('Network Security', 'Wireless Security', 'WEP/WPA/WPA2 cracking, deauthentication attacks, rogue access points, Wi-Fi phishing, KARMA attack, PMKID attack'),
    ('Network Security', 'Firewall Evasion', 'Port knocking, tunneling, fragmentation attacks, protocol manipulation, evasion techniques, covert channels'),
    ('System Security', 'Privilege Escalation', 'Kernel exploits, SUID binaries, capabilities, sudo misconfigurations, cron jobs, PATH hijacking, LD_PRELOAD'),
    ('System Security', 'Malware Analysis', 'Static analysis, dynamic analysis, reverse engineering, deobfuscation, unpacking, behavioral analysis, sandboxing'),
    ('System Security', 'Rootkits', 'User-mode rootkits, kernel-mode rootkits, bootkits, hypervisor-level rootkits, detection and removal'),
    ('Cryptography', 'Cryptographic Attacks', 'Brute force, dictionary attacks, rainbow tables, collision attacks, padding oracle attacks, timing attacks, side-channel attacks'),
    ('Cryptography', 'SSL/TLS Attacks', 'POODLE, BEAST, CRIME, Heartbleed, Lucky13, ROBOT, Logjam, FREAK, Downgrade attacks'),
    ('Cryptography', 'Password Cracking', 'Hashcat rules, mask attacks, combinator attacks, rule-based attacks, GPU acceleration, distributed cracking'),
    ('Social Engineering', 'Phishing', 'Spear phishing, whaling, vishing, smishing, business email compromise (BEC), pretexting, baiting, tailgating'),
    ('Social Engineering', 'Psychological Manipulation', 'Authority, urgency, scarcity, liking, reciprocity, consistency, social proof, influence techniques'),
    ('Advanced Techniques', 'Zero-Day Exploits', 'Fuzzing, symbolic execution, static analysis, dynamic analysis, exploit development, payload generation, shellcode development'),
    ('Advanced Techniques', 'APT (Advanced Persistent Threat)', 'Long-term infiltration, custom malware, targeted attacks, threat actor groups, kill chain, diamond model'),
    ('Advanced Techniques', 'Red Teaming', 'Adversary simulation, full-scope attacks, physical security, social engineering, technical attacks, reporting'),
    ('Defense & Blue Team', 'SIEM', 'Log collection, correlation, alerting, dashboards, incident response, threat hunting, MITRE ATT&CK mapping'),
    ('Defense & Blue Team', 'Endpoint Detection', 'EDR (Endpoint Detection and Response), behavioral analysis, anomaly detection, threat intelligence, automated response'),
    ('Defense & Blue Team', 'Incident Response', 'Preparation, identification, containment, eradication, recovery, lessons learned, forensic analysis, evidence preservation'),
    ('Defense & Blue Team', 'Threat Intelligence', 'OSINT, dark web monitoring, threat feeds, IOCs (Indicators of Compromise), TTPs (Tactics, Techniques, Procedures), threat actor profiles'),
]

# 添加知识到数据库
print('Adding LLM knowledge...')
for domain, topic, content in llm_knowledge:
    cursor.execute('''
        INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at)
        VALUES (?, ?, ?, 0.8, 0, NULL, ?)
    ''', (domain, topic, content, datetime.now()))

print('Adding Hacker knowledge...')
for domain, topic, content in hacker_knowledge:
    cursor.execute('''
        INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at)
        VALUES (?, ?, ?, 0.8, 0, NULL, ?)
    ''', (domain, topic, content, datetime.now()))

conn.commit()

# 统计
cursor.execute('SELECT COUNT(*) FROM knowledge')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM knowledge WHERE domain LIKE "%LLM%" OR domain LIKE "%Hacking%" OR domain LIKE "%Web%" OR domain LIKE "%Network%" OR domain LIKE "%System%" OR domain LIKE "%Crypto%" OR domain LIKE "%Social%" OR domain LIKE "%Advanced%" OR domain LIKE "%Defense%"')
new_count = cursor.fetchone()[0]

print(f'Total knowledge: {total}')
print(f'New knowledge added: {new_count}')
print('Knowledge upgrade complete!')

conn.close()
