#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent实际应用演示 - 简化版（避免编码问题）
"""
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def demo():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("="*70)
    print("Agent Calling System Demo - 179 Agents Available")
    print("="*70)
    
    # Demo 1: Backend Architect
    print("\n[Demo 1] Backend Architect - System Design")
    print("-"*70)
    cursor.execute("SELECT * FROM agent_prompts WHERE name = 'Backend Architect'")
    agent = cursor.fetchone()
    
    if agent:
        print(f"Name: {agent['name']}")
        print(f"Category: {agent['category']}")
        print(f"Description: {agent['description']}")
        print(f"\nCore Philosophy: {agent['vibe']}")
        
        print("\nTask: Design e-commerce order system microservices")
        print("""
Backend Architect considers:
1. Service decomposition (Order, Inventory, Payment, Notification)
2. Database selection (PostgreSQL for orders, Redis for inventory)
3. API design (REST + GraphQL + WebSocket)
4. Security (JWT, encryption, rate limiting)
5. Monitoring (Health checks, circuit breakers)
""")
    
    # Demo 2: Code Reviewer
    print("\n[Demo 2] Code Reviewer - Code Quality")
    print("-"*70)
    cursor.execute("SELECT * FROM agent_prompts WHERE name = 'Code Reviewer'")
    agent = cursor.fetchone()
    
    if agent:
        print(f"Name: {agent['name']}")
        print(f"Category: {agent['category']}")
        print(f"Description: {agent['description']}")
        
        print("\nReview sample code:")
        print("""
def process_payment(user_id, amount):
    payment_gateway.charge(user_id, amount)
    return {"status": "success"}

Issues found:
1. No input validation
2. No error handling
3. No logging
4. No idempotency check
5. No authentication

Recommendations:
- Add validation for amount range
- Use try-except for error handling
- Implement logging system
- Add idempotency key check
- Require JWT authentication
""")
    
    # Demo 3: Growth Hacker
    print("\n[Demo 3] Growth Hacker - Growth Strategy")
    print("-"*70)
    cursor.execute("SELECT * FROM agent_prompts WHERE name = 'Growth Hacker'")
    agent = cursor.fetchone()
    
    if agent:
        print(f"Name: {agent['name']}")
        print(f"Category: {agent['category']}")
        print(f"Description: {agent['description']}")
        
        print("\nStrategy: Grow B2B SaaS from 1K to 10K users in 3 months")
        print("""
AARRR Framework:

Acquisition:
- LinkedIn ads targeting PMs and CTOs
- SEO optimization
- Content marketing (whitepapers)
- Product Hunt launch

Activation:
- Simplified signup (< 30 seconds)
- Interactive onboarding
- 14-day free trial
- Personalized welcome emails

Retention:
- Weekly usage reports
- Team collaboration reminders
- Feature announcements
- Proactive customer success

Revenue:
- Free tier limitations
- Team plan discounts
- Annual billing (20% off)
- Referral program

Referral:
- Invitation rewards
- Team invite incentives
- Social sharing
- Customer case studies
""")
    
    # Demo 4: Multi-Agent Collaboration
    print("\n[Demo 4] Multi-Agent Collaboration")
    print("-"*70)
    
    agents_needed = [
        ('Product Manager', 'product'),
        ('Backend Architect', 'engineering'),
        ('Frontend Developer', 'engineering'),
        ('UI Designer', 'design'),
        ('QA Engineer', 'testing')
    ]
    
    print("Building a user authentication feature:\n")
    for i, (name, category) in enumerate(agents_needed, 1):
        print(f"{i}. {name} ({category})")
    
    print("""
Workflow:

Step 1: Product Manager
- Define requirements
- Write user stories
- Acceptance criteria

Step 2: UI Designer
- Design login UI
- Design registration flow
- Error message styles
- Output: Figma designs

Step 3: Backend Architect
- API architecture
- JWT authentication
- Database schema
- Security measures
- Output: API docs

Step 4: Frontend Developer
- Implement UI
- Integrate APIs
- Form validation
- Error handling
- Output: Frontend code

Step 5: QA Engineer
- Functional testing
- Security testing
- Performance testing
- Edge case testing
- Output: Test report

Result: Complete authentication system
""")
    
    # Demo 5: Statistics
    print("\n[Demo 5] Database Statistics")
    print("-"*70)
    
    cursor.execute("SELECT COUNT(*) FROM agent_prompts")
    total = cursor.fetchone()[0]
    print(f"Total Agents: {total}")
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM agent_prompts
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    print("\nBy Category:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} agents")
    
    # Demo 6: Random Picks
    print("\n[Demo 6] Random Agent Recommendations")
    print("-"*70)
    
    cursor.execute('''
        SELECT name, category, description
        FROM agent_prompts
        ORDER BY RANDOM()
        LIMIT 3
    ''')
    
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n{i}. {row[0]} ({row[1]})")
        desc = row[2][:80] + '...' if len(row[2]) > 80 else row[2]
        print(f"   {desc}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("Demo Complete!")
    print("="*70)
    print("""
Try it yourself:
- python scripts/agent_caller.py "data"
- python scripts/agent_caller.py --random
- python scripts/agent_caller.py --categories

Search examples:
- python scripts/agent_caller.py "AI"
- python scripts/agent_caller.py "marketing"
- python scripts/agent_caller.py "designer"
""")

if __name__ == "__main__":
    demo()
