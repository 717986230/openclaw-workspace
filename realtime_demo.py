"""
实时数据获取演示
获取一次实时数据然后退出
"""

import sys
import os
import json
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage


def get_mock_realtime_data() -> List[Dict]:
    """生成模拟实时数据"""
    print("生成模拟实时数据...")

    # 基于之前爬取的真实数据生成模拟数据
    mock_data = [
        {
            'code': 'TA409',
            'name': 'PTA 409',
            'price': 6000.0 + random.uniform(-50, 50),
            'change': random.uniform(-100, 100),
            'change_percent': random.uniform(-2, 2),
            'open': 6000.0 + random.uniform(-30, 30),
            'high': 6000.0 + random.uniform(0, 50),
            'low': 6000.0 + random.uniform(-50, 0),
            'volume': 1040247 + random.randint(-10000, 10000),
            'amount': 6241482000 + random.randint(-100000000, 100000000),
            'timestamp': datetime.now().isoformat()
        },
        {
            'code': 'FG409',
            'name': '玻璃 409',
            'price': 1450.0 + random.uniform(-20, 20),
            'change': random.uniform(-30, 30),
            'change_percent': random.uniform(-2, 2),
            'open': 1450.0 + random.uniform(-10, 10),
            'high': 1450.0 + random.uniform(0, 20),
            'low': 1450.0 + random.uniform(-20, 0),
            'volume': 989950 + random.randint(-5000, 5000),
            'amount': 1435427500 + random.randint(-50000000, 50000000),
            'timestamp': datetime.now().isoformat()
        },
        {
            'code': 'MA409',
            'name': '甲醇 409',
            'price': 2500.0 + random.uniform(-30, 30),
            'change': random.uniform(-40, 40),
            'change_percent': random.uniform(-2, 2),
            'open': 2500.0 + random.uniform(-15, 15),
            'high': 2500.0 + random.uniform(0, 30),
            'low': 2500.0 + random.uniform(-30, 0),
            'volume': 749894 + random.randint(-5000, 5000),
            'amount': 1874735000 + random.randint(-50000000, 50000000),
            'timestamp': datetime.now().isoformat()
        },
        {
            'code': 'RM409',
            'name': '菜粕 409',
            'price': 2800.0 + random.uniform(-40, 40),
            'change': random.uniform(-50, 50),
            'change_percent': random.uniform(-2, 2),
            'open': 2800.0 + random.uniform(-20, 20),
            'high': 2800.0 + random.uniform(0, 40),
            'low': 2800.0 + random.uniform(-40, 0),
            'volume': 1201173 + random.randint(-10000, 10000),
            'amount': 3363284400 + random.randint(-100000000, 100000000),
            'timestamp': datetime.now().isoformat()
        },
        {
            'code': 'SA409',
            'name': '白糖 409',
            'price': 1900.0 + random.uniform(-25, 25),
            'change': random.uniform(-35, 35),
            'change_percent': random.uniform(-2, 2),
            'open': 1900.0 + random.uniform(-12, 12),
            'high': 1900.0 + random.uniform(0, 25),
            'low': 1900.0 + random.uniform(-25, 0),
            'volume': 729307 + random.randint(-5000, 5000),
            'amount': 1385683300 + random.randint(-50000000, 50000000),
            'timestamp': datetime.now().isoformat()
        }
    ]

    return mock_data


def save_to_database(data: List[Dict], source: str):
    """保存数据到数据库"""
    try:
        db = DatabaseStorage(
            db_type='mysql',
            host='localhost',
            port=3306,
            user='root',
            password='root123',
            database='crawler_db'
        )

        task_id = db.create_task(
            title=f"{source} 实时数据",
            url=f"realtime_{source.lower()}",
            description=f"实时获取 {source} 期货数据"
        )

        for item in data:
            db.create_result(
                task_id=task_id,
                url=f"realtime_{source.lower()}",
                title=f"{source} 实时数据",
                extracted_data=item,
                media_files=None
            )

        print(f"成功保存 {len(data)} 条 {source} 实时数据到数据库")
        db.close()

    except Exception as e:
        print(f"保存数据失败: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("实时数据获取演示")
    print("=" * 60)
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 获取模拟实时数据
    mock_data = get_mock_realtime_data()

    print(f"获取到 {len(mock_data)} 条实时数据")
    print()

    # 显示数据
    print("实时数据预览:")
    print("-" * 60)
    for i, item in enumerate(mock_data):
        print(f"{i+1}. {item['name']} ({item['code']})")
        print(f"   价格: {item['price']:.2f}")
        print(f"   涨跌: {item['change']:.2f} ({item['change_percent']:.2f}%)")
        print(f"   开盘: {item['open']:.2f}")
        print(f"   最高: {item['high']:.2f}")
        print(f"   最低: {item['low']:.2f}")
        print(f"   成交量: {item['volume']:,}")
        print(f"   成交额: {item['amount']:,.0f}")
        print(f"   时间: {item['timestamp']}")
        print()

    # 保存到数据库
    save_to_database(mock_data, 'MOCK')

    # 保存到文件
    results = {
        'timestamp': datetime.now().isoformat(),
        'data': mock_data,
        'source': 'mock_realtime_data'
    }

    with open('realtime_futures_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("数据已保存到:")
    print("  - MySQL 数据库: crawler_db")
    print("  - JSON 文件: realtime_futures_data.json")

    print("\n" + "=" * 60)
    print("实时数据获取完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
