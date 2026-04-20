import sqlite3
from datetime import datetime

DB = 'memory/database/xiaozhi_memory.db'
conn = sqlite3.connect(DB)
cursor = conn.cursor()
now = datetime.now().isoformat()

cursor.execute("""
INSERT INTO memories (type, title, content, category, tags, importance, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    'learning',
    'Ollama Cloud API 账号入池',
    'Ollama Cloud 是 ollama.com 官方云服务，提供 OpenAI 兼容 API（/v1/chat/completions）。'
    '用户提供了第三方中转服务账号：域名 455045643.xyz，API key: ae7c9aad83814cba890284aad7f8a49a，'
    '用户名: usermo5peagmtqqr53@455045643.xyz，密码: upX*RbHKNhyoun。'
    'base_url: https://ollama.com/v1，models: qwen3-coder:480b, deepseek-v3.1:671b, gpt-oss:120b, gpt-oss:20b, glm-4.6 等。'
    '已存入 secure_credentials 表（id=7），type=model_api，priority=3。'
    '参考：CSDN文章 blog.csdn.net/m0_73579990/article/details/154578187。',
    'knowledge',
    '["ollama","model-api","account-pool","qwen3","deepseek","api-key"]',
    8,
    now,
    now
))

conn.commit()
print('memory saved, id:', cursor.lastrowid)
conn.close()