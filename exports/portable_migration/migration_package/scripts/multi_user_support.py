#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多用户支持
Multi-user Support
"""

import sqlite3
import hashlib
import secrets
import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class CollaborationType(Enum):
    SHARED_MEMORY = "shared_memory"
    COLLABORATIVE_EDITING = "collaborative_editing"
    COMMENT = "comment"
    NOTIFICATION = "notification"

@dataclass
class User:
    id: str
    username: str
    email: str
    role: str
    created_at: str

@dataclass
class SharedMemory:
    memory_id: int
    owner_id: str
    shared_with: List[str]
    permissions: Dict
    created_at: str

@dataclass
class Comment:
    id: int
    memory_id: int
    user_id: str
    content: str
    created_at: str

@dataclass
class Notification:
    id: int
    user_id: str
    type: str
    content: str
    read: bool
    created_at: str

class MultiUserSupport:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.users = {}
        self.shared_memories = {}
        self.comments = {}
        self.notifications = {}
        self._initialize_tables()

    def _initialize_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shared_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                owner_id TEXT NOT NULL,
                shared_with TEXT NOT NULL,
                permissions TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories(id),
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id INTEGER NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_id) REFERENCES memories(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        conn.commit()
        conn.close()

    def register_user(self, username: str, email: str, password: str, role: str = 'user') -> User:
        user_id = secrets.token_hex(16)
        password_hash = self._hash_password(password)
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, email, password_hash, role, created_at))

        conn.commit()
        conn.close()

        user = User(id=user_id, username=username, email=email, role=role, created_at=created_at)
        self.users[user_id] = user

        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, password_hash, role, created_at
            FROM users WHERE username = ?
        """, (username,))

        row = cursor.fetchone()
        conn.close()

        if row:
            user_id, username, email, password_hash, role, created_at = row
            if self._verify_password(password, password_hash):
                user = User(id=user_id, username=username, email=email, role=role, created_at=created_at)
                self.users[user_id] = user
                return user

        return None

    def share_memory(self, memory_id: int, owner_id: str, shared_with: List[str], permissions: Dict) -> SharedMemory:
        created_at = datetime.now().isoformat()
        shared_with_json = json.dumps(shared_with)
        permissions_json = json.dumps(permissions)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO shared_memories (memory_id, owner_id, shared_with, permissions, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (memory_id, owner_id, shared_with_json, permissions_json, created_at))

        shared_id = cursor.lastrowid
        conn.commit()
        conn.close()

        shared_memory = SharedMemory(
            memory_id=memory_id,
            owner_id=owner_id,
            shared_with=shared_with,
            permissions=permissions,
            created_at=created_at
        )
        self.shared_memories[shared_id] = shared_memory

        for user_id in shared_with:
            self._send_notification(user_id, 'memory_shared', f'Memory {memory_id} shared with you')

        return shared_memory

    def add_comment(self, memory_id: int, user_id: str, content: str) -> Comment:
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO comments (memory_id, user_id, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (memory_id, user_id, content, created_at))

        comment_id = cursor.lastrowid
        conn.commit()
        conn.close()

        comment = Comment(id=comment_id, memory_id=memory_id, user_id=user_id, content=content, created_at=created_at)
        self.comments[comment_id] = comment

        return comment

    def get_comments(self, memory_id: int) -> List[Comment]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, memory_id, user_id, content, created_at
            FROM comments WHERE memory_id = ?
            ORDER BY created_at DESC
        """, (memory_id,))

        comments = []
        for row in cursor.fetchall():
            comment = Comment(id=row[0], memory_id=row[1], user_id=row[2], content=row[3], created_at=row[4])
            comments.append(comment)

        conn.close()

        return comments

    def _send_notification(self, user_id: str, notification_type: str, content: str) -> Notification:
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO notifications (user_id, type, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, notification_type, content, created_at))

        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()

        notification = Notification(id=notification_id, user_id=user_id, type=notification_type, content=content, read=False, created_at=created_at)
        self.notifications[notification_id] = notification

        return notification

    def get_notifications(self, user_id: str, unread_only: bool = False) -> List[Notification]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if unread_only:
            cursor.execute("""
                SELECT id, user_id, type, content, read, created_at
                FROM notifications WHERE user_id = ? AND read = FALSE
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT id, user_id, type, content, read, created_at
                FROM notifications WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))

        notifications = []
        for row in cursor.fetchall():
            notification = Notification(id=row[0], user_id=row[1], type=row[2], content=row[3], read=row[4], created_at=row[5])
            notifications.append(notification)

        conn.close()

        return notifications

    def mark_notification_read(self, notification_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications SET read = TRUE WHERE id = ?
        """, (notification_id,))

        conn.commit()
        conn.close()

    def get_user_statistics(self, user_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM shared_memories WHERE owner_id = ?", (user_id,))
        shared_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM comments WHERE user_id = ?", (user_id,))
        comment_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND read = FALSE", (user_id,))
        unread_notification_count = cursor.fetchone()[0]

        conn.close()

        return {
            'shared_memories': shared_count,
            'comments': comment_count,
            'unread_notifications': unread_notification_count
        }

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        return self._hash_password(password) == password_hash

if __name__ == "__main__":
    print("Testing Multi-user Support...")
    multi_user = MultiUserSupport("memory/database/xiaozhi_memory.db")
    user = multi_user.register_user("testuser", "test@example.com", "password123", "user")
    print(f"User registered: {user.username}")
    authenticated = multi_user.authenticate_user("testuser", "password123")
    print(f"User authenticated: {authenticated.username if authenticated else 'Failed'}")
    shared = multi_user.share_memory(1, user.id, [user.id], {'read': True, 'write': False})
    print(f"Memory shared: {shared.memory_id}")
    comment = multi_user.add_comment(1, user.id, "This is a test comment")
    print(f"Comment added: {comment.id}")
    comments = multi_user.get_comments(1)
    print(f"Comments: {len(comments)} comments retrieved")
    notifications = multi_user.get_notifications(user.id)
    print(f"Notifications: {len(notifications)} notifications retrieved")
    stats = multi_user.get_user_statistics(user.id)
    print(f"Statistics: {stats}")
    print("Multi-user Support test complete!")
