#!/usr/bin/env python3
"""U 盘便携迁移 - 导入脚本 (新电脑用)"""

import os
import shutil
from pathlib import Path
import sys

# 目标目录
WORKSPACE = Path("C:/Users/Administrator/.openclaw/workspace")
PKG_DIR = Path(__file__).parent / "migration_package"

def check_prerequisites():
    """检查前置条件"""
    print("\n[检查 1/3] 检查 OpenClaw 工作区...")
    if WORKSPACE.exists():
        print(f"  [OK] 工作区存在: {WORKSPACE}")
    else:
        print(f"  [WARN] 工作区不存在，将创建")
    
    # 确保目录存在
    (WORKSPACE / "memory/database").mkdir(parents=True, exist_ok=True)
    print("  [OK] 目录准备完成")
    return True

def check_package():
    """检查迁移包"""
    print("\n[检查 2/3] 检查迁移包...")
    if not PKG_DIR.exists():
        print(f"  [ERROR] 迁移包未找到: {PKG_DIR}")
        print("  请先在原电脑运行: portable_export.py")
        return False
    
    db = PKG_DIR / "xiaozhi_memory.db"
    if not db.exists():
        print(f"  [ERROR] 数据库文件未找到: {db}")
        return False
    
    size = db.stat().st_size / 1024 / 1024
    print(f"  [OK] 找到迁移包 ({size:.2f} MB)")
    return True

def import_data():
    """导入数据"""
    print("\n[检查 3/3] 准备导入...")
    
    # 检查必要文件
    required = ['xiaozhi_memory.db', 'SOUL.md', 'IDENTITY.md']
    missing = []
    for f in required:
        if not (PKG_DIR / f).exists():
            missing.append(f)
    
    if missing:
        print(f"  [WARN] 缺少文件: {missing}")
        return False
    
    print("  [OK] 所有必要文件已找到")
    return True

def do_import():
    """执行导入"""
    print("\n" + "=" * 60)
    print("开始导入 Erbing Agent...")
    print("=" * 60)
    
    # 1. 数据库
    print("\n[1/6] 导入数据库...")
    db_src = PKG_DIR / "xiaozhi_memory.db"
    db_dst = WORKSPACE / "memory/database/xiaozhi_memory.db"
    shutil.copy2(db_src, db_dst)
    print(f"  [OK] 数据库已导入")
    
    # 2. LanceDB
    print("\n[2/6] 导入 LanceDB...")
    lance_src = PKG_DIR / "lancedb"
    lance_dst = WORKSPACE / "memory/database/lancedb"
    if lance_src.exists():
        shutil.copytree(lance_dst, lance_src, dirs_exist_ok=True)
        # Actually we need to copy src to dst
        if lance_dst.exists():
            shutil.rmtree(lance_dst)
        shutil.copytree(lance_src, lance_dst)
        print(f"  [OK] LanceDB 已导入")
    
    # 3. Skills
    print("\n[3/6] 导入 Skills...")
    skills_src = PKG_DIR / "skills"
    skills_dst = WORKSPACE / "skills"
    if skills_src.exists():
        if skills_dst.exists():
            # 合并而非覆盖
            for item in skills_src.iterdir():
                dest = skills_dst / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        else:
            shutil.copytree(skills_src, skills_dst)
        count = len([d for d in skills_src.iterdir() if d.is_dir()])
        print(f"  [OK] {count} 个 Skills 已导入")
    
    # 4. Scripts
    print("\n[4/6] 导入 Scripts...")
    scripts_src = PKG_DIR / "scripts"
    scripts_dst = WORKSPACE / "scripts"
    if scripts_src.exists():
        if scripts_dst.exists():
            for item in scripts_src.iterdir():
                dest = scripts_dst / item.name
                if item.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
        else:
            shutil.copytree(scripts_src, scripts_dst)
        count = len([f for f in scripts_src.iterdir() if f.is_file()])
        print(f"  [OK] {count} 个 Scripts 已导入")
    
    # 5. Config
    print("\n[5/6] 导入 Config...")
    config_src = PKG_DIR / "config"
    config_dst = WORKSPACE / "config"
    if config_src.exists():
        if config_dst.exists():
            for item in config_src.iterdir():
                shutil.copy2(item, config_dst / item.name)
        else:
            shutil.copytree(config_src, config_dst)
        print(f"  [OK] Config 已导入")
    
    # 6. 工作区文件
    print("\n[6/6] 导入工作区文件...")
    ws_files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md']
    for f in ws_files:
        src = PKG_DIR / f
        dst = WORKSPACE / f
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  [OK] {f}")
    
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"\nErbing 已成功迁移到本机！")
    print(f"\n注意: 频道凭证(Discord/Feishu等)需要重新配置")
    print(f"\n建议重启 OpenClaw 服务以加载新数据")

