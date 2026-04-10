#!/usr/bin/env python3
"""Shared runtime configuration for workspace database tooling."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


HOME = Path.home()
WORKSPACE_ROOT = HOME / ".openclaw" / "workspace"
DATABASE_DIR = WORKSPACE_ROOT / "memory" / "database"
SQLITE_DB = DATABASE_DIR / "xiaozhi_memory.db"
SECURE_DB = DATABASE_DIR / "xiaozhi_secure.db"
LANCEDB_DIR = DATABASE_DIR / "lancedb"
CONFIG_PATH = DATABASE_DIR / "runtime_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "workspace_root": str(WORKSPACE_ROOT),
    "sqlite_db": str(SQLITE_DB),
    "secure_db": str(SECURE_DB),
    "lancedb_dir": str(LANCEDB_DIR),
    "mysql": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "111111",
        "database": "erbing_brain",
    },
}


def ensure_directories() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    LANCEDB_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    ensure_directories()
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        return json.loads(json.dumps(DEFAULT_CONFIG))

    data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    merged = json.loads(json.dumps(DEFAULT_CONFIG))
    for key, value in data.items():
        if key == "mysql" and isinstance(value, dict):
            merged["mysql"].update(value)
        else:
            merged[key] = value

    env_password = os.getenv("OPENCLAW_MYSQL_PASSWORD")
    if env_password:
        merged["mysql"]["password"] = env_password

    return merged


CONFIG = load_config()


def get_workspace_root() -> Path:
    return Path(CONFIG["workspace_root"])


def get_sqlite_db_path() -> Path:
    return Path(CONFIG["sqlite_db"])


def get_secure_db_path() -> Path:
    return Path(CONFIG["secure_db"])


def get_lancedb_dir() -> Path:
    return Path(CONFIG["lancedb_dir"])


def get_mysql_config() -> Dict[str, Any]:
    return dict(CONFIG["mysql"])
