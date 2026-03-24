#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试API Key"""
import requests
import json

tests = [
    ("ChatAnywhere", "https://api.chatanywhere.tech/v1/chat/completions", "sk-REDACTED", "gpt-4o-mini"),
    ("Groq", "https://api.groq.com/openai/v1/chat/completions", "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", "llama-3.1-70b-versatile"),
    ("OpenRouter", "https://openrouter.ai/api/v1/chat/completions", "sk-or-v1-REDACTED", "openai/gpt-4o-mini"),
    ("Together.ai", "https://api.together.ai/v1/chat/completions", "key_CZ2YPMGw9wzy761v8T4ei", "meta-llama/Llama-3.1-70B-Instruct-Turbo"),
]

for name, url, key, model in tests:
    print(f"Testing {name}...", end=" ")
    try:
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        if "openrouter" in url:
            headers["HTTP-Referer"] = "https://openclaw.ai"
        r = requests.post(url, headers=headers, json={"model": model, "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 10}, timeout=20)
        if r.status_code == 200:
            print(f"OK ({r.status_code})")
        else:
            print(f"FAIL ({r.status_code}): {r.text[:80]}")
    except Exception as e:
        print(f"ERROR: {e}")