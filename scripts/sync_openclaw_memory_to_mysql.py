import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from typing import Iterable


SQLITE_PATH = r"C:\Users\Administrator\.openclaw\memory\main.sqlite"
MYSQL_EXE = r"C:\CODE\tools\mysql-8.0.45-winx64\bin\mysql.exe"
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "111111"
MYSQL_DB = "openclaw_memory"


def mysql_quote(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    text = text.replace("\\", "\\\\").replace("'", "\\'")
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    return f"'{text}'"


def load_rows(conn: sqlite3.Connection, table: str, columns: list[str]) -> list[tuple]:
    query = f"SELECT {', '.join(columns)} FROM {table}"
    return conn.execute(query).fetchall()


def build_insert_sql(table: str, columns: list[str], rows: Iterable[tuple]) -> list[str]:
    rows = list(rows)
    if not rows:
        return []
    prefix = f"INSERT INTO {table} ({', '.join(columns)}) VALUES "
    statements = []
    batch = []
    for row in rows:
        batch.append("(" + ", ".join(mysql_quote(v) for v in row) + ")")
        if len(batch) >= 200:
            statements.append(prefix + ",\n".join(batch) + ";")
            batch = []
    if batch:
        statements.append(prefix + ",\n".join(batch) + ";")
    return statements


def main() -> int:
    if not os.path.exists(SQLITE_PATH):
        print(f"SQLite memory db not found: {SQLITE_PATH}", file=sys.stderr)
        return 1
    if not os.path.exists(MYSQL_EXE):
        print(f"MySQL client not found: {MYSQL_EXE}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(SQLITE_PATH)
    try:
        meta_rows = load_rows(conn, "meta", ["key", "value"])
        files_rows = load_rows(conn, "files", ["path", "source", "hash", "mtime", "size"])
        chunks_rows = load_rows(
            conn,
            "chunks",
            ["id", "path", "source", "start_line", "end_line", "hash", "model", "text", "embedding", "updated_at"],
        )
        embedding_cache_rows = load_rows(
            conn,
            "embedding_cache",
            ["provider", "model", "provider_key", "hash", "embedding", "dims", "updated_at"],
        )
    finally:
        conn.close()

    sql_parts = [
        f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        f"USE {MYSQL_DB};",
        """
CREATE TABLE IF NOT EXISTS meta (
  `key` VARCHAR(255) PRIMARY KEY,
  `value` LONGTEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip(),
        """
CREATE TABLE IF NOT EXISTS files (
  `path_hash` CHAR(64) PRIMARY KEY,
  `path` TEXT NOT NULL,
  `source` VARCHAR(64) NOT NULL DEFAULT 'memory',
  `hash` VARCHAR(255) NOT NULL,
  `mtime` BIGINT NOT NULL,
  `size` BIGINT NOT NULL,
  KEY `idx_files_source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip(),
        """
CREATE TABLE IF NOT EXISTS chunks (
  `id` VARCHAR(255) PRIMARY KEY,
  `path` TEXT NOT NULL,
  `source` VARCHAR(64) NOT NULL DEFAULT 'memory',
  `start_line` INT NOT NULL,
  `end_line` INT NOT NULL,
  `hash` VARCHAR(255) NOT NULL,
  `model` VARCHAR(255) NOT NULL,
  `text` LONGTEXT NOT NULL,
  `embedding` LONGTEXT NOT NULL,
  `updated_at` BIGINT NOT NULL,
  KEY `idx_chunks_path` (`path`(255)),
  KEY `idx_chunks_source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip(),
        """
CREATE TABLE IF NOT EXISTS embedding_cache (
  `cache_key` CHAR(64) PRIMARY KEY,
  `provider` VARCHAR(128) NOT NULL,
  `model` VARCHAR(255) NOT NULL,
  `provider_key` VARCHAR(255) NOT NULL,
  `hash` VARCHAR(255) NOT NULL,
  `embedding` LONGTEXT NOT NULL,
  `dims` INT NULL,
  `updated_at` BIGINT NOT NULL,
  KEY `idx_embedding_provider_model` (`provider`, `model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip(),
        """
CREATE TABLE IF NOT EXISTS sync_state (
  `sync_name` VARCHAR(128) PRIMARY KEY,
  `sqlite_path` VARCHAR(1024) NOT NULL,
  `last_synced_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `stats_json` JSON NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""".strip(),
        "START TRANSACTION;",
        "DELETE FROM meta;",
        "DELETE FROM files;",
        "DELETE FROM chunks;",
        "DELETE FROM embedding_cache;",
    ]

    sql_parts.extend(build_insert_sql("meta", ["key", "value"], meta_rows))
    mysql_files_rows = []
    for row in files_rows:
        path_value = row[0]
        path_hash = hashlib.sha256(str(path_value).encode("utf-8")).hexdigest()
        mysql_files_rows.append((path_hash, *row))
    sql_parts.extend(build_insert_sql("files", ["path_hash", "path", "source", "hash", "mtime", "size"], mysql_files_rows))
    sql_parts.extend(
        build_insert_sql(
            "chunks",
            ["id", "path", "source", "start_line", "end_line", "hash", "model", "text", "embedding", "updated_at"],
            chunks_rows,
        )
    )
    mysql_embedding_cache_rows = []
    for row in embedding_cache_rows:
        cache_key = hashlib.sha256("||".join("" if v is None else str(v) for v in row[:4]).encode("utf-8")).hexdigest()
        mysql_embedding_cache_rows.append((cache_key, *row))
    sql_parts.extend(
        build_insert_sql(
            "embedding_cache",
            ["cache_key", "provider", "model", "provider_key", "hash", "embedding", "dims", "updated_at"],
            mysql_embedding_cache_rows,
        )
    )

    stats = {
        "meta": len(meta_rows),
        "files": len(files_rows),
        "chunks": len(chunks_rows),
        "embedding_cache": len(embedding_cache_rows),
    }
    stats_json = json.dumps(stats, ensure_ascii=False)
    sql_parts.append(
        "INSERT INTO sync_state (sync_name, sqlite_path, stats_json) VALUES "
        f"('openclaw_memory_main', {mysql_quote(SQLITE_PATH)}, {mysql_quote(stats_json)}) "
        "ON DUPLICATE KEY UPDATE sqlite_path=VALUES(sqlite_path), stats_json=VALUES(stats_json), last_synced_at=CURRENT_TIMESTAMP;"
    )
    sql_parts.append("COMMIT;")
    sql_script = "\n\n".join(sql_parts) + "\n"

    env = os.environ.copy()
    env["MYSQL_PWD"] = MYSQL_PASSWORD
    proc = subprocess.run(
        [
            MYSQL_EXE,
            f"--host={MYSQL_HOST}",
            f"--port={MYSQL_PORT}",
            f"--user={MYSQL_USER}",
            "--default-character-set=utf8mb4",
            "--comments",
        ],
        input=sql_script,
        text=True,
        capture_output=True,
        env=env,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout)
        return proc.returncode

    print(json.dumps({"database": MYSQL_DB, "synced": stats}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
