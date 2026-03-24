#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一AI调用接口 - 二饼专属
自动选择最快最优的免费API
"""
import requests
import json
import time

# API配置 - 按速度优先级排序
# Groq最快(硬件加速) > ChatAnywhere(国内直连) > OpenRouter(模型全) > Together
APIS = {
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": "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",
        "model": "llama-3.3-70b-versatile",
        "priority": 1,  # 最快
        "desc": "Groq - 超快Llama"
    },
    "chatanywhere": {
        "url": "https://api.chatanywhere.tech/v1/chat/completions",
        "key": "sk-YORpYgpef6QBfaZNBH1gdmOUdB0dTz9nHQZb3Q4F24umguwl",
        "model": "gpt-4o-mini",
        "priority": 2,  # 国内快
        "desc": "ChatAnywhere - GPT-4o-mini"
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": "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",
        "model": "openai/gpt-4o-mini",
        "priority": 3,  # 模型全
        "desc": "OpenRouter - 模型最全"
    },
    "together": {
        "url": "https://api.together.ai/v1/chat/completions",
        "key": "tgp_v1_btVaGaTWY37Q4Cms81wAoK6OfMzQtiWbXh005CXNCAo",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "priority": 4,  # 备选
        "desc": "Together - Llama 3.3"
    }
}

# 按优先级排序
SORTED_APIS = sorted(APIS.items(), key=lambda x: x[1]["priority"])

def chat(prompt, api_name=None, max_retries=3):
    """发送聊天请求 - 自动选择最优API"""
    
    # 确定要尝试的API列表
    if api_name and api_name in APIS:
        apis_to_try = [(api_name, APIS[api_name])]
    else:
        apis_to_try = SORTED_APIS
    
    last_error = None
    
    for name, api in apis_to_try:
        for retry in range(max_retries):
            try:
                headers = {"Authorization": f"Bearer {api['key']}", "Content-Type": "application/json"}
                if "openrouter" in api["url"]:
                    headers["HTTP-Referer"] = "https://openclaw.ai"
                
                start_time = time.time()
                
                r = requests.post(api["url"], headers=headers, json={
                    "model": api["model"],
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                }, timeout=60)
                
                elapsed = time.time() - start_time
                
                if r.status_code == 200:
                    result = r.json()
                    response = result["choices"][0]["message"]["content"]
                    print(f"[{api['desc']}] 响应时间: {elapsed:.2f}秒")
                    return response
                elif r.status_code == 402:
                    print(f"[{name}] 余额不足，跳过")
                    break  # 余额不足，不重试
                else:
                    print(f"[{name}] 错误 {r.status_code}: {r.text[:50]}")
                    last_error = r.text
                    
            except requests.exceptions.Timeout:
                print(f"[{name}] 超时 (重试 {retry+1}/{max_retries})")
            except Exception as e:
                print(f"[{name}] 异常: {e}")
                last_error = str(e)
        
        # 如果指定了特定API，失败就不尝试其他的
        if api_name:
            break
    
    return f"抱歉，所有API都不可用。最后错误: {last_error}"

if __name__ == "__main__":
    import sys
    
    # 解析参数
    api_name = None
    prompt_parts = []
    
    for arg in sys.argv[1:]:
        if arg in APIS:
            api_name = arg
        else:
            prompt_parts.append(arg)
    
    prompt = " ".join(prompt_parts) if prompt_parts else "Hi"
    
    result = chat(prompt, api_name)
    print("\n" + "="*50)
    print(result)