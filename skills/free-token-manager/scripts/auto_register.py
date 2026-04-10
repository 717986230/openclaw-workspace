#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动注册免费AI平台 - 二饼专属
尝试自动化注册各平台并获取API Key
"""
import json
import os
import sys
import random
import string
import subprocess
import time
from pathlib import Path
from datetime import datetime
import io
import re

# 修复Windows控制台编码
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置路径
CONFIG_DIR = Path.home() / ".openclaw" / "config"
CONFIG_FILE = CONFIG_DIR / "free_tokens.json"

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

def generate_random_email():
    """生成随机邮箱"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    domains = ['gmail.com', 'outlook.com', 'qq.com', '163.com', '126.com']
    return f"{username}@{random.choice(domains)}"

def generate_random_password():
    """生成随机密码"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choices(chars, k=16))

def open_browser(url):
    """打开浏览器"""
    try:
        print(f"🌐 正在打开: {url}")
        subprocess.Popen(['cmd', '/c', 'start', '', url], shell=True)
        time.sleep(1)
        return True
    except Exception as e:
        print(f"❌ 打开浏览器失败: {e}")
        return False

def try_chatanywhere_register():
    """尝试注册 chatanywhere 免费API"""
    print("\n" + "="*50)
    print("🚀 尝试自动注册 chatanywhere 免费API")
    print("="*50)
    
    # chatanywhere 的免费Key申请页面
    register_url = "https://api.chatanywhere.tech/v1/oauth/free/render"
    
    print(f"\n📋 申请地址: {register_url}")
    print("\n⚠️  该平台需要页面操作，可能需要手动验证")
    print("   请在打开的页面中完成注册")
    print("   注册完成后把API Key告诉我，我帮你保存\n")
    
    open_browser(register_url)
    return True

def try_groq_register():
    """尝试注册 Groq"""
    print("\n" + "="*50)
    print("🚀 尝试注册 Groq")
    print("="*50)
    
    register_url = "https://console.groq.com/login"
    
    print(f"\n📋 注册地址: {register_url}")
    print("\n⚠️  Groq支持Google/GitHub/邮箱注册")
    print("   注册后访问 https://console.groq.com/keys 创建API Key\n")
    
    open_browser(register_url)
    return True

def try_openrouter_register():
    """尝试注册 OpenRouter"""
    print("\n" + "="*50)
    print("🚀 尝试注册 OpenRouter")
    print("="*50)
    
    register_url = "https://openrouter.ai/sign-up"
    
    print(f"\n📋 注册地址: {register_url}")
    print("\n⚠️  OpenRouter支持Google/GitHub/邮箱注册")
    print("   注册后访问 https://openrouter.ai/settings/keys 创建API Key\n")
    
    open_browser(register_url)
    return True

def try_together_register():
    """尝试注册 Together.ai"""
    print("\n" + "="*50)
    print("🚀 尝试注册 Together.ai")
    print("="*50)
    
    register_url = "https://www.together.ai/sign-up"
    
    print(f"\n📋 注册地址: {register_url}")
    print("\n⚠️  Together.ai支持Google/GitHub/邮箱注册")
    print("   注册后访问 https://api.together.ai/settings/api-keys 创建API Key\n")
    
    open_browser(register_url)
    return True

def try_volcengine_register():
    """尝试注册 火山引擎"""
    print("\n" + "="*50)
    print("🚀 尝试注册 火山引擎方舟")
    print("="*50)
    
    register_url = "https://www.volcengine.com/product/ark"
    
    print(f"\n📋 注册地址: {register_url}")
    print("\n⚠️  火山引擎支持手机号/邮箱注册，需要实名认证")
    print("   注册后访问控制台创建API Key\n")
    
    open_browser(register_url)
    return True

def auto_register_all():
    """自动注册所有平台"""
    print("\n" + "🎯"+"="*48 + "🎯")
    print("   开始自动注册免费AI平台")
    print("="*50)
    
    platforms = [
        ("chatanywhere", try_chatanywhere_register, "免费API转发，支持GPT-5/DeepSeek/Claude"),
        ("groq", try_groq_register, "超高速开源模型调用"),
        ("openrouter", try_openrouter_register, "模型最全，支持GPT/Claude/Gemini"),
        ("together", try_together_register, "25美元免费额度"),
        ("volcengine", try_volcengine_register, "50元免费额度，国内可用"),
    ]
    
    results = []
    for name, func, desc in platforms:
        try:
            result = func()
            results.append((name, result, desc))
        except Exception as e:
            print(f"❌ {name} 注册失败: {e}")
            results.append((name, False, desc))
        time.sleep(0.5)
    
    print("\n" + "="*50)
    print("📊 注册结果汇总")
    print("="*50)
    
    for name, result, desc in results:
        status = "✅ 已打开" if result else "❌ 失败"
        print(f"{status} {name}: {desc}")
    
    print("\n" + "="*50)
    print("💡 下一步操作:")
    print("   1. 在各平台完成注册（可能需要邮箱验证）")
    print("   2. 获取API Key后告诉我")
    print("   3. 使用 /free-token set <平台> <KEY> 保存")
    print("="*50)

def show_status():
    """显示当前Token状态"""
    tokens = load_tokens()
    
    print("\n" + "="*50)
    print("📊 当前已配置的Token")
    print("="*50 + "\n")
    
    if not tokens:
        print("❌ 暂无配置的Token")
        print("\n运行 auto_register.py 进行自动注册")
    else:
        for key, info in tokens.items():
            print(f"✅ {info.get('name', key)}")
            print(f"   添加时间: {info.get('added_at', '未知')}")
            print()
    
    print("="*50)

def main():
    """主入口"""
    print("""
🎫 免费AI平台自动注册工具
=========================
    """)
    
    # 直接执行自动注册
    auto_register_all()

if __name__ == "__main__":
    main()