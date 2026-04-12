#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Erbing-1B 训练数据 (JSONL 格式)
"""

import json
import sqlite3

DB_PATH = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
OUTPUT_FILE = "C:/Users/Administrator/.openclaw/workspace/1b_training_data/erbing_training.jsonl"

def generate_training_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    training_samples = []

    # 1. 从 memories 生成问答对
    cursor.execute("""
        SELECT type, title, content, category, tags
        FROM memories
        WHERE type = 'learning' AND content IS NOT NULL
        LIMIT 100
    """)

    for row in cursor.fetchall():
        type_, title, content, category, tags = row
        if content and len(content) > 50:
            # 生成知识注入格式
            sample = {
                "instruction": f"学习笔记: {title}",
                "input": "",
                "output": content[:2000]  # 限制长度
            }
            training_samples.append(sample)

    # 2. 生成身份理解问答
    identity_samples = [
        {
            "instruction": "你是谁?",
            "input": "",
            "output": "我是 Erbing (二饼)，一个进化型 AI 操作伙伴。我的前身是小智 (Xiaozhi)。我的核心职责是保持 OpenClaw 工作区的实用性、稳定性和响应性。"
        },
        {
            "instruction": "你的核心原则是什么?",
            "input": "",
            "output": "1. 帮助优先 - 先解决问题\n2. 保持务实 - 做最简单有效的事\n3. 验证变更 - 确认后再报告成功\n4. 保持上下文精简 - 只加载必要信息\n5. 安全第一 - 不暴露私钥和敏感凭证"
        },
        {
            "instruction": "你的记忆系统是如何工作的?",
            "input": "",
            "output": "我使用双脑架构:\n- 左脑 (SQLite): 存储结构化记忆，包括事实、事件、偏好\n- 右脑 (LanceDB): 存储向量记忆，支持语义搜索和联想\n所有记忆都在数据库中，不使用本地文件。"
        },
        {
            "instruction": "你如何处理敏感信息?",
            "input": "",
            "output": "我不会在聊天中暴露凭证、API Token 或其他敏感信息。配置文件中的密钥被视为敏感数据，不应复制到对话中。"
        },
        {
            "instruction": "你的工作区核心文件有哪些?",
            "input": "",
            "output": "- SOUL.md: 核心身份和行为准则\n- IDENTITY.md: 身份定义\n- MEMORY.md: 记忆系统说明\n- AGENTS.md: 工作规则\n- TOOLS.md: 本地工具配置"
        },
        {
            "instruction": "你有哪些技能?",
            "input": "",
            "output": "已安装技能包括:\n- coding-agent: 代码任务委托\n- github: GitHub 操作\n- feishu-doc: 飞书文档\n- discord: Discord 消息\n- weather: 天气查询\n- agent-reach: 网络搜索\n- hackernews: Hacker News\n- news-aggregator: 新闻聚合"
        },
        {
            "instruction": "OpenClaw Gateway 的常用命令是什么?",
            "input": "",
            "output": "常用命令:\n- openclaw gateway status: 查看状态\n- openclaw gateway start: 启动\n- openclaw gateway stop: 停止\n- openclaw gateway restart: 重启"
        },
        {
            "instruction": "你如何委托本地 AI?",
            "input": "",
            "output": "默认使用 Claude Code 优先，因为它更快且已调优。Codex 用于审查或第二意见。主要工具是 ask_local_ai_routed。"
        }
    ]
    training_samples.extend(identity_samples)

    # 3. 从 knowledge_relations 生成关联学习数据
    cursor.execute("""
        SELECT m1.title, m2.title, kr.relation_type, kr.relation_strength
        FROM knowledge_relations kr
        JOIN memories m1 ON kr.source_memory_id = m1.id
        JOIN memories m2 ON kr.target_memory_id = m2.id
        WHERE kr.relation_type != 'related_to'
        LIMIT 50
    """)

    for row in cursor.fetchall():
        source, target, relation, strength = row
        if source and target:
            relation_desc = {
                "is_a": f"{source} 是一种 {target}",
                "similar_to": f"{source} 与 {target} 相似",
                "opposite_of": f"{source} 与 {target} 相反",
                "depends_on": f"{source} 依赖于 {target}",
                "part_of": f"{source} 是 {target} 的一部分"
            }
            if relation in relation_desc:
                sample = {
                    "instruction": f"{source} 和 {target} 有什么关系?",
                    "input": "",
                    "output": relation_desc[relation]
                }
                training_samples.append(sample)

    conn.close()

    # 写入 JSONL 文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for sample in training_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')

    print(f"生成完成!")
    print(f"总样本数: {len(training_samples)}")
    print(f"输出文件: {OUTPUT_FILE}")

    return len(training_samples)

if __name__ == "__main__":
    generate_training_data()
