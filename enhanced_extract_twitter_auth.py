"""
增强版Chrome Twitter认证信息提取器
支持多种Chrome安装路径和配置文件
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime
import glob


class EnhancedChromeCookieExtractor:
    """增强版Chrome Cookie 提取器"""

    def __init__(self):
        """初始化提取器"""
        self.chrome_paths = self._find_all_chrome_paths()

    def _find_all_chrome_paths(self) -> list:
        """查找所有Chrome Cookie文件路径"""
        paths = []

        # Windows 路径
        if os.name == 'nt':
            local_app_data = os.environ.get('LOCALAPPDATA', '')
            app_data = os.environ.get('APPDATA', '')

            if local_app_data:
                # 标准路径
                standard_path = os.path.join(
                    local_app_data,
                    'Google',
                    'Chrome',
                    'User Data',
                    'Default',
                    'Cookies'
                )
                if os.path.exists(standard_path):
                    paths.append(('Windows Standard', standard_path))

                # 查找所有Profile
                user_data_dir = os.path.join(local_app_data, 'Google', 'Chrome', 'User Data')
                if os.path.exists(user_data_dir):
                    for profile_dir in os.listdir(user_data_dir):
                        if profile_dir.startswith('Profile ') or profile_dir == 'Default':
                            profile_cookies = os.path.join(user_data_dir, profile_dir, 'Cookies')
                            if os.path.exists(profile_cookies):
                                paths.append((f'Windows Profile: {profile_dir}', profile_cookies))

        # macOS 路径
        elif os.name == 'posix' and os.path.exists('/Applications'):
            macos_path = os.path.expanduser(
                '~/Library/Application Support/Google/Chrome/Default/Cookies'
            )
            if os.path.exists(macos_path):
                paths.append(('macOS Standard', macos_path))

        # Linux 路径
        elif os.name == 'posix':
            linux_path = os.path.expanduser(
                '~/.config/google-chrome/Default/Cookies'
            )
            if os.path.exists(linux_path):
                paths.append(('Linux Standard', linux_path))

        return paths

    def list_chrome_paths(self):
        """列出所有找到的Chrome路径"""
        print("找到的Chrome Cookie文件路径:")
        print("-" * 60)

        if not self.chrome_paths:
            print("未找到Chrome Cookie文件")
            print()
            print("可能的原因:")
            print("1. Chrome浏览器未安装")
            print("2. Chrome数据目录被移动")
            print("3. 权限不足")
            return False

        for i, (description, path) in enumerate(self.chrome_paths, 1):
            size = os.path.getsize(path) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i}. {description}")
            print(f"   路径: {path}")
            print(f"   大小: {size:.2f} KB")
            print(f"   修改时间: {mtime}")
            print()

        return True

    def extract_from_path(self, cookies_path: str) -> dict:
        """从指定路径提取Cookie"""
        print(f"从路径提取Cookie: {cookies_path}")

        # 复制Cookie数据库
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_path = f"/tmp/cookies_copy_{timestamp}.db"

        try:
            shutil.copy2(cookies_path, temp_path)
            print(f"Cookie数据库已复制到: {temp_path}")
        except Exception as e:
            print(f"复制Cookie数据库失败: {e}")
            return {'success': False, 'error': f'无法复制Cookie数据库: {e}'}

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
                'source_path': cookies_path,
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

            return result

        except Exception as e:
            print(f"提取Cookie失败: {e}")
            return {'success': False, 'error': str(e)}

    def extract_twitter_cookies(self) -> dict:
        """提取Twitter Cookie（尝试所有路径）"""
        print("=" * 60)
        print("从Chrome浏览器提取Twitter认证信息")
        print("=" * 60)
        print()

        # 列出所有路径
        if not self.list_chrome_paths():
            return {'success': False, 'error': '未找到Chrome Cookie文件'}

        # 尝试从每个路径提取
        for description, path in self.chrome_paths:
            print()
            print(f"尝试从 {description} 提取...")
            print("-" * 60)

            result = self.extract_from_path(path)

            if result['success']:
                return result

        # 所有路径都失败
        return {
            'success': False,
            'error': '所有Chrome路径都未找到Twitter认证信息'
        }

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
    print("[Chrome] Twitter 认证信息提取器 (增强版)")
    print()

    # 创建提取器
    extractor = EnhancedChromeCookieExtractor()

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
