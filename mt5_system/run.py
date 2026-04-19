"""
MT5 顶配盯盘系统 v2 - 启动脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging

from mt5_system.mt5_engine_v2 import EnhancedStrategyEngine, RiskMetrics
from mt5_system.symbol_filter import SymbolFilter
from mt5_system.time_filter import TimeFilter, VolatilityFilter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_system/trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MT5TradingSystem:
    """MT5 交易系统"""

    def __init__(self, config: dict = None):
        """初始化"""
        self.config = config or self._default_config()
        self.connected = False
        self.engine = None
        self.symbol_filter = None
        self.time_filter = None
        self.volatility_filter = None

    def _default_config(self):
        """默认配置"""
        return {
            'symbols': ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'USOIL'],
            'risk_metrics': {
                'max_position_size': 0.02,
                'max_positions': 5,
                'max_daily_loss': 0.05,
                'max_drawdown': 0.15,
                'risk_reward_ratio': 2.0,
            },
            'check_time': True,
            'check_volatility': True,
            'use_ml': True,
            'use_factor_analysis': True,
            'use_multi_tf': True,
        }

    def initialize(self):
        """初始化系统"""
        logger.info("=" * 60)
        logger.info("MT5 顶配盯盘系统 v2 - 启动")
        logger.info("=" * 60)

        # 1. 连接 MT5
        if not self._connect_mt5():
            return False

        # 2. 初始化引擎
        self._initialize_engine()

        # 3. 初始化过滤器
        self._initialize_filters()

        logger.info("✅ 系统初始化完成")
        return True

    def _connect_mt5(self):
        """连接 MT5"""
        logger.info("正在连接 MT5...")

        if not mt5.initialize():
            logger.error(f"MT5 初始化失败: {mt5.last_error()}")
            return False

        # 获取账户信息
        account_info = mt5.account_info()
        if account_info:
            logger.info(f"✅ 账户: {account_info.login}")
            logger.info(f"✅ 余额: {account_info.balance:.2f}")
            logger.info(f"✅ 权益: {account_info.equity:.2f}")
            logger.info(f"✅ 服务器: {account_info.server}")
        else:
            logger.warning("⚠️ 未登录账户")
            return False

        self.connected = True
        return True

    def _initialize_engine(self):
        """初始化引擎"""
        risk_metrics = RiskMetrics(**self.config['risk_metrics'])
        self.engine = EnhancedStrategyEngine(
            risk_metrics=risk_metrics,
            use_ml=self.config['use_ml'],
            use_factor_analysis=self.config['use_factor_analysis'],
            use_multi_tf=self.config['use_multi_tf'],
        )
        logger.info("✅ 策略引擎初始化完成")

    def _initialize_filters(self):
        """初始化过滤器"""
        self.symbol_filter = SymbolFilter()
        self.time_filter = TimeFilter()
        self.volatility_filter = VolatilityFilter()
        logger.info("✅ 过滤器初始化完成")

    def get_symbol_data(self, symbol: str, timeframe: str = 'H1', bars: int = 200) -> pd.DataFrame:
        """获取品种数据"""
        # 时间框架映射
        tf_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1,
        }

        if timeframe not in tf_map:
            logger.error(f"不支持的时间框架: {timeframe}")
            return None

        # 获取数据
        rates = mt5.copy_rates_from_pos(symbol, tf_map[timeframe], 0, bars)

        if rates is None or len(rates) == 0:
            logger.error(f"获取 {symbol} 数据失败: {mt5.last_error()}")
            return None

        # 转换为 DataFrame
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        return df

    def analyze_symbol(self, symbol: str) -> dict:
        """分析单个品种"""
        logger.info(f"正在分析 {symbol}...")

        # 1. 时间检查
        if self.config['check_time']:
            allowed, reason = self.time_filter.is_trade_allowed(symbol)
            if not allowed:
                logger.info(f"  ⏸️ {symbol}: {reason}")
                return {'symbol': symbol, 'signal': 'skip', 'reason': reason}

        # 2. 获取数据
        df = self.get_symbol_data(symbol, 'H1', 200)
        if df is None:
            logger.warning(f"  ⚠️ {symbol}: 无法获取数据")
            return {'symbol': symbol, 'signal': 'error', 'reason': '无法获取数据'}

        # 3. 波动率检查
        if self.config['check_volatility']:
            vol_analysis = self.volatility_filter.analyze_volatility(df)
            if vol_analysis['state'] == 'extreme':
                logger.info(f"  ⚠️ {symbol}: 波动率极端 - {vol_analysis['recommendation']}")

        # 4. 生成信号
        signal = self.engine.analyze_and_generate_signal(
            df, symbol,
            check_time=False,
            check_volatility=False,
        )

        if signal is None:
            logger.info(f"  ⏸️ {symbol}: 无信号")
            return {'symbol': symbol, 'signal': 'none', 'reason': '无信号'}

        # 5. 输出结果
        logger.info(f"  📊 {symbol}: {signal.signal_type}")
        logger.info(f"     置信度: {signal.confidence:.3f}, 强度: {signal.strength:.3f}")
        logger.info(f"     入场: {signal.entry_price:.5f}")
        logger.info(f"     止损: {signal.stop_loss:.5f}, 止盈: {signal.take_profit:.5f}")
        logger.info(f"     仓位: {signal.position_size:.4f}")
        logger.info(f"     原因: {signal.reason}")

        return {
            'symbol': symbol,
            'signal': signal.signal_type,
            'confidence': signal.confidence,
            'strength': signal.strength,
            'entry': signal.entry_price,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit,
            'position_size': signal.position_size,
            'reason': signal.reason,
        }

    def run_analysis(self):
        """运行分析"""
        logger.info()
        logger.info("=" * 60)
        logger.info("开始分析")
        logger.info("=" * 60)

        results = []

        for symbol in self.config['symbols']:
            result = self.analyze_symbol(symbol)
            results.append(result)
            time.sleep(0.5)  # 避免请求过快

        # 汇总结果
        logger.info()
        logger.info("=" * 60)
        logger.info("分析结果汇总")
        logger.info("=" * 60)

        buy_signals = [r for r in results if r['signal'] == 'BUY']
        sell_signals = [r for r in results if r['signal'] == 'SELL']

        if buy_signals:
            logger.info(f"📈 买入信号 ({len(buy_signals)}):")
            for r in buy_signals:
                logger.info(f"  - {r['symbol']}: {r['confidence']:.3f}")

        if sell_signals:
            logger.info(f"📉 卖出信号 ({len(sell_signals)}):")
            for r in sell_signals:
                logger.info(f"  - {r['symbol']}: {r['confidence']:.3f}")

        if not buy_signals and not sell_signals:
            logger.info("⏸️ 无交易信号")

        return results

    def shutdown(self):
        """关闭系统"""
        logger.info()
        logger.info("正在关闭系统...")

        if self.connected:
            mt5.shutdown()
            logger.info("✅ MT5 连接已关闭")

        logger.info("✅ 系统已关闭")


def main():
    """主函数"""
    # 创建系统
    system = MT5TradingSystem()

    try:
        # 初始化
        if not system.initialize():
            logger.error("系统初始化失败")
            return

        # 运行分析
        results = system.run_analysis()

        # 输出结果
        logger.info()
        logger.info("分析完成！")

    except KeyboardInterrupt:
        logger.info("用户中断")
    except Exception as e:
        logger.error(f"错误: {e}", exc_info=True)
    finally:
        # 关闭系统
        system.shutdown()


if __name__ == "__main__":
    main()