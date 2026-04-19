"""
MT5 顶配盯盘系统 - 多时间框架分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TimeFrame(Enum):
    """时间框架"""
    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"
    W1 = "W1"


@dataclass
class TimeFrameAnalysis:
    """时间框架分析结果"""
    timeframe: str
    trend: str  # 'up', 'down', 'sideways'
    strength: float  # 0-1
    key_levels: Dict[str, float]  # 关键价位
    signals: List[str]  # 信号列表


class MultiTimeFrameAnalyzer:
    """多时间框架分析器"""

    def __init__(self):
        """初始化分析器"""
        self.timeframes = {
            'M1': 1,
            'M5': 5,
            'M15': 15,
            'M30': 30,
            'H1': 60,
            'H4': 240,
            'D1': 1440,
            'W1': 10080,
        }

    def analyze(
        self,
        data_dict: Dict[str, pd.DataFrame],
        symbol: str
    ) -> Dict[str, any]:
        """
        多时间框架分析
        
        Args:
            data_dict: 不同时间框架的数据字典
                {
                    'M1': DataFrame,
                    'M5': DataFrame,
                    'H1': DataFrame,
                    'D1': DataFrame,
                }
        """
        results = {
            'symbol': symbol,
            'timeframes': {},
            'alignment': {},
            'confluence': 0.0,
            'signal': 'neutral',
            'confidence': 0.0,
            'trend': 'neutral',
        }

        analyses = {}
        trends = []
        strengths = []

        # 分析每个时间框架
        for tf_name, df in data_dict.items():
            if df is None or len(df) < 50:
                continue

            analysis = self._analyze_single_timeframe(df, tf_name)
            analyses[tf_name] = analysis
            results['timeframes'][tf_name] = {
                'trend': analysis.trend,
                'strength': analysis.strength,
                'key_levels': analysis.key_levels,
            }

            trends.append(analysis.trend)
            strengths.append(analysis.strength)

        # 计算趋势一致性
        trend_alignment = self._calculate_trend_alignment(trends)
        results['alignment']['trend'] = trend_alignment

        # 计算信号一致性
        all_signals = []
        for analysis in analyses.values():
            all_signals.extend(analysis.signals)

        signal_alignment = self._calculate_signal_alignment(all_signals)
        results['alignment']['signals'] = signal_alignment

        # 计算汇合度
        confluence = self._calculate_confluence(trend_alignment, signal_alignment, strengths)
        results['confluence'] = confluence

        # 生成最终信号
        signal, confidence, trend = self._generate_final_signal(
            analyses, trend_alignment, signal_alignment, confluence
        )
        results['signal'] = signal
        results['confidence'] = confidence
        results['trend'] = trend

        # 添加关键价位
        results['key_levels'] = self._aggregate_key_levels(analyses)

        return results

    def _analyze_single_timeframe(self, df: pd.DataFrame, timeframe: str) -> TimeFrameAnalysis:
        """分析单个时间框架"""
        close = df['close']
        high = df['high']
        low = df['low']

        # 计算趋势
        trend, strength = self._determine_trend(df)

        # 计算关键价位
        key_levels = self._calculate_key_levels(df, timeframe)

        # 生成信号
        signals = self._generate_timeframe_signals(df, timeframe)

        return TimeFrameAnalysis(
            timeframe=timeframe,
            trend=trend,
            strength=strength,
            key_levels=key_levels,
            signals=signals
        )

    def _determine_trend(self, df: pd.DataFrame) -> Tuple[str, float]:
        """判断趋势"""
        close = df['close']

        # 计算多条均线
        ma_20 = close.rolling(20).mean()
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean()

        # 计算趋势强度
        current_price = close.iloc[-1]
        price_vs_ma20 = (current_price - ma_20.iloc[-1]) / ma_20.iloc[-1]
        price_vs_ma50 = (current_price - ma_50.iloc[-1]) / ma_50.iloc[-1]

        # 判断趋势
        if len(ma_200) > 0 and not pd.isna(ma_200.iloc[-1]):
            if current_price > ma_200.iloc[-1]:
                if price_vs_ma20 > 0 and price_vs_ma50 > 0:
                    trend = 'up'
                    strength = min(abs(price_vs_ma20) * 10 + abs(price_vs_ma50) * 5, 1.0)
                elif price_vs_ma20 > 0 or price_vs_ma50 > 0:
                    trend = 'up'
                    strength = 0.6
                else:
                    trend = 'sideways'
                    strength = 0.5
            elif current_price < ma_200.iloc[-1]:
                if price_vs_ma20 < 0 and price_vs_ma50 < 0:
                    trend = 'down'
                    strength = min(abs(price_vs_ma20) * 10 + abs(price_vs_ma50) * 5, 1.0)
                elif price_vs_ma20 < 0 or price_vs_ma50 < 0:
                    trend = 'down'
                    strength = 0.6
                else:
                    trend = 'sideways'
                    strength = 0.5
            else:
                trend = 'sideways'
                strength = 0.5
        else:
            # 短期趋势判断
            if price_vs_ma20 > 0:
                trend = 'up'
                strength = min(abs(price_vs_ma20) * 20, 1.0)
            elif price_vs_ma20 < 0:
                trend = 'down'
                strength = min(abs(price_vs_ma20) * 20, 1.0)
            else:
                trend = 'sideways'
                strength = 0.5

        return trend, strength

    def _calculate_key_levels(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> Dict[str, float]:
        """计算关键价位"""
        high = df['high']
        low = df['low']
        close = df['close']

        key_levels = {}

        # 枢轴点
        pivot = (high.iloc[-1] + low.iloc[-1] + close.iloc[-1]) / 3
        key_levels['pivot'] = pivot

        # 支撑位
        s1 = 2 * pivot - high.iloc[-1]
        s2 = pivot - (high.iloc[-1] - low.iloc[-1])
        s3 = low.iloc[-1] - 2 * (high.iloc[-1] - pivot)
        key_levels['s1'] = s1
        key_levels['s2'] = s2
        key_levels['s3'] = s3

        # 阻力位
        r1 = 2 * pivot - low.iloc[-1]
        r2 = pivot + (high.iloc[-1] - low.iloc[-1])
        r3 = high.iloc[-1] + 2 * (pivot - low.iloc[-1])
        key_levels['r1'] = r1
        key_levels['r2'] = r2
        key_levels['r3'] = r3

        # 近期高低点
        key_levels['recent_high'] = high.tail(20).max()
        key_levels['recent_low'] = low.tail(20).min()

        # 布林带
        sma = close.rolling(20).mean().iloc[-1]
        std = close.rolling(20).std().iloc[-1]
        key_levels['bb_upper'] = sma + 2 * std
        key_levels['bb_middle'] = sma
        key_levels['bb_lower'] = sma - 2 * std

        return key_levels

    def _generate_timeframe_signals(
        self,
        df: pd.DataFrame,
        timeframe: str
    ) -> List[str]:
        """生成时间框架信号"""
        signals = []
        close = df['close']

        # 计算指标
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        rsi = self._calculate_rsi(close)

        # 金叉死叉
        if len(sma_50) > 0 and not pd.isna(sma_50.iloc[-1]):
            if sma_20.iloc[-2] < sma_50.iloc[-2] and sma_20.iloc[-1] > sma_50.iloc[-1]:
                signals.append('golden_cross')
            elif sma_20.iloc[-2] > sma_50.iloc[-2] and sma_20.iloc[-1] < sma_50.iloc[-1]:
                signals.append('death_cross')

        # RSI 信号
        if rsi > 70:
            signals.append('rsi_overbought')
        elif rsi < 30:
            signals.append('rsi_oversold')

        return signals

    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> float:
        """计算 RSI"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0

    def _calculate_trend_alignment(self, trends: List[str]) -> float:
        """计算趋势一致性"""
        if not trends:
            return 0.0

        up_count = trends.count('up')
        down_count = trends.count('down')
        total = len(trends)

        # 最高时间框架权重更大
        if up_count > down_count:
            return up_count / total
        elif down_count > up_count:
            return -down_count / total
        else:
            return 0.0

    def _calculate_signal_alignment(self, signals: List[str]) -> float:
        """计算信号一致性"""
        if not signals:
            return 0.0

        buy_signals = ['golden_cross', 'rsi_oversold']
        sell_signals = ['death_cross', 'rsi_overbought']

        buy_count = sum(1 for s in signals if s in buy_signals)
        sell_count = sum(1 for s in signals if s in sell_signals)

        total = len(signals)
        if buy_count > sell_count:
            return buy_count / total
        elif sell_count > buy_count:
            return -sell_count / total
        else:
            return 0.0

    def _calculate_confluence(
        self,
        trend_alignment: float,
        signal_alignment: float,
        strengths: List[float]
    ) -> float:
        """计算汇合度"""
        # 权重
        trend_weight = 0.4
        signal_weight = 0.4
        strength_weight = 0.2

        # 平均强度
        avg_strength = sum(strengths) / len(strengths) if strengths else 0.5

        # 计算汇合度
        confluence = (
            abs(trend_alignment) * trend_weight +
            abs(signal_alignment) * signal_weight +
            avg_strength * strength_weight
        )

        return confluence

    def _generate_final_signal(
        self,
        analyses: Dict[str, TimeFrameAnalysis],
        trend_alignment: float,
        signal_alignment: float,
        confluence: float
    ) -> Tuple[str, float, str]:
        """生成最终信号"""
        # 确定趋势
        if trend_alignment > 0.5:
            trend = 'up'
        elif trend_alignment < -0.5:
            trend = 'down'
        else:
            trend = 'sideways'

        # 确定信号
        total_alignment = (trend_alignment + signal_alignment) / 2

        if total_alignment > 0.4 and confluence > 0.6:
            signal = 'buy'
            confidence = confluence
        elif total_alignment < -0.4 and confluence > 0.6:
            signal = 'sell'
            confidence = confluence
        else:
            signal = 'neutral'
            confidence = 1 - confluence

        return signal, confidence, trend

    def _aggregate_key_levels(
        self,
        analyses: Dict[str, TimeFrameAnalysis]
    ) -> Dict[str, float]:
        """汇总关键价位"""
        all_levels = {}

        for tf_name, analysis in analyses.items():
            for level_name, level_value in analysis.key_levels.items():
                if level_name not in all_levels:
                    all_levels[level_name] = []
                all_levels[level_name].append(level_value)

        # 计算平均值
        aggregated = {}
        for level_name, values in all_levels.items():
            aggregated[level_name] = sum(values) / len(values)

        return aggregated


