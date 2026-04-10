#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
免费Token管理器 - 二饼专属技能
自动管理各大平台免费AI Token
"""
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import webbrowser
import io

# 修复Windows控制台编码
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置路径
CONFIG_DIR = Path.home() / ".openclaw" / "config"
CONFIG_FILE = CONFIG_DIR / "free_tokens.json"
TOKEN_DB_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "database"

# 支持的平台信息
PLATFORMS = {
    "chatanywhere": {
        "name": "ChatAnywhere 免费API",
        "url": "https://api.chatanywhere.tech",
        "free_amount": "200次/天",
        "register_url": "https://api.chatanywhere.tech/v1/oauth/free/render"
    },
    "groq": {
        "name": "Groq",
        "url": "https://console.groq.com/keys",
        "free_amount": "无限(速率限制)",
        "register_url": "https://console.groq.com/login"
    },
    "openrouter": {
        "name": "OpenRouter",
        "url": "https://openrouter.ai",
        "free_amount": "5美元",
        "register_url": "https://openrouter.ai/sign-up"
    },
    "together": {
        "name": "Together.ai",
        "url": "https://api.together.ai",
        "free_amount": "25美元",
        "register_url": "https://www.together.ai/sign-up"
    },
    "volcengine": {
        "name": "火山引擎方舟",
        "url": "https://www.volcengine.com/product/ark",
        "free_amount": "50元",
        "register_url": "https://www.volcengine.com/product/ark"
    },
    "doubao": {
        "name": "字节跳动豆包",
        "url": "https://www.doubao.com/openapi",
        "free_amount": "100万Token",
        "register_url": "https://www.doubao.com/openapi"
    },
    "baidu": {
        "name": "百度文心一言",
        "url": "https://cloud.baidu.com/product/wenxinworkshop",
        "free_amount": "免费额度",
        "register_url": "https://cloud.baidu.com/product/wenxinworkshop"
    },
    "tencent": {
        "name": "腾讯混元",
        "url": "https://cloud.tencent.com/product/hunyuan",
        "free_amount": "免费额度",
        "register_url": "https://cloud.tencent.com/product/hunyuan"
    },
    "aliyun": {
        "name": "阿里通义千问",
        "url": "https://www.aliyun.com/product/dashscope",
        "free_amount": "免费额度",
        "register_url": "https://www.aliyun.com/product/dashscope"
    },
    "gemini": {
        "name": "Google Gemini",
        "url": "https://ai.google.dev",
        "free_amount": "免费额度",
        "register_url": "https://ai.google.dev"
    }
}


def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_tokens():
    """加载已保存的Token"""
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载配置失败: {e}")
        return {}


def save_tokens(tokens):
    """保存Token配置"""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存配置失败: {e}")
        return False


def open_browser(url):
    """打开浏览器"""
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"打开浏览器失败: {e}")
        return False


def cmd_scan(args):
    """扫描可用平台"""
    print("\n" + "="*50)
    print("🔍 免费AI Token平台扫描")
    print("="*50 + "\n")
    
    for key, info in PLATFORMS.items():
        print(f"📌 {info['name']}")
        print(f"   免费额度: {info['free_amount']}")
        print(f"   网址: {info['register_url']}")
        print()
    
    print("="*50)
    print("💡 使用 /free-token claim <平台名> 领取Token")
    print("="*50)


def cmd_claim(args):
    """领取Token"""
    if not args:
        print("❌ 请指定平台名")
        print("可用平台:")
        for key in PLATFORMS:
            print(f"  - {key}: {PLATFORMS[key]['name']}")
        return
    
    platform = args[0].lower()
    if platform not in PLATFORMS:
        print(f"❌ 未知平台: {platform}")
        print("可用平台:")
        for key in PLATFORMS:
            print(f"  - {key}: {PLATFORMS[key]['name']}")
        return
    
    info = PLATFORMS[platform]
    print(f"\n🎯 正在打开 {info['name']} 注册页面...")
    print(f"📍 网址: {info['register_url']}")
    print("\n请在浏览器中完成注册并获取API Key")
    print("注册完成后，使用 /free-token set <平台名> <API_KEY> 保存Token\n")
    
    # 自动打开浏览器
    open_browser(info['register_url'])


def cmd_set(args):
    """手动设置Token"""
    if len(args) < 2:
        print("❌ 请提供平台名和API Key")
        print("格式: /free-token set <平台名> <API_KEY>")
        return
    
    platform = args[0].lower()
    api_key = args[1]
    
    if platform not in PLATFORMS:
        print(f"❌ 未知平台: {platform}")
        return
    
    tokens = load_tokens()
    tokens[platform] = {
        "api_key": api_key,
        "name": PLATFORMS[platform]["name"],
        "added_at": datetime.now().isoformat(),
        "last_used": None
    }
    
    if save_tokens(tokens):
        print(f"✅ {PLATFORMS[platform]['name']} Token已保存!")


def cmd_list(args):
    """列出所有Token"""
    tokens = load_tokens()
    
    print("\n" + "="*50)
    print("📋 已配置的Token列表")
    print("="*50 + "\n")
    
    if not tokens:
        print("暂无配置的Token")
        print("使用 /free-token claim <平台名> 领取免费Token")
        return
    
    for key, info in tokens.items():
        platform_info = PLATFORMS.get(key, {"name": key})
        print(f"✅ {platform_info.get('name', key)}")
        print(f"   添加时间: {info.get('added_at', '未知')}")
        print(f"   最后使用: {info.get('last_used', '未使用')}")
        print()
    
    print("="*50)


def cmd_delete(args):
    """删除Token"""
    if not args:
        print("❌ 请指定要删除的平台名")
        return
    
    platform = args[0].lower()
    tokens = load_tokens()
    
    if platform not in tokens:
        print(f"❌ 未找到平台 {platform} 的Token")
        return
    
    del tokens[platform]
    if save_tokens(tokens):
        print(f"✅ {PLATFORMS.get(platform, {}).get('name', platform)} Token已删除")


def cmd_test(args):
    """测试Token"""
    if not args:
        print("❌ 请指定要测试的平台名")
        return
    
    platform = args[0].lower()
    tokens = load_tokens()
    
    if platform not in tokens:
        print(f"❌ 平台 {platform} 未配置Token")
        return
    
    api_key = tokens[platform].get("api_key", "")
    print(f"🧪 测试 {PLATFORMS.get(platform, {}).get('name', platform)}...")
    print(f"   API Key: {api_key[:10]}...{api_key[-5:]}")
    print("\n⚠️  Token测试需要根据各平台API文档实现具体测试逻辑")
    print("   建议手动在对应平台控制台测试API是否生效")


def cmd_refresh(args):
    """刷新Token状态"""
    print("🔄 Token刷新功能")
    print("\n⚠️ 自动刷新功能需要各平台支持")
    print("   建议手动登录各平台查看剩余额度")


def cmd_help(args):
    """帮助信息"""
    print("""
