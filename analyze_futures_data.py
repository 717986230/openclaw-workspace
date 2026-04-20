"""
期货数据分析
分析郑州商品交易所和东方财富的期货数据
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage


def analyze_czce_data(data_str):
    """分析郑州商品交易所数据"""
    print("=" * 60)
    print("郑州商品交易所 (CZCE) 数据分析")
    print("=" * 60)

    lines = data_str.split('\n')
    futures_data = []

    for line in lines:
        if line.strip() and not line.startswith('合约代码') and not line.startswith('品种') and not line.startswith('总计'):
            parts = line.split('|')
            if len(parts) >= 12:
                try:
                    futures_data.append({
                        'contract': parts[0].strip(),
                        'open': parts[1].strip(),
                        'high': parts[2].strip(),
                        'low': parts[3].strip(),
                        'close': parts[4].strip(),
                        'settlement': parts[5].strip(),
                        'change1': parts[6].strip(),
                        'change2': parts[7].strip(),
                        'volume': parts[10].strip(),
                        'open_interest': parts[11].strip(),
                        'change': parts[12].strip(),
                        'amount': parts[13].strip(),
                        'oi_change': parts[14].strip()
                    })
                except:
                    continue

    if not futures_data:
        print("没有找到有效的期货数据")
        return None

    # 转换为 DataFrame
    df = pd.DataFrame(futures_data)

    # 清洗数据
    numeric_columns = ['open', 'high', 'low', 'close', 'settlement', 'volume', 'open_interest', 'amount']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')

    print(f"\n总合约数: {len(df)}")
    print(f"总成交量: {df['volume'].sum():,.0f} 手")
    print(f"总持仓量: {df['open_interest'].sum():,.0f} 手")
    print(f"总成交额: {df['amount'].sum():,.2f} 万元")

    # 按品种分组
    df['variety'] = df['contract'].str[:2]
    variety_stats = df.groupby('variety').agg({
        'volume': 'sum',
        'open_interest': 'sum',
        'amount': 'sum'
    }).sort_values('volume', ascending=False)

    print("\n按品种统计 (按成交量排序):")
    print(varity_stats.head(10))

    # 成交量前10的合约
    top_volume = df.nlargest(10, 'volume')[['contract', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    print("\n成交量前10的合约:")
    print(top_volume.to_string(index=False))

    # 涨跌分析
    df['change_numeric'] = pd.to_numeric(df['change'].str.replace(',', ''), errors='coerce')
    top_gainers = df.nlargest(5, 'change_numeric')[['contract', 'close', 'change']]
    top_losers = df.nsmallest(5, 'change_numeric')[['contract', 'close', 'change']]

    print("\n涨幅前5:")
    print(top_gainers.to_string(index=False))

    print("\n跌幅前5:")
    print(top_losers.to_string(index=False))

    return df


def analyze_eastmoney_data(futures_list):
    """分析东方财富期货数据"""
    print("\n" + "=" * 60)
    print("东方财富期货数据分析")
    print("=" * 60)

    if not futures_list:
        print("没有找到期货数据")
        return None

    # 转换为 DataFrame
    df = pd.DataFrame(futures_list)

    print(f"\n总合约数: {len(df)}")
    print(f"总成交量: {df['volume'].sum():,.0f}")
    print(f"总成交额: {df['amount'].sum():,.2f} 元")

    # 涨跌分析
    top_gainers = df.nlargest(5, 'change_percent')[['code', 'name', 'price', 'change', 'change_percent']]
    top_losers = df.nsmallest(5, 'change_percent')[['code', 'name', 'price', 'change', 'change_percent']]

    print("\n涨幅前5:")
    print(top_gainers.to_string(index=False))

    print("\n跌幅前5:")
    print(top_losers.to_string(index=False))

    # 成交量前10
    top_volume = df.nlargest(10, 'volume')[['code', 'name', 'price', 'volume', 'amount']]
    print("\n成交量前10:")
    print(top_volume.to_string(index=False))

    return df


def main():
    """主函数"""
    print("=" * 60)
    print("期货数据分析")
    print("=" * 60)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 连接 MySQL
    db = DatabaseStorage(
        db_type="mysql",
        host="localhost",
        port=3306,
        user="root",
        password="root123",
        database="crawler_db"
    )

    # 查询所有期货数据
    results = db.get_results(limit=20)

    print(f"找到 {len(results)} 条记录\n")

    # 分析每个数据源
    for result in results:
        if 'CZCE' in result['url']:
            print(f"\n分析 CZCE 数据...")
            data = result['extracted_data']
            if isinstance(data, str):
                analyze_czce_data(data)

        elif 'EASTMONEY' in result['url'] and result['task_id'] == 5:
            print(f"\n分析东方财富数据...")
            data = result['extracted_data']
            if isinstance(data, list):
                analyze_eastmoney_data(data)

    db.close()

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