def do_export():
    """执行导出（复用 portable_export.py 的逻辑）"""
    print("\n" + "=" * 60)
    print("开始导出 Erbing Agent...")
    print("=" * 60)
    
    PKG_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. 数据库
    print("\n[1/5] 导出数据库...")
    db_src = WORKSPACE / "memory/database/xiaozhi_memory.db"
    db_dst = PKG_DIR / "xiaozhi_memory.db"
    if db_src.exists():
        shutil.copy2(db_src, db_dst)
        size = db_src.stat().st_size / 1024 / 1024
        print(f"  [OK] Database ({size:.2f} MB)")
    
    # 2. LanceDB
    print("\n[2/5] 导出 LanceDB...")
    lance_src = WORKSPACE / "memory/database/lancedb"
    lance_dst = PKG_DIR / "lancedb"
    if lance_src.exists():
        shutil.copytree(lance_src, lance_dst, dirs_exist_ok=True)
        print(f"  [OK] LanceDB")
    
    # 3-5. Skills, Scripts, Workspace files
    print("\n[3/5] 导出 Skills...")
    skills_src = WORKSPACE / "skills"
    if skills_src.exists():
        shutil.copytree(skills_src, PKG_DIR / "skills", dirs_exist_ok=True)
        print(f"  [OK] Skills")
    
    print("\n[4/5] 导出 Scripts...")
    scripts_src = WORKSPACE / "scripts"
    if scripts_src.exists():
        shutil.copytree(scripts_src, PKG_DIR / "scripts", dirs_exist_ok=True)
        print(f"  [OK] Scripts")
    
    print("\n[5/5] 导出工作区文件...")
    ws_files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md']
    for f in ws_files:
        src = WORKSPACE / f
        if src.exists():
            shutil.copy2(src, PKG_DIR / f)
            print(f"  [OK] {f}")
    
    total_size = sum(f.stat().st_size for f in PKG_DIR.rglob('*') if f.is_file())
    print(f"\n{'='*60}")
    print(f"导出完成！({total_size / 1024 / 1024:.2f} MB)")
    print(f"{'='*60}")

def do_check():
    """验证迁移包"""
    print("\n" + "=" * 60)
    print("验证迁移包...")
    print("=" * 60)
    
    if not PKG_DIR.exists():
        print("[ERROR] 迁移包不存在")
        return
    
    print(f"\n检查文件...")
    
    required = {
        'xiaozhi_memory.db': '数据库',
        'SOUL.md': '身份文件',
        'IDENTITY.md': '身份文件',
        'skills': 'Skills文件夹',
        'scripts': 'Scripts文件夹',
    }
    
    all_ok = True
    for item, desc in required.items():
        path = PKG_DIR / item
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / 1024 / 1024
                print(f"  [OK] {desc} ({size:.2f} MB)")
            else:
                count = len([d for d in path.iterdir()])
                print(f"  [OK] {desc} ({count} items)")
        else:
            print(f"  [MISSING] {desc}")
            all_ok = False
    
    print(f"\n{'='*60}")
    if all_ok:
        print("验证通过！迁移包完整。")
    else:
        print("验证完成，部分文件缺失。")
    print(f"{'='*60}")

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == '--import' or cmd == 'import':
            if check_prerequisites() and check_package() and import_data():
                do_import()
            return
        elif cmd == '--export' or cmd == 'export':
            do_export()
            return
        elif cmd == '--check' or cmd == 'check':
            do_check()
            return
    
    # 默认显示菜单
    print("=" * 60)
    print("Erbing Agent - U 盘便携迁移")
    print("=" * 60)
    print("\n用法:")
    print("  python portable_import.py --export   导出到U盘")
    print("  python portable_import.py --import   从U盘导入")
    print("  python portable_import.py --check    验证迁移包")
    print("\n或者双击运行 migrate.bat")

if __name__ == "__main__":
    main()