#!/usr/bin/env python3
"""
Erbing 概念图记忆系统
把记忆从"条目列表"进化成"概念图"——节点 + 边构成的网状结构。

核心概念：
- 节点（Node）：实体（人、项目、概念、技术）
- 边（Edge）：关系（uses/depends_on/belongs_to/learned_from/improved_from/partners_with）
- 记忆通过 memory_nodes 关联到节点

数据库表（在 xiaozhi_memory.db 中创建）：
- concept_nodes   : 概念节点表
- concept_edges   : 概念边表
- memory_nodes    : 记忆→节点关联表
"""

import sqlite3
import re
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple

DB_PATH = "/Users/xinglong/openclaw-workspace/memory/database/xiaozhi_memory.db"

# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
-- 概念节点表
CREATE TABLE IF NOT EXISTS concept_nodes (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL UNIQUE,
    node_type    TEXT,
    description  TEXT,
    importance   INTEGER DEFAULT 5,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 概念边表
CREATE TABLE IF NOT EXISTS concept_edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    from_node_id  INTEGER,
    to_node_id    INTEGER,
    relation      TEXT,
    weight        REAL    DEFAULT 1.0,
    context       TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_node_id) REFERENCES concept_nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (to_node_id)   REFERENCES concept_nodes(id) ON DELETE CASCADE
);

