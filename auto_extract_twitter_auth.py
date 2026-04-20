"""
自动从Chrome浏览器提取Twitter认证信息
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime
import urllib.parse


class ChromeCookieExtractor:
    """Chrome Cookie 提取器"""

    def __init__(self):
        """初始化提取器"""
        self.chrome_paths = self._get_chrome_paths()

    def _get_chrome_paths(self) -> dict:
        """获取Chrome数据路径"""
        paths = {}

        # Windows
        if os.name == 'nt':
            local_app_data = os.environ.get('LOCALAPPDATA', '')
            if local_app_data:
                paths['windows'] = os.path.join(
                    local_app_data,
                    'Google',
                    'Chrome',
                    'User Data',
                    'Default',
                    'Cookies'
                )

        # macOS
        elif os.name == 'posix' and os.path.exists('/Applications'):
            paths['macos'] = os.path.expanduser(
                '~/Library/Application Support/Google/Chrome/Default/Cookies'
            )

        # Linux
        elif os.name == 'posix':
            paths['linux'] = os.path.expanduser(
                '~/.config/google-chrome/Default/Cookies'
            )

        return paths

    def _find_chrome_cookies(self) -> str:
        """查找Chrome Cookie文件"""
        for platform, path in self.chrome_paths.items():
            if os.path.exists(path):
                print(f"找到Chrome Cookie文件: {path}")
                return path

        print("未找到Chrome Cookie文件")
        return None

    def _copy_cookies_db(self, original_path: str) -> str:
        """复制Cookie数据库（避免锁定）"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f"/tmp/cookies_copy_{timestamp}.db"

        try:
            shutil.copy2(original_path, temp_path)
            print(f"Cookie数据库已复制到: {temp_path}")
            return temp_path
        except Exception as e:
            print(f"复制Cookie数据库失败: {e}")
            return None

    def extract_twitter_cookies(self) -> dict:
        """提取Twitter Cookie"""
        print("=" * 60)
        print("从Chrome浏览器提取Twitter认证信息")
        print("=" * 60)
        print()

        # 查找Chrome Cookie文件
        cookies_path = self._find_chrome_cookies()
        if not cookies_path:
            return {'success': False, 'error': '未找到Chrome Cookie文件'}

        # 复制Cookie数据库
        temp_path = self._copy_cookies_db(cookies_path)
        if not temp_path:
            return {'success': False, 'error': '无法复制Cookie数据库'}

        try:
            # 连接到Cookie数据库
            print("连接到Cookie数据库...")
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()

            # 查询Twitter相关的Cookie
            print("查询Twitter Cookie...")

            # 查询auth_token
            cursor.execute("""
                SELECT name, value, host_key
                FROM cookies
                WHERE host_key LIKE '%twitter%'
                AND name = 'auth_token'
                ORDER BY creation_utc DESC
                LIMIT 1
            """)

            auth_token_row = cursor.fetchone()

            # 查询ct0
            cursor.execute("""
                SELECT name, value, host_key
                FROM cookies
                WHERE host_key LIKE '%twitter%'
                AND name = 'ct0'
                ORDER BY creation_utc DESC
                LIMIT 1
            """)

            ct0_row = cursor.fetchone()

            # 关闭连接
            conn.close()

            # 清理临时文件
            try:
                os.remove(temp_path)
                print("临时文件已清理")
            except:
                pass

            # 检查结果
            result = {
                'success': False,
                'auth_token': None,
                'ct0': None,
                'timestamp': datetime.now().isoformat()
            }

            if auth_token_row:
                result['auth_token'] = auth_token_row[1]
                print(f"[OK] 找到 auth_token")

            if ct0_row:
                result['ct0'] = ct0_row[1]
                print(f"[OK] 找到 ct0")

            if result['auth_token'] or result['ct0']:
                result['success'] = True
                print()
                print("[OK] 成功提取Twitter认证信息")
            else:
                print()
                print("[X] 未找到Twitter认证信息")
                print("请确保：")
                print("  1. Chrome浏览器已安装")
                print("  2. 已登录Twitter账号")
                print("  3. Twitter网站已访问过")

            return result

        except Exception as e:
            print(f"提取Cookie失败: {e}")
            return {'success': False, 'error': str(e)}

    def save_to_file(self, cookies: dict, filename: str = 'twitter_auth.json'):
        """保存到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2, ensure_ascii=False)
            print(f"认证信息已保存到: {filename}")
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False

    def generate_env_commands(self, cookies: dict) -> str:
        """生成环境变量设置命令"""
        commands = []
        commands.append("# PowerShell 环境变量设置")
        commands.append("")

        if cookies.get('auth_token'):
            auth_token = cookies['auth_token']
            commands.append(f"$env:TWITTER_AUTH_TOKEN = '{auth_token}'")

        if cookies.get('ct0'):
            ct0 = cookies['ct0']
            commands.append(f"$env:TWITTER_CT0 = '{ct0}'")

        commands.append("")
        commands.append("# 测试认证")
        commands.append("twitter feed -n 1")

        return '\n'.join(commands)


def main():
    """主函数"""
    print()
    print("[Chrome] Twitter 认证信息提取器")
    print()

    # 创建提取器
    extractor = ChromeCookieExtractor()

    # 提取Cookie
    cookies = extractor.extract_twitter_cookies()

    print()
    print("=" * 60)

    if cookies['success']:
        print("提取结果:")
        print("-" * 60)

        if cookies.get('auth_token'):
            auth_token = cookies['auth_token']
            print(f"auth_token: {auth_token[:20]}...{auth_token[-10:]}")
            print(f"  (长度: {len(auth_token)} 字符)")

        if cookies.get('ct0'):
            ct0 = cookies['ct0']
            print(f"ct0: {ct0[:20]}...{ct0[-10:]}")
            print(f"  (长度: {len(ct0)} 字符)")

        print()
        print("=" * 60)

        # 保存到文件
        extractor.save_to_file(cookies)

        # 生成环境变量命令
        print()
        print("环境变量设置命令:")
        print("-" * 60)
        print(extractor.generate_env_commands(cookies))

        print()
        print("=" * 60)
        print("[OK] 完成！")
        print()
        print("下一步:")
        print("1. 复制上述环境变量命令到PowerShell中执行")
        print("2. 运行测试命令: twitter feed -n 1")
        print("3. 如果成功，就可以开始爬取Twitter内容了")

    else:
        print("[X] 提取失败")
        print("-" * 60)
        if 'error' in cookies:
            print(f"错误: {cookies['error']}")
        else:
            print("未找到Twitter认证信息")
            print()
            print("可能的原因:")
            print("1. Chrome浏览器未安装")
            print("2. 未登录Twitter账号")
            print("3. Twitter网站未访问过")
            print("4. Chrome浏览器正在运行（请关闭后重试）")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
