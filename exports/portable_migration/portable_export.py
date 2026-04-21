#!/usr/bin/env python3
"""U 盘便携迁移 - 使用 Python 避免编码问题"""

import os
import shutil
from pathlib import Path

# 源目录
WORKSPACE = Path("C:/Users/Administrator/.openclaw/workspace")
EXPORT_DIR = Path("C:/Users/Administrator/.openclaw/workspace/exports/portable_migration")
PKG_DIR = EXPORT_DIR / "migration_package"

# 迁移包目录
PKG_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("Erbing Agent - U 盘便携迁移")
print("=" * 60)

# 1. 数据库
print("\n[1/5] Exporting Database...")
db_src = WORKSPACE / "memory/database/xiaozhi_memory.db"
db_dst = PKG_DIR / "xiaozhi_memory.db"
if db_src.exists():
    shutil.copy2(db_src, db_dst)
    size = db_src.stat().st_size / 1024 / 1024
    print(f"  [OK] Database ({size:.2f} MB)")
else:
    print("  [SKIP] Database not found")

# 2. LanceDB
print("\n[2/5] Exporting LanceDB...")
lance_src = WORKSPACE / "memory/database/lancedb"
lance_dst = PKG_DIR / "lancedb"
if lance_src.exists():
    shutil.copytree(lance_src, lance_dst, dirs_exist_ok=True)
    print(f"  [OK] LanceDB")
else:
    print("  [SKIP] LanceDB not found")

# 3. Skills
print("\n[3/5] Exporting Skills...")
skills_src = WORKSPACE / "skills"
skills_dst = PKG_DIR / "skills"
if skills_src.exists():
    shutil.copytree(skills_src, skills_dst, dirs_exist_ok=True)
    count = len([d for d in skills_src.iterdir() if d.is_dir()])
    print(f"  [OK] {count} skills")
else:
    print("  [SKIP] Skills not found")

# 4. Scripts
print("\n[4/5] Exporting Scripts...")
scripts_src = WORKSPACE / "scripts"
scripts_dst = PKG_DIR / "scripts"
if scripts_src.exists():
    shutil.copytree(scripts_src, scripts_dst, dirs_exist_ok=True)
    count = len([f for f in scripts_src.iterdir() if f.is_file()])
    print(f"  [OK] {count} scripts")
else:
    print("  [SKIP] Scripts not found")

# 5. 工作区文件
print("\n[5/5] Exporting Workspace Files...")
ws_files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md']
for f in ws_files:
    src = WORKSPACE / f
    dst = PKG_DIR / f
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  [OK] {f}")

# 计算总大小
total_size = sum(f.stat().st_size for f in PKG_DIR.rglob('*') if f.is_file())
print(f"\n{'='*60}")
print(f"Export Complete!")
print(f"Total Size: {total_size / 1024 / 1024:.2f} MB")
print(f"Package Location: {PKG_DIR}")
print(f"{'='*60}")
print("\nNext steps:")
print("1. Copy the entire 'exports/portable_migration' folder to USB")
print("2. On new computer: python portable_export.py --import")
print("   OR run migrate.bat import")