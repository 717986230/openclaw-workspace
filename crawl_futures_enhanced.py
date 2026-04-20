"""
国内期货市场数据爬虫 - 增强版
使用东方财富等可靠数据源
"""

import sys
import os
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.crawler import Crawler
from scripts.database_storage import DatabaseStorage


def parse_czce_data(data_str):
    """解析郑州商品交易所数据"""
    print("解析 CZCE 数据...")

    lines = data_str.split('\n')
    futures_data = []

    for line in lines:
        if line.strip() and not line.startswith('合约代码'):
            # 解析每行数据
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
                        'volume': parts[10].strip(),
                        'amount': parts[11].strip()
                    })
                except:
                    continue

    print(f"解析出 {len(futures_data)} 条期货合约数据")
    return futures_data


def crawl_eastmoney_futures():
    """爬取东方财富期货数据"""
    print("=" * 60)
    print("爬取东方财富期货数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # 东方财富期货数据接口
    url = "http://quote.eastmoney.com/center/gridlist.html#hs_a_board"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 提取期货数据
        data = crawler.extract(html, {
            'title': 'title::text',
            'content': 'body::text'
        })

        print(f"提取到数据: {data}")

        return data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_sina_futures_detailed():
    """爬取新浪期货详细数据"""
    print("\n" + "=" * 60)
    print("爬取新浪期货详细数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # 新浪期货数据接口
    url = "http://hq.sinajs.cn/list=hf_CL0,hf_GC0,hf_SI0"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 解析新浪数据格式
        # 格式: var hq_str_hf_CL0="CL0,原油连续,67.23,67.50,66.80,67.23,...";
        pattern = r'var hq_str_(\w+)="([^"]+)"'
        matches = re.findall(pattern, html)

        futures_data = []
        for contract, data in matches:
            parts = data.split(',')
            if len(parts) >= 6:
                futures_data.append({
                    'code': contract,
                    'name': parts[1],
                    'open': parts[2],
                    'high': parts[3],
                    'low': parts[4],
                    'close': parts[5]
                })

        print(f"解析出 {len(futures_data)} 条期货数据")

        return futures_data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_jqka_futures():
    """爬取集思录期货数据"""
    print("\n" + "=" * 60)
    print("爬取集思录期货数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # 集思录期货数据接口
    url = "https://www.jisilu.cn/data/futures/"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 提取数据
        data = crawler.extract(html, {
            'futures': 'table::text'
        })

        print(f"提取到数据")

        return data

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


def main():
    """主函数"""
    print("=" * 60)
    print("国内期货市场数据爬虫 - 增强版")
    print("=" * 60)
    print(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = {}

    # 1. 爬取新浪期货详细数据
    sina_data = crawl_sina_futures_detailed()
    if sina_data:
        results['SINA'] = sina_data
        save_futures_data_to_mysql(sina_data, 'SINA')

    # 2. 爬取东方财富期货数据
    eastmoney_data = crawl_eastmoney_futures()
    if eastmoney_data:
        results['EASTMONEY'] = eastmoney_data
        save_futures_data_to_mysql(eastmoney_data, 'EASTMONEY')

    # 3. 爬取集思录期货数据
    jqka_data = crawl_jqka_futures()
    if jqka_data:
        results['JISILU'] = jqka_data
        save_futures_data_to_mysql(jqka_data, 'JISILU')

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
