# -*- coding: utf-8 -*-
"""
将模型API配置添加到账号池 - Add Model API Configurations to Account Pool
"""

import sqlite3
import json
from datetime import datetime

# 模型API配置
model_api_configs = [
    {
        "service_name": "nvidia-main",
        "credential_type": "api_key",
        "api_key": "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",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions",
        "description": "NVIDIA API - Main",
        "models": [
            "z-ai/glm5",
            "z-ai/glm4.7",
            "moonshotai/kimi-k2.5",
            "minimaxai/minimax-m2.5"
        ]
    },
    {
        "service_name": "nvidia-backup1",
        "credential_type": "api_key",
        "api_key": "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",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions",
        "description": "NVIDIA API - Backup 1",
        "models": [
            "z-ai/glm5",
            "z-ai/glm4.7",
            "moonshotai/kimi-k2.5",
            "minimaxai/minimax-m2.5"
        ]
    },
    {
        "service_name": "nvidia-backup2",
        "credential_type": "api_key",
        "api_key": "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",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions",
        "description": "NVIDIA API - Backup 2",
        "models": [
            "z-ai/glm5",
            "z-ai/glm4.7",
            "moonshotai/kimi-k2.5",
            "minimaxai/minimax-m2.5"
        ]
    },
    {
        "service_name": "lmstudio",
        "credential_type": "api_key",
        "api_key": "lmstudio-local",
        "base_url": "http://127.0.0.1:1234/v1",
        "api": "openai-completions",
        "description": "LM Studio - Local",
        "models": [
            "gemma-2-2b-it:2",
            "text-embedding-nomic-embed-text-v1.5"
        ]
    }
]

# 保存到数据库
print("Adding model API configurations to account pool...")

try:
    conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
    cursor = conn.cursor()

    # 保存每个API配置
    for config in model_api_configs:
        # 创建凭证数据
        credential_data = {
            "api_key": config["api_key"],
            "base_url": config["base_url"],
            "api": config["api"],
            "models": config["models"]
        }

        # 保存到secure_credentials表
        cursor.execute("""
            INSERT OR REPLACE INTO secure_credentials
            (service_name, credential_type, encrypted_value, encryption_key_ref, description, created_at, last_used_at, expires_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            config["service_name"],
            config["credential_type"],
            json.dumps(credential_data).encode('utf-8'),
            "default",
            config["description"],
            datetime.now().isoformat(),
            None,
            None,
            json.dumps({"type": "model_api", "priority": 1 if "main" in config["service_name"] else 2})
        ))

        print(f"  Added: {config['service_name']}")

    conn.commit()
    conn.close()

    print(f"\nSuccessfully added {len(model_api_configs)} model API configurations to account pool")

except Exception as e:
    print(f"Error adding configurations: {e}")
    import traceback
    traceback.print_exc()
