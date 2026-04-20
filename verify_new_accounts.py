import sqlite3
import json

conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 查询所有模型API配置
cursor.execute("SELECT * FROM secure_credentials WHERE credential_type = 'api_key'")
rows = cursor.fetchall()

print(f"Total API configurations: {len(rows)}")
print()

for row in rows:
    id = row[0]
    service_name = row[1]
    encrypted_value = row[3]
    description = row[5]

    # 解密凭证数据
    credential_data = json.loads(encrypted_value.decode('utf-8'))

    # 解析元数据（处理None情况）
    metadata = json.loads(row[8]) if row[8] else {}

    print(f"ID: {id}")
    print(f"Service: {service_name}")
    print(f"Description: {description}")
    print(f"Email: {credential_data.get('email', 'N/A')}")
    print(f"API Key: {credential_data.get('api_key', 'N/A')[:20]}...")
    print(f"Base URL: {credential_data.get('base_url', 'N/A')}")
    print(f"Models: {', '.join(credential_data.get('models', []))}")
    print(f"Priority: {metadata.get('priority', 'N/A')}")
    print()

conn.close()
