#!/usr/bin/env python3
"""
Uv包管理集成 - 替代pip的高性能包管理器
使用方式：python scripts/uv_package_manager.py
"""
import subprocess
import sys
from pathlib import Path

class UvPackageManager:
    """Uv包管理器封装"""
    
    def __init__(self):
        self.uv_available = self._check_uv()
    
    def _check_uv(self):
        """检查uv是否可用"""
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def install(self, package):
        """安装包"""
        cmd = ["uv", "pip", "install", package] if self.uv_available else [sys.executable, "-m", "pip", "install", package]
        subprocess.run(cmd)
    
    def sync_requirements(self, requirements_file="requirements.txt"):
        """同步依赖"""
        if not Path(requirements_file).exists():
            print(f"[跳过] {requirements_file} 不存在")
            return
        
        cmd = ["uv", "pip", "install", "-r", requirements_file] if self.uv_available else [sys.executable, "-m", "pip", "install", "-r", requirements_file]
        print(f"[执行] {'uv' if self.uv_available else 'pip'} install -r {requirements_file}")
        subprocess.run(cmd)

def main():
    manager = UvPackageManager()
    
    if manager.uv_available:
        print("[✓] Uv已安装 - 高性能包管理（10-100倍速度）")
    else:
        print("[!] Uv未安装")
        print("\n安装方法：")
        print("  Windows: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("  Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("\n当前使用: pip（标准速度）")
    
    # 同步依赖（如果存在）
    if Path("requirements.txt").exists():
        print("\n[同步依赖]")
        manager.sync_requirements()

if __name__ == "__main__":
    main()
