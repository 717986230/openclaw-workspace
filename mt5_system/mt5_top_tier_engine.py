"""
MT5 顶配盯盘系统 - 核心引擎
集成数据采集、技术分析、信号生成、风险管理、执行引擎
"""

import sys
import os
import time
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mt5_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SignalType(Enum):
    """信号类型"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"


class OrderType(Enum):
    """订单类型"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


@dataclass
class TradingSignal:
    """交易信号"""
    symbol: str
    signal_type: SignalType
    confidence: float  # 0-1
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    timestamp: datetime = field(default_factory=datetime.now)
    reason: str = ""
    indicators: Dict = field(default_factory=dict)


@dataclass
class Position:
    """持仓信息"""
    symbol: str
    position_type: SignalType
    entry_price: float
    current_price: float
    size: float
    stop_loss: float
    take_profit: float
    pnl: float
    open_time: datetime
    ticket: int = 0


@dataclass
class RiskMetrics:
    """风险指标"""
    max_position_size: float = 0.02  # 最大仓位比例
    max_daily_loss: float = 0.05  # 最大日亏损比例
    max_drawdown: float = 0.15  # 最大回撤比例
    risk_reward_ratio: float = 2.0  # 风险收益比
    max_positions: int = 5  # 最大持仓数


class MT5DataCollector:
    """MT5 数据采集器"""

    def __init__(self):
        """初始化数据采集器"""
        self.connected = False
        self.symbols = []
        self.executor = ThreadPoolExecutor(max_workers=10)

    def connect(self) -> bool:
        """连接到 MT5"""
        try:
            if not mt5.initialize():
                logger.error(f"MT5 初始化失败: {mt5.last_error()}")
                return False

            account_info = mt5.account_info()
            if account_info is None:
                logger.error("无法获取账户信息")
                return False

            logger.info(f"成功连接到 MT5 - 账户: {account_info.login}")
            self.connected = True
            return True

        except Exception as e:
            logger.error(f"连接 MT5 失败: {e}")
            return False

    def disconnect(self):
        """断开 MT5 连接"""
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("已断开 MT5 连接")

    def get_symbols(self) -> List[str]:
        """获取所有交易品种"""
        if not self.connected:
            return []

        try:
            symbols = mt5.symbols_get()
            self.symbols = [s.name for s in symbols if s.visible]
            logger.info(f"获取到 {len(self.symbols)} 个交易品种")
            return self.symbols

        except Exception as e:
            logger.error(f"获取交易品种失败: {e}")
            return []

    def get_rates(self, symbol: str, timeframe: int, count: int = 100) -> pd.DataFrame:
        """获取历史价格数据"""
        if not self.connected:
            return pd.DataFrame()

        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None or len(rates) == 0:
                logger.warning(f"无法获取 {symbol} 的价格数据")
                return pd.DataFrame()

            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)

            return df

        except Exception as e:
            logger.error(f"获取 {symbol} 价格数据失败: {e}")
            return pd.DataFrame()

    def get_tick(self, symbol: str) -> Optional[Dict]:
        """获取实时报价"""
        if not self.connected:
            return None

        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                return None

            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': tick.ask - tick.bid,
                'time': datetime.now()
            }

        except Exception as e:
            logger.error(f"获取 {symbol} 实时报价失败: {e}")
            return None

    def get_account_info(self) -> Optional[Dict]:
        """获取账户信息"""
        if not self.connected:
            return None

        try:
            account = mt5.account_info()
            if account is None:
                return None

            return {
                'login': account.login,
                'balance': account.balance,
                'equity': account.equity,
                'margin': account.margin,
                'free_margin': account.margin_free,
                'margin_level': account.margin_level,
                'profit': account.profit
            }

        except Exception as e:
            logger.error(f"获取账户信息失败: {e}")
            return None

    def get_positions(self) -> List[Dict]:
        """获取当前持仓"""
        if not self.connected:
            return []

        try:
            positions = mt5.positions_get()
            if positions is None:
                return []

            result = []
            for pos in positions:
                result.append({
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': pos.type,
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'sl': pos.sl,
                    'tp': pos.tp,
                    'price_current': pos.price_current,
                    'profit': pos.profit,
                    'time': datetime.fromtimestamp(pos.time)
                })

            return result

        except Exception as e:
            logger.error(f"获取持仓失败: {e}")
            return []


