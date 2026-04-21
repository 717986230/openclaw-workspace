"""
带数据库存储的爬虫示例
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from crawler import Crawler
from batch_crawler import BatchCrawler
from dynamic_crawler import DynamicCrawler
from database_storage import DatabaseStorage


def demo_sqlite_storage():
    """演示 SQLite 存储"""
    print("=" * 60)
    print("SQLite 数据库存储示例")
    print("=" * 60)

    # 初始化数据库存储
    print("\n1. 初始化 SQLite 数据库...")
    db = DatabaseStorage(db_type="sqlite", db_path="crawler_data.db")

    # 创建爬虫
    print("\n2. 初始化爬虫...")
    crawler = Crawler(delay_range=(0.5, 1.0))

    # 创建任务
    print("\n3. 创建爬取任务...")
    task_id = db.create_task("SQLite 测试任务", "https://httpbin.org/html")
    print(f"   任务 ID: {task_id}")

    # 更新任务状态
    db.update_task_status(task_id, "running")

    try:
        # 爬取页面
        print("\n4. 开始爬取...")
        html = crawler.fetch('https://httpbin.org/html')
        print(f"   页面长度: {len(html)} 字符")

        # 提取数据
        print("\n5. 提取数据...")
        data = crawler.extract(html, {
            'title': 'title::text',
            'heading': 'h1::text'
        })
        print(f"   提取结果: {data}")

        # 保存到数据库
        print("\n6. 保存到数据库...")
        result_id = db.save_result(
            task_id=task_id,
            url="https://httpbin.org/html",
            title=data.get('title'),
            content=html[:1000],  # 只保存前1000字符
            extracted_data=data
        )
        print(f"   结果 ID: {result_id}")

        # 更新任务状态
        db.update_task_status(task_id, "completed")

        # 获取统计
        print("\n7. 获取统计信息...")
        stats = db.get_statistics()
        print(f"   统计: {stats}")

        # 获取结果
        print("\n8. 获取保存的结果...")
        results = db.get_results(task_id=task_id)
        for result in results:
            print(f"   URL: {result['url']}")
            print(f"   标题: {result['title']}")
            print(f"   提取数据: {result['extracted_data']}")

        # 导出数据
        print("\n9. 导出数据到 CSV...")
        csv_path = db.export_to_csv(task_id, "crawl_results.csv")
        print(f"   导出路径: {csv_path}")

    except Exception as e:
        print(f"   爬取失败: {e}")
        db.update_task_status(task_id, "failed", str(e))

    finally:
        db.close()


def demo_batch_with_storage():
    """演示批量爬取并存储"""
    print("\n" + "=" * 60)
    print("批量爬取 + 数据库存储示例")
    print("=" * 60)

    # 初始化数据库
    print("\n1. 初始化数据库...")
    db = DatabaseStorage(db_type="sqlite", db_path="batch_crawler.db")

    # 准备 URL 列表
    urls = [
        'https://httpbin.org/html',
        'https://httpbin.org/html',
        'https://httpbin.org/html',
    ]

    print(f"\n2. 准备批量爬取 {len(urls)} 个页面...")

    # 创建任务
    task_id = db.create_task("批量爬取任务", ",".join(urls))
    db.update_task_status(task_id, "running")

    try:
        # 批量爬取
        print("\n3. 开始批量爬取...")
        batch = BatchCrawler(concurrent=2, delay_range=(0.5, 1.0))

        results = batch.crawl(urls, extract_rules={
            'title': 'title::text'
        })

        print(f"   爬取统计: {batch.get_stats()}")

        # 保存所有结果
        print("\n4. 保存结果到数据库...")
        for i, result in enumerate(results, 1):
            if result.get('success'):
                result_id = db.save_result(
                    task_id=task_id,
                    url=result.get('url'),
                    title=result.get('data', {}).get('title'),
                    extracted_data=result.get('data')
                )
                print(f"   保存结果 {i}: ID {result_id}")

        # 更新任务状态
        db.update_task_status(task_id, "completed")

        # 获取统计
        print("\n5. 获取统计信息...")
        stats = db.get_statistics()
        print(f"   统计: {stats}")

    except Exception as e:
        print(f"   批量爬取失败: {e}")
        db.update_task_status(task_id, "failed", str(e))

    finally:
        db.close()


def demo_mysql_storage():
    """演示 MySQL 存储（需要先安装 MySQL）"""
    print("\n" + "=" * 60)
    print("MySQL 数据库存储示例")
    print("=" * 60)

    print("\n⚠️  注意：使用 MySQL 需要先安装和配置 MySQL")
    print("   1. 下载 MySQL: https://dev.mysql.com/downloads/mysql/")
    print("   2. 安装 MySQL 并设置 root 密码")
    print("   3. 创建数据库: CREATE DATABASE crawler_db;")
    print("   4. 安装 Python MySQL 客户端: pip install pymysql")

    print("\n示例代码：")
    print("""
    # MySQL 连接配置
    db = DatabaseStorage(
        db_type="mysql",
        host="localhost",
        port=3306,
        user="root",
        password="your_password",
        database="crawler_db"
    )

    # 使用方式与 SQLite 完全相同
    task_id = db.create_task("MySQL 任务", "https://example.com")
    result_id = db.save_result(task_id, "https://example.com", title="示例")
    """)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" 带数据库存储的爬虫示例 ")
    print("=" * 60)

    # SQLite 示例
    demo_sqlite_storage()

    # 批量爬取示例
    demo_batch_with_storage()

    # MySQL 说明
    demo_mysql_storage()

    print("\n" + "=" * 60)
    print("所有示例已完成！")
    print("=" * 60)
    print("\n生成的文件:")
    print("  - crawler_data.db (SQLite 数据库)")
    print("  - batch_crawler.db (批量爬取数据库)")
    print("  - crawl_results.csv (导出的 CSV 文件)")
