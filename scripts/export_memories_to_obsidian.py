#!/usr/bin/env python3
"""
记忆系统 → Obsidian 双向桥接
把 SQLite + LanceDB 里的记忆导出为 Obsidian 笔记
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime

VAULT_PATH = Path("/Users/xinglong/Documents/Obsidian Vault")
DB_PATH = Path(__file__).parent.parent / "memory/database/xiaozhi_memory.db"

# 记忆类型 → Obsidian 文件夹
TYPE_FOLDERS = {
    "core_memory": "🧠 记忆/核心记忆",
    "learning": "📚 学习",
    "skill": "🛠️ 技能",
    "event": "📋 事件",
    "preference": "⚙️ 偏好",
    "principle": "📌 原则",
    "improvement": "💡 改进",
}

def ensure_folder(vault: Path, name: str) -> Path:
    p = vault / name
    p.mkdir(parents=True, exist_ok=True)
    return p

def memory_to_markdown(row: dict) -> str:
    """把一条记忆转成 Obsidian 笔记格式"""
    title = row["title"] or "无标题"
    created = row.get("created_at", "")
    updated = row.get("updated_at", created)
    tags = json.loads(row["tags"]) if row.get("tags") else []
    metadata = json.loads(row["metadata"]) if row.get("metadata") else {}
    importance = row.get("importance", 5)

    tag_str = " ".join(f"#{t}" for t in tags) if tags else ""
    if row.get("category"):
        tag_str += f" #{row['category']}"

    content = row.get("content", "") or ""

    lines = [
        "---",
        f"created: {created}",
        f"modified: {updated}",
        f"tags: [{', '.join(tags) if tags else ''}]",
        f"importance: {importance}",
        f"memory_id: {row['id']}",
        f"memory_type: {row['type']}",
    ]
    if metadata.get("source"):
        lines.append(f"source: {metadata['source']}")
    if metadata.get("summary"):
        lines.append(f"summary: {metadata['summary']}")
    if metadata.get("mastery_level"):
        lines.append(f"mastery_level: {metadata['mastery_level']}")

    lines.extend(["---", ""])
    lines.append(f"# {title}")
    lines.append("")
    if content:
        lines.append(content)
        lines.append("")
    if tag_str:
        lines.append(tag_str)

    return "\n".join(lines)

def export_memories():
    """导出所有记忆到 Obsidian"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM memories ORDER BY type, importance DESC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    print(f"[Bridge] 准备导出 {len(rows)} 条记忆到 Obsidian...")
    print(f"[Bridge] Vault: {VAULT_PATH}")

    exported = 0
    for row in rows:
        row = dict(row)
        folder = TYPE_FOLDERS.get(row["type"], "🧠 记忆/其他")

        folder_path = ensure_folder(VAULT_PATH, folder)

        # 文件名：去掉非法字符
        safe_title = row["title"].replace("/", " ").replace("\\", " ").replace(":", "：").replace("*", "").replace("?", "？")[:80]
        filename = f"{folder}/{safe_title}.md"

        filepath = VAULT_PATH / filename
        content = memory_to_markdown(row)

        # 避免覆盖已有（只写新文件）
        if filepath.exists():
            # 比对内容判断是否更新
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()
            if existing.strip() == content.strip():
                continue  # 完全相同，跳过

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        exported += 1
        print(f"  ✅ [{row['type']}] {row['title'][:50]}")

    print(f"\n[Bridge] 导出完成: {exported} 条新/更新笔记")
    return exported

def create_dashboard():
    """创建记忆仪表盘"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT type, COUNT(*) as cnt,
               MAX(importance) as max_imp,
               MAX(created_at) as last_created
        FROM memories
        GROUP BY type
        ORDER BY cnt DESC
    """)
    stats = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total, MAX(importance) as max_imp FROM memories")
    overall = dict(cursor.fetchone())

    conn.close()

    lines = [
        "# 🧠 二饼记忆系统仪表盘",
        "",
        f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 总体",
        "",
        f"- 总记忆数: **{overall['total']}**",
        f"- 最高重要性: **{overall['max_imp']}/10**",
        "",
        "## 按类型分布",
        "",
    ]

    for s in stats:
        folder = TYPE_FOLDERS.get(s["type"], "其他")
        lines.append(f"- [[{folder}|{s['type']}]]: **{s['cnt']}** 条 (最高重要性 {s['max_imp']})")

    lines += [
        "",
        "## 快捷操作",
        "",
        "```",
        f"python3 {DB_PATH.parent.parent}/scripts/erbing_brain_api.py",
        "```",
        "",
        "---",
        "*由二饼的记忆系统自动生成*",
    ]

    dashboard_path = VAULT_PATH / "🧠 记忆/记忆仪表盘.md"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Bridge] 仪表盘已生成: {dashboard_path}")

if __name__ == "__main__":
    n = export_memories()
    create_dashboard()
    print(f"\n🎉 完成！{n} 条记忆已同步到 Obsidian Vault")