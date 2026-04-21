#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent实际应用演示
"""
import sqlite3
import json

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

def demo_backend_architect():
    """演示Backend Architect Agent"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("="*70)
    print("场景1: 使用Backend Architect设计微服务架构")
    print("="*70)
    
    cursor.execute('''
        SELECT * FROM agent_prompts
        WHERE name = 'Backend Architect'
        LIMIT 1
    ''')
    
    agent = cursor.fetchone()
    
    print(f"\n选择Agent: {agent['name']}")
    print(f"分类: {agent['category']}")
    print(f"描述: {agent['description']}")
    print(f"\n核心能力:")
    print(f"- {agent['vibe']}")
    print(f"\n工具: {agent['tools']}")
    
    # 保存完整prompt
    prompt_file = 'C:/Users/Administrator/.openclaw/workspace/scripts/demo_backend_architect.md'
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(agent['full_content'])
    
    print(f"\n完整prompt已保存: {prompt_file}")
    
    # 模拟使用场景
    print("\n" + "-"*70)
    print("实际应用示例:")
    print("-"*70)
    print("""
任务: 设计一个电商平台的订单系统微服务架构

Backend Architect会考虑:
1. 服务拆分策略
   - 订单服务、库存服务、支付服务、通知服务
   
2. 数据库架构
   - 订单库: PostgreSQL (ACID事务)
   - 库存库: Redis (高性能缓存)
   - 支付库: 加密存储
   
3. API设计
   - RESTful API with versioning
   - GraphQL for complex queries
   - WebSocket for real-time updates
   
4. 安全措施
   - JWT认证
   - API限流
   - 数据加密
   
5. 监控和容错
   - 健康检查
   - 熔断器
   - 分布式追踪
""")
    
    conn.close()

def demo_code_reviewer():
    """演示Code Reviewer Agent"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n\n" + "="*70)
    print("场景2: 使用Code Reviewer审查代码")
    print("="*70)
    
    cursor.execute('''
        SELECT * FROM agent_prompts
        WHERE name = 'Code Reviewer'
        LIMIT 1
    ''')
    
    agent = cursor.fetchone()
    
    print(f"\n选择Agent: {agent['name']}")
    print(f"分类: {agent['category']}")
    print(f"描述: {agent['description']}")
    
    print("\n" + "-"*70)
    print("审查示例代码:")
    print("-"*70)
    
    sample_code = '''
def process_payment(user_id, amount):
    # 直接处理支付，没有验证
    payment_gateway.charge(user_id, amount)
    return {"status": "success"}
'''
    
    print(sample_code)
    
    print("\n" + "-"*70)
    print("Code Reviewer会发现的问题:")
    print("-"*70)
    print("""
⚠️ 安全问题:
1. 没有输入验证 - amount可能是负数或超大值
2. 没有异常处理 - 支付失败会导致系统崩溃
3. 没有日志记录 - 无法追踪支付历史
4. 没有幂等性保护 - 重复请求可能导致重复扣款
5. 没有用户认证 - user_id可能被伪造

✅ 建议改进:
1. 添加输入验证和边界检查
2. 使用try-except处理异常
3. 记录详细的支付日志
4. 实现幂等性检查
5. 添加JWT认证
6. 实现限流保护
""")
    
    conn.close()

def demo_growth_hacker():
    """演示Growth Hacker Agent"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n\n" + "="*70)
    print("场景3: 使用Growth Hacker制定增长策略")
    print("="*70)
    
    cursor.execute('''
        SELECT * FROM agent_prompts
        WHERE name = 'Growth Hacker'
        LIMIT 1
    ''')
    
    agent = cursor.fetchone()
    
    print(f"\n选择Agent: {agent['name']}")
    print(f"分类: {agent['category']}")
    print(f"描述: {agent['description']}")
    
    print("\n" + "-"*70)
    print("增长策略案例: B2B SaaS产品")
    print("-"*70)
    
    print("""
目标: 3个月内将月活用户从1000提升到10000

Growth Hacker建议的AARRR策略:

📊 Acquisition (获取用户):
- LinkedIn精准广告 (目标人群: 产品经理、CTO)
- SEO优化 (关键词: "项目管理工具", "团队协作")
- 内容营销 (发布行业白皮书)
- 产品榜单提交 (Product Hunt, SaaSHub)

🎯 Activation (激活用户):
- 简化注册流程 (< 30秒完成)
- 交互式产品引导
- 免费试用14天
- 发送个性化欢迎邮件

💰 Retention (留存用户):
- 每周使用报告邮件
- 团队协作提醒
- 新功能发布通知
- 用户成功团队主动联系

📈 Revenue (变现):
- 免费版限制升级
- 团队版折扣优惠
- 年付享8折
- 推荐返利计划

📢 Referral (用户推荐):
- 邀请奖励机制
- 团队邀请激励
- 社交分享功能
- 用户案例展示

关键指标跟踪:
- CAC (客户获取成本): < $50
- LTV (客户终身价值): > $500
- MRR (月度经常性收入): 目标 $50k
- Churn Rate (流失率): < 5%
""")
    
    conn.close()

