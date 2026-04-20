"""
从Chrome Network目录提取Twitter认证信息
支持现代Chrome的Cookie存储机制
"""

import os
import sqlite3
import json
import shutil
from datetime import datetime


class ChromeNetworkCookieExtractor:
    """Chrome Network Cookie 提取器"""

    def __init__(self):
        """初始化提取器"""
        self.chrome_user_data = os.path.join(
            os.environ.get('LOCALAPPDATA', ''),
            'Google',
            'Chrome',
            'User Data'
        )

    def find_network_cookies(self) -> list:
        """查找Network Cookies文件"""
        cookies_files = []

        if not os.path.exists(self.chrome_user_data):
            print(f"Chrome用户数据目录不存在: {self.chrome_user_data}")
            return cookies_files

        # 搜索所有Profile目录
        for root, dirs, files in os.walk(self.chrome_user_data):
            for file in files:
                if file == 'Cookies' or file.startswith('Cookies'):
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        profile_name = os.path.basename(os.path.dirname(root))
                        cookies_files.append((profile_name, file_path))

        return cookies_files

    def extract_from_file(self, cookies_path: str) -> dict:
        """从指定文件提取Cookie"""
        print(f"从文件提取Cookie: {cookies_path}")

        # 复制Cookie数据库
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_dir = os.environ.get('TEMP', '/tmp')
        temp_path = os.path.join(temp_dir, f'cookies_copy_{timestamp}.db')

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

            # 先查看表结构
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"数据库中的表: {[t[0] for t in tables]}")

            # 查询Twitter相关的Cookie
            print("查询Twitter Cookie...")

            # 尝试不同的表名和查询方式
            auth_token = None
            ct0 = None

            # 尝试cookies表
            try:
                cursor.execute("""
                    SELECT name, value, host_key
                    FROM cookies
                    WHERE host_key LIKE '%twitter%'
                    AND name = 'auth_token'
                    ORDER BY creation_utc DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    auth_token = row[1]
                    print(f"[OK] 从cookies表找到 auth_token")
            except Exception as e:
                print(f"查询cookies表失败: {e}")

            # 尝试network_cookies表
            if not auth_token:
                try:
                    cursor.execute("""
                        SELECT name, value, host_key
                        FROM network_cookies
                        WHERE host_key LIKE '%twitter%'
                        AND name = 'auth_token'
                        ORDER BY creation_utc DESC
                        LIMIT 1
                    """)
                    row = cursor.fetchone()
                    if row:
                        auth_token = row[1]
                        print(f"[OK] 从network_cookies表找到 auth_token")
                except Exception as e:
                    print(f"查询network_cookies表失败: {e}")

            # 查询ct0
            try:
                cursor.execute("""
                    SELECT name, value, host_key
                    FROM cookies
                    WHERE host_key LIKE '%twitter%'
                    AND name = 'ct0'
                    ORDER BY creation_utc DESC
                    LIMIT 1
                """)
                row = cursor.fetchone()
                if row:
                    ct0 = row[1]
                    print(f"[OK] 从cookies表找到 ct0")
            except Exception as e:
                print(f"查询ct0失败: {e}")

            # 如果没找到，尝试network_cookies表
            if not ct0:
                try:
                    cursor.execute("""
                        SELECT name, value, host_key
                        FROM network_cookies
                        WHERE host_key LIKE '%twitter%'
                        AND name = 'ct0'
                        ORDER BY creation_utc DESC
                        LIMIT 1
                    """)
                    row = cursor.fetchone()
                    if row:
                        ct0 = row[1]
                        print(f"[OK] 从network_cookies表找到 ct0")
                except Exception as e:
                    print(f"查询network_cookies表ct0失败: {e}")

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

            if auth_token:
                result['auth_token'] = auth_token

            if ct0:
                result['ct0'] = ct0

            if auth_token or ct0:
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
        """提取Twitter Cookie"""
        print("=" * 60)
        print("从Chrome Network目录提取Twitter认证信息")
        print("=" * 60)
        print()

        # 查找Network Cookies文件
        cookies_files = self.find_network_cookies()

        if not cookies_files:
            print("未找到Cookies文件")
            return {'success': False, 'error': '未找到Cookies文件'}

        print(f"找到 {len(cookies_files)} 个Cookies文件:")
        for i, (profile, path) in enumerate(cookies_files, 1):
            size = os.path.getsize(path) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{i}. Profile: {profile}")
            print(f"   路径: {path}")
            print(f"   大小: {size:.2f} KB")
            print(f"   修改时间: {mtime}")
            print()

        # 尝试从每个文件提取
        for profile, path in cookies_files:
            print(f"尝试从 {profile} 提取...")
            print("-" * 60)

            result = self.extract_from_file(path)

            if result['success']:
                return result

        # 所有文件都失败
        return {
            'success': False,
            'error': '所有Cookies文件都未找到Twitter认证信息'
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
    print("[Chrome Network] Twitter 认证信息提取器")
    print()

    # 创建提取器
    extractor = ChromeNetworkCookieExtractor()

    # 提取Cookie
    cookies = extractor.extract_twitter_cookies()

    print()
    print("=" * 60)

    if cookies['success']:
        print("提取结果:")
        print("-" * 60)

        print(f"来源路径: {cookies.get('source_path', 'Unknown')}")

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
            print("1. 未登录Twitter账号")
            print("2. Twitter网站未访问过")
            print("3. Chrome浏览器正在运行（请关闭后重试）")
            print("4. Cookie已过期或被清除")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
