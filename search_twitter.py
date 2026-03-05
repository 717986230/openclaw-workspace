
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter 搜索脚本 - 使用 twscrape
搜索原油大事件和战火消息
"""

import asyncio
import sys
from twscrape import API, gather
from twscrape.logger import set_log_level

# 降低日志级别
set_log_level("ERROR")

async def main():
    print("="*60)
    print("  🐦 Twitter 搜索 - 原油大事件")
    print("="*60)
    print()
    
    # 初始化 API
    api = API()
    
    # 从 cookies 文件添加账号
    try:
        # 读取 cookies
        cookies = {}
        with open('twitter_cookies.txt', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split('\t')
                if len(parts) &gt;= 7:
                    key = parts[5]
                    value = parts[6]
                    cookies[key] = value
        
        print("✅ Cookies 已加载")
        print(f"   找到 {len(cookies)} 个 cookie")
        print()
        
        # 这里需要完整的账号信息，twscrape 需要：
        # username, password, email, email_password, cookies
        
        # 由于我们只有 cookies，让我们用另一种方式
        # 直接用 Playwright 或浏览器方式会更简单
        
        print("⚠️  twscrape 需要完整账号信息")
        print("   我们只有 cookies，让我用更简单的方式...")
        print()
        print("💡 建议：")
        print("   1. 直接在浏览器中搜索")
        print("   2. 或者我帮你用其他方式")
        print()
        
    except FileNotFoundError:
        print("❌ 找不到 twitter_cookies.txt")
        return
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    print("="*60)
    print("  📋 搜索关键词建议")
    print("="*60)
    print()
    print("🔥 战火消息：")
    print("   war conflict military attack")
    print("   最新战火消息")
    print()
    print("🛢️ 原油大事件：")
    print("   oil crude prices major event")
    print("   OPEC production cut")
    print("   原油价格 大涨")
    print()
    print("="*60)
    print()
    print("💡 请在浏览器中搜索以上关键词，然后把结果复制给我！")
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
        sys.exit(0)