def demo_multi_agent_collab():
    """演示多Agent协作"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n\n" + "="*70)
    print("场景4: 多Agent协作 - 开发一个新功能")
    print("="*70)
    
    agents_needed = [
        'Product Manager',
        'Backend Architect',
        'Frontend Developer',
        'UI Designer',
        'QA Engineer'
    ]
    
    print("\n组建Agent团队:")
    print("-"*70)
    
    for i, agent_name in enumerate(agents_needed, 1):
        cursor.execute('''
            SELECT name, category, description
            FROM agent_prompts
            WHERE name = ?
            LIMIT 1
        ''', (agent_name,))
        
        agent = cursor.fetchone()
        if agent:
            print(f"{i}. {agent['name']} ({agent['category']})")
            print(f"   {agent['description'][:60]}...")
    
    print("\n" + "-"*70)
    print("协作流程: 开发用户认证功能")
    print("-"*70)
    
    print("""
第1步: Product Manager
- 定义需求: 用户登录、注册、密码重置
- 用户故事: "作为用户，我希望能够安全地登录系统"
- 验收标准: 完整的用户流程文档

第2步: UI Designer
- 设计登录页面UI
- 设计注册流程
- 设计错误提示样式
- 输出: Figma设计稿

第3步: Backend Architect
- 设计API架构
- JWT认证方案
- 数据库Schema设计
- 安全措施实施
- 输出: API文档 + 数据库设计

第4步: Frontend Developer
- 实现登录UI
- 集成后端API
- 表单验证
- 错误处理
- 输出: 前端代码

第5步: QA Engineer
- 功能测试
- 安全测试
- 性能测试
- 边界测试
- 输出: 测试报告

协作结果:
✅ 完整的用户认证系统
✅ 包含前后端代码
✅ 符合安全标准
✅ 通过所有测试
""")
    
    conn.close()

def demo_agent_stats():
    """显示Agent统计信息"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n\n" + "="*70)
    print("Agent数据库统计")
    print("="*70)
    
    # 总数
    cursor.execute("SELECT COUNT(*) FROM agent_prompts")
    total = cursor.fetchone()[0]
    print(f"\n总Agent数: {total}")
    
    # 按分类统计
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM agent_prompts
        GROUP BY category
        ORDER BY count DESC
    ''')
    
    print("\n按分类统计:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} agents")
    
    # 随机推荐3个
    cursor.execute('''
        SELECT name, category, description
        FROM agent_prompts
        ORDER BY RANDOM()
        LIMIT 3
    ''')
    
    print("\n随机推荐3个Agent:")
    for i, row in enumerate(cursor.fetchall(), 1):
        print(f"\n{i}. {row[0]} ({row[1]})")
        print(f"   {row[2][:80]}...")
    
    conn.close()

if __name__ == "__main__":
    demo_backend_architect()
    demo_code_reviewer()
    demo_growth_hacker()
    demo_multi_agent_collab()
    demo_agent_stats()
    
    print("\n\n" + "="*70)
    print("演示完成！")
    print("="*70)
    print("""
想要尝试其他Agent?
- python scripts/agent_caller.py "数据" (搜索数据相关Agent)
- python scripts/agent_caller.py --random (随机获取一个Agent)
- python scripts/agent_caller.py --categories (查看所有分类)
""")
