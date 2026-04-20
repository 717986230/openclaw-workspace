"""
MT5 模拟账户测试启动脚本
"""

import sys
import os
import time
import signal
import logging
from datetime import datetime
import MetaTrader5 as mt5

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mt5_top_tier_engine import (
    MT5TopTierSystem,
    RiskMetrics,
    SignalType,
    OrderType
)
from config import (
    SYMBOLS_CONFIG,
    RISK_CONFIG,
    MONITORING_CONFIG,
    LOGGING_CONFIG,
    MT5_CONFIG
)

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['handlers']['file']['filename']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MT5DemoLauncher:
    """MT5 模拟账户启动器"""

    def __init__(self):
        """初始化启动器"""
        self.system = None
        self.running = False

    def setup(self):
        """设置系统"""
        logger.info("设置 MT5 模拟账户测试系统...")

        try:
            # 创建风险指标
            risk_metrics = RiskMetrics(
                max_position_size=RISK_CONFIG['max_position_size'],
                max_daily_loss=RISK_CONFIG['max_daily_loss'],
                max_drawdown=RISK_CONFIG['max_drawdown'],
                risk_reward_ratio=RISK_CONFIG['risk_reward_ratio']
            )

            # 创建 MT5 系统
            self.system = MT5TopTierSystem(
                symbols=SYMBOLS_CONFIG['enabled'],
                risk_metrics=risk_metrics
            )

            logger.info("系统创建成功")
            return True

        except Exception as e:
            logger.error(f"系统创建失败: {e}")
            return False

    def start(self):
        """启动系统"""
        logger.info("启动 MT5 模拟账户测试系统...")

        try:
            # 连接 MT5
            if not self.system.data_collector.connect():
                logger.error("MT5 连接失败")
                return False

            logger.info("MT5 连接成功")

            # 获取账户信息
            account_info = self.system.data_collector.get_account_info()
            logger.info(f"账户信息: {account_info}")

            # 获取余额
            if account_info:
                balance = account_info.get('balance', 0)
                logger.info(f"账户余额: {balance}")

            # 获取持仓
            positions = self.system.data_collector.get_positions()
            logger.info(f"当前持仓: {len(positions)} 个")

            # 测试获取报价
            for symbol in SYMBOLS_CONFIG['enabled'][:3]:  # 测试前 3 个品种
                try:
                    tick = self.system.data_collector.get_tick(symbol)
                    if tick:
                        logger.info(f"{symbol} 报价: Bid={tick['bid']}, Ask={tick['ask']}")
                    else:
                        logger.warning(f"{symbol} 报价获取失败")
                except Exception as e:
                    logger.error(f"获取 {symbol} 报价失败: {e}")

            # 测试获取 K 线
            for symbol in SYMBOLS_CONFIG['enabled'][:2]:  # 测试前 2 个品种
                try:
                    timeframe = SYMBOLS_CONFIG['timeframes'].get(symbol, 'H1')
                    # 转换时间框架
                    timeframe_map = {'M1': mt5.TIMEFRAME_M1, 'M5': mt5.TIMEFRAME_M5, 'M15': mt5.TIMEFRAME_M15,
                                     'M30': mt5.TIMEFRAME_M30, 'H1': mt5.TIMEFRAME_H1, 'H4': mt5.TIMEFRAME_H4,
                                     'D1': mt5.TIMEFRAME_D1, 'W1': mt5.TIMEFRAME_W1, 'MN1': mt5.TIMEFRAME_MN1}
                    tf = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
                    rates = self.system.data_collector.get_rates(symbol, tf, 10)
                    if rates is not None and len(rates) > 0:
                        logger.info(f"{symbol} ({timeframe}) K 线: {len(rates)} 条")
                    else:
                        logger.warning(f"{symbol} ({timeframe}) K 线获取失败")
                except Exception as e:
                    logger.error(f"获取 {symbol} K 线失败: {e}")

            logger.info("MT5 模拟账户测试系统启动成功")
            return True

        except Exception as e:
            logger.error(f"系统启动失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def stop(self):
        """停止系统"""
        logger.info("停止 MT5 模拟账户测试系统...")

        if self.system:
            self.system.stop()

        self.running = False
        logger.info("系统已停止")


def main():
    """主函数"""
    print("=" * 60)
    print("MT5 模拟账户测试系统启动")
    print("=" * 60)
    print()

    # 显示配置信息
    print("【配置信息】")
    print(f"  账号: {MT5_CONFIG['login']}")
    print(f"  服务器: {MT5_CONFIG['server']}")
    print(f"  路径: {MT5_CONFIG['path']}")
    print(f"  交易品种: {', '.join(SYMBOLS_CONFIG['enabled'])}")
    print()

    # 显示风险配置
    print("【风险配置】")
    print(f"  最大仓位比例: {RISK_CONFIG['max_position_size'] * 100:.1f}%")
    print(f"  最大日亏损比例: {RISK_CONFIG['max_daily_loss'] * 100:.1f}%")
    print(f"  最大回撤比例: {RISK_CONFIG['max_drawdown'] * 100:.1f}%")
    print(f"  风险收益比: {RISK_CONFIG['risk_reward_ratio']}")
    print()

    # 创建启动器
    launcher = MT5DemoLauncher()

    # 设置系统
    if not launcher.setup():
        print("系统设置失败")
        return

    # 启动系统
    if not launcher.start():
        print("系统启动失败")
        return

    print()
    print("=" * 60)
    print("MT5 模拟账户测试系统启动成功")
    print("=" * 60)
    print()
    print("测试完成！")
    print()

    # 停止系统
    launcher.stop()


if __name__ == "__main__":
    main()