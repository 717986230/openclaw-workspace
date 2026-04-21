#!/usr/bin/env python3
"""
抖音 AI 智能评论回复系统 v2
使用 requests + 官方 API，无需浏览器

依赖: requests, sqlite3
"""

import os
import time
import json
import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests

# ============ 配置 ============
CONFIG = {
    # 抖音 Cookie（从浏览器登录后复制）
    # 登录 mp.douyin.com -> F12 -> Application -> Cookies -> 复制 cookie 字符串
    'douyin_cookie': None,  # 示例: 'ttwid=xxx; sessionid=xxx; ...'
    
    # AI 配置
    'use_lm_studio': True,
    'lm_studio_ports': [1234, 8080, 41343],  # 自动检测可用端口
    'lm_studio_url': None,  # 自动设置
    'lm_studio_model': 'lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF',
    
    # 回复策略
    'auto_reply': True,
    'max_replies_per_run': 30,
    'reply_interval': 3,  # 秒
    'max_reply_length': 100,
    
    # 黑名单关键词
    'blacklist': ['微商', '加我', '微信', 'QQ号', '网址', '链接', 'http'],
    
    # 数据库
    'db_path': 'memory/database/douyin_comments.db',
}

# ============ 数据库 ============
def init_db(db_path):
    """初始化数据库"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS replied_comments (
            comment_id TEXT PRIMARY KEY,
            content TEXT,
            reply TEXT,
            replied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            date TEXT PRIMARY KEY,
            total_replied INTEGER DEFAULT 0,
            total_skipped INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

# ============ AI 回复生成 ============
def find_lm_studio_port(config: Dict) -> str:
    """自动检测 LM Studio 端口"""
    for port in config.get('lm_studio_ports', [1234, 8080]):
        try:
            r = requests.get(f'http://localhost:{port}/v1/models', timeout=2)
            if r.status_code == 200:
                print(f'  Found LM Studio on port {port}')
                return f'http://localhost:{port}/v1/chat/completions'
        except:
            pass
    return None

def generate_reply(comment: str, config: Dict) -> str:
    """使用 AI 生成回复"""
    
    prompt = f"""你是一个抖音博主，正在回复粉丝评论。
要求：
- 控制在 {config['max_reply_length']} 字以内
- 简洁自然，像真人聊天
- 可以用 emoji
- 负面评论要友善化解

粉丝评论: {comment}

回复:"""

    # 自动检测 LM Studio URL
    if config['use_lm_studio'] and not config.get('lm_studio_url'):
        config['lm_studio_url'] = find_lm_studio_port(config)

    try:
        if config['use_lm_studio'] and config.get('lm_studio_url'):
            resp = requests.post(
                config['lm_studio_url'],
                json={
                    "model": config['lm_studio_model'],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.8
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"AI Error: {e}")
    
    # Fallback
    replies = [
        "感谢支持！😊",
        "爱你哦～",
        "谢谢你的关注！",
        "来了来了！",
        "哈哈太可爱了",
        "感谢有你！",
    ]
    return random.choice(replies)

# ============ 抖音 API ============
def get_douyin_token(cookie: str) -> Dict:
    """获取访问令牌"""
    # 这里简化处理，实际需要从 cookie 中解析或刷新
    return {'cookie': cookie}

def fetch_comments(video_id: str, cookie: str = None) -> List[Dict]:
    """获取视频评论（模拟）"""
    # 实际需要调用抖音开放平台 API
    # https://open.douyin.com/video/comment/list
    
    # 演示数据
    return [
        {
            'comment_id': '1234567890',
            'user': '粉丝小明',
            'content': '视频太棒了！学到很多',
            'like_count': 52
        },
        {
            'comment_id': '1234567891', 
            'user': '路人甲',
            'content': '这个多少钱？',
            'like_count': 3
        },
        {
            'comment_id': '1234567892',
            'user': '关注用户',
            'content': '关注了，期待更多内容',
            'like_count': 8
        },
    ]

def post_reply(comment_id: str, content: str, video_id: str, cookie: str = None) -> bool:
    """发布回复（模拟）"""
    # 实际需要调用抖音 API
    # POST https://open.douyin.com/video/comment/reply
    print(f"  [POST] Reply to {comment_id}: {content}")
    return True

# ============ 主流程 ============
def run(video_url: str = None, cookie: str = None, config: Dict = None):
    """运行自动回复"""
    if config is None:
        config = CONFIG
    
    init_db(config['db_path'])
    
    print("=" * 50)
    print("抖音 AI 评论回复系统 v2")
    print("=" * 50)
    
    # 提取视频 ID
    video_id = None
    if video_url:
        # 从 URL 提取视频 ID
        if '/video/' in video_url:
            video_id = video_url.split('/video/')[-1].split('?')[0]
        elif 'video_id=' in video_url:
            video_id = video_url.split('video_id=')[-1].split('&')[0]
    
    if not video_id:
        video_id = input("请输入视频 ID 或 URL: ").strip()
        if 'video' in video_id and '/' in video_id:
            video_id = video_id.split('/video/')[-1].split('?')[0]
    
    print(f"\n视频 ID: {video_id}")
    
    # 获取评论
    print("获取评论...")
    comments = fetch_comments(video_id, cookie)
    print(f"获取到 {len(comments)} 条评论\n")
    
    # 统计
    replied = 0
    skipped = 0
    
    for comment in comments[:config['max_replies_per_run']]:
        comment_id = comment['comment_id']
        content = comment['content']
        user = comment['user']
        
        # 检查黑名单
        should_skip = any(kw in content for kw in config['blacklist'])
        
        # 检查是否已回复
        conn = sqlite3.connect(config['db_path'])
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM replied_comments WHERE comment_id = ?", (comment_id,))
        already_replied = cursor.fetchone() is not None
        conn.close()
        
        if already_replied:
            print(f"[跳过] @{user}: {content[:20]}... (已回复)")
            skipped += 1
            continue
        
        if should_skip:
            print(f"[跳过] @{user}: {content[:20]}... (黑名单)")
            skipped += 1
            continue
        
        # 生成 AI 回复
        print(f"[评论] @{user}: {content[:30]}...")
        reply = generate_reply(content, config)
        print(f"[回复] {reply}")
        
        # 发布回复
        if config['auto_reply']:
            post_reply(comment_id, reply, video_id, cookie)
            
            # 保存
            conn = sqlite3.connect(config['db_path'])
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO replied_comments (comment_id, content, reply) VALUES (?, ?, ?)",
                (comment_id, content, reply)
            )
            conn.commit()
            conn.close()
            
            replied += 1
            time.sleep(config['reply_interval'])
    
    # 统计
    print("\n" + "=" * 50)
    print(f"完成! 回复: {replied}, 跳过: {skipped}")
    print("=" * 50)
    
    return {'replied': replied, 'skipped': skipped}

# ============ 入口 ============
if __name__ == "__main__":
    import sys
    
    video_url = None
    cookie = CONFIG.get('douyin_cookie')
    
    # 命令行参数
    if len(sys.argv) > 1:
        video_url = sys.argv[1]
    if len(sys.argv) > 2:
        cookie = sys.argv[2]
    
    # 运行
    run(video_url, cookie)