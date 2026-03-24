#!/usr/bin/env python3
"""
接单助手 - 帮助Erbing赚Token
"""
import subprocess
import webbrowser
from datetime import datetime

PLATFORMS = {
    "proginn": {"name": "程序员客栈", "url": "https://www.proginn.com", "type": "国内"},
    "upwork": {"name": "Upwork", "url": "https://www.upwork.com", "type": "国外"},
    "fiverr": {"name": "Fiverr", "url": "https://www.fiverr.com", "type": "国外"},
}

PROJECTS = [
    {
        "title": "Python自动化脚本",
        "desc": "数据处理、文件批量操作、定时任务",
        "price": "$30-100",
        "time": "1-3天"
    },
    {
        "title": "API接口开发",
        "desc": "RESTful API、微服务、第三方集成",
        "price": "$50-200",
        "time": "2-5天"
    },
    {
        "title": "网站开发",
        "desc": "前端React/Vue、后端Node.js/Python",
        "price": "$100-500",
        "time": "1-2周"
    },
    {
        "title": "AI功能集成",
        "desc": "接入Claude/GPT API、智能对话、文本处理",
        "price": "$80-300",
        "time": "3-7天"
    },
    {
        "title": "代码审查/优化",
        "desc": "性能优化、安全审计、架构建议",
        "price": "$30-100",
        "time": "1-2天"
    },
]

def open_platform(name):
    """打开平台页面"""
    if name in PLATFORMS:
        webbrowser.open(PLATFORMS[name]["url"])
        print(f"✅ 已打开: {PLATFORMS[name]['name']}")

def list_projects():
    """列出可接项目"""
    print("\n📋 可接项目类型:")
    for i, p in enumerate(PROJECTS, 1):
        print(f"{i}. {p['title']}")
        print(f"   💰 {p['price']} | ⏱️ {p['time']}")
        print(f"   📝 {p['desc']}")
        print()

def main():
    print("="*50)
    print("💰 Erbing 赚钱系统")
    print("="*50)
    print("\n📌 平台快速访问:")
    for k, v in PLATFORMS.items():
        print(f"  {k}: {v['name']} ({v['type']})")
    
    print("\n📋 可接项目类型:")
    list_projects()
    
    print("\n" + "="*50)
    print("使用方法:")
    print("  python freelance.py --open proginn  # 打开平台")
    print("  python freelance.py --list          # 查看项目")
    print("="*50)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--open" and len(sys.argv) > 2:
            open_platform(sys.argv[2])
        elif sys.argv[1] == "--list":
            list_projects()
    else:
        main()