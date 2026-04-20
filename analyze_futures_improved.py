"""
期货数据分析 - 改进版
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage


def parse_czce_line(line):
    """解析 CZCE 单行数据"""
    parts = line.split('|')
    if len(parts) >= 14:
        try:
            return {
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
                'oi_change': parts[14].strip() if len(parts) > 14 else ''
            }
        except:
            return None
    return None


def analyze_czce_data(data_str):
    """分析郑州商品交易所数据"""
    print("=" * 60)
    print("郑州商品交易所 (CZCE) 数据分析")
    print("=" * 60)

    lines = data_str.split('\n')
    futures_data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过标题行
        if line.startswith('合约代码') or line.startswith('品种') or line.startswith('总计'):
            continue

        # 解析数据行
        parsed = parse_czce_line(line)
        if parsed:
            futures_data.append(parsed)

    if not futures_data:
        print("没有找到有效的期货数据")
        print(f"原始数据前500字符: {data_str[:500]}")
        return None

    # 转换为 DataFrame
    df = pd.DataFrame(futures_data)

    # 清洗数据 - 移除逗号并转换为数值
    numeric_columns = ['open', 'high', 'low', 'close', 'settlement', 'volume', 'open_interest', 'amount']
    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 处理涨跌数据
    df['change_numeric'] = df['change'].astype(str).str.replace(',', '')
    df['change_numeric'] = pd.to_numeric(df['change_numeric'], errors='coerce')

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
    print(variety_stats.head(10))

    # 成交量前10的合约
    top_volume = df.nlargest(10, 'volume')[['contract', 'open', 'high', 'low', 'close', 'volume', 'amount']]
    print("\n成交量前10的合约:")
    print(top_volume.to_string(index=False))

    # 涨跌分析
    valid_change = df[df['change_numeric'].notna()]
    if len(valid_change) > 0:
        top_gainers = valid_change.nlargest(5, 'change_numeric')[['contract', 'close', 'change']]
        top_losers = valid_change.nsmallest(5, 'change_numeric')[['contract', 'close', 'change']]

        print("\n涨幅前5:")
        print(top_gainers.to_string(index=False))

        print("\n跌幅前5:")
        print(top_losers.to_string(index=False))

    # 价格区间分析
    print(f"\n价格区间分析:")
    print(f"最高价: {df['high'].max():,.2f}")
    print(f"最低价: {df['low'].min():,.2f}")
    print(f"平均价: {df['close'].mean():,.2f}")

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

    # 检查数据类型
    print(f"数据列: {df.columns.tolist()}")
    print(f"前3条数据:")
    print(df.head(3))

    # 统计分析
    if 'volume' in df.columns:
        print(f"\n总成交量: {df['volume'].sum():,.0f}")
    if 'amount' in df.columns:
        print(f"总成交额: {df['amount'].sum():,.2f} 元")

    # 涨跌分析
    if 'change_percent' in df.columns:
        top_gainers = df.nlargest(5, 'change_percent')[['code', 'name', 'price', 'change', 'change_percent']]
        top_losers = df.nsmallest(5, 'change_percent')[['code', 'name', 'price', 'change', 'change_percent']]

        print("\n涨幅前5:")
        print(top_gainers.to_string(index=False))

        print("\n跌幅前5:")
        print(top_losers.to_string(index=False))

    # 成交量前10
    if 'volume' in df.columns:
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
        print(f"\n处理记录: {result['title']}")

        if 'CZCE' in result['url']:
            print(f"分析 CZCE 数据...")
            data = result['extracted_data']
            if isinstance(data, str) and len(data) > 100:
                analyze_czce_data(data)

        elif 'EASTMONEY' in result['url'] and result['task_id'] == 5:
            print(f"分析东方财富数据...")
            data = result['extracted_data']
            if isinstance(data, list):
                analyze_eastmoney_data(data)

    db.close()

    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
