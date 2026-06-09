#!/usr/bin/env python3
"""事实表存储 - 记忆的最小体积表格化存储层

记忆以原子事实行存储（主体-关系-值），而非散文段落：
- 一行事实 ~100-200 字节，UNIQUE 约束天然去重
- valid_from/valid_to 支持事实更替（新事实顶掉旧事实，而非堆积）
- render 生成极简 markdown 视图供 OpenClaw memory-core 索引

用法:
  fact_store.py init                      初始化数据库
  fact_store.py add <主体> <关系> <值> [--conf 0.9] [--source xxx]
  fact_store.py ingest [文件...]          从 memory/*.md 的 FACTS 表格提取事实
  fact_store.py render                    渲染视图到 memory/facts/knowledge.md
  fact_store.py query <关键词>            按主体/关系/值模糊查询
  fact_store.py stats                     统计

FACTS 表格格式（memoryFlush 产出，写在任意 memory/*.md 里）:
  ## FACTS
  | subject | predicate | object | confidence |
  |---|---|---|---|
  | 用户 | 使用编辑器 | Obsidian | 1.0 |
"""
import argparse
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DB_PATH = WORKSPACE / "memory" / "database" / "facts.sqlite"
VIEW_PATH = WORKSPACE / "memory" / "facts" / "knowledge.md"

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
) STRICT;
CREATE TABLE IF NOT EXISTS facts (
  subject INTEGER NOT NULL REFERENCES entities(id),
  predicate TEXT NOT NULL,
  object TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 1.0,
  valid_from TEXT NOT NULL DEFAULT (date('now')),
  valid_to TEXT,
  source TEXT,
  UNIQUE(subject, predicate, object)
) STRICT;
CREATE INDEX IF NOT EXISTS idx_facts_subject ON facts(subject);
PRAGMA journal_mode = WAL;
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    return conn


def entity_id(conn, name: str) -> int:
    conn.execute("INSERT OR IGNORE INTO entities(name) VALUES (?)", (name,))
    return conn.execute("SELECT id FROM entities WHERE name=?", (name,)).fetchone()[0]


def add_fact(conn, subject: str, predicate: str, obj: str,
             confidence: float = 1.0, source: str = None) -> bool:
    """插入事实。同主体同关系的旧事实自动标记失效（事实更替而非堆积）。"""
    sid = entity_id(conn, subject.strip())
    obj = obj.strip()
    predicate = predicate.strip()
    # 同主体同关系、值不同的旧事实 → 关闭有效期
    conn.execute(
        "UPDATE facts SET valid_to = date('now') "
        "WHERE subject=? AND predicate=? AND object!=? AND valid_to IS NULL",
        (sid, predicate, obj))
    cur = conn.execute(
        "INSERT INTO facts(subject, predicate, object, confidence, source) "
        "VALUES (?,?,?,?,?) "
        "ON CONFLICT(subject, predicate, object) DO UPDATE SET "
        "confidence=excluded.confidence, valid_to=NULL",
        (sid, predicate, obj, confidence, source))
    return cur.rowcount > 0


FACTS_HEADER_RE = re.compile(r"^##\s*FACTS\s*$", re.IGNORECASE)
ROW_RE = re.compile(r"^\s*\|(.+)\|\s*$")


def ingest_file(conn, path: Path) -> int:
    """提取文件中 ## FACTS 段落下的表格行。"""
    count = 0
    in_facts = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if FACTS_HEADER_RE.match(line):
            in_facts = True
            continue
        if in_facts and line.startswith("#"):
            in_facts = False
            continue
        if not in_facts:
            continue
        m = ROW_RE.match(line)
        if not m:
            continue
        cells = [c.strip() for c in m.group(1).split("|")]
        if len(cells) < 3 or cells[0].lower() in ("subject", "主体") \
                or set(cells[0]) <= {"-", ":", " "}:
            continue
        conf = 1.0
        if len(cells) >= 4:
            try:
                conf = float(cells[3])
            except ValueError:
                pass
        if add_fact(conn, cells[0], cells[1], cells[2], conf, source=path.name):
            count += 1
    return count


def render(conn) -> str:
    """渲染当前有效事实为极简 markdown（每事实一行），供 memory-core 索引。"""
    rows = conn.execute(
        "SELECT e.name, f.predicate, f.object, f.confidence FROM facts f "
        "JOIN entities e ON e.id = f.subject "
        "WHERE f.valid_to IS NULL ORDER BY e.name, f.predicate").fetchall()
    lines = [f"# 知识库（事实表渲染视图）",
             f"",
             f"> 自动生成于 {date.today()}，源数据: memory/database/facts.sqlite，勿手工编辑",
             f""]
    current = None
    for name, pred, obj, conf in rows:
        if name != current:
            lines.append(f"\n## {name}\n")
            current = name
        marker = "" if conf >= 0.95 else f"（置信 {conf:.0%}）"
        lines.append(f"- {pred}: {obj}{marker}")
    text = "\n".join(lines) + "\n"
    VIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    VIEW_PATH.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p_add = sub.add_parser("add")
    p_add.add_argument("subject"); p_add.add_argument("predicate"); p_add.add_argument("object")
    p_add.add_argument("--conf", type=float, default=1.0)
    p_add.add_argument("--source", default="manual")
    p_ing = sub.add_parser("ingest")
    p_ing.add_argument("files", nargs="*", help="默认扫描 memory/*.md")
    sub.add_parser("render")
    p_q = sub.add_parser("query")
    p_q.add_argument("keyword")
    sub.add_parser("stats")
    args = ap.parse_args()

    conn = connect()
    try:
        if args.cmd == "init":
            print(f"已初始化: {DB_PATH}")
        elif args.cmd == "add":
            add_fact(conn, args.subject, args.predicate, args.object, args.conf, args.source)
            conn.commit()
            render(conn)
            print("已写入并刷新视图")
        elif args.cmd == "ingest":
            files = [Path(f) for f in args.files] if args.files \
                else sorted((WORKSPACE / "memory").glob("*.md"))
            total = sum(ingest_file(conn, f) for f in files if f.is_file())
            conn.commit()
            render(conn)
            print(f"提取 {total} 条事实（扫描 {len(files)} 个文件），视图已刷新")
        elif args.cmd == "render":
            render(conn)
            n = conn.execute("SELECT count(*) FROM facts WHERE valid_to IS NULL").fetchone()[0]
            print(f"已渲染 {n} 条有效事实 → {VIEW_PATH}")
        elif args.cmd == "query":
            kw = f"%{args.keyword}%"
            for name, pred, obj, conf, vf, vt in conn.execute(
                    "SELECT e.name, f.predicate, f.object, f.confidence, f.valid_from, f.valid_to "
                    "FROM facts f JOIN entities e ON e.id=f.subject "
                    "WHERE e.name LIKE ? OR f.predicate LIKE ? OR f.object LIKE ?",
                    (kw, kw, kw)):
                status = "✓" if vt is None else f"已失效({vt})"
                print(f"{name} | {pred} | {obj} | {conf} | {status}")
        elif args.cmd == "stats":
            n_e = conn.execute("SELECT count(*) FROM entities").fetchone()[0]
            n_f = conn.execute("SELECT count(*) FROM facts").fetchone()[0]
            n_v = conn.execute("SELECT count(*) FROM facts WHERE valid_to IS NULL").fetchone()[0]
            size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
            print(f"实体 {n_e} · 事实 {n_f}（有效 {n_v}）· 库体积 {size/1024:.1f}KB")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
