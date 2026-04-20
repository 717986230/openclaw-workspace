"""
使用智能反爬虫策略的期货数据爬虫
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage
from smart_anti_detection import SmartCrawler


class SmartFuturesCrawler:
    """智能期货数据爬虫"""

    def __init__(self, db_config: Dict):
        """初始化爬虫"""
        self.db = DatabaseStorage(**db_config)
        self.crawler = SmartCrawler()

        # 添加Cookie管理
        self.crawler.add_cookie_manager()

        # 可选：添加代理（需要代理列表）
        # proxy_list = [
        #     'http://proxy1.example.com:8080',
        #     'http://proxy2.example.com:8080',
        # ]
        # self.crawler.add_proxy_rotator(proxy_list)

    def get_eastmoney_futures(self) -> List[Dict]:
        """获取东方财富期货数据"""
        try:
            print("获取东方财富期货数据...")

            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 50,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:90',  # 期货板块
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152'
            }

            response = self.crawler.get_request(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get('rc') == 0 and 'data' in data:
                diff = data['data'].get('diff', [])

                futures_data = []
                for item in diff:
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
                        'amount': item.get('f6', 0),
                        'timestamp': datetime.now().isoformat()
                    })

                print(f"成功获取 {len(futures_data)} 条东方财富数据")
                return futures_data

        except Exception as e:
            print(f"获取东方财富数据失败: {e}")

        return []

    def get_sina_futures(self) -> List[Dict]:
        """获取新浪期货数据"""
        try:
            print("获取新浪期货数据...")

            contracts = ['CL0', 'GC0', 'SI0', 'CU0', 'AL0', 'IF0', 'IC0', 'IH0']
            futures_data = []

            for contract in contracts:
                try:
                    url = f"http://hq.sinajs.cn/list=hf_{contract}"

                    response = self.crawler.get_request(url)
                    response.raise_for_status()

                    data = response.text

                    if 'var hq_str_' in data:
                        parts = data.split('"')
                        if len(parts) >= 2:
                            values = parts[1].split(',')
                            if len(values) >= 10 and values[0]:
                                futures_data.append({
                                    'code': contract,
                                    'name': values[0],
                                    'price': float(values[1]) if values[1] else 0,
                                    'open': float(values[2]) if values[2] else 0,
                                    'high': float(values[3]) if values[3] else 0,
                                    'low': float(values[4]) if values[4] else 0,
                                    'volume': float(values[5]) if values[5] else 0,
                                    'timestamp': datetime.now().isoformat()
                                })

                except Exception as e:
                    print(f"获取 {contract} 数据失败: {e}")
                    continue

            print(f"成功获取 {len(futures_data)} 条新浪数据")
            return futures_data

        except Exception as e:
            print(f"获取新浪数据失败: {e}")

        return []

    def get_10jqka_futures(self) -> List[Dict]:
        """获取同花顺期货数据"""
        try:
            print("获取同花顺期货数据...")

            url = "http://d.10jqka.com.cn/v2/realhead/hs_futures/real.js"

            response = self.crawler.get_request(url)
            response.raise_for_status()

            data = response.text

            # 解析JSONP数据
            if 'data=' in data:
                json_str = data.split('data=')[1].rstrip(';')
                json_data = json.loads(json_str)

                if 'data' in json_data:
                    futures_data = []
                    for item in json_data['data']:
                        futures_data.append({
                            'code': item.get('code', ''),
                            'name': item.get('name', ''),
                            'price': item.get('price', 0),
                            'change': item.get('change', 0),
                            'change_percent': item.get('change_percent', 0),
                            'volume': item.get('volume', 0),
                            'timestamp': datetime.now().isoformat()
                        })

                    print(f"成功获取 {len(futures_data)} 条同花顺数据")
                    return futures_data

        except Exception as e:
            print(f"获取同花顺数据失败: {e}")

        return []

    def save_to_database(self, data: List[Dict], source: str):
        """保存数据到数据库"""
        try:
            task_id = self.db.create_task(
                title=f"{source} 智能爬取数据",
                url=f"smart_{source.lower()}",
                description=f"使用智能反爬虫策略获取 {source} 期货数据"
            )

            for item in data:
                self.db.create_result(
                    task_id=task_id,
                    url=f"smart_{source.lower()}",
                    title=f"{source} 智能爬取数据",
                    extracted_data=item,
                    media_files=None
                )

            print(f"成功保存 {len(data)} 条 {source} 数据到数据库")

        except Exception as e:
            print(f"保存数据失败: {e}")

    def crawl_all(self) -> Dict[str, any]:
        """爬取所有数据源"""
        print("=" * 60)
        print("智能期货数据爬取")
        print("=" * 60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        results = {
            'timestamp': datetime.now().isoformat(),
            'eastmoney': [],
            'sina': [],
            '10jqka': []
        }

        # 爬取东方财富
        eastmoney_data = self.get_eastmoney_futures()
        if eastmoney_data:
            results['eastmoney'] = eastmoney_data
            self.save_to_database(eastmoney_data, 'EASTMONEY')

        # 爬取新浪
        sina_data = self.get_sina_futures()
        if sina_data:
            results['sina'] = sina_data
            self.save_to_database(sina_data, 'SINA')

        # 爬取同花顺
        jqka_data = self.get_10jqka_futures()
        if jqka_data:
            results['10jqka'] = jqka_data
            self.save_to_database(jqka_data, '10JQKA')

        print()
        print("=" * 60)
        print("爬取完成")
        print("=" * 60)
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"东方财富: {len(results['eastmoney'])} 条")
        print(f"新浪: {len(results['sina'])} 条")
        print(f"同花顺: {len(results['10jqka'])} 条")

        # 显示爬虫统计
        stats = self.crawler.get_stats()
        print()
        print("爬虫统计:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功: {stats['total_success']}")
        print(f"  失败: {stats['total_failure']}")
        print(f"  成功率: {stats['total_success']/stats['total_requests']*100:.1f}%")

        return results

    def close(self):
        """关闭数据库连接"""
        self.db.close()


def main():
    """主函数"""
    # 数据库配置
    db_config = {
        'db_type': 'mysql',
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root123',
        'database': 'crawler_db'
    }

    # 创建智能爬虫
    crawler = SmartFuturesCrawler(db_config)

    try:
        # 爬取所有数据
        results = crawler.crawl_all()

        # 保存到文件
        with open('smart_futures_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print()
        print("数据已保存到:")
        print("  - MySQL 数据库: crawler_db")
        print("  - JSON 文件: smart_futures_data.json")

    finally:
        crawler.close()


if __name__ == "__main__":
    main()
