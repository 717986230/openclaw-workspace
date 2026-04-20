"""
实时期货数据获取器
支持定时获取和实时更新
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skills', 'smart-crawler'))

from scripts.database_storage import DatabaseStorage


class RealTimeFuturesCrawler:
    """实时期货数据爬虫"""

    def __init__(self, db_config: Dict):
        """初始化爬虫"""
        self.db = DatabaseStorage(**db_config)
        self.last_update = None

    def get_eastmoney_realtime(self) -> List[Dict]:
        """获取东方财富实时数据"""
        try:
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': 1,
                'pz': 100,
                'po': 1,
                'np': 1,
                'fltt': 2,
                'invt': 2,
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152'
            }

            response = requests.get(url, params=params, timeout=10)
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
            print(f"获取东方财富实时数据失败: {e}")

        return []

    def get_sina_realtime(self) -> List[Dict]:
        """获取新浪实时数据"""
        try:
            url = "http://hq.sinajs.cn/list=hf_CL,hf_GC,hf_SI,hf_CU,hf_AL"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.text

            futures_data = []
            lines = data.split('\n')

            for line in lines:
                if 'var hq_str_' in line:
                    parts = line.split('"')
                    if len(parts) >= 2:
                        values = parts[1].split(',')
                        if len(values) >= 10:
                            futures_data.append({
                                'name': values[0],
                                'price': float(values[1]) if values[1] else 0,
                                'open': float(values[2]) if values[2] else 0,
                                'high': float(values[3]) if values[3] else 0,
                                'low': float(values[4]) if values[4] else 0,
                                'volume': float(values[5]) if values[5] else 0,
                                'timestamp': datetime.now().isoformat()
                            })

            return futures_data

        except Exception as e:
            print(f"获取新浪实时数据失败: {e}")

        return []

    def get_czce_realtime(self) -> str:
        """获取郑州商品交易所实时数据"""
        try:
            url = "http://www.czce.com.cn/portal/enstaticsdata/datashow.html"

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            return response.text

        except Exception as e:
            print(f"获取CZCE实时数据失败: {e}")

        return ""

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
            'czce': ''
        }

        # 获取东方财富数据
        eastmoney_data = self.get_eastmoney_realtime()
        if eastmoney_data:
            results['eastmoney'] = eastmoney_data
            self.save_to_database(eastmoney_data, 'EASTMONEY')
            print(f"东方财富: 获取 {len(eastmoney_data)} 条数据")

        # 获取新浪数据
        sina_data = self.get_sina_realtime()
        if sina_data:
            results['sina'] = sina_data
            self.save_to_database(sina_data, 'SINA')
            print(f"新浪: 获取 {len(sina_data)} 条数据")

        # 获取CZCE数据
        czce_data = self.get_czce_realtime()
        if czce_data:
            results['czce'] = czce_data
            self.save_to_database([czce_data], 'CZCE')
            print(f"CZCE: 获取 {len(czce_data)} 字符数据")

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
    crawler = RealTimeFuturesCrawler(db_config)

    try:
        # 获取一次实时数据
        results = crawler.get_all_realtime()

        print("\n" + "=" * 60)
        print("实时数据汇总")
        print("=" * 60)
        print(f"东方财富: {len(results['eastmoney'])} 条")
        print(f"新浪: {len(results['sina'])} 条")
        print(f"CZCE: {len(results['czce'])} 字符")
        print(f"更新时间: {results['timestamp']}")

        # 保存到文件
        with open('realtime_futures_data.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n数据已保存到: realtime_futures_data.json")

        # 询问是否启动实时监控
        print("\n是否启动实时监控？")
        print("1. 启动监控 (每60秒更新一次)")
        print("2. 退出")

        choice = input("请选择 (1/2): ")

        if choice == '1':
            crawler.start_realtime_monitor(interval=60)

    finally:
        crawler.close()


if __name__ == "__main__":
    main()