class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """简单移动平均"""
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """指数移动平均"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """相对强弱指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD 指标"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """布林带"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """平均真实波幅"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                    k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """随机指标"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        return k_percent, d_percent


class SignalGenerator:
    """信号生成器"""

    def __init__(self, risk_metrics: RiskMetrics):
        """初始化信号生成器"""
        self.risk_metrics = risk_metrics
        self.indicators = TechnicalIndicators()

    def generate_signals(self, df: pd.DataFrame, symbol: str) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []

        if len(df) < 50:
            return signals

        # 计算技术指标
        close = df['close']
        high = df['high']
        low = df['low']

        sma_20 = self.indicators.sma(close, 20)
        sma_50 = self.indicators.sma(close, 50)
        ema_12 = self.indicators.ema(close, 12)
        ema_26 = self.indicators.ema(close, 26)
        rsi = self.indicators.rsi(close, 14)
        macd, signal, histogram = self.indicators.macd(close)
        upper_bb, middle_bb, lower_bb = self.indicators.bollinger_bands(close)
        atr = self.indicators.atr(high, low, close)

        latest = df.iloc[-1]
        current_price = latest['close']

        # 买入信号条件
        buy_conditions = [
            sma_20.iloc[-1] > sma_50.iloc[-1],  # 短期均线上穿长期均线
            ema_12.iloc[-1] > ema_26.iloc[-1],  # EMA 金叉
            rsi.iloc[-1] < 70 and rsi.iloc[-1] > 30,  # RSI 在合理区间
            macd.iloc[-1] > signal.iloc[-1],  # MACD 金叉
            current_price < upper_bb.iloc[-1],  # 价格低于布林带上轨
            histogram.iloc[-1] > histogram.iloc[-2],  # MACD 柱状图上升
        ]

        # 卖出信号条件
        sell_conditions = [
            sma_20.iloc[-1] < sma_50.iloc[-1],  # 短期均线下穿长期均线
            ema_12.iloc[-1] < ema_26.iloc[-1],  # EMA 死叉
            rsi.iloc[-1] > 70,  # RSI 超买
            macd.iloc[-1] < signal.iloc[-1],  # MACD 死叉
            current_price > lower_bb.iloc[-1],  # 价格高于布林带下轨
            histogram.iloc[-1] < histogram.iloc[-2],  # MACD 柱状图下降
        ]

        # 计算信号强度
        buy_strength = sum(buy_conditions) / len(buy_conditions)
        sell_strength = sum(sell_conditions) / len(sell_conditions)

        # 生成买入信号
        if buy_strength >= 0.6:
            stop_loss = current_price - (atr.iloc[-1] * 2)
            take_profit = current_price + (atr.iloc[-1] * 3)
            position_size = self._calculate_position_size(current_price, stop_loss)

            signal = TradingSignal(
                symbol=symbol,
                signal_type=SignalType.BUY,
                confidence=buy_strength,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=position_size,
                reason=f"买入信号强度: {buy_strength:.2f}",
                indicators={
                    'sma_20': sma_20.iloc[-1],
                    'sma_50': sma_50.iloc[-1],
                    'rsi': rsi.iloc[-1],
                    'macd': macd.iloc[-1],
                    'signal': signal.iloc[-1]
                }
            )
            signals.append(signal)

        # 生成卖出信号
        elif sell_strength >= 0.6:
            stop_loss = current_price + (atr.iloc[-1] * 2)
            take_profit = current_price - (atr.iloc[-1] * 3)
            position_size = self._calculate_position_size(current_price, stop_loss)

            signal = TradingSignal(
                symbol=symbol,
                signal_type=SignalType.SELL,
                confidence=sell_strength,
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                position_size=position_size,
                reason=f"卖出信号强度: {sell_strength:.2f}",
                indicators={
                    'sma_20': sma_20.iloc[-1],
                    'sma_50': sma_50.iloc[-1],
                    'rsi': rsi.iloc[-1],
                    'macd': macd.iloc[-1],
                    'signal': signal.iloc[-1]
                }
            )
            signals.append(signal)

        return signals

    def _calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """计算仓位大小"""
        risk_per_trade = self.risk_metrics.max_position_size
        risk_amount = abs(entry_price - stop_loss)

        if risk_amount == 0:
            return 0.01

        position_size = risk_per_trade / risk_amount

        # 限制最大仓位
        max_size = self.risk_metrics.max_position_size
        position_size = min(position_size, max_size)

        return round(position_size, 2)


