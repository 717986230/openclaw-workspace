import sqlite3

# 连接数据库
conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_nodes'")
table_exists = cursor.fetchone()

if table_exists:
    # 检查表结构
    cursor.execute("PRAGMA table_info(knowledge_nodes)")
    columns = cursor.fetchall()
    print("Existing table structure:")
    for col in columns:
        print(f"  {col}")
    
    # 删除旧表
    cursor.execute("DROP TABLE knowledge_nodes")
    print("Old table dropped")

if table_exists:
    # 检查表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_edges'")
    edge_exists = cursor.fetchone()
    if edge_exists:
        cursor.execute("DROP TABLE knowledge_edges")
        print("Old edges table dropped")

conn.commit()
conn.close()

print("Ready to create new tables")
