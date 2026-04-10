
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Pinchtab 学习笔记到混合记忆系统
"""

import sys
from pathlib import Path

# 添加 database 目录到路径
db_path = Path(__file__).parent.parent / "memory" / "database"
sys.path.insert(0, str(db_path))

from hybrid_memory import get_memory

def add_pinchtab_memory():
    """添加 Pinchtab 学习笔记"""
    mem = get_memory()
    
    memory_id = mem.add_memory(
        type_="learning",
        title="Pinchtab - AI Agent浏览器控制工具（12MB二进制）",
        content="""
Pinchtab 是一个仅 12MB 的二进制文件，可以让任何 AI Agent 完全自动化控制浏览器。

核心特性：
- 不限开发语言、不绑定任何 SDK
- 甚至通过 curl 都能直接调用
- GitHub: https://github.com/pinchtab/pinchtab

对比 OpenClaw / Playwright 的四大优势：

1. 零配置：丢进去就能跑，直接接管本地 Chrome
2. 省钱神器：传统截图方案1页面消耗1万Tokens，Pinchtab只要800，成本直接砍掉13倍
3. 隐身潜行：自带 stealth mode，主流网站的反爬策略基本是摆设
4. 智能 Diff：每次只返回变化的内容，Agent不用反复读废话

适用场景：
- 做全自动网页操作 Agent
- 需要低成本浏览器控制的项目
- 需要绕过反爬策略的场景
- Token 预算有限的项目
        """.strip(),
        category="工具",
        tags=["Pinchtab", "浏览器", "AI Agent", "成本优化", "工具", "自动化"],
        importance=9,
        metadata={
            "source": "https://x.com/gojun315/status/2029471852633174037",
            "learned_at": "2026-03-06"
        }
    )
    
    print(f"✅ Pinchtab 学习笔记已添加到数据库 (ID: {memory_id})")
    
    # 验证添加成功
    added = mem.get_by_id(memory_id)
    if added:
        print(f"   标题: {added['title']}")
        print(f"   类型: {added['type']}")
        print(f"   重要性: {added['importance']}")
        print(f"   标签: {added['tags']}")
    
    # 显示统计
    stats = mem.get_stats()
    print(f"\n📊 当前记忆统计:")
    print(f"   总记忆数: {stats['total']}")
    print(f"   按类型分布: {stats['by_type']}")

if __name__ == "__main__":
    add_pinchtab_memory()

