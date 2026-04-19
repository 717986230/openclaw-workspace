"""
MT5 顶配盯盘系统 - 启动脚本
"""

import sys
import os
import time
import signal
import logging
from datetime import datetime

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
    LOGGING_CONFIG
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


class MT5SystemLauncher:
    """MT5 系统启动器"""

    def __init__(self):
        """初始化启动器"""
        self.system = None
        self.running = False

    def setup(self):
        """设置系统"""
        logger.info("设置 MT5 顶配盯盘系统...")

        # 配置风险指标
        risk_metrics = RiskMetrics(
            max_position_size=RISK_CONFIG['max_position_size'],
            max_daily_loss=RISK_CONFIG['max_daily_loss'],
            max_drawdown=RISK_CONFIG['max_drawdown'],
            risk_reward_ratio=RISK_CONFIG['risk_reward_ratio'],
            max_positions=RISK_CONFIG['max_positions']
        )

        # 创建系统
        self.system = MT5TopTierSystem(
            symbols=SYMBOLS_CONFIG['enabled'],
            risk_metrics=risk_metrics
        )

        logger.info("系统设置完成")

    def start(self):
        """启动系统"""
        logger.info("=" * 60)
        logger.info("MT5 顶配盯盘系统启动")
        logger.info("=" * 60)
        logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"交易品种: {', '.join(SYMBOLS_CONFIG['enabled'])}")
        logger.info(f"最大持仓数: {RISK_CONFIG['max_positions']}")
        logger.info(f"最大仓位比例: {RISK_CONFIG['max_position_size'] * 100}%")
        logger.info(f"最大日亏损: {RISK_CONFIG['max_daily_loss'] * 100}%")
        logger.info(f"最大回撤: {RISK_CONFIG['max_drawdown'] * 100}%")
        logger.info(f"风险收益比: {RISK_CONFIG['risk_reward_ratio']}")
        logger.info("=" * 60)

        # 设置系统
        self.setup()

        # 启动系统
        if self.system.start():
            self.running = True
            logger.info("系统启动成功")
            return True
        else:
            logger.error("系统启动失败")
            return False

    def stop(self):
        """停止系统"""
        logger.info("停止系统...")
        self.running = False
        if self.system:
            self.system.stop()
        logger.info("系统已停止")

    def run(self):
        """运行系统"""
        if not self.start():
            return

        # 设置信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # 运行主循环
        try:
            self.system.run()
        except Exception as e:
            logger.error(f"系统运行出错: {e}")
        finally:
            self.stop()

    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，准备停止系统...")
        self.running = False
        if self.system:
            self.system.running = False


def main():
    """主函数"""
    launcher = MT5SystemLauncher()

    try:
        launcher.run()
    except KeyboardInterrupt:
        logger.info("收到键盘中断信号")
        launcher.stop()
    except Exception as e:
        logger.error(f"系统异常: {e}")
        launcher.stop()


if __name__ == '__main__':
    main()