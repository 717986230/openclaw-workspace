#!/usr/bin/env python3
"""
在 Obsidian Vault 中建立基因系统 / 大脑皮层系统 / 神经系统 的文件夹和索引笔记
"""
from pathlib import Path
import json
from datetime import datetime

VAULT = Path("/Users/xinglong/Documents/Obsidian Vault")
SYSTEMS = [
    {"id": "gene", "name": "🧬 基因系统", "desc": "存放核心身份、长期约束、进化蓝图", "icon": "🧬"},
    {"id": "cortex", "name": "🧠 大脑皮层系统", "desc": "高级抽象、元认知、技能学习、概念模型", "icon": "🧠"},
    {"id": "nervous", "name": "⚡ 神经系统", "desc": "信息传递、记忆检索、技能路由、反馈回路", "icon": "⚡"},
]

def ensure_folder(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path

def create_index_note(system: dict) -> str:
    folder_path = ensure_folder(VAULT / system["name"])
    index_file = folder_path / "索引.md"
    content = f"""# {system['name']} 索引

> {system['desc']}

## 说明
本文件夹用于存放与 **{system['name']}** 相关的知识、笔记和记录。

## 自动同步
- 由 `setup_obsidian_brain_systems.py` 脚本维护结构
- 实际数据存储在记忆系统 (SQLite + LanceDB) 中，可通过混合记忆 API 查询
- 如需在此编辑，请使用 [[记忆仪表盘]] 或直接编辑笔记

## 快捷链接
- [[记忆仪表盘]]
- [[🧠 记忆/核心记忆]]
- [[🧬 基因系统]]
- [[🧠 大脑皮层系统]]
- [[⚡ 神经系统]]

---
*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}* 
"""
    index_file.write_text(content, encoding="utf-8")
    return str(index_file.relative_to(VAULT))

def update_brain_dashboard():
    dashboard = VAULT / "🧠 记忆/记忆仪表盘.md"
    if dashboard.exists():
        existing = dashboard.read_text(encoding="utf-8")
        # Add a section if missing
        if "## 脑系统结构" not in existing:
            new_section = f"""

## 脑系统结构
- [[🧬 基因系统]]: 核心身份、长期约束、进化蓝图
- [[🧠 大脑皮层系统]]: 高级抽象、元认知、技能学习
- [[⚡ 神经系统]]: 信息传递、记忆检索、技能路由
"""
            dashboard.write_text(existing + new_section, encoding="utf-8")
            print(f"[Obsidian] Updated {dashboard.name} with 脑系统结构")
    else:
        print(f"[Obsidian] Dashboard not found: {dashboard}")

def main():
    print("🔧 初始化 Obsidian 脑系统结构...")
    created = []
    for sys in SYSTEMS:
        rel = create_index_note(sys)
        created.append(rel)
        print(f"  ✅ {sys['name']} -> {rel}")

    update_brain_dashboard()
    print(f"\n🎉 已创建 {len(created)} 个脑系统索引笔记")
    print("请在 Obsidian 中刷新查看：")
    for sys in SYSTEMS:
        print(f"  - {sys['name']}")

if __name__ == "__main__":
    main()