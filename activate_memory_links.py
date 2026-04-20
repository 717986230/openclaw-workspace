"""
激活记忆链接和记忆关联系统
"""

import os
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple
import re

print('=' * 60)
print('激活记忆链接和记忆关联系统')
print('=' * 60)
print()

# 连接数据库
db_path = 'memory/database/xiaozhi_memory.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 激活记忆链接
print('【1/2】激活记忆链接')

# 获取所有记忆
cursor.execute('''
    SELECT id, title, content, tags, category
    FROM memories
''')
memories = cursor.fetchall()

print(f'  总记忆数: {len(memories)}')

# 创建记忆链接
link_count = 0

for i, (id1, title1, content1, tags1, category1) in enumerate(memories):
    for j, (id2, title2, content2, tags2, category2) in enumerate(memories):
        if i >= j:  # 避免重复和自链接
            continue

        # 基于标签创建链接
        if tags1 and tags2:
            try:
                tags1_list = json.loads(tags1)
                tags2_list = json.loads(tags2)

                # 检查是否有共同标签
                common_tags = set(tags1_list) & set(tags2_list)
                if common_tags:
                    # 创建链接
                    cursor.execute('''
                        INSERT INTO memory_links (memory_id_1, memory_id_2, link_type, strength, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id1, id2, 'tag_based', len(common_tags), datetime.now().isoformat()))
                    link_count += 1
            except:
                pass

        # 基于分类创建链接
        if category1 and category2 and category1 == category2:
            cursor.execute('''
                INSERT INTO memory_links (memory_id_1, memory_id_2, link_type, strength, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (id1, id2, 'category_based', 1, datetime.now().isoformat()))
            link_count += 1

print(f'  [OK] 创建了 {link_count} 条记忆链接')

# 2. 激活记忆关联
print()
print('【2/2】激活记忆关联')

# 创建记忆关联
assoc_count = 0

for i, (id1, title1, content1, tags1, category1) in enumerate(memories):
    for j, (id2, title2, content2, tags2, category2) in enumerate(memories):
        if i >= j:  # 避免重复和自关联
            continue

        # 基于内容相似度创建关联
        if content1 and content2:
            # 简单的相似度计算（基于共同词汇）
            words1 = set(re.findall(r'\w+', content1.lower()))
            words2 = set(re.findall(r'\w+', content2.lower()))

            if words1 and words2:
                common_words = words1 & words2
                similarity = len(common_words) / max(len(words1), len(words2))

                if similarity > 0.3:  # 相似度阈值
                    cursor.execute('''
                        INSERT INTO memory_associations (memory_a_id, memory_b_id, association_type, relevance_score, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id1, id2, 'content_similarity', similarity, datetime.now().isoformat()))
                    assoc_count += 1

        # 基于时间序列创建关联
        cursor.execute('''
            SELECT created_at FROM memories WHERE id = ?
        ''', (id1,))
        created_at1 = cursor.fetchone()[0]

        cursor.execute('''
            SELECT created_at FROM memories WHERE id = ?
        ''', (id2,))
        created_at2 = cursor.fetchone()[0]

        if created_at1 and created_at2:
            try:
                time1 = datetime.fromisoformat(created_at1)
                time2 = datetime.fromisoformat(created_at2)
                time_diff = abs((time1 - time2).total_seconds())

                # 如果时间差小于 1 小时，创建关联
                if time_diff < 3600:
                    cursor.execute('''
                        INSERT INTO memory_associations (memory_a_id, memory_b_id, association_type, relevance_score, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id1, id2, 'temporal_proximity', 1 - time_diff/3600, datetime.now().isoformat()))
                    assoc_count += 1
            except:
                pass

print(f'  [OK] 创建了 {assoc_count} 条记忆关联')

# 提交
conn.commit()

# 验证
print()
print('【验证】')

cursor.execute('SELECT COUNT(*) FROM memory_links')
new_link_count = cursor.fetchone()[0]
print(f'  记忆链接: {new_link_count} 条')

cursor.execute('SELECT COUNT(*) FROM memory_associations')
new_assoc_count = cursor.fetchone()[0]
print(f'  记忆关联: {new_assoc_count} 条')

conn.close()

print()
print('=' * 60)
print('记忆链接和记忆关联系统激活完成')
print('=' * 60)