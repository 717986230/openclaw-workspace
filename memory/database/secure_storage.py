#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全的账户密码存储模块
注意：这是一个基础版本，生产环境应该使用系统密钥链或加密库
"""

import sqlite3
import json
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# 数据库路径
BASE_PATH = Path(__file__).parent
SECURE_DB = BASE_PATH / "xiaozhi_secure.db"


class SecureStorage:
    """安全存储（基础版本）"""

    def __init__(self):
        self.conn = sqlite3.connect(SECURE_DB)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        cursor = self.conn.cursor()

        # 账户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                username TEXT,
                password_encoded TEXT,
                url TEXT,
                notes TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_service ON accounts(service)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_accounts_category ON accounts(category)
        """)

        self.conn.commit()

    def _simple_encode(self, text: str) -> str:
        """简单编码（不是加密！仅用于混淆）"""
        # 注意：生产环境应该使用 cryptography 或系统密钥链
        # 这里只用 base64 做基础混淆
        if not text:
            return ""
        return base64.b64encode(text.encode()).decode()

    def _simple_decode(self, encoded: str) -> str:
        """简单解码"""
        if not encoded:
            return ""
        return base64.b64decode(encoded.encode()).decode()

    def add_account(
        self,
        service: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url: Optional[str] = None,
        notes: Optional[str] = None,
        category: Optional[str] = None
    ) -> int:
        """添加账户"""
        cursor = self.conn.cursor()

        password_encoded = self._simple_encode(password) if password else None

        cursor.execute("""
            INSERT INTO accounts (service, username, password_encoded, url, notes, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (service, username, password_encoded, url, notes, category))

        account_id = cursor.lastrowid
        self.conn.commit()
        return account_id

    def get_account(self, account_id: int) -> Optional[Dict]:
        """获取账户（不返回密码）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, service, username, url, notes, category, created_at, updated_at
            FROM accounts WHERE id = ?
        """, (account_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_password(self, account_id: int) -> Optional[str]:
        """获取密码（仅在需要时调用）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT password_encoded FROM accounts WHERE id = ?
        """, (account_id,))
        row = cursor.fetchone()
        if row and row["password_encoded"]:
            return self._simple_decode(row["password_encoded"])
        return None

    def search_accounts(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """搜索账户（不返回密码）"""
        cursor = self.conn.cursor()

        where_clauses = ["(service LIKE ? OR username LIKE ? OR notes LIKE ?)"]
        params = [f"%{query}%", f"%{query}%", f"%{query}%"]

        if category:
            where_clauses.append("category = ?")
            params.append(category)

        sql = """
            SELECT id, service, username, url, notes, category, created_at
            FROM accounts
            WHERE {}
            ORDER BY created_at DESC
        """.format(" AND ".join(where_clauses))

        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]

    def list_all(self, category: Optional[str] = None) -> List[Dict]:
        """列出所有账户（不返回密码）"""
        cursor = self.conn.cursor()

        if category:
            cursor.execute("""
                SELECT id, service, username, url, notes, category, created_at
                FROM accounts WHERE category = ?
                ORDER BY service
            """, (category,))
        else:
            cursor.execute("""
                SELECT id, service, username, url, notes, category, created_at
                FROM accounts ORDER BY service
            """)

        return [dict(row) for row in cursor.fetchall()]

    def delete_account(self, account_id: int) -> bool:
        """删除账户"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_stats(self) -> Dict:
        """获取统计"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT category, COUNT(*) as cnt
            FROM accounts
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        by_category = {row[0]: row[1] for row in cursor.fetchall()}

        return {
            "total": total,
            "by_category": by_category
        }


# 全局实例
_secure_storage = None


def get_secure_storage() -> SecureStorage:
    """获取安全存储实例"""
    global _secure_storage
    if _secure_storage is None:
        _secure_storage = SecureStorage()
    return _secure_storage


if __name__ == "__main__":
    print("=" * 50)
    print("小智的安全存储模块")
    print("=" * 50)
    print()
    print("[WARNING] 这是基础版本，仅使用 base64 混淆")
    print("[WARNING] 生产环境请使用系统密钥链或加密库")
    print()

    storage = get_secure_storage()
    stats = storage.get_stats()

    print(f"账户总数: {stats['total']}")
    if stats['by_category']:
        print(f"按分类: {stats['by_category']}")
    print()
    print("[OK] 安全存储模块就绪！")
