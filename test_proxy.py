
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

proxies = {
    'http': 'http://127.0.0.1:7891',
    'https': 'http://127.0.0.1:7891',
}

print("🔍 测试代理连接...")
print(f"代理: {proxies}")
print()

try:
    # 测试 1: 检查代理是否工作
    print("测试 1: 连接到 Hacker News API...")
    r = requests.get(
        'https://hn.algolia.com/api/v1/search?query=oil&tags=story&hitsPerPage=3',
        proxies=proxies,
        timeout=10
    )
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        hits = data.get('hits', [])
        print(f"找到 {len(hits)} 条结果")
        print()
        print("🔥 第一条结果:")
        if hits:
            print(f"标题: {hits[0].get('title', 'N/A')}")
            print(f"作者: {hits[0].get('author', 'N/A')}")
            print(f"热度: {hits[0].get('points', 'N/A')} 点")
            print(f"链接: {hits[0].get('url', 'N/A')}")
        print()
        print("✅ 代理工作正常！")
    else:
        print(f"❌ 请求失败: {r.text}")
        
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
