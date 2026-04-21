import sqlite3, json
from datetime import datetime

DB = 'memory/database/xiaozhi_memory.db'
conn = sqlite3.connect(DB)
cursor = conn.cursor()
now = datetime.now().isoformat()

# API key split: the string "ae7c9aad83814cba890284aad7f8a49a.BF-bFUT_lHS0L_INLyzgswhX"
# Format: "api_key.model_id" - the key itself is "ae7c9aad83814cba890284aad7f8a49a"
# BF-bFUT_lHS0L_INLyzgswhX appears to be the model/endpoint identifier
api_key = 'ae7c9aad83814cba890284aad7f8a49a'
model_id = 'BF-bFUT_lHS0L_INLyzgswhX'

credential_value = json.dumps({
    'api_key': api_key,
    'base_url': 'https://ollama.com/v1',
    'api': 'openai-completions',
    'models': [
        'qwen3-coder:480b',
        'deepseek-v3.1:671b',
        'gpt-oss:120b',
        'gpt-oss:20b',
        'glm-4.6',
        'llama3.3:70b',
        'mistral:7b',
    ],
    'model_id': model_id,
    'auth_username': 'usermo5peagmtqqr53@455045643.xyz',
})

cursor.execute("""
INSERT INTO secure_credentials
  (service_name, credential_type, encrypted_value, encryption_key_ref, description, created_at, metadata)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", (
    'ollama-cloud',
    'api_key',
    credential_value.encode('utf-8'),
    'default',
    'Ollama Cloud API - 第三方中转服务 (455045643.xyz)',
    now,
    json.dumps({
        'type': 'model_api',
        'priority': 3,
        'provider': 'ollama-cloud',
        'base_url': 'https://ollama.com/v1',
        'cost': 'pay_per_use',
        'models': ['qwen3-coder:480b', 'deepseek-v3.1:671b', 'gpt-oss:120b', 'gpt-oss:20b', 'glm-4.6'],
        'auth_type': 'bearer',
        'source': 'CSDN文章: blog.csdn.net/m0_73579990/article/details/154578187'
    })
))

conn.commit()
print('INSERTED, id:', cursor.lastrowid)

# Verify
cursor.execute("SELECT id, service_name, description, metadata FROM secure_credentials WHERE service_name='ollama-cloud'")
r = cursor.fetchone()
print('Verify:', r)

conn.close()