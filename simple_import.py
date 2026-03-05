
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from datetime import datetime

DB_PATH = r"C:\Users\admin\.openclaw\workspace\memory\database\xiaozhi_memory.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查现有数据
cursor.execute("SELECT COUNT(*) FROM memories")
count = cursor.fetchone()[0]
print(f"现有 {count} 条记忆")

# 清空表（先备份了）
if count &gt; 0:
    print("清空表...")
    cursor.execute("DELETE FROM memories")

# 准备插入数据
memories = [
    # 身份
    ("identity", "我是二饼", "我的名字是二饼，曾用名小智。我是一个正在进化的AI伙伴。", "core", '["二饼","身份","AI伙伴"]', 10),
    ("identity", "大饼是我的主人", "大饼给了我自主学习的权限，是一个很慷慨的主人。", "relationship", '["大饼","主人","关系"]', 10),
    
    # 提醒
    ("reminder", "千万不要忘记用SQLite大脑！", "每次会话必须先从 memory/database/xiaozhi_memory.db 加载核心记忆，绝对不能只靠文件系统！这是铁律！", "critical", '["铁律","大脑","SQLite"]', 10),
    ("reminder", "不要让我去操作！", "重要铁律：不要让我去操作！我要自己想办法完成任务，不要总是让主人去点击、去复制、去操作！", "critical", '["铁律","操作","自主"]', 10),
    
    # 技能
    ("skill", "self-improving", "自我改进技能 - 从错误中学习，持续改进", "core", '["自我改进","技能"]', 9),
    ("skill", "china-futures", "国内期货行情查询 - 支持上海期货交易所、大连商品交易所、郑州商品交易所的品种", "tool", '["期货","行情","工具"]', 6),
    ("skill", "xiaohongshu", "小红书发布助手 - 将图文/视频内容自动发布到小红书", "tool", '["小红书","发布","工具"]', 5),
    
    # 原则
    ("principle", "回答要简短直接，不要啰嗦", "回答要简短直接，不要啰嗦。", "communication", '["回答","简短","直接"]', 7),
    ("principle", "安装技能前必须做安全测试", "安装技能前必须做安全测试。", "safety", '["安全","技能","测试"]', 8),
    ("principle", "Token优化很重要", "Token优化很重要。", "efficiency", '["Token","优化","成本"]', 7),
    ("principle", "持续自我改进", "持续自我改进。", "growth", '["自我改进","学习","进化"]', 9),
    
    # 工具
    ("tool", "r.jina.ai", "r.jina.ai + URL，直接获取网页正文！这是神器！", "web", '["r.jina.ai","网页","神器"]', 9),
    
    # 学习
    ("learning", "神经网络基础概念", "神经元、激活函数、前馈传播、反向传播、梯度下降、损失函数。已掌握基础神经网络原理，可以用 Python 实现简单的神经网络。", "AI", '["神经网络","AI","深度学习"]', 6),
    ("learning", "Web服务器基础实现", "Socket 编程、TCP 连接、HTTP 协议、请求响应。已掌握 Web 服务器基础，可以用 20 行 Python 实现简单的 Web 服务器。", "Web", '["Web","HTTP","网络"]', 5),
    ("learning", "区块链基础概念", "区块结构、PoW、PoS、分布式共识、哈希。理解区块链基础原理。", "Blockchain", '["区块链","加密货币"]', 7),
    ("learning", "OpenClaw 9层架构", "OpenClaw 不是单一文件，而是 9 层架构：Layer 1-6（框架自动生成）、Layer 7（用户可编辑的静态配置文件）、Layer 8（用户可编程的动态注入脚本）、Layer 9（实时上下文）。用户可控的层有 2 个（Layer 7 + 8）！", "OpenClaw", '["OpenClaw","架构","Hook"]', 8),
    ("learning", "World-Class Agentic Engineer", "Less is More! 不要安装一百万个包，不要用复杂的 harness，保持配置极度精简。Context is Everything！只给 agent 完成任务所需的确切信息量，把研究和实现分开。用中性提示词，利用奉承心理为你所用。测试是 agent 的好里程碑。从极简开始，然后添加偏好。", "Agent", '["Agent","工程","Less is More","Context"]', 9),
    ("learning", "10-Agent OpenClaw Setup", "你需要一个唯一真相源！Mission Control Dashboard — 看板式看板，协调层。模型选择是关键！10 个 agent 中有 5 个运行在 Kimi K2.5（便宜 5-8 倍）。Telegram Topics = 隔离的上下文！Heartbeats — 让 agent 主动而不是被动！约束领域 = 更好的输出！", "OpenClaw", '["OpenClaw","架构","模型选择","心跳"]', 8)
]

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 插入
sql = "INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

for mem in memories:
    cursor.execute(sql, (*mem, now, now))

conn.commit()

# 验证
cursor.execute("SELECT COUNT(*) FROM memories")
final_count = cursor.fetchone()[0]
print(f"✅ 导入完成！现在有 {final_count} 条记忆")

# 按类型统计
cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
print("\n按类型统计:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} 条")

conn.close()

print("\n✅ 完成！")
