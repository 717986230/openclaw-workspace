"""
查看期货数据详情
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage

# 连接 MySQL
db = DatabaseStorage(
    db_type="mysql",
    host="localhost",
    port=3306,
    user="root",
    password="root123",
    database="crawler_db"
)

# 查询期货数据
print("查询期货数据...")
results = db.get_results(limit=20)

print(f"\n找到 {len(results)} 条记录\n")

for result in results:
    print(f"任务 ID: {result['task_id']}")
    print(f"URL: {result['url']}")
    print(f"标题: {result['title']}")
    print(f"状态: {result['status']}")
    print(f"创建时间: {result['created_at']}")

    # 显示提取的数据
    if result['extracted_data']:
        data = result['extracted_data']
        if isinstance(data, list):
            print(f"数据类型: 列表，共 {len(data)} 条记录")
            if len(data) > 0:
                print("前 3 条记录:")
                for i, item in enumerate(data[:3], 1):
                    print(f"  {i}. {item}")
        else:
            print(f"数据: {data}")

    print("-" * 60)

db.close()
