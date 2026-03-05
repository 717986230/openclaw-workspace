#!/usr/bin/env python3
"""
AI Robot Clone Tool (Universal Version)
任何 AI 机器人都可以使用此工具导出/导入配置
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

# 核心配置文件列表
CORE_FILES = [
    "SOUL.md",
    "IDENTITY.md",
    "USER.md",
    "MEMORY.md",
    "HEARTBEAT.md",
    "TOOLS.md",
    "AGENTS.md",
]

# 排除的目录和文件
EXCLUDE_PATTERNS = [
    ".git/",
    "__pycache__/",
    ".openclaw/workspace-state.json",
    "*.log",
    ".DS_Store",
    "*.pyc",
]


def find_workspace_root():
    """自动查找 workspace 根目录"""
    # 优先使用当前目录
    current = Path.cwd()
    
    # 检查是否有 SOUL.md（核心标识）
    if (current / "SOUL.md").exists():
        return current
    
    # 尝试常见路径
    common_paths = [
        Path.home() / ".openclaw" / "workspace",
        Path.home() / "workspace",
        Path.cwd() / "workspace",
    ]
    
    for path in common_paths:
        if path.exists() and (path / "SOUL.md").exists():
            return path
    
    return current


def should_exclude(path_str):
    """检查路径是否应该排除"""
    for pattern in EXCLUDE_PATTERNS:
        if pattern.endswith("/"):
            if pattern[:-1] in path_str:
                return True
        elif pattern.startswith("*"):
            if path_str.endswith(pattern[1:]):
                return True
        elif pattern in path_str:
            return True
    return False


def scan_workspace(source_path):
    """扫描工作区文件"""
    print("📋 扫描工作区...")
    
    source = Path(source_path)
    found_files = []
    
    for file in CORE_FILES:
        file_path = source / file
        if file_path.exists():
            size = file_path.stat().st_size
            found_files.append({
                "name": file,
                "path": str(file_path),
                "size": size,
                "size_str": f"{size/1024:.1f}KB"
            })
            print(f"  ✅ {file} ({size/1024:.1f}KB)")
        else:
            print(f"  ⚠️  {file} (不存在)")
    
    return found_files


def export_config(source_path=None, output_path=None):
    """导出配置到克隆包"""
    if not source_path:
        source_path = find_workspace_root()
    
    print(f"📦 导出配置...")
    print(f"   源：{source_path}")
    
    # 扫描文件
    found_files = scan_workspace(source_path)
    
    if not found_files:
        print("❌ 未找到核心配置文件")
        return False
    
    # 生成输出文件名
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = f"clone-package-{timestamp}.zip"
    
    # 创建临时目录
    temp_dir = Path("/tmp/ai-clone-temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    try:
        # 复制文件到临时目录
        print("\n📋 复制文件...")
        for file_info in found_files:
            src = Path(file_info["path"])
            dst = temp_dir / file_info["name"]
            shutil.copy2(src, dst)
            print(f"  ✅ {file_info['name']}")
        
        # 创建元数据
        metadata = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "source_workspace": str(source_path),
            "files": [f["name"] for f in found_files],
            "description": "AI Robot Clone Package"
        }
        
        metadata_path = temp_dir / "clone_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  ✅ clone_metadata.json")
        
        # 打包为 zip
        print(f"\n🗜️  打包为 {output_path}...")
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in temp_dir.iterdir():
                zipf.write(file, file.name)
        
        # 计算大小
        output_size = Path(output_path).stat().st_size
        
        print(f"\n✅ 导出完成！")
        print(f"   文件：{output_path}")
        print(f"   大小：{output_size/1024:.1f}KB")
        print(f"   包含：{len(found_files)} 个核心文件")
        
        return True
        
    finally:
        # 清理临时目录
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def import_config(package_path, target_path=None, preview=False):
    """从克隆包导入配置"""
    package = Path(package_path)
    
    if not package.exists():
        print(f"❌ 文件不存在：{package_path}")
        return False
    
    if not package.suffix.lower() == ".zip":
        print(f"❌ 不是 zip 文件：{package_path}")
        return False
    
    print(f"📥 导入配置...")
    print(f"   包：{package_path}")
    
    if not target_path:
        target_path = str(Path.cwd())
    
    target = Path(target_path)
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
    
    print(f"   目标：{target}")
    
    # 读取元数据
    try:
        with zipfile.ZipFile(package, 'r') as zipf:
            if "clone_metadata.json" in zipf.namelist():
                metadata_content = zipf.read("clone_metadata.json").decode("utf-8")
                metadata = json.loads(metadata_content)
                print(f"\n📋 克隆包信息:")
                print(f"   创建时间：{metadata.get('created_at', '未知')}")
                print(f"   源工作区：{metadata.get('source_workspace', '未知')}")
                print(f"   文件数量：{len(metadata.get('files', []))}")
    except Exception as e:
        print(f"⚠️  无法读取元数据：{e}")
    
    # 预览模式
    if preview:
        print(f"\n📋 包内文件:")
        with zipfile.ZipFile(package, 'r') as zipf:
            for name in zipf.namelist():
                if name != "clone_metadata.json":
                    print(f"  ✅ {name}")
        print(f"\n💡 使用 --import 参数执行实际导入")
        return True
    
    # 列出将要复制的文件
    print(f"\n📋 即将导入以下文件:")
    files_to_import = []
    with zipfile.ZipFile(package, 'r') as zipf:
        for name in zipf.namelist():
            if name != "clone_metadata.json":
                print(f"  ✅ {name}")
                files_to_import.append(name)
    
    # 确认
    print(f"\n⚠️  注意：这将覆盖目标目录的现有文件！")
    
    # 解压文件
    print(f"\n📥 正在导入...")
    target = Path(target_path)
    target.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(package, 'r') as zipf:
        for name in zipf.namelist():
            if name != "clone_metadata.json":
                zipf.extract(name, target)
                print(f"  ✅ {name}")
    
    print(f"\n✅ 导入完成！")
    print(f"   目标：{target_path}")
    print(f"   导入：{len(files_to_import)} 个文件")
    print(f"\n🎉 机器人已成功复制配置！")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="AI 机器人克隆工具 - 导出/导入配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 机器人 A 导出配置
  python clone_robot.py export
  python clone_robot.py export --output my-clone.zip
  
  # 机器人 B 导入配置
  python clone_robot.py import clone-package.zip
  python clone_robot.py import clone-package.zip --preview
  python clone_robot.py import clone-package.zip --target /path/to/workspace
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # export 命令
    export_parser = subparsers.add_parser("export", help="导出配置到克隆包")
    export_parser.add_argument("--source", type=str, help="源工作区路径")
    export_parser.add_argument("--output", type=str, help="输出文件名")
    
    # import 命令
    import_parser = subparsers.add_parser("import", help="从克隆包导入配置")
    import_parser.add_argument("package", type=str, help="克隆包文件路径")
    import_parser.add_argument("--target", type=str, help="目标工作区路径")
    import_parser.add_argument("--preview", action="store_true", help="预览包内容")
    
    args = parser.parse_args()
    
    if args.command == "export":
        success = export_config(args.source, args.output)
        sys.exit(0 if success else 1)
    elif args.command == "import":
        success = import_config(args.package, args.target, args.preview)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
