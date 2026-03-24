#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动获取各平台API Key - 二饼专属
使用已登录的浏览器会话获取API Key
"""
import json
import os
import sys
import time
import io
from pathlib import Path
from datetime import datetime

# 修复Windows控制台编码
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 配置路径
CONFIG_DIR = Path.home() / ".openclaw" / "config"
CONFIG_FILE = CONFIG_DIR / "free_tokens.json"

def ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_tokens():
    ensure_config_dir()
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_tokens(tokens):
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def get_api_keys():
    """使用Selenium获取各平台API Key"""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("\n🚀 启动Chrome浏览器...")
    
    # 使用已存在的Chrome会话（不打开新窗口）
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-popup-blocking')
    # 复用已有浏览器 session
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        # 使用webdriver-manager自动管理ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ 浏览器连接成功\n")
    except Exception as e:
        print(f"❌ 连接浏览器失败: {e}")
        print("\n请先手动打开Chrome并启用远程调试：")
        print("在Chrome快捷方式后添加: --remote-debugging-port=9222")
        import traceback
        traceback.print_exc()
        return {}
    
    results = {}
    
    # 平台配置
    platforms = [
        {
            "name": "chatanywhere",
            "display": "ChatAnywhere 免费API",
            "url": "https://api.chatanywhere.tech/v1/oauth/free/render",
            "key_selectors": ["code", ".api-key", "#apiKey", "[class*='key']", "pre"],
            "description": "免费API转发"
        },
        {
            "name": "groq",
            "display": "Groq",
            "url": "https://console.groq.com/keys",
            "key_selectors": ["[data-testid='api-key']", ".api-key-value", "code", "pre"],
            "description": "超高速开源模型"
        },
        {
            "name": "openrouter",
            "display": "OpenRouter",
            "url": "https://openrouter.ai/settings/keys",
            "key_selectors": ["[class*='key']", "code", "pre", ".api-key"],
            "description": "模型最全"
        },
        {
            "name": "together",
            "display": "Together.ai",
            "url": "https://api.together.ai/settings/api-keys",
            "key_selectors": ["[class*='key']", "code", "pre"],
            "description": "25美元免费额度"
        },
    ]
    
    for platform in platforms:
        print(f"\n{'='*50}")
        print(f"📋 正在获取: {platform['display']}")
        print(f"🔗 {platform['url']}")
        print('='*50)
        
        try:
            driver.get(platform['url'])
            time.sleep(3)  # 等待页面加载
            
            # 尝试多种选择器获取API Key
            api_key = None
            for selector in platform['key_selectors']:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if 'sk-' in text and len(text) > 20:
                            api_key = text
                            break
                    if api_key:
                        break
                except:
                    continue
            
            if api_key:
                # 提取第一个API Key
                lines = api_key.split('\n')
                for line in lines:
                    if 'sk-' in line:
                        api_key = line.strip()
                        break
                
                print(f"✅ 找到API Key: {api_key[:15]}...")
                results[platform['name']] = {
                    "api_key": api_key,
                    "name": platform['display'],
                    "url": platform['url'],
                    "added_at": datetime.now().isoformat()
                }
            else:
                print(f"⚠️ 未找到API Key")
                print(f"   页面标题: {driver.title}")
                
                # 保存页面截图供调试
                try:
                    driver.save_screenshot(f"debug_{platform['name']}.png")
                    print(f"   已保存截图: debug_{platform['name']}.png")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ 获取失败: {e}")
    
    print(f"\n{'='*50}")
    print("📊 获取结果汇总")
    print('='*50)
    
    if results:
        for name, info in results.items():
            print(f"✅ {name}: {info['api_key'][:20]}...")
    else:
        print("❌ 未能获取到任何API Key")
        print("\n可能原因:")
        print("1. 浏览器未登录对应平台")
        print("2. 页面需要验证码")
        print("3. API Key页面结构变化")
    
    driver.quit()
    return results

def main():
    print("""
🎫 自动获取平台API Key
======================
    """)
    
    # 获取API Keys
    results = get_api_keys()
    
    if results:
        # 保存到配置
        tokens = load_tokens()
        tokens.update(results)
        
        if save_tokens(tokens):
            print(f"\n✅ 成功保存 {len(results)} 个API Key到配置")
        else:
            print("\n❌ 保存失败")
    else:
        print("\n⚠️ 没有获取到任何API Key")

if __name__ == "__main__":
    main()