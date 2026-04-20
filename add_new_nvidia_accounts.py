# -*- coding: utf-8 -*-
"""
添加新的NVIDIA API账号到账号池 - Add New NVIDIA API Accounts to Account Pool
"""

import sqlite3
import json
from datetime import datetime

# 新的NVIDIA API账号配置
new_nvidia_accounts = [
    {
        "service_name": "nvidia-account1",
        "credential_type": "api_key",
        "email": "clcrgyfn7708@wpnhx222.132103.xyz",
        "password": "fGgxi@opT0w6",
        "api_key": "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",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions",
        "website": "https://build.nvidia.com/",
        "description": "NVIDIA API - Account 1",
        "models": [
            "z-ai/glm5",
            "z-ai/glm4.7",
            "moonshotai/kimi-k2.5",
            "minimaxai/minimax-m2.5"
        ]
    },
    {
        "service_name": "nvidia-account2",
        "credential_type": "api_key",
        "email": "hkfrdbhw4774@gwcjl207.132103.xyz",
        "password": "5AsR4cj1^DoA",
        "api_key": "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",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api": "openai-completions",
        "website": "https://build.nvidia.com/",
        "description": "NVIDIA API - Account 2",
        "models": [
            "z-ai/glm5",
            "z-ai/glm4.7",
            "moonshotai/kimi-k2.5",
            "minimaxai/minimax-m2.5"
        ]
    }
]

# 保存到数据库
print("Adding new NVIDIA API accounts to account pool...")

try:
    conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
    cursor = conn.cursor()

    # 保存每个API配置
    for account in new_nvidia_accounts:
        # 创建凭证数据
        credential_data = {
            "email": account["email"],
            "password": account["password"],
            "api_key": account["api_key"],
            "base_url": account["base_url"],
            "api": account["api"],
            "website": account["website"],
            "models": account["models"]
        }

        # 保存到secure_credentials表
        cursor.execute("""
            INSERT OR REPLACE INTO secure_credentials
            (service_name, credential_type, encrypted_value, encryption_key_ref, description, created_at, last_used_at, expires_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            account["service_name"],
            account["credential_type"],
            json.dumps(credential_data).encode('utf-8'),
            "default",
            account["description"],
            datetime.now().isoformat(),
            None,
            None,
            json.dumps({"type": "model_api", "priority": 2, "provider": "nvidia"})
        ))

        print(f"  Added: {account['service_name']}")
        print(f"    Email: {account['email']}")
        print(f"    API Key: {account['api_key'][:20]}...")

    conn.commit()
    conn.close()

    print(f"\nSuccessfully added {len(new_nvidia_accounts)} new NVIDIA API accounts to account pool")

except Exception as e:
    print(f"Error adding accounts: {e}")
    import traceback
    traceback.print_exc()
