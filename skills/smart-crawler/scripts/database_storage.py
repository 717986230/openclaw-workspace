"""
Database Storage - 数据库存储模块
支持 SQLite 和 MySQL
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os


class DatabaseStorage:
    """数据库存储类"""

    def __init__(self, db_type: str = "sqlite", **kwargs):
        """
        初始化数据库存储

        Args:
            db_type: 数据库类型 (sqlite/mysql)
            kwargs: 数据库连接参数
                - SQLite: db_path (数据库文件路径)
                - MySQL: host, port, user, password, database
        """
        self.db_type = db_type
        self.connection = None

        if db_type == "sqlite":
            db_path = kwargs.get("db_path", "crawler_data.db")
            self.connection = sqlite3.connect(db_path, check_same_thread=False)
            self.placeholder = "?"
        elif db_type == "mysql":
            import pymysql
            self.connection = pymysql.connect(
                host=kwargs.get("host", "localhost"),
                port=kwargs.get("port", 3306),
                user=kwargs.get("user", "root"),
                password=kwargs.get("password", ""),
                database=kwargs.get("database", "crawler_db"),
                charset="utf8mb4"
            )
            self.placeholder = "%s"
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

        self._create_tables()

    def _create_tables(self):
        """创建数据表"""
        cursor = self.connection.cursor()

        # 根据数据库类型选择自增语法
        if self.db_type == "sqlite":
            auto_increment = "INTEGER PRIMARY KEY AUTOINCREMENT"
        else:  # mysql
            auto_increment = "INT AUTO_INCREMENT PRIMARY KEY"

        # 爬取任务表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS crawl_tasks (
                id {auto_increment},
                task_name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                error_message TEXT
            )
        """)

        # 爬取结果表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS crawl_results (
                id {auto_increment},
                task_id INT,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                extracted_data TEXT,
                status VARCHAR(50) DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES crawl_tasks(id)
            )
        """)

        # 媒体文件表
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS media_files (
                id {auto_increment},
                result_id INT,
                file_type VARCHAR(50),
                file_path TEXT,
                file_size INT,
                url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (result_id) REFERENCES crawl_results(id)
            )
        """)

        self.connection.commit()

    def create_task(self, task_name: str, url: str) -> int:
        """创建爬取任务"""
        cursor = self.connection.cursor()
        cursor.execute(
            f"INSERT INTO crawl_tasks (task_name, url) VALUES ({self.placeholder}, {self.placeholder})",
            (task_name, url)
        )
        self.connection.commit()
        return cursor.lastrowid

    def update_task_status(self, task_id: int, status: str, error_message: str = None):
        """更新任务状态"""
        cursor = self.connection.cursor()
        if error_message:
            cursor.execute(
                f"UPDATE crawl_tasks SET status = {self.placeholder}, error_message = {self.placeholder}, updated_at = CURRENT_TIMESTAMP WHERE id = {self.placeholder}",
                (status, error_message, task_id)
            )
        else:
            cursor.execute(
                f"UPDATE crawl_tasks SET status = {self.placeholder}, updated_at = CURRENT_TIMESTAMP WHERE id = {self.placeholder}",
                (status, task_id)
            )
        self.connection.commit()

    def save_result(self, task_id: int, url: str, title: str = None,
                    content: str = None, extracted_data: dict = None) -> int:
        """保存爬取结果"""
        cursor = self.connection.cursor()

        # 将提取的数据转换为 JSON 字符串
        data_json = json.dumps(extracted_data, ensure_ascii=False) if extracted_data else None

        cursor.execute(
            f"""INSERT INTO crawl_results
               (task_id, url, title, content, extracted_data)
               VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})""",
            (task_id, url, title, content, data_json)
        )
        self.connection.commit()
        return cursor.lastrowid

    def save_media_file(self, result_id: int, file_type: str, file_path: str,
                        file_size: int, url: str = None) -> int:
        """保存媒体文件信息"""
        cursor = self.connection.cursor()
        cursor.execute(
            f"""INSERT INTO media_files
               (result_id, file_type, file_path, file_size, url)
               VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})""",
            (result_id, file_type, file_path, file_size, url)
        )
        self.connection.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict]:
        """获取任务信息"""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM crawl_tasks WHERE id = {self.placeholder}", (task_id,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def get_results(self, task_id: int = None, limit: int = 100) -> List[Dict]:
        """获取爬取结果"""
        cursor = self.connection.cursor()

        if task_id:
            cursor.execute(
                f"SELECT * FROM crawl_results WHERE task_id = {self.placeholder} LIMIT {self.placeholder}",
                (task_id, limit)
            )
        else:
            cursor.execute(f"SELECT * FROM crawl_results LIMIT {self.placeholder}", (limit,))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        results = []
        for row in rows:
            result = dict(zip(columns, row))
            # 解析 JSON 数据
            if result.get('extracted_data'):
                try:
                    result['extracted_data'] = json.loads(result['extracted_data'])
                except:
                    pass
            results.append(result)

        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        cursor = self.connection.cursor()

        # 任务统计
        cursor.execute("SELECT status, COUNT(*) FROM crawl_tasks GROUP BY status")
        task_stats = dict(cursor.fetchall())

        # 结果统计
        cursor.execute("SELECT status, COUNT(*) FROM crawl_results GROUP BY status")
        result_stats = dict(cursor.fetchall())

        # 媒体文件统计
        cursor.execute("SELECT file_type, COUNT(*) FROM media_files GROUP BY file_type")
        media_stats = dict(cursor.fetchall())

        return {
            "tasks": task_stats,
            "results": result_stats,
            "media": media_stats
        }

    def export_to_csv(self, task_id: int, output_path: str):
        """导出数据到 CSV"""
        import pandas as pd

        results = self.get_results(task_id=task_id, limit=10000)

        # 转换为 DataFrame
        df = pd.DataFrame(results)

        # 保存到 CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        return output_path

    def export_to_excel(self, task_id: int, output_path: str):
        """导出数据到 Excel"""
        import pandas as pd

        results = self.get_results(task_id=task_id, limit=10000)

        # 转换为 DataFrame
        df = pd.DataFrame(results)

        # 保存到 Excel
        df.to_excel(output_path, index=False)

        return output_path

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()


# 使用示例
if __name__ == "__main__":
    # SQLite 示例
    print("=== SQLite 示例 ===")
    db = DatabaseStorage(db_type="sqlite", db_path="test_crawler.db")

    # 创建任务
    task_id = db.create_task("测试任务", "https://example.com")
    print(f"创建任务 ID: {task_id}")

    # 保存结果
    result_id = db.save_result(
        task_id=task_id,
        url="https://example.com",
        title="示例页面",
        content="<html>...</html>",
        extracted_data={"title": "示例", "price": "100"}
    )
    print(f"保存结果 ID: {result_id}")

    # 获取统计
    stats = db.get_statistics()
    print(f"统计信息: {stats}")

    # 获取结果
    results = db.get_results(task_id=task_id)
    print(f"获取结果: {len(results)} 条")

    db.close()

    # MySQL 示例（需要先安装 MySQL）
    # print("\n=== MySQL 示例 ===")
    # db = DatabaseStorage(
    #     db_type="mysql",
    #     host="localhost",
    #     port=3306,
    #     user="root",
    #     password="your_password",
    #     database="crawler_db"
    # )
