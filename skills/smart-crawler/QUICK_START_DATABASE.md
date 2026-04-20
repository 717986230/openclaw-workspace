# 爬虫数据存储 - 快速开始

## ✅ 当前状态

**SQLite 数据库存储已配置完成，立即可用！**

### 生成的文件
- `crawler_data.db` - SQLite 数据库
- `batch_crawler.db` - 批量爬取数据库
- `crawl_results.csv` - 导出的 CSV 文件

---

## 🚀 立即使用

### 1. 基础爬取 + 存储

```python
from scripts.crawler import Crawler
from scripts.database_storage import DatabaseStorage

# 初始化数据库
db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

# 创建爬虫
crawler = Crawler(delay_range=(0.5, 1.0))

# 创建任务
task_id = db.create_task("我的第一个爬虫任务", "https://example.com")

# 爬取页面
html = crawler.fetch('https://example.com')

# 提取数据
data = crawler.extract(html, {
    'title': 'title::text',
    'links': 'a::attr(href)'
})

# 保存到数据库
result_id = db.save_result(
    task_id=task_id,
    url="https://example.com",
    title=data.get('title'),
    extracted_data=data
)

print(f"保存成功！结果 ID: {result_id}")
```

### 2. 批量爬取 + 存储

```python
from scripts.batch_crawler import BatchCrawler
from scripts.database_storage import DatabaseStorage

# 初始化数据库
db = DatabaseStorage(db_type="sqlite", db_path="batch_crawler.db")

# 准备 URL 列表
urls = [
    'https://example.com/page/1',
    'https://example.com/page/2',
    'https://example.com/page/3',
]

# 创建任务
task_id = db.create_task("批量爬取", ",".join(urls))

# 批量爬取
batch = BatchCrawler(concurrent=3, delay_range=(1, 2))
results = batch.crawl(urls, extract_rules={'title': 'title::text'})

# 保存所有结果
for result in results:
    if result.get('success'):
        db.save_result(
            task_id=task_id,
            url=result.get('url'),
            extracted_data=result.get('data')
        )

print(f"批量爬取完成！成功: {len([r for r in results if r.get('success')])}")
```

### 3. 查询数据

```python
from scripts.database_storage import DatabaseStorage

# 初始化数据库
db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

# 获取所有结果
results = db.get_results(limit=10)

for result in results:
    print(f"URL: {result['url']}")
    print(f"标题: {result['title']}")
    print(f"数据: {result['extracted_data']}")
    print("-" * 40)

# 获取统计信息
stats = db.get_statistics()
print(f"统计: {stats}")
```

### 4. 导出数据

```python
from scripts.database_storage import DatabaseStorage

# 初始化数据库
db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

# 导出为 CSV
csv_path = db.export_to_csv(task_id=1, output_path="results.csv")
print(f"CSV 导出: {csv_path}")

# 导出为 Excel
excel_path = db.export_to_excel(task_id=1, output_path="results.xlsx")
print(f"Excel 导出: {excel_path}")
```

---

## 📊 数据库结构

### 表：crawl_tasks（爬取任务）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 任务 ID（主键） |
| task_name | VARCHAR(255) | 任务名称 |
| url | TEXT | 目标 URL |
| status | VARCHAR(50) | 状态（pending/running/completed/failed） |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| error_message | TEXT | 错误信息 |

### 表：crawl_results（爬取结果）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 结果 ID（主键） |
| task_id | INTEGER | 任务 ID（外键） |
| url | TEXT | 页面 URL |
| title | TEXT | 页面标题 |
| content | TEXT | 页面内容 |
| extracted_data | TEXT | 提取的数据（JSON） |
| status | VARCHAR(50) | 状态 |
| created_at | TIMESTAMP | 创建时间 |

### 表：media_files（媒体文件）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 文件 ID（主键） |
| result_id | INTEGER | 结果 ID（外键） |
| file_type | VARCHAR(50) | 文件类型 |
| file_path | TEXT | 文件路径 |
| file_size | INTEGER | 文件大小 |
| url | TEXT | 原始 URL |
| created_at | TIMESTAMP | 创建时间 |

---

## 🎯 完整示例