class TrendStrengthCalculator:
    """趋势强度计算器"""

    @staticmethod
    def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.Series:
        """
        计算超级趋势指标
        
        Supertrend 是一种趋势跟踪指标，结合了 ATR 和价格位置
        """
        high = df['high']
        low = df['low']
        close = df['close']

        # 计算 ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        # 计算上下轨
        hl2 = (high + low) / 2
        upper_band = hl2 + multiplier * atr
        lower_band = hl2 - multiplier * atr

        # 计算 Supertrend
        supertrend = pd.Series(index=close.index, data=0.0)
        direction = pd.Series(index=close.index, data=1)  # 1 = 上涨, -1 = 下跌

        for i in range(1, len(close)):
            if pd.isna(atr.iloc[i]) or pd.isna(close.iloc[i]):
                continue

            # 上涨趋势
            if close.iloc[i] > upper_band.iloc[i]:
                direction.iloc[i] = 1
            # 下跌趋势
            elif close.iloc[i] < lower_band.iloc[i]:
                direction.iloc[i] = -1
            # 延续趋势
            else:
                direction.iloc[i] = direction.iloc[i-1]

            # 计算 Supertrend 值
            if direction.iloc[i] == 1:
                supertrend.iloc[i] = lower_band.iloc[i]
            else:
                supertrend.iloc[i] = upper_band.iloc[i]

        return supertrend

    @staticmethod
    def calculate_ichimoku(df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        计算 Ichimoku Cloud (一目均衡表)
        
        包含:
        - Tenkan-sen (转换线)
        - Kijun-sen (基准线)
        - Senkou Span A (先行Span A)
        - Senkou Span B (先行Span B)
        - Chikou Span (延迟线)
        """
        high = df['high']
        low = df['low']
        close = df['close']

        # Tenkan-sen (9 周期)
        tenkan_sen = (high.rolling(9).max() + low.rolling(9).min()) / 2

        # Kijun-sen (26 周期)
        kijun_sen = (high.rolling(26).max() + low.rolling(26).min()) / 2

        # Senkou Span A (转换线 + 基准线) / 2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)

        # Senkou Span B (52 周期)
        senkou_span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2).shift(26)

        # Chikou Span (延迟线)
        chikou_span = close.shift(-26)

        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span,
        }

    @staticmethod
    def calculate_vortex_indicator(df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """
        计算 Vortex 指标
        
        用于识别趋势反转
        """
        high = df['high']
        low = df['low']
        close = df['close']

        # 计算 VM+ 和 VM-
        vm_plus = abs(high - low.shift())
        vm_minus = abs(low - high.shift())

        # 计算真实范围
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)

        # 计算 VI+ 和 VI-
        vi_plus = vm_plus.rolling(window=period).sum() / tr.rolling(window=period).sum()
        vi_minus = vm_minus.rolling(window=period).sum() / tr.rolling(window=period).sum()

        return vi_plus, vi_minus

    @staticmethod
    def calculate_trend_intensity(df: pd.DataFrame, period: int = 30) -> float:
        """
        计算趋势强度
        
        返回 0-100 的值:
        - 0-30: 弱趋势
        - 30-70: 中等趋势
        - 70-100: 强趋势
        """
        close = df['close']

        # 计算价格与均线的偏离
        ma = close.rolling(period).mean()
        std = close.rolling(period).std()

        # 计算趋势强度
        deviation = abs(close - ma) / std
        intensity = deviation.mean() * 100 / 3  # 归一化到 0-100

        return min(intensity, 100.0)