class RiskManager:
    """风险管理器"""

    def __init__(self, risk_metrics: RiskMetrics):
        """初始化风险管理器"""
        self.risk_metrics = risk_metrics
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = 0.0

    def check_risk(self, signal: TradingSignal, account_info: Dict,
                   current_positions: List[Dict]) -> Tuple[bool, str]:
        """检查风险"""
        # 检查最大持仓数
        if len(current_positions) >= self.risk_metrics.max_positions:
            return False, f"已达到最大持仓数 {self.risk_metrics.max_positions}"

        # 检查日亏损限制
        if self.daily_pnl < -self.risk_metrics.max_daily_loss * account_info['balance']:
            return False, f"已达到日亏损限制 {self.risk_metrics.max_daily_loss * 100}%"

        # 检查回撤限制
        if self.peak_equity > 0:
            current_drawdown = (self.peak_equity - account_info['equity']) / self.peak_equity
            if current_drawdown > self.risk_metrics.max_drawdown:
                return False, f"已达到最大回撤 {self.risk_metrics.max_drawdown * 100}%"

        # 检查风险收益比
        risk = abs(signal.entry_price - signal.stop_loss)
        reward = abs(signal.take_profit - signal.entry_price)
        if reward / risk < self.risk_metrics.risk_reward_ratio:
            return False, f"风险收益比不足: {reward/risk:.2f} < {self.risk_metrics.risk_reward_ratio}"

        # 检查保证金
        required_margin = signal.position_size * signal.entry_price * 0.1  # 假设10%保证金
        if required_margin > account_info['free_margin']:
            return False, f"保证金不足: 需要 {required_margin:.2f}, 可用 {account_info['free_margin']:.2f}"

        return True, "风险检查通过"

    def update_daily_pnl(self, pnl: float):
        """更新日盈亏"""
        self.daily_pnl += pnl

    def update_drawdown(self, equity: float):
        """更新回撤"""
        if equity > self.peak_equity:
            self.peak_equity = equity

        if self.peak_equity > 0:
            self.max_drawdown = max(
                self.max_drawdown,
                (self.peak_equity - equity) / self.peak_equity
            )

    def reset_daily(self):
        """重置日数据"""
        self.daily_pnl = 0.0


class OrderExecutor:
    """订单执行器"""

    def __init__(self):
        """初始化订单执行器"""
        self.order_timeout = 30  # 订单超时时间（秒）

    def execute_order(self, signal: TradingSignal, order_type: OrderType = OrderType.MARKET) -> Optional[Dict]:
        """执行订单"""
        try:
            # 确定订单类型
            if signal.signal_type == SignalType.BUY:
                trade_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(signal.symbol).ask
            else:
                trade_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(signal.symbol).bid

            # 构建订单请求
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": signal.symbol,
                "volume": signal.position_size,
                "type": trade_type,
                "price": price,
                "sl": signal.stop_loss,
                "tp": signal.take_profit,
                "deviation": 20,
                "magic": 123456,
                "comment": f"MT5 顶配系统 - {signal.reason}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # 发送订单
            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"订单执行失败: {result.retcode} - {result.comment}")
                return None

            logger.info(f"订单执行成功: {signal.symbol} {signal.signal_type.value} @ {price}")
            return {
                'ticket': result.order,
                'symbol': signal.symbol,
                'type': signal.signal_type.value,
                'volume': signal.position_size,
                'price': price,
                'sl': signal.stop_loss,
                'tp': signal.take_profit,
                'time': datetime.now()
            }

        except Exception as e:
            logger.error(f"执行订单异常: {e}")
            return None

    def close_position(self, ticket: int) -> bool:
        """平仓"""
        try:
            position = mt5.positions_get(ticket=ticket)
            if not position:
                logger.error(f"找不到持仓: {ticket}")
                return False

            pos = position[0]

            # 构建平仓请求
            if pos.type == mt5.POSITION_TYPE_BUY:
                trade_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(pos.symbol).bid
            else:
                trade_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(pos.symbol).ask

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": trade_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 123456,
                "comment": "MT5 顶配系统 - 平仓",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)

            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"平仓失败: {result.retcode} - {result.comment}")
                return False

            logger.info(f"平仓成功: {ticket}")
            return True

        except Exception as e:
            logger.error(f"平仓异常: {e}")
            return False


