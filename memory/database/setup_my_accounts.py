#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
给小智创建自己的账户记录
"""

import sys
sys.path.insert(0, str(sys.path[0]))
from secure_storage import get_secure_storage


def setup_my_accounts():
    """创建小智的账户"""
    storage = get_secure_storage()

    print("=" * 50)
    print("创建小智的账户记录")
    print("=" * 50)
    print()

    # 1. 本地数据库 - MySQL
    print("[1/5] 添加 MySQL 账户...")
    storage.add_account(
        service="MySQL Local",
        username="root",
        password="",  # 空密码，需要主人填写
        url="localhost:3306",
        notes="本地 MySQL 5.7 数据库",
        category="database"
    )
    print("  [OK] MySQL 账户已添加（需要填写密码）")

    # 2. 本地数据库 - SQLite（记忆库）
    print("[2/5] 添加 SQLite 记忆库...")
    storage.add_account(
        service="SQLite - Xiaozhi Memory",
        username="",
        password="",
        url="xiaozhi_memory.db",
        notes="小智的混合记忆系统主数据库",
        category="database"
    )
    print("  [OK] SQLite 记忆库已添加")

    # 3. 安全存储库
    print("[3/5] 添加安全存储库...")
    storage.add_account(
        service="SQLite - Secure Storage",
        username="",
        password="",
        url="xiaozhi_secure.db",
        notes="小智的安全存储模块（账户密码）",
        category="database"
    )
    print("  [OK] 安全存储库已添加")

    # 4. LanceDB 向量数据库
    print("[4/5] 添加 LanceDB...")
    storage.add_account(
        service="LanceDB - Vector Memory",
        username="",
        password="",
        url="lancedb/",
        notes="小智的向量记忆数据库",
        category="database"
    )
    print("  [OK] LanceDB 已添加")

    # 5. OpenClaw Gateway
    print("[5/5] 添加 OpenClaw Gateway...")
    storage.add_account(
        service="OpenClaw Gateway",
        username="",
        password="",
        url="http://127.0.0.1:18789",
        notes="OpenClaw 网关服务（仅本地访问）",
        category="service"
    )
    print("  [OK] OpenClaw Gateway 已添加")

    print()
    print("=" * 50)
    stats = storage.get_stats()
    print(f"账户总数: {stats['total']}")
    if stats['by_category']:
        print(f"按分类: {stats['by_category']}")
    print("=" * 50)
    print()
    print("[DONE] 小智的账户记录创建完成！")
    print("[NOTE] 敏感密码需要主人手动补充")


if __name__ == "__main__":
    setup_my_accounts()
