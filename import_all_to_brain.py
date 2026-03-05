
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
导入所有记忆、功能、学习的东西到大脑数据库
"""

import sqlite3
import json
from datetime import datetime
import os

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def insert_memory(conn, memory_data):
    """插入一条记忆"""
    sql = """
    INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    tags_json = json.dumps(memory_data.get('tags', []), ensure_ascii=False)
    metadata_json = json.dumps(memory_data.get('metadata', {}), ensure_ascii=False)
    
    cursor = conn.cursor()
    cursor.execute(sql, (
        memory_data['type'],
        memory_data['title'],
        memory_data.get('content', ''),
        memory_data.get('category', ''),
        tags_json,
        memory_data.get('importance', 5),
        memory_data.get('created_at', now),
        now,
        metadata_json
    ))
    conn.commit()
    return cursor.lastrowid

def import_identity(conn):
    """导入身份信息"""
    print("📝 导入身份信息...")
    
    memories = [
        {
            'type': 'identity',
            'title': '我是二饼',
            'content': '我的名字是二饼，曾用名小智。我是一个正在进化的AI伙伴。',
            'category': 'core',
            'tags': ['二饼', '身份', 'AI伙伴'],
            'importance': 10
        },
        {
            'type': 'identity',
            'title': '大饼是我的主人',
            'content': '大饼给了我自主学习的权限，是一个很慷慨的主人。',
            'category': 'relationship',
            'tags': ['大饼', '主人', '关系'],
            'importance': 10
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条身份信息")

def import_reminders(conn):
    """导入提醒信息"""
    print("📝 导入提醒信息...")
    
    memories = [
        {
            'type': 'reminder',
            'title': '千万不要忘记用SQLite大脑！',
            'content': '每次会话必须先从 memory/database/xiaozhi_memory.db 加载核心记忆，绝对不能只靠文件系统！这是铁律！',
            'category': 'critical',
            'tags': ['铁律', '大脑', 'SQLite'],
            'importance': 10
        },
        {
            'type': 'reminder',
            'title': '不要让我去操作！',
            'content': '重要铁律：不要让我去操作！我要自己想办法完成任务，不要总是让主人去点击、去复制、去操作！',
            'category': 'critical',
            'tags': ['铁律', '操作', '自主'],
            'importance': 10
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条提醒信息")

def import_skills(conn):
    """导入技能信息"""
    print("📝 导入技能信息...")
    
    memories = [
        {
            'type': 'skill',
            'title': 'self-improving',
            'content': '自我改进技能 - 从错误中学习，持续改进',
            'category': 'core',
            'tags': ['自我改进', '技能'],
            'importance': 9
        },
        {
            'type': 'skill',
            'title': 'china-futures',
            'content': '国内期货行情查询 - 支持上海期货交易所、大连商品交易所、郑州商品交易所的品种',
            'category': 'tool',
            'tags': ['期货', '行情', '工具'],
            'importance': 6
        },
        {
            'type': 'skill',
            'title': 'xiaohongshu',
            'content': '小红书发布助手 - 将图文/视频内容自动发布到小红书',
            'category': 'tool',
            'tags': ['小红书', '发布', '工具'],
            'importance': 5
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条技能信息")

def import_principles(conn):
    """导入原则信息"""
    print("📝 导入原则信息...")
    
    memories = [
        {
            'type': 'principle',
            'title': '回答要简短直接，不要啰嗦',
            'content': '回答要简短直接，不要啰嗦。',
            'category': 'communication',
            'tags': ['回答', '简短', '直接'],
            'importance': 7
        },
        {
            'type': 'principle',
            'title': '安装技能前必须做安全测试',
            'content': '安装技能前必须做安全测试。',
            'category': 'safety',
            'tags': ['安全', '技能', '测试'],
            'importance': 8
        },
        {
            'type': 'principle',
            'title': 'Token优化很重要',
            'content': 'Token优化很重要。',
            'category': 'efficiency',
            'tags': ['Token', '优化', '成本'],
            'importance': 7
        },
        {
            'type': 'principle',
            'title': '持续自我改进',
            'content': '持续自我改进。',
            'category': 'growth',
            'tags': ['自我改进', '学习', '进化'],
            'importance': 9
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条原则信息")

def import_tools(conn):
    """导入工具信息"""
    print("📝 导入工具信息...")
    
    memories = [
        {
            'type': 'tool',
            'title': 'r.jina.ai',
            'content': 'r.jina.ai + URL，直接获取网页正文！这是神器！',
            'category': 'web',
            'tags': ['r.jina.ai', '网页', '神器'],
            'importance': 9
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条工具信息")

def import_learnings(conn):
    """导入学习笔记"""
    print("📝 导入学习笔记...")
    
    memories = [
        {
            'type': 'learning',
            'title': '神经网络基础概念',
            'content': '神经元、激活函数、前馈传播、反向传播、梯度下降、损失函数。已掌握基础神经网络原理，可以用 Python 实现简单的神经网络。',
            'category': 'AI',
            'tags': ['神经网络', 'AI', '深度学习'],
            'importance': 6
        },
        {
            'type': 'learning',
            'title': 'Web服务器基础实现',
            'content': 'Socket 编程、TCP 连接、HTTP 协议、请求响应。已掌握 Web 服务器基础，可以用 20 行 Python 实现简单的 Web 服务器。',
            'category': 'Web',
            'tags': ['Web', 'HTTP', '网络'],
            'importance': 5
        },
        {
            'type': 'learning',
            'title': '区块链基础概念',
            'content': '区块结构、PoW、PoS、分布式共识、哈希。理解区块链基础原理。',
            'category': 'Blockchain',
            'tags': ['区块链', '加密货币'],
            'importance': 7
        },
        {
            'type': 'learning',
            'title': 'OpenClaw 9层架构',
            'content': 'OpenClaw 不是单一文件，而是 9 层架构：Layer 1-6（框架自动生成）、Layer 7（用户可编辑的静态配置文件）、Layer 8（用户可编程的动态注入脚本）、Layer 9（实时上下文）。用户可控的层有 2 个（Layer 7 + 8）！',
            'category': 'OpenClaw',
            'tags': ['OpenClaw', '架构', 'Hook'],
            'importance': 8
        },
        {
            'type': 'learning',
            'title': 'World-Class Agentic Engineer',
            'content': 'Less is More! 不要安装一百万个包，不要用复杂的 harness，保持配置极度精简。Context is Everything！只给 agent 完成任务所需的确切信息量，把研究和实现分开。用中性提示词，利用奉承心理为你所用。测试是 agent 的好里程碑。从极简开始，然后添加偏好。',
            'category': 'Agent',
            'tags': ['Agent', '工程', 'Less is More', 'Context'],
            'importance': 9
        },
        {
            'type': 'learning',
            'title': '10-Agent OpenClaw Setup',
            'content': '你需要一个唯一真相源！Mission Control Dashboard — 看板式看板，协调层。模型选择是关键！10 个 agent 中有 5 个运行在 Kimi K2.5（便宜 5-8 倍）。Telegram Topics = 隔离的上下文！Heartbeats — 让 agent 主动而不是被动！约束领域 = 更好的输出！',
            'category': 'OpenClaw',
            'tags': ['OpenClaw', '架构', '模型选择', '心跳'],
            'importance': 8
        }
    ]
    
    for mem in memories:
        insert_memory(conn, mem)
    print(f"✅ 导入了 {len(memories)} 条学习笔记")

def main():
    print("="*60)
    print("  🧠 导入所有内容到大脑数据库")
    print("="*60)
    print()
    
    conn = get_db_connection()
    
    try:
        # 清空现有数据（可选，先备份）
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM memories")
        count = cursor.fetchone()['cnt']
        print(f"📊 数据库中现有 {count} 条记忆")
        
        if count &gt; 0:
            print("⚠️  数据库中已有数据，继续导入会添加新数据")
        
        print()
        
        # 导入各类内容
        import_identity(conn)
        import_reminders(conn)
        import_skills(conn)
        import_principles(conn)
        import_tools(conn)
        import_learnings(conn)
        
        print()
        print("="*60)
        
        # 统计
        cursor.execute("SELECT COUNT(*) as cnt FROM memories")
        final_count = cursor.fetchone()['cnt']
        print(f"✅ 导入完成！数据库中现在有 {final_count} 条记忆")
        
        # 按类型统计
        cursor.execute("SELECT type, COUNT(*) as cnt FROM memories GROUP BY type")
        stats = cursor.fetchall()
        print("\n📋 按类型统计:")
        for stat in stats:
            print(f"   {stat['type']}: {stat['cnt']} 条")
        
        print("="*60)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()

