"""
MT5 系统启动指南
"""

print("=" * 60)
print("MT5 交易项目启动指南")
print("=" * 60)
print()

print("【1/3】检查 MT5 终端")
print()

import os
mt5_path = r"C:\Program Files\MetaTrader 5\terminal64.exe"

if os.path.exists(mt5_path):
    print(f"[OK] MT5 终端已安装: {mt5_path}")
else:
    print(f"[ERROR] MT5 终端未安装: {mt5_path}")
    print("请先安装 MT5 终端")

print()

print("【2/3】检查 MT5 配置")
print()

from mt5_system.config import MT5_CONFIG

print(f"MT5 账号: {MT5_CONFIG['login']}")
print(f"MT5 服务器: {MT5_CONFIG['server']}")
print(f"MT5 路径: {MT5_CONFIG['path']}")
print()

print("【3/3】启动步骤")
print()

print("步骤 1: 手动登录 MT5 终端")
print("  - 打开 MT5 终端")
print("  - 使用账号和密码登录")
print("  - 确保连接成功")
print()

print("步骤 2: 启动 MT5 系统")
print("  - 运行: python mt5_system/start.py")
print("  - 或运行: python mt5_system/start_v2.bat")
print()

print("步骤 3: 访问 Web 界面")
print("  - 打开浏览器")
print("  - 访问: http://localhost:5000")
print("  - 查看实时监控界面")
print()

print("=" * 60)
print("MT5 交易项目启动指南完成")
print("=" * 60)