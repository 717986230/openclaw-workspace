"""
MT5 顶配盯盘系统 - 因子分析模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FactorType(Enum):
    """因子类型"""
    TREND = "trend"  # 趋势因子
    MOMENTUM = "momentum"  # 动量因子
    VOLATILITY = "volatility"  # 波动率因子
    VOLUME = "volume"  # 成交量因子
    MEAN_REVERSION = "mean_reversion"  # 均值回归因子
    SENTIMENT = "sentiment"  # 情绪因子


@dataclass
class Factor:
    """因子数据"""
    name: str
    type: FactorType
    value: float
    weight: float
    signal: str  # 'buy', 'sell', 'neutral'
    confidence: float
    description: str


class FactorAnalyzer:
    """因子分析器"""

    def __init__(self):
        """初始化因子分析器"""
        self.factors: List[Factor] = []

    def analyze(self, df: pd.DataFrame, symbol: str) -> Dict[str, any]:
        """分析所有因子"""
        if len(df) < 100:
            return {'error': '数据不足，需要至少 100 根 K线'}

        results = {
            'symbol': symbol,
            'factors': [],
            'composite_score': 0.0,
            'signal': 'neutral',
            'confidence': 0.0,
        }

        # 计算各类因子
        trend_factors = self._analyze_trend_factors(df)
        momentum_factors = self._analyze_momentum_factors(df)
        volatility_factors = self._analyze_volatility_factors(df)
        volume_factors = self._analyze_volume_factors(df)
        mean_reversion_factors = self._analyze_mean_reversion_factors(df)

        # 合并所有因子
        all_factors = (
            trend_factors +
            momentum_factors +
            volatility_factors +
            volume_factors +
            mean_reversion_factors
        )

        results['factors'] = all_factors

        # 计算综合得分
        composite_score = self._calculate_composite_score(all_factors)
        results['composite_score'] = composite_score

        # 生成信号
        signal, confidence = self._generate_signal(composite_score, all_factors)
        results['signal'] = signal
        results['confidence'] = confidence

        return results

    def _analyze_trend_factors(self, df: pd.DataFrame) -> List[Factor]:
        """分析趋势因子"""
        factors = []
        close = df['close']

        # 1. ADX (Average Directional Index) - 趋势强度
        adx = self._calculate_adx(df)
        adx_signal = 'buy' if adx > 25 else 'neutral'
        factors.append(Factor(
            name='ADX',
            type=FactorType.TREND,
            value=adx,
            weight=0.15,
            signal=adx_signal,
            confidence=min(adx / 50, 1.0),
            description=f'趋势强度: {adx:.2f} (强趋势 > 25)'
        ))

        # 2. MA Slope - 均线斜率
        ma_slope = self._calculate_ma_slope(close, 20)
        ma_signal = 'buy' if ma_slope > 0 else 'sell'
        factors.append(Factor(
            name='MA_Slope',
            type=FactorType.TREND,
            value=ma_slope,
            weight=0.10,
            signal=ma_signal,
            confidence=min(abs(ma_slope) * 100, 1.0),
            description=f'均线斜率: {ma_slope:.4f} (正数向上)'
        ))

        # 3. Price vs MA - 价格与均线关系
        price_vs_ma = (close.iloc[-1] - close.rolling(50).mean().iloc[-1]) / close.rolling(50).mean().iloc[-1]
        price_signal = 'buy' if price_vs_ma > 0 else 'sell'
        factors.append(Factor(
            name='Price_vs_MA',
            type=FactorType.TREND,
            value=price_vs_ma,
            weight=0.10,
            signal=price_signal,
            confidence=min(abs(price_vs_ma) * 10, 1.0),
            description=f'价格偏离均线: {price_vs_ma:.2%}'
        ))

        return factors

    def _analyze_momentum_factors(self, df: pd.DataFrame) -> List[Factor]:
        """分析动量因子"""
        factors = []
        close = df['close']

        # 1. ROC (Rate of Change) - 变化率
        roc = self._calculate_roc(close, 10)
        roc_signal = 'buy' if roc > 0 else 'sell'
        factors.append(Factor(
            name='ROC',
            type=FactorType.MOMENTUM,
            value=roc,
            weight=0.12,
            signal=roc_signal,
            confidence=min(abs(roc) / 10, 1.0),
            description=f'10日变化率: {roc:.2%}'
        ))

        # 2. Momentum - 动量
        momentum = close.iloc[-1] - close.iloc[-20]
        mom_signal = 'buy' if momentum > 0 else 'sell'
        factors.append(Factor(
            name='Momentum',
            type=FactorType.MOMENTUM,
            value=momentum,
            weight=0.10,
            signal=mom_signal,
            confidence=min(abs(momentum) / close.iloc[-1] * 10, 1.0),
            description=f'20日动量: {momentum:.4f}'
        ))

        # 3. Williams %R - 威廉指标
        williams_r = self._calculate_williams_r(df)
        wr_signal = 'buy' if williams_r < -80 else ('sell' if williams_r > -20 else 'neutral')
        factors.append(Factor(
            name='Williams_R',
            type=FactorType.MOMENTUM,
            value=williams_r,
            weight=0.08,
            signal=wr_signal,
            confidence=min(abs(williams_r + 50) / 50, 1.0),
            description=f'威廉指标: {williams_r:.2f} (超买 > -20, 超卖 < -80)'
        ))

        return factors

    def _analyze_volatility_factors(self, df: pd.DataFrame) -> List[Factor]:
        """分析波动率因子"""
        factors = []
        close = df['close']

        # 1. ATR - 平均真实波幅
        atr = self._calculate_atr(df)
        atr_ratio = atr / close.iloc[-1]
        atr_signal = 'neutral'
        factors.append(Factor(
            name='ATR',
            type=FactorType.VOLATILITY,
            value=atr_ratio,
            weight=0.08,
            signal=atr_signal,
            confidence=min(atr_ratio * 100, 1.0),
            description=f'波动率: {atr_ratio:.2%} (适中 0.5%-2%)'
        ))

        # 2. Bollinger Band Width - 布林带宽度
        bb_width = self._calculate_bb_width(df)
        bb_signal = 'neutral'
        factors.append(Factor(
            name='BB_Width',
            type=FactorType.VOLATILITY,
            value=bb_width,
            weight=0.07,
            signal=bb_signal,
            confidence=min(bb_width / 0.1, 1.0),
            description=f'布林带宽度: {bb_width:.4f} (宽 > 0.05)'
        ))

        # 3. Historical Volatility - 历史波动率
        hist_vol = self._calculate_historical_volatility(close)
        vol_signal = 'neutral'
        factors.append(Factor(
            name='Hist_Vol',
            type=FactorType.VOLATILITY,
            value=hist_vol,
            weight=0.05,
            signal=vol_signal,
            confidence=min(hist_vol / 0.3, 1.0),
            description=f'历史波动率: {hist_vol:.2%}'
        ))

        return factors

    def _analyze_volume_factors(self, df: pd.DataFrame) -> List[Factor]:
        """分析成交量因子"""
        factors = []

        if 'volume' not in df.columns:
            return factors

        volume = df['volume']
        close = df['close']

        # 1. Volume Ratio - 成交量比率
        vol_ratio = volume.iloc[-1] / volume.rolling(20).mean().iloc[-1]
        vol_signal = 'buy' if vol_ratio > 1.5 else 'neutral'
        factors.append(Factor(
            name='Volume_Ratio',
            type=FactorType.VOLUME,
            value=vol_ratio,
            weight=0.08,
            signal=vol_signal,
            confidence=min(vol_ratio / 3, 1.0),
            description=f'成交量比率: {vol_ratio:.2f} (放量 > 1.5)'
        ))

        # 2. OBV (On-Balance Volume) - 能量潮
        obv = self._calculate_obv(df)
        obv_signal = 'buy' if obv > 0 else 'sell'
        factors.append(Factor(
            name='OBV',
            type=FactorType.VOLUME,
            value=obv,
            weight=0.07,
            signal=obv_signal,
            confidence=min(abs(obv) / 1000000, 1.0),
            description=f'能量潮: {obv:.0f} (正数向上)'
        ))

        return factors

    def _analyze_mean_reversion_factors(self, df: pd.DataFrame) -> List[Factor]:
        """分析均值回归因子"""
        factors = []
        close = df['close']

        # 1. Z-Score - Z分数
        z_score = self._calculate_z_score(close)
        z_signal = 'sell' if z_score > 2 else ('buy' if z_score < -2 else 'neutral')
        factors.append(Factor(
            name='Z_Score',
            type=FactorType.MEAN_REVERSION,
            value=z_score,
            weight=0.10,
            signal=z_signal,
            confidence=min(abs(z_score) / 3, 1.0),
            description=f'Z分数: {z_score:.2f} (超买 > 2, 超卖 < -2)'
        ))

        # 2. Bollinger Band Position - 布林带位置
        bb_position = self._calculate_bb_position(df)
        bb_signal = 'sell' if bb_position > 0.8 else ('buy' if bb_position < 0.2 else 'neutral')
        factors.append(Factor(
            name='BB_Position',
            type=FactorType.MEAN_REVERSION,
            value=bb_position,
            weight=0.08,
            signal=bb_signal,
            confidence=min(abs(bb_position - 0.5) * 2, 1.0),
            description=f'布林带位置: {bb_position:.2f} (0-1)'
        ))

        return factors

    def _calculate_composite_score(self, factors: List[Factor]) -> float:
        """计算综合得分"""
        buy_score = 0.0
        sell_score = 0.0

        for factor in factors:
            if factor.signal == 'buy':
                buy_score += factor.weight * factor.confidence
            elif factor.signal == 'sell':
                sell_score += factor.weight * factor.confidence

        # 归一化到 -1 到 1
        total_weight = sum(f.weight for f in factors)
        if total_weight > 0:
            composite = (buy_score - sell_score) / total_weight
        else:
            composite = 0.0

        return composite

    def _generate_signal(self, composite_score: float, factors: List[Factor]) -> Tuple[str, float]:
        """生成信号"""
        # 计算置信度
        buy_factors = [f for f in factors if f.signal == 'buy']
        sell_factors = [f for f in factors if f.signal == 'sell']

        buy_confidence = sum(f.weight * f.confidence for f in buy_factors)
        sell_confidence = sum(f.weight * f.confidence for f in sell_factors)
        total_confidence = buy_confidence + sell_confidence

        if total_confidence > 0:
            confidence = max(buy_confidence, sell_confidence) / total_confidence
        else:
            confidence = 0.0

        # 生成信号
        if composite_score > 0.3:
            return 'buy', confidence
        elif composite_score < -0.3:
            return 'sell', confidence
        else:
            return 'neutral', confidence

    # 辅助计算函数
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算 ADX"""
        high = df['high']
        low = df['low']
        close = df['close']

        plus_dm = high.diff()
        minus_dm = low.diff()

        plus_dm = plus_dm.where((plus_dm > 0) & (plus_dm > minus_dm), 0)
        minus_dm = minus_dm.where((minus_dm > 0) & (minus_dm > plus_dm), 0)

        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)

        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0.0

    def _calculate_ma_slope(self, data: pd.Series, period: int) -> float:
        """计算均线斜率"""
        ma = data.rolling(window=period).mean()
        slope = (ma.iloc[-1] - ma.iloc[-5]) / 5
        return slope

    def _calculate_roc(self, data: pd.Series, period: int) -> float:
        """计算变化率"""
        return (data.iloc[-1] - data.iloc[-period]) / data.iloc[-period]

    def _calculate_williams_r(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算威廉指标"""
        high = df['high']
        low = df['low']
        close = df['close']

        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()

        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
        return williams_r.iloc[-1] if not pd.isna(williams_r.iloc[-1]) else 0.0

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """计算 ATR"""
        high = df['high']
        low = df['low']
        close = df['close']

        high_low = high - low
        high_close = abs(high - close.shift())
        low_close = abs(low - close.shift())

        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.0

    def _calculate_bb_width(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> float:
        """计算布林带宽度"""
        close = df['close']
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        bb_width = (upper_band - lower_band) / sma
        return bb_width.iloc[-1] if not pd.isna(bb_width.iloc[-1]) else 0.0

    def _calculate_historical_volatility(self, data: pd.Series, period: int = 20) -> float:
        """计算历史波动率"""
        returns = np.log(data / data.shift())
        volatility = returns.rolling(window=period).std() * np.sqrt(252)
        return volatility.iloc[-1] if not pd.isna(volatility.iloc[-1]) else 0.0

    def _calculate_obv(self, df: pd.DataFrame) -> float:
        """计算 OBV"""
        if 'volume' not in df.columns:
            return 0.0

        close = df['close']
        volume = df['volume']

        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv.iloc[-1] if not pd.isna(obv.iloc[-1]) else 0.0

    def _calculate_z_score(self, data: pd.Series, period: int = 20) -> float:
        """计算 Z分数"""
        mean = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        z_score = (data - mean) / std
        return z_score.iloc[-1] if not pd.isna(z_score.iloc[-1]) else 0.0

    def _calculate_bb_position(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> float:
        """计算布林带位置"""
        close = df['close']
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)

        position = (close - lower_band) / (upper_band - lower_band)
        return position.iloc[-1] if not pd.isna(position.iloc[-1]) else 0.5