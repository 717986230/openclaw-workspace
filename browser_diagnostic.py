"""
浏览器诊断脚本
检查系统中安装的浏览器和Cookie文件位置
"""

import os
import glob
from datetime import datetime


def check_chrome():
    """检查Chrome浏览器"""
    print("检查 Chrome...")
    print("-" * 60)

    paths_to_check = []

    # Windows
    if os.name == 'nt':
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        if local_app_data:
            chrome_exe = os.path.join(local_app_data, 'Google', 'Chrome', 'Application', 'chrome.exe')
            chrome_user_data = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data')

            paths_to_check.append(('Chrome 可执行文件', chrome_exe))
            paths_to_check.append(('Chrome 用户数据', chrome_user_data))

    # macOS
    elif os.name == 'posix' and os.path.exists('/Applications'):
        chrome_app = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        chrome_user_data = os.path.expanduser('~/Library/Application Support/Google/Chrome')

        paths_to_check.append(('Chrome 可执行文件', chrome_app))
        paths_to_check.append(('Chrome 用户数据', chrome_user_data))

    # Linux
    elif os.name == 'posix':
        chrome_exe = '/usr/bin/google-chrome'
        chrome_user_data = os.path.expanduser('~/.config/google-chrome')

        paths_to_check.append(('Chrome 可执行文件', chrome_exe))
        paths_to_check.append(('Chrome 用户数据', chrome_user_data))

    found = False
    for description, path in paths_to_check:
        if os.path.exists(path):
            found = True
            if os.path.isfile(path):
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[OK] {description}: {path}")
                print(f"     大小: {size:.2f} MB, 修改时间: {mtime}")
            else:
                print(f"[OK] {description}: {path}")

    if not found:
        print("[X] Chrome 未安装")

    print()
    return found


def check_edge():
    """检查Edge浏览器"""
    print("检查 Edge...")
    print("-" * 60)

    paths_to_check = []

    # Windows
    if os.name == 'nt':
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        if local_app_data:
            edge_exe = os.path.join(local_app_data, 'Microsoft', 'Edge', 'Application', 'msedge.exe')
            edge_user_data = os.path.join(local_app_data, 'Microsoft', 'Edge', 'User Data')

            paths_to_check.append(('Edge 可执行文件', edge_exe))
            paths_to_check.append(('Edge 用户数据', edge_user_data))

    found = False
    for description, path in paths_to_check:
        if os.path.exists(path):
            found = True
            if os.path.isfile(path):
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[OK] {description}: {path}")
                print(f"     大小: {size:.2f} MB, 修改时间: {mtime}")
            else:
                print(f"[OK] {description}: {path}")

    if not found:
        print("[X] Edge 未安装")

    print()
    return found


def check_firefox():
    """检查Firefox浏览器"""
    print("检查 Firefox...")
    print("-" * 60)

    paths_to_check = []

    # Windows
    if os.name == 'nt':
        app_data = os.environ.get('APPDATA', '')
        if app_data:
            firefox_exe = os.path.join(os.environ.get('PROGRAMFILES', ''), 'Mozilla Firefox', 'firefox.exe')
            firefox_profiles = os.path.join(app_data, 'Mozilla', 'Firefox', 'Profiles')

            paths_to_check.append(('Firefox 可执行文件', firefox_exe))
            paths_to_check.append(('Firefox 配置文件', firefox_profiles))

    # macOS
    elif os.name == 'posix' and os.path.exists('/Applications'):
        firefox_app = '/Applications/Firefox.app/Contents/MacOS/firefox'
        firefox_profiles = os.path.expanduser('~/Library/Application Support/Firefox/Profiles')

        paths_to_check.append(('Firefox 可执行文件', firefox_app))
        paths_to_check.append(('Firefox 配置文件', firefox_profiles))

    # Linux
    elif os.name == 'posix':
        firefox_exe = '/usr/bin/firefox'
        firefox_profiles = os.path.expanduser('~/.mozilla/firefox')

        paths_to_check.append(('Firefox 可执行文件', firefox_exe))
        paths_to_check.append(('Firefox 配置文件', firefox_profiles))

    found = False
    for description, path in paths_to_check:
        if os.path.exists(path):
            found = True
            if os.path.isfile(path):
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[OK] {description}: {path}")
                print(f"     大小: {size:.2f} MB, 修改时间: {mtime}")
            else:
                print(f"[OK] {description}: {path}")

    if not found:
        print("[X] Firefox 未安装")

    print()
    return found


def check_brave():
    """检查Brave浏览器"""
    print("检查 Brave...")
    print("-" * 60)

    paths_to_check = []

    # Windows
    if os.name == 'nt':
        local_app_data = os.environ.get('LOCALAPPDATA', '')
        if local_app_data:
            brave_exe = os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'Application', 'brave.exe')
            brave_user_data = os.path.join(local_app_data, 'BraveSoftware', 'Brave-Browser', 'User Data')

            paths_to_check.append(('Brave 可执行文件', brave_exe))
            paths_to_check.append(('Brave 用户数据', brave_user_data))

    found = False
    for description, path in paths_to_check:
        if os.path.exists(path):
            found = True
            if os.path.isfile(path):
                size = os.path.getsize(path) / (1024 * 1024)  # MB
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                print(f"[OK] {description}: {path}")
                print(f"     大小: {size:.2f} MB, 修改时间: {mtime}")
            else:
                print(f"[OK] {description}: {path}")

    if not found:
        print("[X] Brave 未安装")

    print()
    return found


def check_system_info():
    """检查系统信息"""
    print("系统信息:")
    print("-" * 60)
    print(f"操作系统: {os.name}")
    print(f"Python版本: {os.sys.version}")

    if os.name == 'nt':
        print(f"LOCALAPPDATA: {os.environ.get('LOCALAPPDATA', '未设置')}")
        print(f"APPDATA: {os.environ.get('APPDATA', '未设置')}")
        print(f"PROGRAMFILES: {os.environ.get('PROGRAMFILES', '未设置')}")

    print()


def main():
    """主函数"""
    print()
    print("=" * 60)
    print("浏览器诊断工具")
    print("=" * 60)
    print()

    # 检查系统信息
    check_system_info()

    # 检查各个浏览器
    chrome_found = check_chrome()
    edge_found = check_edge()
    firefox_found = check_firefox()
    brave_found = check_brave()

    # 总结
    print("=" * 60)
    print("诊断总结:")
    print("-" * 60)

    browsers_found = []
    if chrome_found:
        browsers_found.append("Chrome")
    if edge_found:
        browsers_found.append("Edge")
    if firefox_found:
        browsers_found.append("Firefox")
    if brave_found:
        browsers_found.append("Brave")

    if browsers_found:
        print(f"找到的浏览器: {', '.join(browsers_found)}")
        print()
        print("建议:")
        print("1. 确保已登录Twitter账号")
        print("2. 确保已访问过Twitter网站")
        print("3. 关闭浏览器后重试提取")
    else:
        print("未找到任何支持的浏览器")
        print()
        print("建议:")
        print("1. 安装Chrome、Edge、Firefox或Brave浏览器")
        print("2. 登录Twitter账号")
        print("3. 访问Twitter网站")
        print("4. 重新运行提取脚本")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
