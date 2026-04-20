"""
国内期货市场数据爬虫
爬取上海期货交易所、大连商品交易所、郑州商品交易所的实时数据
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.crawler import Crawler
from scripts.database_storage import DatabaseStorage


def crawl_shfe_data():
    """爬取上海期货交易所数据"""
    print("=" * 60)
    print("爬取上海期货交易所 (SHFE) 数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # SHFE 官方数据接口
    url = "https://www.shfe.com.cn/data/dailydata/kx/kx{}.dat".format(
        datetime.now().strftime("%Y%m%d")
    )

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 解析数据（SHFE 返回的是 JSON 格式）
        import json
        data = json.loads(html)

        print(f"获取到 {len(data.get('cursor', []))} 条记录")

        return data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_dce_data():
    """爬取大连商品交易所数据"""
    print("\n" + "=" * 60)
    print("爬取大连商品交易所 (DCE) 数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # DCE 官方数据接口
    url = "https://www.dce.com.cn/publicweb/quotesdata/dayquotesch.html"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 提取表格数据
        data = crawler.extract(html, {
            'tables': 'table::text'
        })

        print(f"提取到数据: {data}")

        return data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_czce_data():
    """爬取郑州商品交易所数据"""
    print("\n" + "=" * 60)
    print("爬取郑州商品交易所 (CZCE) 数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # CZCE 官方数据接口
    url = "https://www.czce.com.cn/cn/DFSStaticFiles/Future/2024/20240416/FutureDataDaily.txt"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # CZCE 返回的是文本格式，需要解析
        lines = html.split('\n')
        print(f"获取到 {len(lines)} 行数据")

        return html

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def crawl_sina_futures():
    """爬取新浪期货数据（备用方案）"""
    print("\n" + "=" * 60)
    print("爬取新浪期货数据")
    print("=" * 60)

    crawler = Crawler(delay_range=(0.5, 1.0))

    # 新浪期货数据接口
    url = "http://finance.sina.com.cn/futuremarket/futuresqh.shtml"

    try:
        print(f"正在爬取: {url}")
        html = crawler.fetch(url)
        print(f"数据长度: {len(html)} 字符")

        # 提取期货数据
        data = crawler.extract(html, {
            'futures': 'table.futures-table::text'
        })

        print(f"提取到数据: {data}")

        return data

    except Exception as e:
        print(f"爬取失败: {e}")
        return None


def save_to_mysql(data, exchange_name):
    """保存数据到 MySQL"""
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
            f"{exchange_name} - {datetime.now().strftime('%Y-%m-%d')}"
        )

        # 保存结果
        result_id = db.save_result(
            task_id=task_id,
            url=f"{exchange_name} - {datetime.now().strftime('%Y-%m-%d')}",
            title=f"{exchange_name} 期货数据",
            extracted_data=data
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
    print("国内期货市场数据爬虫")
    print("=" * 60)
    print(f"爬取日期: {datetime.now().strftime('%Y-%m-%d')}")
    print()

    # 爬取各交易所数据
    results = {}

    # 1. 上海期货交易所
    shfe_data = crawl_shfe_data()
    if shfe_data:
        results['SHFE'] = shfe_data
        save_to_mysql(shfe_data, 'SHFE')

    # 2. 大连商品交易所
    dce_data = crawl_dce_data()
    if dce_data:
        results['DCE'] = dce_data
        save_to_mysql(dce_data, 'DCE')

    # 3. 郑州商品交易所
    czce_data = crawl_czce_data()
    if czce_data:
        results['CZCE'] = czce_data
        save_to_mysql(czce_data, 'CZCE')

    # 4. 新浪期货（备用）
    sina_data = crawl_sina_futures()
    if sina_data:
        results['SINA'] = sina_data
        save_to_mysql(sina_data, 'SINA')

    # 总结
    print("\n" + "=" * 60)
    print("爬取完成总结")
    print("=" * 60)
    print(f"成功爬取 {len(results)} 个交易所的数据")
    for exchange, data in results.items():
        print(f"  - {exchange}: {len(str(data))} 字符")

    print("\n数据已保存到 MySQL 数据库")

    return results


if __name__ == "__main__":
    main()
