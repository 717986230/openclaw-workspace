#!/usr/bin/env python3
"""Simple local secure storage backed by SQLite."""

from __future__ import annotations

import base64
import sqlite3
from typing import Dict, List, Optional

from runtime_config import ensure_directories, get_secure_db_path


SECURE_DB = get_secure_db_path()


class SecureStorage:
    def __init__(self):
        ensure_directories()
        self.conn = sqlite3.connect(SECURE_DB)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
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
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_service ON accounts(service)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accounts_category ON accounts(category)")
        self.conn.commit()

    def _encode(self, text: str) -> str:
        return base64.b64encode(text.encode("utf-8")).decode("ascii") if text else ""

    def _decode(self, encoded: str) -> str:
        return base64.b64decode(encoded.encode("ascii")).decode("utf-8") if encoded else ""

    def add_account(
        self,
        service: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        url: Optional[str] = None,
        notes: Optional[str] = None,
        category: Optional[str] = None,
    ) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO accounts (service, username, password_encoded, url, notes, category)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (service, username, self._encode(password) if password else None, url, notes, category),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def get_account(self, account_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT id, service, username, url, notes, category, created_at, updated_at
            FROM accounts WHERE id = ?
            """,
            (account_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_password(self, account_id: int) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT password_encoded FROM accounts WHERE id = ?", (account_id,))
        row = cursor.fetchone()
        if not row or not row["password_encoded"]:
            return None
        return self._decode(row["password_encoded"])

    def list_all(self, category: Optional[str] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if category:
            cursor.execute(
                """
                SELECT id, service, username, url, notes, category, created_at
                FROM accounts WHERE category = ?
                ORDER BY service
                """,
                (category,),
            )
        else:
            cursor.execute(
                """
                SELECT id, service, username, url, notes, category, created_at
                FROM accounts ORDER BY service
                """
            )
        return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM accounts")
        total = cursor.fetchone()[0]
        cursor.execute(
            """
            SELECT category, COUNT(*) as cnt
            FROM accounts
            WHERE category IS NOT NULL
            GROUP BY category
            """
        )
        return {"total": total, "by_category": {row[0]: row[1] for row in cursor.fetchall()}}


_secure_storage: Optional[SecureStorage] = None


def get_secure_storage() -> SecureStorage:
    global _secure_storage
    if _secure_storage is None:
        _secure_storage = SecureStorage()
    return _secure_storage


if __name__ == "__main__":
    storage = get_secure_storage()
    print(f"[OK] Secure DB ready: {SECURE_DB}")
    print(storage.get_stats())
