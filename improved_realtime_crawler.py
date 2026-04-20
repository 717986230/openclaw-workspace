"""
改进的实时期货数据获取器
使用多种数据源和反爬虫策略
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


class ImprovedRealTimeFuturesCrawler:
    """改进的实时期货数据爬虫"""

    def __init__(self, db_config: Dict):
        """初始化爬虫"""
        self.db = DatabaseStorage(**db_config)
        self.last_update = None

        # 请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'http://www.eastmoney.com/'
        }

    def get_eastmoney_futures(self) -> List[Dict]:
        """获取东方财富期货数据（备用方法）"""
        try:
            # 使用不同的API端点
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

            # 添加随机延迟
            time.sleep(random.uniform(0.5, 1.5))

            response = requests.get(url, params=params, headers=self.headers, timeout=15)
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

                return futures_data

        except Exception as e:
            print(f"获取东方财富期货数据失败: {e}")

        return []

    def get_sina_futures(self) -> List[Dict]:
        """获取新浪期货数据（备用方法）"""
        try:
            # 使用不同的合约代码
            contracts = [
                'CL0', 'GC0', 'SI0', 'CU0', 'AL0',  # 国际期货
                'IF0', 'IC0', 'IH0', 'IM0',  # 股指期货
                'RB0', 'HC0', 'CU0', 'AL0', 'ZN0',  # 商品期货
            ]

            futures_data = []

            for contract in contracts:
                try:
                    url = f"http://hq.sinajs.cn/list=hf_{contract}"

                    time.sleep(random.uniform(0.3, 0.8))

                    response = requests.get(url, headers=self.headers, timeout=10)
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

            return futures_data

        except Exception as e:
            print(f"获取新浪期货数据失败: {e}")

        return []

    def get_10jqka_futures(self) -> List[Dict]:
        """获取同花顺期货数据"""
        try:
            url = "http://d.10jqka.com.cn/v2/realhead/hs_futures/real.js"

            time.sleep(random.uniform(0.5, 1.0))

            response = requests.get(url, headers=self.headers, timeout=15)
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

                    return futures_data

        except Exception as e:
            print(f"获取同花顺期货数据失败: {e}")

        return []

    def get_mock_realtime_data(self) -> List[Dict]:
        """生成模拟实时数据（用于演示）"""
        print("使用模拟实时数据...")

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

    def save_to_database(self, data: List[Dict], source: str):
        """保存数据到数据库"""
        try:
            task_id = self.db.create_task(
                title=f"{source} 实时数据",
                url=f"realtime_{source.lower()}",
                description=f"实时获取 {source} 期货数据"
            )

            for item in data:
                self.db.create_result(
                    task_id=task_id,
                    url=f"realtime_{source.lower()}",
                    title=f"{source} 实时数据",
                    extracted_data=item,
                    media_files=None
                )

            print(f"成功保存 {len(data)} 条 {source} 实时数据到数据库")

        except Exception as e:
            print(f"保存数据失败: {e}")

    def get_all_realtime(self) -> Dict[str, any]:
        """获取所有实时数据"""
        print(f"开始获取实时数据... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        results = {
            'timestamp': datetime.now().isoformat(),
            'eastmoney': [],
            'sina': [],
            '10jqka': [],
            'mock': []
        }

        # 尝试获取东方财富数据
        eastmoney_data = self.get_eastmoney_futures()
        if eastmoney_data:
            results['eastmoney'] = eastmoney_data
            self.save_to_database(eastmoney_data, 'EASTMONEY')
            print(f"东方财富: 获取 {len(eastmoney_data)} 条数据")
        else:
            print("东方财富: 获取失败")

        # 尝试获取新浪数据
        sina_data = self.get_sina_futures()
        if sina_data:
            results['sina'] = sina_data
            self.save_to_database(sina_data, 'SINA')
            print(f"新浪: 获取 {len(sina_data)} 条数据")
        else:
            print("新浪: 获取失败")

        # 尝试获取同花顺数据
        jqka_data = self.get_10jqka_futures()
        if jqka_data:
            results['10jqka'] = jqka_data
            self.save_to_database(jqka_data, '10JQKA')
            print(f"同花顺: 获取 {len(jqka_data)} 条数据")
        else:
            print("同花顺: 获取失败")

        # 如果所有真实数据源都失败，使用模拟数据
        if not results['eastmoney'] and not results['sina'] and not results['10jqka']:
            print("所有真实数据源都失败，使用模拟数据")
            mock_data = self.get_mock_realtime_data()
            results['mock'] = mock_data
            self.save_to_database(mock_data, 'MOCK')
            print(f"模拟数据: 生成 {len(mock_data)} 条数据")

        self.last_update = datetime.now()
        print(f"实时数据获取完成: {self.last_update.strftime('%Y-%m-%d %H:%M:%S')}")

        return results

    def start_realtime_monitor(self, interval: int = 60):
        """启动实时监控"""
        print(f"启动实时监控，间隔: {interval} 秒")
        print("按 Ctrl+C 停止监控")

        try:
            while True:
                self.get_all_realtime()
                print(f"下次更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n监控已停止")

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

    # 创建爬虫
    crawler = ImprovedRealTimeFuturesCrawler(db_config)

    try:
        # 获取一次实时数据
        results = crawler.get_all_realtime()

        print("\n" + "=" * 60)
        print("实时数据汇总")
        print("=" * 60)
        print(f"东方财富: {len(results['eastmoney'])} 条")
        print(f"新浪: {len(results['sina'])} 条")
        print(f"同花顺: {len(results['10jqka'])} 条")
        print(f"模拟数据: {len(results['mock'])} 条")
        print(f"更新时间: {results['timestamp']}")

        # 显示数据预览
        all_data = results['eastmoney'] + results['sina'] + results['10jqka'] + results['mock']
        if all_data:
            print("\n数据预览:")
            for i, item in enumerate(all_data[:5]):
                print(f"{i+1}. {item.get('name', 'N/A')} ({item.get('code', 'N/A')}): "
                      f"价格={item.get('price', 0):.2f}, "
                      f"涨跌={item.get('change_percent', 0):.2f}%")

        # 保存到文件
        with open('realtime_futures_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n数据已保存到: realtime_futures_data.json")

        # 自动启动监控
        print("\n启动实时监控 (每60秒更新一次)...")
        print("按 Ctrl+C 停止监控\n")

        crawler.start_realtime_monitor(interval=60)

    finally:
        crawler.close()


if __name__ == "__main__":
    main()
