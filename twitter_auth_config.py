"""
Twitter 认证配置助手
帮助用户配置 Twitter 认证信息
"""

import os
import sys


def configure_twitter_auth():
    """配置 Twitter 认证"""
    print("=" * 60)
    print("Twitter 认证配置助手")
    print("=" * 60)
    print()

    print("请按照以下步骤获取 Twitter Cookie:")
    print()
    print("1. 在浏览器中登录 Twitter/X")
    print("2. 按 F12 打开开发者工具")
    print("3. 切换到 'Application' 或 '存储' 标签")
    print("4. 左侧菜单 -> Cookies -> https://twitter.com")
    print("5. 找到并复制以下两个 Cookie 的值:")
    print("   - auth_token")
    print("   - ct0")
    print()

    # 获取 auth_token
    auth_token = input("请输入 auth_token 的值: ").strip()

    if not auth_token:
        print("❌ auth_token 不能为空")
        return False

    # 获取 ct0
    ct0 = input("请输入 ct0 的值: ").strip()

    if not ct0:
        print("❌ ct0 不能为空")
        return False

    # 设置环境变量
    print()
    print("设置环境变量...")

    # Windows PowerShell
    print("\n# 在 PowerShell 中运行以下命令:")
    print(f"$env:TWITTER_AUTH_TOKEN = '{auth_token}'")
    print(f"$env:TWITTER_CT0 = '{ct0}'")

    # Windows CMD
    print("\n# 或者在 CMD 中运行以下命令:")
    print(f"set TWITTER_AUTH_TOKEN={auth_token}")
    print(f"set TWITTER_CT0={ct0}")

    # Linux/Mac
    print("\n# 或者在 Linux/Mac 终端中运行以下命令:")
    print(f"export TWITTER_AUTH_TOKEN='{auth_token}'")
    print(f"export TWITTER_CT0='{ct0}'")

    # 测试认证
    print()
    print("测试认证...")
    print()

    # 设置临时环境变量
    os.environ['TWITTER_AUTH_TOKEN'] = auth_token
    os.environ['TWITTER_CT0'] = ct0

    # 测试命令
    import subprocess
    try:
        result = subprocess.run(
            ['twitter', 'feed', '-n', '1'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            print("✅ 认证配置成功！")
            print()
            print("现在可以使用以下命令:")
            print("  twitter feed -n 20              # 获取首页时间线")
            print("  twitter user @username         # 获取用户资料")
            print("  twitter user-posts @username   # 获取用户推文")
            print("  twitter search 'query'         # 搜索推文")
            return True
        else:
            print("❌ 认证配置失败")
            print(f"错误信息: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def save_to_profile():
    """保存到配置文件"""
    print()
    print("=" * 60)
    print("永久保存配置")
    print("=" * 60)
    print()

    print("要永久保存配置，请将以下内容添加到您的 PowerShell 配置文件中:")
    print()

    pwsh_profile = "$env:TWITTER_AUTH_TOKEN = 'your_auth_token_here'"
    pwsh_profile += "\n$env:TWITTER_CT0 = 'your_ct0_here'"

    print(pwsh_profile)
    print()

    print("PowerShell 配置文件位置:")
    print("  - Windows PowerShell: 使用 $PROFILE 变量")
    print("  - PowerShell Core: 使用 $PROFILE.CurrentUserCurrentHost 变量")
    print()

    print("创建或编辑配置文件:")
    print("  notepad $PROFILE")
    print()

    print("或者使用以下命令查看配置文件位置:")
    print("  echo $PROFILE")


def show_current_config():
    """显示当前配置"""
    print()
    print("=" * 60)
    print("当前配置")
    print("=" * 60)
    print()

    auth_token = os.environ.get('TWITTER_AUTH_TOKEN', '未设置')
    ct0 = os.environ.get('TWITTER_CT0', '未设置')

    print(f"TWITTER_AUTH_TOKEN: {'✅ 已设置' if auth_token != '未设置' else '❌ 未设置'}")
    print(f"TWITTER_CT0: {'✅ 已设置' if ct0 != '未设置' else '❌ 未设置'}")
    print()

    if auth_token != '未设置':
        print(f"auth_token (前10位): {auth_token[:10]}...")
    if ct0 != '未设置':
        print(f"ct0 (前10位): {ct0[:10]}...")


def main():
    """主函数"""
    print()
    print("🐦 Twitter 认证配置助手")
    print()

    while True:
        print("请选择操作:")
        print("1. 配置 Twitter 认证")
        print("2. 查看当前配置")
        print("3. 查看永久保存方法")
        print("4. 退出")
        print()

        choice = input("请输入选项 (1-4): ").strip()

        if choice == '1':
            configure_twitter_auth()
        elif choice == '2':
            show_current_config()
        elif choice == '3':
            save_to_profile()
        elif choice == '4':
            print("再见！")
            break
        else:
            print("无效选项，请重新选择")

        print()


if __name__ == "__main__":
    main()