```python
"""
完整的爬虫 + 数据库存储示例
"""

from scripts.crawler import Crawler
from scripts.database_storage import DatabaseStorage

def main():
    # 1. 初始化数据库
    print("1. 初始化数据库...")
    db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

    # 2. 创建爬虫
    print("2. 初始化爬虫...")
    crawler = Crawler(delay_range=(0.5, 1.0))

    # 3. 创建任务
    print("3. 创建任务...")
    task_id = db.create_task("示例爬虫", "https://httpbin.org/html")
    db.update_task_status(task_id, "running")

    try:
        # 4. 爬取页面
        print("4. 爬取页面...")
        html = crawler.fetch('https://httpbin.org/html')
        print(f"   页面长度: {len(html)} 字符")

        # 5. 提取数据
        print("5. 提取数据...")
        data = crawler.extract(html, {
            'title': 'title::text',
            'heading': 'h1::text'
        })
        print(f"   提取结果: {data}")

        # 6. 保存到数据库
        print("6. 保存到数据库...")
        result_id = db.save_result(
            task_id=task_id,
            url="https://httpbin.org/html",
            title=data.get('title'),
            content=html[:1000],
            extracted_data=data
        )
        print(f"   保存成功！结果 ID: {result_id}")

        # 7. 更新任务状态
        db.update_task_status(task_id, "completed")

        # 8. 查询结果
        print("7. 查询结果...")
        results = db.get_results(task_id=task_id)
        for result in results:
            print(f"   URL: {result['url']}")
            print(f"   标题: {result['title']}")
            print(f"   数据: {result['extracted_data']}")

        # 9. 获取统计
        print("8. 获取统计...")
        stats = db.get_statistics()
        print(f"   统计: {stats}")

        # 10. 导出数据
        print("9. 导出数据...")
        csv_path = db.export_to_csv(task_id, "results.csv")
        print(f"   CSV 导出: {csv_path}")

    except Exception as e:
        print(f"错误: {e}")
        db.update_task_status(task_id, "failed", str(e))

    finally:
        db.close()

if __name__ == "__main__":
    main()
```

---

## 🔧 高级功能

### 1. 自定义查询

```python
import sqlite3

# 直接查询 SQLite
conn = sqlite3.connect('my_crawler.db')
cursor = conn.cursor()

# 查询特定任务的结果
cursor.execute("""
    SELECT url, title, extracted_data
    FROM crawl_results
    WHERE task_id = ?
    ORDER BY created_at DESC
    LIMIT 10
""", (task_id,))

results = cursor.fetchall()
for row in results:
    print(row)

conn.close()
```

### 2. 数据分析

```python
import pandas as pd
from scripts.database_storage import DatabaseStorage

# 初始化数据库
db = DatabaseStorage(db_type="sqlite", db_path="my_crawler.db")

# 获取所有结果
results = db.get_results(limit=1000)

# 转换为 DataFrame
df = pd.DataFrame(results)

# 数据分析
print(f"总记录数: {len(df)}")
print(f"成功爬取: {len(df[df['status'] == 'success'])}")
print(f"失败爬取: {len(df[df['status'] == 'failed'])}")

# 按日期统计
df['date'] = pd.to_datetime(df['created_at']).dt.date
daily_stats = df.groupby('date').size()
print(f"每日爬取统计:\n{daily_stats}")
```

### 3. 定时任务

```python
import schedule
import time

def scheduled_crawl():
    """定时爬取任务"""
    from scripts.crawler import Crawler
    from scripts.database_storage import DatabaseStorage

    db = DatabaseStorage(db_type="sqlite", db_path="scheduled_crawler.db")
    crawler = Crawler()

    # 爬取逻辑
    # ...

    db.close()

# 每小时执行一次
schedule.every().hour.do(scheduled_crawl)

while True:
    schedule.run_pending()
    time.sleep(60)
```

---

## 📈 性能优化

### 1. 批量插入

```python
# 批量保存结果
results_data = [
    {"url": "https://example.com/1", "title": "页面1"},
    {"url": "https://example.com/2", "title": "页面2"},
    # ...
]

for data in results_data:
    db.save_result(task_id=task_id, **data)
```

### 2. 索引优化

```python
import sqlite3

conn = sqlite3.connect('my_crawler.db')
cursor = conn.cursor()

# 添加索引
cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_id ON crawl_results(task_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_url ON crawl_results(url)")

conn.commit()
conn.close()
```

---

## 🎉 开始使用

现在你可以：

1. ✅ 使用 SQLite 立即开始存储爬虫数据
2. ✅ 查询和分析爬取结果
3. ✅ 导出数据为 CSV/Excel
4. ✅ 需要时升级到 MySQL

需要帮助配置具体的爬取任务吗？