-- 记忆到节点的关联表
CREATE TABLE IF NOT EXISTS memory_nodes (
    memory_id  INTEGER,
    node_id    INTEGER,
    PRIMARY KEY (memory_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_edges_from  ON concept_edges(from_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_to    ON concept_edges(to_node_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel   ON concept_edges(relation);
CREATE INDEX IF NOT EXISTS idx_nodes_type  ON concept_nodes(node_type);
CREATE INDEX IF NOT EXISTS idx_nodes_name  ON concept_nodes(name);
"""

RELATIONS = {
    "uses", "depends_on", "belongs_to", "learned_from", "improved_from",
    "partners_with", "created_by", "powered_by", "similar_to", "leads_to",
    "contains", "implements", "supports", "competes_with", "succeeded_by",
}

NODE_TYPES = {
    "person", "project", "concept", "technology", "skill",
    "tool", "company", "event", "product", "framework", "language",
}


def get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    conn = get_conn(db_path)
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


# ─── NodeManager ──────────────────────────────────────────────────────────────

class NodeManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def add_node(self, name: str, node_type: str = "concept",
                 description: str = "", importance: int = 5) -> int:
        conn = get_conn(self.db_path)
        cur = conn.execute(
            "INSERT INTO concept_nodes (name, node_type, description, importance) VALUES (?, ?, ?, ?)",
            (name, node_type, description, importance),
        )
        node_id = cur.lastrowid
        conn.commit()
        conn.close()
        return node_id

    def find_or_create(self, name: str, node_type: str = "concept",
                       description: str = "", importance: int = 5) -> Tuple[int, bool]:
        conn = get_conn(self.db_path)
        row = conn.execute("SELECT id FROM concept_nodes WHERE name = ?", (name,)).fetchone()
        if row:
            conn.close()
            return row["id"], False
        cur = conn.execute(
            "INSERT INTO concept_nodes (name, node_type, description, importance) VALUES (?, ?, ?, ?)",
            (name, node_type, description, importance),
        )
        node_id = cur.lastrowid
        conn.commit()
        conn.close()
        return node_id, True

    def get_node(self, name: str) -> Optional[Dict[str, Any]]:
        conn = get_conn(self.db_path)
        row = conn.execute("SELECT * FROM concept_nodes WHERE name = ?", (name,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_node_by_id(self, node_id: int) -> Optional[Dict[str, Any]]:
        conn = get_conn(self.db_path)
        row = conn.execute("SELECT * FROM concept_nodes WHERE id = ?", (node_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_nodes_by_type(self, node_type: str) -> List[Dict[str, Any]]:
        conn = get_conn(self.db_path)
        rows = conn.execute(
            "SELECT * FROM concept_nodes WHERE node_type = ? ORDER BY importance DESC, name",
            (node_type,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_nodes(self, limit: int = 500) -> List[Dict[str, Any]]:
        conn = get_conn(self.db_path)
        rows = conn.execute(
            "SELECT * FROM concept_nodes ORDER BY importance DESC, name LIMIT ?", (limit,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_node(self, node_id: int, **kwargs) -> bool:
        allowed = {"name", "node_type", "description", "importance"}
        bad = set(kwargs) - allowed
        if bad:
            raise ValueError(f"Unknown fields: {bad}")
        if not kwargs:
            return False
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [node_id]
        conn = get_conn(self.db_path)
        cur = conn.execute(
            f"UPDATE concept_nodes SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", vals,
        )
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok

    def delete_node(self, node_id: int) -> bool:
        conn = get_conn(self.db_path)
        cur = conn.execute("DELETE FROM concept_nodes WHERE id = ?", (node_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok

    def search_nodes(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        conn = get_conn(self.db_path)
        rows = conn.execute(
            "SELECT * FROM concept_nodes WHERE name LIKE ? OR description LIKE ? ORDER BY importance DESC LIMIT ?",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]


# ─── EdgeManager ──────────────────────────────────────────────────────────────

class EdgeManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._nodes = NodeManager(db_path)

    def add_edge(self, from_name: str, to_name: str, relation: str,
                 weight: float = 1.0, context: str = "") -> int:
        from_id, _ = self._nodes.find_or_create(from_name)
        to_id, _ = self._nodes.find_or_create(to_name)
        conn = get_conn(self.db_path)
        cur = conn.execute(
            "INSERT INTO concept_edges (from_node_id, to_node_id, relation, weight, context) VALUES (?, ?, ?, ?, ?)",
            (from_id, to_id, relation, weight, context),
        )
        edge_id = cur.lastrowid
        conn.commit()
        conn.close()
        return edge_id

    def get_edges_from(self, node_name: str) -> List[Dict[str, Any]]:
        node = self._nodes.get_node(node_name)
        if not node:
            return []
        conn = get_conn(self.db_path)
        rows = conn.execute(
            """SELECT e.*, n.name as to_name
               FROM concept_edges e
               JOIN concept_nodes n ON e.to_node_id = n.id
               WHERE e.from_node_id = ?""",
            (node["id"],),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_edges_to(self, node_name: str) -> List[Dict[str, Any]]:
        node = self._nodes.get_node(node_name)
        if not node:
            return []
        conn = get_conn(self.db_path)
        rows = conn.execute(
            """SELECT e.*, n.name as from_name
               FROM concept_edges e
               JOIN concept_nodes n ON e.from_node_id = n.id
               WHERE e.to_node_id = ?""",
            (node["id"],),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_related_nodes(self, node_name: str, depth: int = 1) -> List[Dict[str, Any]]:
        """获取与某节点直接相连的所有节点"""
        node = self._nodes.get_node(node_name)
        if not node:
            return []
        conn = get_conn(self.db_path)
        rows = conn.execute(
            """SELECT DISTINCT n.*, e.relation, e.weight
               FROM concept_edges e
               JOIN concept_nodes n ON n.id IN (e.from_node_id, e.to_node_id)
               WHERE (e.from_node_id = ? OR e.to_node_id = ?) AND n.id != ?""",
            (node["id"], node["id"], node["id"]),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_edge(self, edge_id: int, **kwargs) -> bool:
        allowed = {"relation", "weight", "context"}
        bad = set(kwargs) - allowed
        if bad:
            raise ValueError(f"Unknown fields: {bad}")
        if not kwargs:
            return False
        sets = ", ".join(f"{k} = ?" for k in kwargs)
        vals = list(kwargs.values()) + [edge_id]
        conn = get_conn(self.db_path)
        cur = conn.execute(f"UPDATE concept_edges SET {sets} WHERE id = ?", vals)
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok

    def delete_edge(self, edge_id: int) -> bool:
        conn = get_conn(self.db_path)
        cur = conn.execute("DELETE FROM concept_edges WHERE id = ?", (edge_id,))
        conn.commit()
        ok = cur.rowcount > 0
        conn.close()
        return ok


# ─── MemoryGraphIntegrator ────────────────────────────────────────────────────

class MemoryGraphIntegrator:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._nodes = NodeManager(db_path)
        self._edges = EdgeManager(db_path)

    def link_memory_to_nodes(self, memory_id: int, node_names: List[str]) -> None:
        for name in node_names:
            node_id, _ = self._nodes.find_or_create(name)
            conn = get_conn(self.db_path)
            conn.execute(
                "INSERT OR IGNORE INTO memory_nodes (memory_id, node_id) VALUES (?, ?)",
                (memory_id, node_id),
            )
            conn.commit()
            conn.close()

    def get_memory_graph(self, memory_id: int) -> Dict[str, Any]:
        """返回某个记忆关联的概念子图"""
        conn = get_conn(self.db_path)
        rows = conn.execute(
            "SELECT node_id FROM memory_nodes WHERE memory_id = ?", (memory_id,),
        ).fetchall()
        conn.close()

        if not rows:
            return {"nodes": [], "edges": []}

        node_ids = [r["node_id"] for r in rows]
        placeholders = ",".join("?" * len(node_ids))

        conn = get_conn(self.db_path)
        nodes = conn.execute(
            f"SELECT * FROM concept_nodes WHERE id IN ({placeholders})", node_ids,
        ).fetchall()
        edges = conn.execute(
            f"""SELECT e.*, fn.name as from_name, tn.name as to_name
                FROM concept_edges e
                JOIN concept_nodes fn ON e.from_node_id = fn.id
                JOIN concept_nodes tn ON e.to_node_id = tn.id
                WHERE e.from_node_id IN ({placeholders}) OR e.to_node_id IN ({placeholders})""",
            node_ids + node_ids,
        ).fetchall()
        conn.close()

        return {
            "nodes": [dict(r) for r in nodes],
            "edges": [dict(r) for r in edges],
        }

    def extract_nodes_from_memory(self, memory_content: str, memory_title: str = "") -> List[str]:
        """从记忆内容中自动提取实体（简单规则匹配）"""
        entities = set()
        # 标题作为实体
        if memory_title:
            entities.add(memory_title.strip())
        # 英文大写词（疑似专有名词）
        entities.update(re.findall(r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*", memory_content))
        # 中文人名/项目名等
        entities.update(re.findall(r"[\u4e00-\u9fff]{2,8}", memory_content))
        # 去掉太短的
        entities = {e for e in entities if len(e) >= 2}
        return list(entities)

    def populate_graph_from_memories(self) -> int:
        """从现有memories表提取实体，填充概念图。返回填充的实体数。"""
        conn = get_conn(self.db_path)
        rows = conn.execute("SELECT id, title, content FROM memories").fetchall()
        conn.close()

        count = 0
        for row in rows:
            extracted = self.extract_nodes_from_memory(row["content"] or "", row["title"] or "")
            for name in extracted[:10]:  # 每条记忆最多提取10个实体
                self._nodes.find_or_create(name)
                count += 1
            linked = conn.execute(
                "SELECT id FROM concept_nodes WHERE name IN ({})".format(
                    ",".join("?" * len(extracted[:10])) if extracted else "NULL"
                ),
                extracted[:10],
            ).fetchall() if extracted else []
            for lrow in linked:
                conn.execute(
                    "INSERT OR IGNORE INTO memory_nodes (memory_id, node_id) VALUES (?, ?)",
                    (row["id"], lrow["id"]),
                )
            conn.commit()
        return count


# ─── GraphQuery ────────────────────────────────────────────────────────────────

class GraphQuery:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._nodes = NodeManager(db_path)
        self._edges = EdgeManager(db_path)

    def query(self, question: str) -> Dict[str, Any]:
        """简单的自然语言查询接口（基于关键词匹配）"""
        keywords = re.findall(r"[\w]+", question.lower())
        nodes = self._nodes.get_all_nodes(limit=100)

        scored = []
        for node in nodes:
            score = 0
            name_lower = node["name"].lower()
            desc_lower = (node["description"] or "").lower()
            for kw in keywords:
                if kw in name_lower:
                    score += 3
                if kw in desc_lower:
                    score += 1
            if score > 0:
                scored.append((score, node))

        scored.sort(reverse=True)
        return {"results": [n for _, n in scored[:10]], "question": question}

    def find_path(self, start_name: str, end_name: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """找两节点之间的路径（BFS）"""
        start = self._nodes.get_node(start_name)
        end = self._nodes.get_node(end_name)
        if not start or not end:
            return []

        conn = get_conn(self.db_path)
        visited = {start["id"]}
        queue = [(start["id"], [])]

        while queue:
            current_id, path = queue.pop(0)
            if current_id == end["id"]:
                conn.close()
                return path

            if len(path) >= max_depth:
                continue

            rows = conn.execute(
                """SELECT e.*, n.id as neighbor_id, n.name
                   FROM concept_edges e
                   JOIN concept_nodes n ON n.id IN (e.from_node_id, e.to_node_id)
                   WHERE (e.from_node_id = ? OR e.to_node_id = ?) AND n.id NOT IN ({})""".format(
                       ",".join("?" * len(visited))
                   ),
                [current_id, current_id] + list(visited),
            ).fetchall()

            for row in rows:
                neighbor_id = row["neighbor_id"]
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    new_path = path + [{
                        "from": start_name if row["from_node_id"] == start["id"] else row["from_name"],
                        "relation": row["relation"],
                        "to": row["to_name"],
                    }]
                    queue.append((neighbor_id, new_path))

        conn.close()
        return []

    def get_concept_clusters(self) -> List[List[Dict[str, Any]]]:
        """简单的连通分量检测，找出概念簇"""
        conn = get_conn(self.db_path)
        nodes = conn.execute("SELECT id, name, node_type FROM concept_nodes").fetchall()
        edges = conn.execute("SELECT from_node_id, to_node_id FROM concept_edges").fetchall()
        conn.close()

        if not nodes:
            return []

        adj = {n["id"]: set() for n in nodes}
        for e in edges:
            if e["from_node_id"] in adj and e["to_node_id"] in adj:
                adj[e["from_node_id"]].add(e["to_node_id"])
                adj[e["to_node_id"]].add(e["from_node_id"])

        visited = set()
        clusters = []

        for start_id in adj:
            if start_id in visited:
                continue
            cluster = []
            stack = [start_id]
            while stack:
                nid = stack.pop()
                if nid in visited:
                    continue
                visited.add(nid)
                node = next((n for n in nodes if n["id"] == nid), None)
                if node:
                    cluster.append(dict(node))
                for neighbor in adj[nid]:
                    if neighbor not in visited:
                        stack.append(neighbor)
            if cluster:
                clusters.append(cluster)

        return clusters


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # 初始化数据库
    init_db()
    print("✅ 概念图数据库初始化完成")

    nodes = NodeManager()
    edges = EdgeManager()
    integrator = MemoryGraphIntegrator()
    graphq = GraphQuery()

    # 填充一些示例数据
    sample_data = [
        ("Erbing", "person", "AI workspace agent for 大饼", 10),
        ("大饼", "person", "Erbing的主人，很慷慨", 10),
        ("OpenClaw", "framework", "AI agent运行框架", 8),
        ("Claude Code", "tool", "代码编辑器AI工具", 8),
        ("SQLite", "technology", "关系数据库", 7),
        ("概念图", "concept", "图状知识表示方法", 7),
    ]

    for name, ntype, desc, imp in sample_data:
        nodes.find_or_create(name, ntype, desc, imp)

    # 建立示例关系
    relations = [
        ("Erbing", "OpenClaw", "runs_on"),
        ("Erbing", "Claude Code", "uses"),
        ("Erbing", "大饼", "serves"),
        ("概念图", "SQLite", "stored_in"),
        ("OpenClaw", "Claude Code", "integrates_with"),
    ]
    for from_n, to_n, rel in relations:
        try:
            edges.add_edge(from_n, to_n, rel)
        except Exception:
            pass

    print(f"✅ 示例数据填充完成：{len(nodes.get_all_nodes())} 节点")

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(f"\n🔍 查询: {query}")
        results = graphq.query(query)
        for r in results["results"]:
            print(f"  • {r['name']} ({r['node_type']}) - {r.get('description', '')[:60]}")