import sqlite3
from datetime import datetime

conn = sqlite3.connect('erbing_virtual_world.db')
cursor = conn.cursor()

# 暗网知识
dark_web_knowledge = [
    ('Dark Web', 'Tor Network', 'Tor (The Onion Router) provides anonymous communication by routing traffic through multiple relays. Hidden services use .onion addresses. Tor browser required for access. 3-hop circuit for anonymity'),
    ('Dark Web', 'Onion Routing', 'Multiple layers of encryption, each relay only knows previous and next hop. Exit nodes can see unencrypted traffic. Entry guards protect against enumeration. Circuit construction uses Diffie-Hellman'),
    ('Dark Web', 'Hidden Services', ' onion addresses are 56-character base32 strings. Services dont reveal IP address. Introduction points and rendezvous points for connection. Client-authenticated services require private key'),
    ('Dark Web', 'Darknet Markets', 'Silk Road model: escrow, multisig, vendor bonds. Rating systems and dispute resolution. Exit scams and law enforcement takedowns. AlphaBay, Hansa, Wall Street Market examples'),
    ('Dark Web', 'Cryptocurrency', 'Bitcoin mixing services, Monero for privacy. Tumblers and mixers to obfuscate transactions. CoinJoin, CoinSwap protocols. Privacy coins: Monero, Zcash, Dash'),
    ('Dark Web', 'Threat Actor Communities', 'Exploit forums, malware markets, carding shops. Access brokers, initial access brokers. Ransomware-as-a-Service (RaaS). Credential stuffing and account takeover'),
    ('Dark Web', 'Data Leaks', 'Credential dumps, breach databases. Paste sites for leaked data. DDoS-for-hire services. Personal information trading. Corporate data ransom'),
    ('Dark Web', 'OSINT Techniques', 'Dark web crawling, onion search engines. Threat intelligence gathering. Monitoring forums and marketplaces. Attribution challenges. OPSEC for researchers'),
    ('Dark Web', 'Security Risks', 'Malware-laden sites, phishing .onion addresses. Law enforcement honeypots. JavaScript exploits. Traffic correlation attacks. Node compromise'),
    ('Dark Web', 'Legal Considerations', 'Accessing dark web is legal in most countries. Illegal content is still illegal. Research exemptions vary by jurisdiction. Log retention and evidence handling. Ethical research guidelines'),
]

# 添加知识到数据库
print('Adding Dark Web knowledge...')
for domain, topic, content in dark_web_knowledge:
    cursor.execute('''
        INSERT INTO knowledge (domain, topic, content, confidence, usage_count, last_used, created_at)
        VALUES (?, ?, ?, 0.8, 0, NULL, ?)
    ''', (domain, topic, content, datetime.now()))

conn.commit()

# 统计
cursor.execute('SELECT COUNT(*) FROM knowledge')
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM knowledge WHERE domain = 'Dark Web'")
dark_web_count = cursor.fetchone()[0]

print(f'Total knowledge: {total}')
print(f'Dark Web knowledge: {dark_web_count}')
print('Dark Web knowledge added successfully!')

# 展示添加的暗网知识
print()
print('=== Dark Web Knowledge Added ===')
cursor.execute("SELECT topic, content FROM knowledge WHERE domain = 'Dark Web'")
for topic, content in cursor.fetchall():
    print(f'{topic}:')
    print(f'  {content[:100]}...' if len(content) > 100 else f'  {content}')
    print()

conn.close()