🎫 免费Token管理帮助
====================

可用命令:
  /free-token scan           - 扫描所有可用平台
  /free-token claim <平台>   - 领取平台免费Token（打开注册页面）
  /free-token set <平台> <KEY> - 手动设置Token
  /free-token list           - 列出所有已配置的Token
  /free-token delete <平台>  - 删除Token
  /free-token test <平台>    - 测试Token
  /free-token refresh        - 刷新Token状态
  /free-token help           - 显示帮助

示例:
  /free-token scan
  /free-token claim volcengine
  /free-token set volcengine sk-xxxxx
  /free-token list
""")


def main():
    """主入口"""
    args = sys.argv[1:]
    
    if not args or args[0] in ['help', '-h', '--help']:
        cmd_help([])
        return
    
    cmd = args[0].lower()
    
    cmd_map = {
        'scan': cmd_scan,
        'claim': cmd_claim,
        'set': cmd_set,
        'list': cmd_list,
        'ls': cmd_list,
        'delete': cmd_delete,
        'rm': cmd_delete,
        'test': cmd_test,
        'refresh': cmd_refresh,
        'help': cmd_help
    }
    
    if cmd in cmd_map:
        cmd_map[cmd](args[1:])
    else:
        print(f"❌ 未知命令: {cmd}")
        print("使用 /free-token help 查看帮助")


if __name__ == "__main__":
    main()