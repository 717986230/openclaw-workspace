"""
查看Chrome Cookie数据库内容
"""

import os
import sqlite3
import shutil
from datetime import datetime


def view_cookie_database():
    """查看Cookie数据库内容"""
    cookies_path = r"C:\Users\Administrator\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies"

    print(f"Cookie文件路径: {cookies_path}")
    print(f"文件大小: {os.path.getsize(cookies_path) / 1024:.2f} KB")
    print()

    # 复制Cookie数据库
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_dir = os.environ.get('TEMP', '/tmp')
    temp_path = os.path.join(temp_dir, f'cookies_copy_{timestamp}.db')

    try:
        shutil.copy2(cookies_path, temp_path)
        print(f"Cookie数据库已复制到: {temp_path}")
    except Exception as e:
        print(f"复制Cookie数据库失败: {e}")
        return

    try:
        # 连接到Cookie数据库
        print("连接到Cookie数据库...")
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[t[0] for t in tables]}")
        print()

        # 查看cookies表结构
        if any('cookies' in t[0] for t in tables):
            print("查看cookies表结构:")
            cursor.execute("PRAGMA table_info(cookies)")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
            print()

            # 查看cookies表中的所有域名
            print("查看cookies表中的所有域名:")
            cursor.execute("SELECT DISTINCT host_key FROM cookies ORDER BY host_key")
            host_keys = cursor.fetchall()
            print(f"总共 {len(host_keys)} 个域名")
            print()

            # 查找Twitter相关的域名
            print("查找Twitter相关的域名:")
            twitter_hosts = []
            for host in host_keys:
                if 'twitter' in host[0].lower() or 'x.com' in host[0].lower():
                    twitter_hosts.append(host[0])

            if twitter_hosts:
                print(f"找到 {len(twitter_hosts)} 个Twitter相关域名:")
                for host in twitter_hosts:
                    print(f"  - {host}")
                print()

                # 查看这些域名的所有Cookie
                print("Twitter域名的所有Cookie:")
                for host in twitter_hosts:
                    cursor.execute("""
                        SELECT name, value, host_key
                        FROM cookies
                        WHERE host_key = ?
                        ORDER BY creation_utc DESC
                    """, (host,))
                    cookies = cursor.fetchall()
                    print(f"\n域名: {host}")
                    print(f"Cookie数量: {len(cookies)}")
                    for name, value, host_key in cookies:
                        value_preview = value[:30] + "..." if len(value) > 30 else value
                        print(f"  {name}: {value_preview}")
            else:
                print("未找到Twitter相关的域名")
                print()
                print("前20个域名:")
                for host in host_keys[:20]:
                    print(f"  - {host[0]}")

        # 关闭连接
        conn.close()

        # 清理临时文件
        try:
            os.remove(temp_path)
            print("\n临时文件已清理")
        except:
            pass

    except Exception as e:
        print(f"查看Cookie数据库失败: {e}")


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("Chrome Cookie 数据库查看器")
    print("=" * 60)
    print()

    view_cookie_database()

    print()
    print("=" * 60)
