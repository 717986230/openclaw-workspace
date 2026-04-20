"""
期货数据可视化分析
生成图表展示期货市场数据
"""

import sys
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
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


def visualize_czce_data(data_str):
    """可视化 CZCE 数据"""
    print("生成 CZCE 数据可视化图表...")

    lines = data_str.split('\n')
    futures_data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('合约代码') or line.startswith('品种') or line.startswith('总计'):
            continue

        parsed = parse_czce_line(line)
        if parsed:
            futures_data.append(parsed)

    if not futures_data:
        print("没有找到有效的期货数据")
        return

    # 转换为 DataFrame
    df = pd.DataFrame(futures_data)

    # 清洗数据
    numeric_columns = ['open', 'high', 'low', 'close', 'settlement', 'volume', 'open_interest', 'amount']
    for col in numeric_columns:
        df[col] = df[col].astype(str).str.replace(',', '')
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 按品种分组
    df['variety'] = df['contract'].str[:2]
    variety_stats = df.groupby('variety').agg({
        'volume': 'sum',
        'open_interest': 'sum',
        'amount': 'sum'
    }).sort_values('volume', ascending=False).head(10)

    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('郑州商品交易所期货数据分析', fontsize=16, fontweight='bold')

    # 1. 成交量柱状图
    ax1 = axes[0, 0]
    variety_stats['volume'].plot(kind='bar', ax=ax1, color='steelblue')
    ax1.set_title('各品种成交量 (前10)', fontweight='bold')
    ax1.set_xlabel('品种')
    ax1.set_ylabel('成交量(手)')
    ax1.tick_params(axis='x', rotation=45)

    # 2. 持仓量柱状图
    ax2 = axes[0, 1]
    variety_stats['open_interest'].plot(kind='bar', ax=ax2, color='coral')
    ax2.set_title('各品种持仓量 (前10)', fontweight='bold')
    ax2.set_xlabel('品种')
    ax2.set_ylabel('持仓量(手)')
    ax2.tick_params(axis='x', rotation=45)

    # 3. 成交额柱状图
    ax3 = axes[1, 0]
    variety_stats['amount'].plot(kind='bar', ax=ax3, color='lightgreen')
    ax3.set_title('各品种成交额 (前10)', fontweight='bold')
    ax3.set_xlabel('品种')
    ax3.set_ylabel('成交额(万元)')
    ax3.tick_params(axis='x', rotation=45)

    # 4. 成交量前10合约
    ax4 = axes[1, 1]
    top_contracts = df.nlargest(10, 'volume')[['contract', 'volume']]
    ax4.barh(top_contracts['contract'], top_contracts['volume'], color='purple')
    ax4.set_title('成交量前10合约', fontweight='bold')
    ax4.set_xlabel('成交量(手)')
    ax4.set_ylabel('合约')

    plt.tight_layout()
    plt.savefig('czce_analysis.png', dpi=300, bbox_inches='tight')
    print("CZCE 分析图表已保存: czce_analysis.png")

    return df


def visualize_eastmoney_data(futures_list):
    """可视化东方财富数据"""
    print("生成东方财富数据可视化图表...")

    if not futures_list:
        print("没有找到期货数据")
        return None

    # 转换为 DataFrame
    df = pd.DataFrame(futures_list)

    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('东方财富市场数据分析', fontsize=16, fontweight='bold')

    # 1. 涨跌幅前10
    ax1 = axes[0, 0]
    top_gainers = df.nlargest(10, 'change_percent')[['name', 'change_percent']]
    ax1.barh(top_gainers['name'], top_gainers['change_percent'], color='green')
    ax1.set_title('涨幅前10', fontweight='bold')
    ax1.set_xlabel('涨跌幅(%)')

    # 2. 跌幅前10
    ax2 = axes[0, 1]
    top_losers = df.nsmallest(10, 'change_percent')[['name', 'change_percent']]
    ax2.barh(top_losers['name'], top_losers['change_percent'], color='red')
    ax2.set_title('跌幅前10', fontweight='bold')
    ax2.set_xlabel('涨跌幅(%)')

    # 3. 成交量前10
    ax3 = axes[1, 0]
    top_volume = df.nlargest(10, 'volume')[['name', 'volume']]
    ax3.barh(top_volume['name'], top_volume['volume'], color='blue')
    ax3.set_title('成交量前10', fontweight='bold')
    ax3.set_xlabel('成交量')

    # 4. 价格分布
    ax4 = axes[1, 1]
    ax4.hist(df['price'], bins=20, color='orange', edgecolor='black')
    ax4.set_title('价格分布', fontweight='bold')
    ax4.set_xlabel('价格')
    ax4.set_ylabel('数量')

    plt.tight_layout()
    plt.savefig('eastmoney_analysis.png', dpi=300, bbox_inches='tight')
    print("东方财富分析图表已保存: eastmoney_analysis.png")

    return df


def main():
    """主函数"""
    print("=" * 60)
    print("期货数据可视化分析")
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
            print(f"可视化 CZCE 数据...")
            data = result['extracted_data']
            if isinstance(data, str) and len(data) > 100:
                visualize_czce_data(data)

        elif 'EASTMONEY' in result['url'] and result['task_id'] == 5:
            print(f"可视化东方财富数据...")
            data = result['extracted_data']
            if isinstance(data, list):
                visualize_eastmoney_data(data)

    db.close()

    print("\n" + "=" * 60)
    print("可视化完成")
    print("=" * 60)
    print("\n生成的图表:")
    print("  - czce_analysis.png (郑州商品交易所分析)")
    print("  - eastmoney_analysis.png (东方财富分析)")


if __name__ == "__main__":
    main()
