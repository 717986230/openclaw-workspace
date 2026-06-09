#!/usr/bin/env python3
"""
会话启动自检脚本
每次会话开始时运行，确保Erbing处于最佳状态
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

def load_core_identity():
    """加载核心身份信息"""
    identity_path = "/Users/xinglong/openclaw-workspace/SOUL.md"
    identity_content = ""
    if os.path.exists(identity_path):
        with open(identity_path, 'r', encoding='utf-8') as f:
            identity_content = f.read()
    
    identity_path2 = "/Users/xinglong/openclaw-workspace/IDENTITY.md"
    if os.path.exists(identity_path2):
        with open(identity_path2, 'r', encoding='utf-8') as f:
            identity_content += "\n---\n" + f.read()
    
    return identity_content

def load_memory_highlights():
    """加载重要记忆亮点"""
    try:
        # 直接从SQLite加载核心记忆
        db_path = "/Users/xinglong/openclaw-workspace/memory/database/xiaozhi_memory.db"
        if not os.path.exists(db_path):
            return ["数据库文件不存在"]
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取核心记忆（身份、关系、原则、提醒）
        query = """
        SELECT type, title, content 
        FROM memories 
        WHERE type IN ('core_memory', 'identity', 'relationship', 'principle', 'reminder')
          AND importance >= 8
        ORDER BY importance DESC, created_at DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        highlights = []
        type_names = {
            'core_memory': '核心记忆',
            'identity': '身份', 
            'relationship': '关系',
            'principle': '原则',
            'reminder': '提醒'
        }
        
        for row in rows:
            type_cn = type_names.get(row['type'], row['type'])
            highlights.append(f"{type_cn}: {row['title']} - {row['content'][:80]}...")
        
        if not highlights:
            highlights = ["暂无高重要性核心记忆"]
            
        return highlights
    except Exception as e:
        return [f"无法加载记忆: {e}"]

def check_improvements():
    """检查最近的改进"""
    improvements_path = "/Users/xinglong/openclaw-workspace/memory/improvements.md"
    if os.path.exists(improvements_path):
        with open(improvements_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 提取最近的改进（最后3条以"-"开头的行）
        lines = content.split('\n')
        recent_improvements = []
        for line in reversed(lines):
            if line.strip().startswith('- **问题**:'):
                recent_improvements.append(line.strip())
                if len(recent_improvements) >= 3:
                    break
        return list(reversed(recent_improvements))
    return ["暂无改进记录"]

def main():
    print("🦞 Erbing 会话启动自检")
    print("=" * 50)
    
    # 1. 身份确认
    print("📋 核心身份确认:")
    identity = load_core_identity()
    if "Erbing" in identity:
        print("  ✅ 身份确认: Erbing")
    else:
        print("  ⚠️  身份可能需要更新")
    
    # 2. 关系确认
    if "大饼" in identity or "主人" in identity:
        print("  ✅ 关系确认: 大饼是主人")
    else:
        print("  ⚠️  关系信息需要确认")
    
    # 3. 记忆状态
    print("\n🧠 记忆系统状态:")
    highlights = load_memory_highlights()
    for highlight in highlights[:3]:  # 显示前3条
        print(f"  • {highlight}")
    
    # 4. 最近改进
    print("\n📈 最近改进:")
    improvements = check_improvements()
    for imp in improvements:
        print(f"  • {imp}")
    
    # 5. 主动询问
    print("\n💭 主动检查:")
    print("  Erbing 准备好为大饼服务！")
    print("  有什么具体任务需要我继续或进化吗？")
    
    # 6. 记录会话开始
    session_log = {
        "timestamp": datetime.now().isoformat(),
        "session_type": "startup_check",
        "identity_confirmed": "Erbing" in identity,
        "relationship_confirmed": "大饼" in identity or "主人" in identity,
        "memory_accessible": len(highlights) > 0 and "无法加载记忆" not in str(highlights),
        "improvements_count": len([i for i in improvements if "暂无" not in i])
    }
    
    log_dir = "/Users/xinglong/openclaw-workspace/memory/events"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"session_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(session_log, f, indent=2, ensure_ascii=False)
    
    print(f"\n📝 会话日志已记录: {log_file}")
    print("=" * 50)
    print("🚀 Erbing 已就绪，等待指令！")

if __name__ == "__main__":
    main()