"""
MT5 顶配盯盘系统 - 机器学习预测模块
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MLPrediction:
    """ML 预测结果"""
    direction: str  # 'up', 'down', 'neutral'
    confidence: float  # 0-1
    probability_up: float
    probability_down: float
    probability_neutral: float
    features: Dict[str, float]
    model_name: str


class MLPricePredictor:
    """机器学习价格预测器"""

    def __init__(self):
        self.models = {}
        self.feature_columns = []
        self.is_trained = False

    def prepare_features(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        准备特征

        生成技术指标作为 ML 特征
        """
        data = df.copy()
        close = data['close']
        high = data['high']
        low = data['low']

        features = pd.DataFrame(index=data.index)

        # 价格特征
        features['returns'] = close.pct_change()
        features['log_returns'] = np.log(close / close.shift(1))

        # 移动平均
        for period in [5, 10, 20, 50, 100, 200]:
            if len(close) >= period:
                features[f'sma_{period}'] = close.rolling(period).mean()
                features[f'ema_{period}'] = close.ewm(span=period, adjust=False).mean()
                features[f'price_vs_sma_{period}'] = (close - features[f'sma_{period}']) / features[f'sma_{period}']

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-6)
        features['rsi'] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()
        features['macd'] = ema_12 - ema_26
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean()
        features['macd_histogram'] = features['macd'] - features['macd_signal']

        # 布林带
        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        features['bb_upper'] = sma_20 + 2 * std_20
        features['bb_lower'] = sma_20 - 2 * std_20
        features['bb_position'] = (close - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'] + 1e-6)

        # ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        features['atr'] = tr.rolling(14).mean()
        features['atr_ratio'] = features['atr'] / close

        # 波动率
        features['volatility_10'] = close.pct_change().rolling(10).std()
        features['volatility_20'] = close.pct_change().rolling(20).std()

        # 动量
        for period in [5, 10, 20]:
            features[f'momentum_{period}'] = close / close.shift(period) - 1

        # 成交量特征 (如果有)
        if 'volume' in data.columns:
            features['volume'] = data['volume']
            features['volume_sma'] = data['volume'].rolling(20).mean()
            features['volume_ratio'] = data['volume'] / (features['volume_sma'] + 1e-6)

        # 目标变量: 未来收益
        features['target'] = close.shift(-1) / close - 1

        # 删除 NaN
        features = features.dropna()

        self.feature_columns = [col for col in features.columns if col != 'target']

        return features

    def predict(
        self,
        df: pd.DataFrame,
        model_type: str = 'ensemble'
    ) -> MLPrediction:
        """
        价格预测

        Args:
            df: 历史数据
            model_type: 'lr', 'rf', 'gb', 'ensemble'

        Returns:
            MLPrediction: 预测结果
        """
        features = self.prepare_features(df)

        if len(features) < 100:
            return MLPrediction(
                direction='neutral',
                confidence=0.0,
                probability_up=0.33,
                probability_down=0.33,
                probability_neutral=0.34,
                features={},
                model_name=model_type
            )

        # 使用简单规则-based 预测
        # 实际应该使用训练好的模型
        prediction = self._rule_based_predict(features)

        return prediction

    def _rule_based_predict(
        self,
        features: pd.DataFrame
    ) -> MLPrediction:
        """基于规则的预测"""
        latest = features.iloc[-1]

        # 计算各指标信号
        buy_signals = 0
        sell_signals = 0

        # RSI
        if latest['rsi'] < 30:
            buy_signals += 1
        elif latest['rsi'] > 70:
            sell_signals += 1

        # MACD
        if latest['macd'] > latest['macd_signal']:
            buy_signals += 1
        elif latest['macd'] < latest['macd_signal']:
            sell_signals += 1

        # 价格 vs SMA
        for period in [20, 50, 200]:
            col = f'price_vs_sma_{period}'
            if col in latest.index:
                if latest[col] > 0:
                    buy_signals += 1
                elif latest[col] < 0:
                    sell_signals += 1

        # 动量
        if latest['momentum_10'] > 0:
            buy_signals += 1
        elif latest['momentum_10'] < 0:
            sell_signals += 1

        # 计算概率
        total_signals = buy_signals + sell_signals
        if total_signals > 0:
            prob_up = buy_signals / total_signals
            prob_down = sell_signals / total_signals
        else:
            prob_up = 0.33
            prob_down = 0.33

        prob_neutral = 1 - prob_up - prob_down

        # 确定方向
        if buy_signals > sell_signals:
            direction = 'up'
            confidence = prob_up
        elif sell_signals > buy_signals:
            direction = 'down'
            confidence = prob_down
        else:
            direction = 'neutral'
            confidence = 0.5

        # 提取关键特征
        key_features = {
            'rsi': float(latest.get('rsi', 50)),
            'macd_histogram': float(latest.get('macd_histogram', 0)),
            'momentum_10': float(latest.get('momentum_10', 0)),
            'volatility_20': float(latest.get('volatility_20', 0)),
        }

        return MLPrediction(
            direction=direction,
            confidence=float(confidence),
            probability_up=float(prob_up),
            probability_down=float(prob_down),
            probability_neutral=float(prob_neutral),
            features=key_features,
            model_name='rule_based'
        )


class SignalEnsemble:
    """信号集成器 - 综合多个信号源"""

    def __init__(self):
        self.predictor = MLPricePredictor()
        self.weights = {
            'ml': 0.3,
            'technical': 0.4,
            'factor': 0.3,
        }

    def generate_ensemble_signal(
        self,
        df: pd.DataFrame,
        ml_prediction: MLPrediction = None,
        technical_signal: str = 'neutral',
        factor_score: float = 0.0
    ) -> Dict[str, any]:
        """
        生成集成信号

        Args:
            df: 价格数据
            ml_prediction: ML 预测结果
            technical_signal: 技术分析信号
            factor_score: 因子分析得分 (-1 到 1)

        Returns:
            {
                'signal': str,
                'confidence': float,
                'strength': float,
                'sources': Dict,
            }
        """
        # ML 信号
        if ml_prediction is None:
            ml_prediction = self.predictor.predict(df)

        ml_signal = ml_prediction.direction
        ml_confidence = ml_prediction.confidence

        # 技术信号
        tech_signals = {
            'buy': 1,
            'sell': -1,
            'neutral': 0,
        }
        tech_value = tech_signals.get(technical_signal, 0)

        # 因子信号
        factor_value = factor_score  # -1 到 1

        # 综合得分
        total_signal = (
            ml_signal_map(ml_signal) * ml_confidence * self.weights['ml'] +
            tech_value * self.weights['technical'] +
            factor_value * self.weights['factor']
        )

        # 计算置信度
        total_confidence = (
            ml_confidence * self.weights['ml'] +
            self.weights['technical'] +
            abs(factor_value) * self.weights['factor']
        ) / sum(self.weights.values())

        # 确定最终信号
        if total_signal > 0.3:
            final_signal = 'buy'
            strength = min(total_signal, 1.0)
        elif total_signal < -0.3:
            final_signal = 'sell'
            strength = min(abs(total_signal), 1.0)
        else:
            final_signal = 'neutral'
            strength = 1 - abs(total_signal)

        return {
            'signal': final_signal,
            'confidence': total_confidence,
            'strength': strength,
            'total_score': total_signal,
            'sources': {
                'ml': {
                    'signal': ml_signal,
                    'confidence': ml_confidence,
                    'probabilities': {
                        'up': ml_prediction.probability_up,
                        'down': ml_prediction.probability_down,
                        'neutral': ml_prediction.probability_neutral,
                    }
                },
                'technical': {
                    'signal': technical_signal,
                    'value': tech_value,
                },
                'factor': {
                    'score': factor_score,
                    'value': factor_value,
                }
            }
        }


def ml_signal_map(signal: str) -> float:
    """信号映射到数值"""
    mapping = {
        'up': 1.0,
        'down': -1.0,
        'neutral': 0.0,
    }
    return mapping.get(signal, 0.0)


class TrendlineDetector:
    """趋势线检测器"""

    @staticmethod
    def detect_support_resistance(
        df: pd.DataFrame,
        window: int = 20
    ) -> Dict[str, List[float]]:
        """
        检测支撑和阻力位

        使用局部极值方法
        """
        high = df['high']
        low = df['low']

        # 找局部高点和低点
        support_levels = []
        resistance_levels = []

        for i in range(window, len(df) - window):
            # 检查是否是局部高点
            is_resistance = True
            for j in range(i - window, i + window + 1):
                if j != i and high.iloc[j] >= high.iloc[i]:
                    is_resistance = False
                    break
            if is_resistance:
                resistance_levels.append(high.iloc[i])

            # 检查是否是局部低点
            is_support = True
            for j in range(i - window, i + window + 1):
                if j != i and low.iloc[j] <= low.iloc[i]:
                    is_support = False
                    break
            if is_support:
                support_levels.append(low.iloc[i])

        # 聚类相似的价位
        support_clustered = TrendlineDetector._cluster_levels(support_levels)
        resistance_clustered = TrendlineDetector._cluster_levels(resistance_levels)

        return {
            'support': sorted(support_clustered, reverse=True),
            'resistance': sorted(resistance_clustered, reverse=False),
        }

    @staticmethod
    def _cluster_levels(
        levels: List[float],
        tolerance: float = 0.002
    ) -> List[float]:
        """聚类相似的价位"""
        if not levels:
            return []

        sorted_levels = sorted(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]

        for level in sorted_levels[1:]:
            if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) < tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]

        clusters.append(np.mean(current_cluster))

        return clusters

    @staticmethod
    def detect_trendline(
        df: pd.DataFrame,
        lookback: int = 50
    ) -> Dict[str, any]:
        """
        检测趋势线

        使用简单的线性回归
        """
        close = df['close'].tail(lookback)

        # 简单线性回归
        x = np.arange(len(close))
        y = close.values

        # 计算斜率
        n = len(x)
        slope = (n * np.sum(x * y) - np.sum(x) * np.sum(y)) / (n * np.sum(x * x) - np.sum(x) ** 2)
        intercept = (np.sum(y) - slope * np.sum(x)) / n

        # 判断趋势
        if slope > 0:
            trend = 'up'
        elif slope < 0:
            trend = 'down'
        else:
            trend = 'sideways'

        return {
            'trend': trend,
            'slope': slope,
            'intercept': intercept,
            'current_price': close.iloc[-1],
            'trendline_price': slope * (n - 1) + intercept,
        }