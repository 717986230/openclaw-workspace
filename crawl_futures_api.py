"""
国内期货市场数据爬虫 - API 版本
使用东方财富 API 等可靠数据源
"""

import sys
import os
import json
import requests
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage


def crawl_eastmoney_futures_api():
    """使用东方财富 API 爬取期货数据"""
    print("=" * 60)
    print("爬取东方财富期货数据 (API)")
    print("=" * 60)

    try:
        # 东方财富期货数据 API
        url = "http://push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': 1,
            'pz': 50,
            'po': 1,
            'np': 1,
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }

        print(f"正在请求: {url}")
        response = requests.get(url, params=params, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"获取到数据")

            # 解析期货数据
            futures_list = data.get('data', {}).get('diff', [])
            print(f"期货合约数量: {len(futures_list)}")

            futures_data = []
            for item in futures_list:
                futures_data.append({
                    'code': item.get('f12', ''),
                    'name': item.get('f14', ''),
                    'price': item.get('f2', 0),
                    'change': item.get('f4', 0),
                    'change_percent': item.get('f3', 0),
                    'open': item.get('f17', 0),
                    'high': item.get('f15', 0),
                    'low': item.get('f16', 0),
                    'volume': item.get('f5', 0),
                    'amount': item.get('f6', 0)
                })

            print(f"解析出 {len(futures_data)} 条期货数据")
            return futures_data

        else:
            print(f"请求失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_sina_futures_api():
    """使用新浪 API 爬取期货数据"""
    print("\n" + "=" * 60)
    print("爬取新浪期货数据 (API)")
    print("=" * 60)

    try:
        # 新浪期货数据 API
        # 主要期货合约代码
        contracts = [
            'CL0',  # 原油
            'GC0',  # 黄金
            'SI0',  # 白银
            'CU0',  # 铜
            'AL0',  # 铝
            'ZN0',  # 锌
            'NI0',  # 镍
            'RB0',  # 螺纹钢
            'HC0',  # 热卷
            'AG0',  # 白银
            'AU0',  # 黄金
            'BU0',  # 沥青
            'RU0',  # 橡胶
            'FU0',  # 燃料油
            'SC0'   # 原油
        ]

        futures_data = []

        for contract in contracts:
            try:
                url = f"http://hq.sinajs.cn/list=hf_{contract}"
                print(f"正在请求: {url}")

                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    # 解析数据
                    data_str = response.text
                    if f'hq_str_hf_{contract}="' in data_str:
                        start = data_str.find(f'hq_str_hf_{contract}="') + len(f'hq_str_hf_{contract}="')
                        end = data_str.find('";', start)
                        data = data_str[start:end]

                        parts = data.split(',')
                        if len(parts) >= 6:
                            futures_data.append({
                                'code': contract,
                                'name': parts[1] if len(parts) > 1 else '',
                                'open': parts[2] if len(parts) > 2 else '',
                                'high': parts[3] if len(parts) > 3 else '',
                                'low': parts[4] if len(parts) > 4 else '',
                                'close': parts[5] if len(parts) > 5 else ''
                            })

            except Exception as e:
                print(f"  {contract} 爬取失败: {e}")
                continue

        print(f"解析出 {len(futures_data)} 条期货数据")
        return futures_data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_10jqka_futures():
    """爬取同花顺期货数据"""
    print("\n" + "=" * 60)
    print("爬取同花顺期货数据")
    print("=" * 60)

    try:
        # 同花顺期货数据接口
        url = "http://d.10jqka.com.cn/v2/realhead/hs_futures/real.js"

        print(f"正在请求: {url}")
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print(f"获取到数据")
            # 同花顺返回的是 JavaScript 格式，需要解析
            return response.text

        else:
            print(f"请求失败: {response.status_code}")
            return None

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def save_futures_data_to_mysql(futures_data, exchange_name):
    """保存期货数据到 MySQL"""
    print(f"\n保存 {exchange_name} 数据到 MySQL...")

    try:
        db = DatabaseStorage(
            db_type="mysql",
            host="localhost",
            port=3306,
            user="root",
            password="root123",
            database="crawler_db"
        )

        # 创建任务
        task_id = db.create_task(
            f"期货数据爬取 - {exchange_name}",
            f"{exchange_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # 保存结果
        result_id = db.save_result(
            task_id=task_id,
            url=f"{exchange_name} - {datetime.now().strftime('%Y-%m-%d')}",
            title=f"{exchange_name} 期货数据",
            extracted_data=futures_data
        )

        print(f"保存成功！任务 ID: {task_id}, 结果 ID: {result_id}")

        db.close()

        return task_id, result_id

    except Exception as e:
        print(f"保存失败: {e}")
        return None, None


def display_futures_data(futures_data):
    """显示期货数据"""
    print("\n" + "=" * 60)
    print("期货数据预览")
    print("=" * 60)

    if isinstance(futures_data, list):
        print(f"共 {len(futures_data)} 条记录\n")

        # 显示前 10 条
        for i, item in enumerate(futures_data[:10], 1):
            print(f"{i}. {item.get('code', '')} - {item.get('name', '')}")
            print(f"   价格: {item.get('price', item.get('close', ''))}")
            print(f"   涨跌: {item.get('change', '')} ({item.get('change_percent', '')}%)")
            print(f"   开盘: {item.get('open', '')} 最高: {item.get('high', '')} 最低: {item.get('low', '')}")
            print(f"   成交量: {item.get('volume', '')}")
            print()

        if len(futures_data) > 10:
            print(f"... 还有 {len(futures_data) - 10} 条记录")


def main():
    """主函数"""
    print("=" * 60)
    print("国内期货市场数据爬虫 - API 版本")
    print("=" * 60)
    print(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}

    # 1. 爬取东方财富期货数据
    eastmoney_data = crawl_eastmoney_futures_api()
    if eastmoney_data:
        results['EASTMONEY'] = eastmoney_data
        save_futures_data_to_mysql(eastmoney_data, 'EASTMONEY')
        display_futures_data(eastmoney_data)

    # 2. 爬取新浪期货数据
    sina_data = crawl_sina_futures_api()
    if sina_data:
        results['SINA'] = sina_data
        save_futures_data_to_mysql(sina_data, 'SINA')
        display_futures_data(sina_data)

    # 3. 爬取同花顺期货数据
    jqka_data = crawl_10jqka_futures()
    if jqka_data:
        results['10JQKA'] = jqka_data
        save_futures_data_to_mysql(jqka_data, '10JQKA')

    # 总结
    print("\n" + "=" * 60)
    print("爬取完成总结")
    print("=" * 60)
    print(f"成功爬取 {len(results)} 个数据源")

    for exchange, data in results.items():
        if isinstance(data, list):
            print(f"  - {exchange}: {len(data)} 条期货合约")
        else:
            print(f"  - {exchange}: {len(str(data))} 字符")

    print("\n数据已保存到 MySQL 数据库")

    return results


if __name__ == "__main__":
    main()
