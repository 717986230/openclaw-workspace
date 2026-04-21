#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Migration System - 一键迁移脚本
将 Erbing 完整迁移到新设备
Usage:
    python migrate_agent.py --export           # 导出当前环境
    python migrate_agent.py --import           # 导入到新设备
    python migrate_agent.py --check            # 检查迁移包完整性
"""

import os
import sys
import json
import sqlite3
import shutil
import hashlib
import argparse
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("C:/Users/Administrator/.openclaw/workspace")
MEMORY_DB = WORKSPACE / "memory/database/xiaozhi_memory.db"
LANCE_DB = WORKSPACE / "memory/database/lancedb"
SKILLS_DIR = WORKSPACE / "skills"
SCRIPTS_DIR = WORKSPACE / "scripts"
CONFIG_DIR = WORKSPACE / "config"
MIGRATION_DIR = WORKSPACE / "migration"

# 迁移包名称
MIGRATION_PACKAGE = "erbing_migration_{date}.zip"
EXPORTS_DIR = WORKSPACE / "exports"

class AgentMigration:
    def __init__(self):
        self.version = "1.0.0"
        self.date = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def get_file_hash(self, filepath):
        """计算文件SHA256哈希"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def scan_database_tables(self):
        """扫描数据库表结构"""
        conn = sqlite3.connect(str(MEMORY_DB))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_info[table] = {"count": count}
        
        conn.close()
        return table_info
    
    def export(self, output_path=None):
        """导出当前环境"""
        print("=" * 60)
        print("Erbing Agent Migration - Export Mode")
        print("=" * 60)
        
        if output_path is None:
            output_path = EXPORTS_DIR / f"erbing_migration_{self.date}"
        else:
            output_path = Path(output_path)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. 创建导出清单
        manifest = {
            "version": self.version,
            "export_date": self.date,
            "agent_name": "Erbing",
            "platform": "Windows" if os.name == 'nt' else "Unix",
            "components": {}
        }
        
        # 2. 导出数据库
        print("\n[1/6] Exporting Memory Database...")
        db_stats = self.scan_database_tables()
        manifest["components"]["memory_database"] = {
            "path": str(MEMORY_DB),
            "exists": MEMORY_DB.exists(),
            "size": MEMORY_DB.stat().st_size if MEMORY_DB.exists() else 0,
            "tables": db_stats
        }
        
        if MEMORY_DB.exists():
            shutil.copy2(MEMORY_DB, output_path / "xiaozhi_memory.db")
            print(f"  - Copied: {MEMORY_DB.name} ({db_stats['memories']['count']} memories)")
        
        # 3. 导出 LanceDB
        print("\n[2/6] Exporting LanceDB Vector Database...")
        if LANCE_DB.exists():
            shutil.copytree(LANCE_DB, output_path / "lancedb", dirs_exist_ok=True)
            manifest["components"]["lancedb"] = {
                "path": str(LANCE_DB),
                "exists": True,
                "copied": True
            }
            print(f"  - Copied: lancedb/")
        else:
            manifest["components"]["lancedb"] = {"exists": False}
            print("  - Not found (optional)")
        
        # 4. 导出 Skills
        print("\n[3/6] Exporting Skills...")
        skills_list = []
        if SKILLS_DIR.exists():
            for skill in SKILLS_DIR.iterdir():
                if skill.is_dir():
                    skills_list.append(skill.name)
            shutil.copytree(SKILLS_DIR, output_path / "skills", dirs_exist_ok=True)
        manifest["components"]["skills"] = {
            "count": len(skills_list),
            "list": skills_list
        }
        print(f"  - Copied: {len(skills_list)} skills")
        
        # 5. 导出 Scripts
        print("\n[4/6] Exporting Scripts...")
        scripts_list = []
        if SCRIPTS_DIR.exists():
            for script in SCRIPTS_DIR.iterdir():
                if script.suffix in ['.py', '.ps1', '.bat', '.sh']:
                    scripts_list.append(script.name)
            shutil.copytree(SCRIPTS_DIR, output_path / "scripts", dirs_exist_ok=True)
        manifest["components"]["scripts"] = {
            "count": len(scripts_list),
            "list": scripts_list
        }
        print(f"  - Copied: {len(scripts_list)} scripts")
        
        # 6. 导出配置
        print("\n[5/6] Exporting Configuration...")
        config_files = []
        if CONFIG_DIR.exists():
            for cfg in CONFIG_DIR.rglob('*.json'):
                config_files.append(str(cfg.relative_to(WORKSPACE)))
            shutil.copytree(CONFIG_DIR, output_path / "config", dirs_exist_ok=True)
        manifest["components"]["config"] = {
            "count": len(config_files),
            "list": config_files
        }
        print(f"  - Copied: {len(config_files)} config files")
        
        # 7. 导出 Workspace 根目录重要文件
        print("\n[6/6] Exporting Workspace Files...")
        workspace_files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md']
        exported_ws = []
        for f in workspace_files:
            src = WORKSPACE / f
            if src.exists():
                shutil.copy2(src, output_path / f)
                exported_ws.append(f)
        manifest["components"]["workspace_files"] = exported_ws
        print(f"  - Copied: {len(exported_ws)} files")
        
        # 8. 保存清单
        manifest_path = output_path / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        # 9. 创建导入脚本
        print("\n[+] Creating Import Script...")
        self.create_import_script(output_path)
        
        # 10. 创建 requirements 文件
        print("[+] Creating Requirements File...")
        self.create_requirements(output_path)
        
        # 11. 计算哈希
        print("\n[+] Calculating Checksums...")
        checksum_file = output_path / "checksums.json"
        checksums = {}
        for f in output_path.rglob('*'):
            if f.is_file():
                rel_path = str(f.relative_to(output_path))
                checksums[rel_path] = self.get_file_hash(f)
        with open(checksum_file, 'w') as f:
            json.dump(checksums, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"Export Complete!")
        print(f"Package Location: {output_path}")
        print("=" * 60)
        
        # 统计
        total_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
        print(f"\nTotal Size: {total_size / 1024 / 1024:.2f} MB")
        print(f"Total Files: {len(list(output_path.rglob('*')))}")
        print(f"\nTo import on new device:")
        print(f"  1. Copy the '{output_path.name}' folder to new device")
        print(f"  2. Run: python migrate_agent.py --import")
        
        return str(output_path)
    
    def create_import_script(self, package_dir):
        """创建导入脚本"""
        import_script = package_dir / "import.bat"
        
        content = '''@echo off
REM Erbing Agent Migration - Import Script
REM 一键导入 Erbing 到新设备

echo ============================================================
echo Erbing Agent Migration - Import Mode
echo ============================================================
echo.

set WORKSPACE=%USERPROFILE%\\.openclaw\\workspace
set MIGRATION_DIR=%~dp0

echo [1/5] Checking directories...
if not exist "%WORKSPACE%" mkdir "%WORKSPACE%"
if not exist "%WORKSPACE%\\memory" mkdir "%WORKSPACE%\\memory"
if not exist "%WORKSPACE%\\memory\\database" mkdir "%WORKSPACE%\\memory\\database"

echo [2/5] Importing Memory Database...
if exist "%MIGRATION_DIR%\\xiaozhi_memory.db" (
    copy /Y "%MIGRATION_DIR%\\xiaozhi_memory.db" "%WORKSPACE%\\memory\\database\\"
    echo   - Database imported
)

echo [3/5] Importing LanceDB...
if exist "%MIGRATION_DIR%\\lancedb" (
    xcopy /E /Y "%MIGRATION_DIR%\\lancedb" "%WORKSPACE%\\memory\\database\\lancedb\\"
    echo   - LanceDB imported
)

echo [4/5] Importing Skills and Scripts...
if exist "%MIGRATION_DIR%\\skills" (
    xcopy /E /Y "%MIGRATION_DIR%\\skills" "%WORKSPACE%\\skills\\"
    echo   - Skills imported
)
if exist "%MIGRATION_DIR%\\scripts" (
    xcopy /E /Y "%MIGRATION_DIR%\\scripts" "%WORKSPACE%\\scripts\\"
    echo   - Scripts imported
)
if exist "%MIGRATION_DIR%\\config" (
    xcopy /E /Y "%MIGRATION_DIR%\\config" "%WORKSPACE%\\config\\"
    echo   - Config imported
)

echo [5/5] Importing Workspace Files...
for %%f in (SOUL.md IDENTITY.md USER.md AGENTS.md MEMORY.md TOOLS.md BOOTSTRAP.md HEARTBEAT.md) do (
    if exist "%MIGRATION_DIR%%%f" (
        copy /Y "%MIGRATION_DIR%%%f" "%WORKSPACE%%f"
    )
)

echo.
echo ============================================================
echo Import Complete!
echo ============================================================
echo.
echo Starting verification...
python "%MIGRATION_DIR%\\verify_import.py"
echo.
pause
'''
        
        with open(import_script, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def create_requirements(self, package_dir):
        """创建依赖文件"""
        req_file = package_dir / "requirements.txt"
        deps = [
            "sqlite3 (built-in)",
            "lancedb>=0.3.0",
            "sentence-transformers>=2.0.0",
            "networkx>=2.0",
            "numpy>=1.20.0",
            "requests>=2.25.0"
        ]
        with open(req_file, 'w') as f:
            f.write("\n".join(deps))
    
    def import_data(self, package_path):
        """导入数据"""
        print("=" * 60)
        print("Erbing Agent Migration - Import Mode")
        print("=" * 60)
        
        package_path = Path(package_path)
        manifest_path = package_path / "manifest.json"
        
        if not manifest_path.exists():
            print("ERROR: Invalid migration package - manifest.json not found")
            return False
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"\nPackage Info:")
        print(f"  - Version: {manifest['version']}")
        print(f"  - Export Date: {manifest['export_date']}")
        print(f"  - Agent: {manifest['agent_name']}")
        
        workspace = Path.home() / ".openclaw" / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)
        
        # 导入数据库
        print("\n[1/4] Importing Database...")
        src_db = package_path / "xiaozhi_memory.db"
        if src_db.exists():
            dest_db = workspace / "memory/database/xiaozhi_memory.db"
            dest_db.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_db, dest_db)
            print(f"  - Database imported: {dest_db}")
        
        # 导入 LanceDB
        print("\n[2/4] Importing LanceDB...")
        src_lance = package_path / "lancedb"
        if src_lance.exists():
            dest_lance = workspace / "memory/database/lancedb"
            shutil.copytree(src_lance, dest_lance, dirs_exist_ok=True)
            print(f"  - LanceDB imported: {dest_lance}")
        
        # 导入 Skills/Scripts
        print("\n[3/4] Importing Skills & Scripts...")
        for item in ['skills', 'scripts', 'config']:
            src = package_path / item
            if src.exists():
                dest = workspace / item
                shutil.copytree(src, dest, dirs_exist_ok=True)
                print(f"  - {item} imported")
        
        # 导入工作区文件
        print("\n[4/4] Importing Workspace Files...")
        ws_files = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md', 'MEMORY.md', 'TOOLS.md', 'BOOTSTRAP.md', 'HEARTBEAT.md']
        for f in ws_files:
            src = package_path / f
            if src.exists():
                shutil.copy2(src, workspace / f)
                print(f"  - {f}")
        
        print("\n" + "=" * 60)
        print("Import Complete!")
        print("=" * 60)
        
        return True
    
    def verify(self, package_path):
        """验证迁移包完整性"""
        print("=" * 60)
        print("Erbing Migration - Verification Mode")
        print("=" * 60)
        
        package_path = Path(package_path)
        manifest_path = package_path / "manifest.json"
        checksum_path = package_path / "checksums.json"
        
        if not manifest_path.exists():
            print("ERROR: Invalid package - no manifest")
            return False
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        print(f"\nManifest Version: {manifest['version']}")
        print(f"Export Date: {manifest['export_date']}")
        print(f"Agent: {manifest['agent_name']}")
        
        # 验证文件
        print("\nChecking files...")
        all_ok = True
        
        if manifest['components']['memory_database']['exists']:
            db_path = package_path / "xiaozhi_memory.db"
            if db_path.exists():
                expected_size = manifest['components']['memory_database']['size']
                actual_size = db_path.stat().st_size
                if expected_size == actual_size:
                    print(f"  [OK] xiaozhi_memory.db ({actual_size} bytes)")
                else:
                    print(f"  [FAIL] xiaozhi_memory.db size mismatch")
                    all_ok = False
            else:
                print(f"  [FAIL] xiaozhi_memory.db missing")
                all_ok = False
        
        skills = manifest['components']['skills']
        skills_path = package_path / "skills"
        if skills_path.exists():
            actual_count = len([d for d in skills_path.iterdir() if d.is_dir()])
            if actual_count == skills['count']:
                print(f"  [OK] skills ({actual_count} folders)")
            else:
                print(f"  [WARN] skills count mismatch: expected {skills['count']}, got {actual_count}")
        
        # 验证 checksum
        if checksum_path.exists():
            print("\nVerifying checksums...")
            with open(checksum_path, 'r') as f:
                checksums = json.load(f)
            
            for rel_path, expected_hash in checksums.items():
                file_path = package_path / rel_path
                if file_path.exists():
                    actual_hash = self.get_file_hash(file_path)
                    if actual_hash == expected_hash:
                        print(f"  [OK] {rel_path}")
                    else:
                        print(f"  [FAIL] {rel_path} - checksum mismatch!")
                        all_ok = False
                else:
                    print(f"  [FAIL] {rel_path} - file missing!")
                    all_ok = False
        
        print("\n" + "=" * 60)
        if all_ok:
            print("Verification PASSED!")
        else:
            print("Verification FAILED - some issues found")
        print("=" * 60)
        
        return all_ok

def main():
    parser = argparse.ArgumentParser(description='Erbing Agent Migration System')
    parser.add_argument('--export', action='store_true', help='Export current environment')
    parser.add_argument('--import', dest='import_mode', action='store_true', help='Import to new device')
    parser.add_argument('--check', action='store_true', help='Verify migration package')
    parser.add_argument('--path', help='Path to migration package')
    
    args = parser.parse_args()
    
    migration = AgentMigration()
    
    if args.export:
        migration.export()
    elif args.import_mode:
        path = args.path or input("Enter migration package path: ")
        migration.import_data(path)
    elif args.check:
        path = args.path or input("Enter migration package path: ")
        migration.verify(path)
    else:
        print(__doc__)
        print("\nExamples:")
        print("  python migrate_agent.py --export")
        print("  python migrate_agent.py --import --path ./erbing_migration_20260421")
        print("  python migrate_agent.py --check --path ./erbing_migration_20260421")

if __name__ == "__main__":
    main()