class MT5TopTierSystem:
    """MT5 顶配盯盘系统"""

    def __init__(self, symbols: List[str], risk_metrics: RiskMetrics):
        """初始化系统"""
        self.symbols = symbols
        self.risk_metrics = risk_metrics

        # 初始化组件
        self.data_collector = MT5DataCollector()
        self.signal_generator = SignalGenerator(risk_metrics)
        self.risk_manager = RiskManager(risk_metrics)
        self.order_executor = OrderExecutor()

        # 系统状态
        self.running = False
        self.positions = []

    def start(self):
        """启动系统"""
        logger.info("启动 MT5 顶配盯盘系统...")

        # 连接 MT5
        if not self.data_collector.connect():
            logger.error("无法连接到 MT5，系统启动失败")
            return False

        logger.info("MT5 顶配盯盘系统启动成功")
        self.running = True

        return True

    def stop(self):
        """停止系统"""
        logger.info("停止 MT5 顶配盯盘系统...")
        self.running = False
        self.data_collector.disconnect()
        logger.info("系统已停止")

    def run(self):
        """运行主循环"""
        logger.info("开始运行主循环...")

        while self.running:
            try:
                # 获取账户信息
                account_info = self.data_collector.get_account_info()
                if not account_info:
                    logger.warning("无法获取账户信息")
                    time.sleep(5)
                    continue

                # 更新回撤
                self.risk_manager.update_drawdown(account_info['equity'])

                # 获取当前持仓
                current_positions = self.data_collector.get_positions()
                self.positions = current_positions

                # 处理每个交易品种
                for symbol in self.symbols:
                    try:
                        # 获取历史数据
                        df = self.data_collector.get_rates(symbol, mt5.TIMEFRAME_H1, 100)
                        if df.empty:
                            continue

                        # 生成信号
                        signals = self.signal_generator.generate_signals(df, symbol)

                        # 处理信号
                        for signal in signals:
                            # 风险检查
                            risk_ok, risk_msg = self.risk_manager.check_risk(
                                signal, account_info, current_positions
                            )

                            if not risk_ok:
                                logger.info(f"{symbol} 信号被风险控制拒绝: {risk_msg}")
                                continue

                            # 执行订单
                            order_result = self.order_executor.execute_order(signal)
                            if order_result:
                                logger.info(f"成功执行订单: {order_result}")

                    except Exception as e:
                        logger.error(f"处理 {symbol} 时出错: {e}")

                # 检查现有持仓的止损止盈
                self._check_positions()

                # 等待下一个周期
                time.sleep(60)  # 每分钟检查一次

            except KeyboardInterrupt:
                logger.info("收到中断信号，停止系统")
                break
            except Exception as e:
                logger.error(f"主循环出错: {e}")
                time.sleep(10)

    def _check_positions(self):
        """检查持仓的止损止盈"""
        for pos in self.positions:
            try:
                current_price = self.data_collector.get_tick(pos['symbol'])
                if not current_price:
                    continue

                # 检查止损
                if pos['type'] == 0:  # 买单
                    if current_price['bid'] <= pos['sl']:
                        logger.info(f"{pos['symbol']} 触发止损")
                        self.order_executor.close_position(pos['ticket'])
                    elif current_price['bid'] >= pos['tp']:
                        logger.info(f"{pos['symbol']} 触发止盈")
                        self.order_executor.close_position(pos['ticket'])
                else:  # 卖单
                    if current_price['ask'] >= pos['sl']:
                        logger.info(f"{pos['symbol']} 触发止损")
                        self.order_executor.close_position(pos['ticket'])
                    elif current_price['ask'] <= pos['tp']:
                        logger.info(f"{pos['symbol']} 触发止盈")
                        self.order_executor.close_position(pos['ticket'])

            except Exception as e:
                logger.error(f"检查持仓 {pos['ticket']} 时出错: {e}")


def main():
    """主函数"""
    # 配置交易品种
    symbols = [
        'EURUSD',
        'GBPUSD',
        'USDJPY',
        'XAUUSD',  # 黄金
        'XAGUSD',  # 白银
    ]

    # 配置风险指标
    risk_metrics = RiskMetrics(
        max_position_size=0.02,
        max_daily_loss=0.05,
        max_drawdown=0.15,
        risk_reward_ratio=2.0,
        max_positions=5
    )

    # 创建系统
    system = MT5TopTierSystem(symbols, risk_metrics)

    # 启动系统
    if system.start():
        try:
            system.run()
        finally:
            system.stop()


if __name__ == '__main__':
    main()