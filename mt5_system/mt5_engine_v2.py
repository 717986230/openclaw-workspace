"""
MT5 顶配盯盘系统 v2 - 增强版策略引擎
集成: 因子分析 + 多时间框架 + 参数优化 + 品种筛选 + 时间过滤 + ML预测
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

from mt5_system.factor_analyzer import FactorAnalyzer, FactorType
from mt5_system.multi_timeframe_analyzer import MultiTimeFrameAnalyzer, TrendStrengthCalculator
from mt5_system.parameter_optimizer import ParameterOptimizer
from mt5_system.symbol_filter import SymbolFilter
from mt5_system.time_filter import TimeFilter, VolatilityFilter
from mt5_system.ml_predictor import MLPricePredictor, SignalEnsemble, TrendlineDetector

logger = logging.getLogger(__name__)


class SignalSource(Enum):
    """信号来源"""
    TECHNICAL = "technical"
    FACTOR = "factor"
    MULTI_TF = "multi_timeframe"
    ML = "ml"
    ENSEMBLE = "ensemble"


@dataclass
class EnhancedSignal:
    """增强信号"""
    symbol: str
    signal_type: str  # BUY, SELL, NEUTRAL
    confidence: float
    strength: float
    sources: Dict[str, float]  # 各来源得分
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    reason: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class RiskMetrics:
    """风险管理参数"""
    max_position_size: float = 0.02
    max_positions: int = 5
    max_daily_loss: float = 0.05
    max_drawdown: float = 0.15
    risk_reward_ratio: float = 2.0
    atr_multiplier_sl: float = 2.0
    atr_multiplier_tp: float = 3.0


class EnhancedStrategyEngine:
    """增强版策略引擎"""

    def __init__(
        self,
        risk_metrics: RiskMetrics = None,
        use_ml: bool = True,
        use_factor_analysis: bool = True,
        use_multi_tf: bool = True,
    ):
        """初始化增强版策略引擎"""
        self.risk_metrics = risk_metrics or RiskMetrics()

        # 初始化各模块
        self.factor_analyzer = FactorAnalyzer()
        self.mtf_analyzer = MultiTimeFrameAnalyzer()
        self.param_optimizer = ParameterOptimizer()
        self.symbol_filter = SymbolFilter()
        self.time_filter = TimeFilter()
        self.volatility_filter = VolatilityFilter()
        self.ml_predictor = MLPricePredictor()
        self.signal_ensemble = SignalEnsemble()
        self.trendline_detector = TrendlineDetector()

        # 配置
        self.use_ml = use_ml
        self.use_factor_analysis = use_factor_analysis
        self.use_multi_tf = use_multi_tf

        # 缓存
        self.optimal_params = None
        self.symbol_rankings = None

    def analyze_and_generate_signal(
        self,
        df: pd.DataFrame,
        symbol: str,
        data_multi_tf: Dict[str, pd.DataFrame] = None,
        check_time: bool = True,
        check_volatility: bool = True,
    ) -> Optional[EnhancedSignal]:
        """
        综合分析并生成信号

        Args:
            df: K线数据
            symbol: 品种
            data_multi_tf: 多时间框架数据
            check_time: 检查交易时间
            check_volatility: 检查波动率

        Returns:
            EnhancedSignal 或 None
        """
        # 1. 时间检查
        if check_time:
            allowed, time_reason = self.time_filter.is_trade_allowed(symbol)
            if not allowed:
                logger.info(f"{symbol}: {time_reason}")
                return None

        # 2. 波动率检查
        if check_volatility:
            vol_analysis = self.volatility_filter.analyze_volatility(df)
            if vol_analysis['state'] in ['extreme']:
                logger.info(f"{symbol}: 波动率极端 - {vol_analysis['recommendation']}")

        # 3. 技术指标信号
        technical_signal = self._generate_technical_signal(df)

        # 4. 因子分析
        factor_score = 0.0
        factor_metadata = {}
        if self.use_factor_analysis:
            factor_result = self.factor_analyzer.analyze(df, symbol)
            factor_score = factor_result['composite_score']
            factor_metadata = {
                'signal': factor_result['signal'],
                'confidence': factor_result['confidence'],
                'factors_count': len(factor_result['factors']),
            }

        # 5. 多时间框架分析
        mtf_signal = 'neutral'
        mtf_metadata = {}
        if self.use_multi_tf and data_multi_tf:
            mtf_result = self.mtf_analyzer.analyze(data_multi_tf, symbol)
            mtf_signal = mtf_result['signal']
            mtf_metadata = {
                'trend': mtf_result['trend'],
                'confluence': mtf_result['confluence'],
                'timeframes': list(mtf_result['timeframes'].keys()),
            }

        # 6. ML 预测
        ml_prediction = None
        if self.use_ml:
            ml_prediction = self.ml_predictor.predict(df)

        # 7. 集成信号
        ensemble_result = self.signal_ensemble.generate_ensemble_signal(
            df=df,
            ml_prediction=ml_prediction,
            technical_signal=technical_signal,
            factor_score=factor_score,
        )

        # 8. 趋势线检测
        trendline = self.trendline_detector.detect_trendline(df)

        # 9. 生成最终信号
        final_signal = ensemble_result['signal']
        final_confidence = ensemble_result['confidence']
        final_strength = ensemble_result['strength']

        # 计算入场、止损、止盈
        current_price = df['close'].iloc[-1]
        atr = self._calculate_atr(df)

        stop_loss = current_price - self.risk_metrics.atr_multiplier_sl * atr
        take_profit = current_price + self.risk_metrics.atr_multiplier_tp * atr

        # 计算仓位
        risk_per_trade = self.risk_metrics.max_position_size
        risk_amount = abs(current_price - stop_loss)
        position_size = risk_per_trade / risk_amount if risk_amount > 0 else 0.01

        # 生成原因
        reasons = []
        if ensemble_result['sources']['ml']['signal'] == final_signal:
            reasons.append(f"ML信号: {ml_prediction.direction if ml_prediction else 'N/A'}")
        if factor_metadata.get('signal') == final_signal:
            reasons.append(f"因子分析: {factor_score:.2f}")
        if mtf_metadata.get('trend') == final_signal:
            reasons.append(f"多时间框架: {mtf_signal}")

        return EnhancedSignal(
            symbol=symbol,
            signal_type=final_signal.upper(),
            confidence=final_confidence,
            strength=final_strength,
            sources={
                'technical': ensemble_result['sources']['technical']['value'],
                'factor': factor_score,
                'multi_tf': mtf_metadata.get('confluence', 0),
                'ml': ensemble_result['sources']['ml']['confidence'],
            },
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            position_size=min(position_size, self.risk_metrics.max_position_size),
            reason=' + '.join(reasons) if reasons else '综合信号',
            metadata={
                'factor_metadata': factor_metadata,
                'mtf_metadata': mtf_metadata,
                'ml_probabilities': {
                    'up': ml_prediction.probability_up,
                    'down': ml_prediction.probability_down,
                    'neutral': ml_prediction.probability_neutral,
                } if ml_prediction else {},
                'trendline': trendline,
                'volatility': vol_analysis if check_volatility else None,
                'time_score': self.time_filter.calculate_trade_score(symbol) if check_time else 100,
            }
        )

    def _generate_technical_signal(self, df: pd.DataFrame) -> str:
        """生成技术分析信号"""
        close = df['close']
        high = df['high']
        low = df['low']

        # 计算指标
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()

        rsi = self._calculate_rsi(close)
        macd, signal, histogram = self._calculate_macd(close)
        upper_bb, middle_bb, lower_bb = self._calculate_bollinger_bands(close)

        # 买入条件
        buy_conditions = [
            sma_20.iloc[-1] > sma_50.iloc[-1],
            ema_12.iloc[-1] > ema_26.iloc[-1],
            30 < rsi.iloc[-1] < 70,
            macd.iloc[-1] > signal.iloc[-1],
            close.iloc[-1] < upper_bb.iloc[-1],
            histogram.iloc[-1] > histogram.iloc[-2],
        ]

        # 卖出条件
        sell_conditions = [
            sma_20.iloc[-1] < sma_50.iloc[-1],
            ema_12.iloc[-1] < ema_26.iloc[-1],
            rsi.iloc[-1] > 70,
            macd.iloc[-1] < signal.iloc[-1],
            close.iloc[-1] > lower_bb.iloc[-1],
            histogram.iloc[-1] < histogram.iloc[-2],
        ]

        buy_score = sum(buy_conditions) / len(buy_conditions)
        sell_score = sum(sell_conditions) / len(sell_conditions)

        if buy_score >= 0.6:
            return 'buy'
        elif sell_score >= 0.6:
            return 'sell'
        else:
            return 'neutral'

    def optimize_params(self, df: pd.DataFrame) -> Dict:
        """优化策略参数"""
        result = self.param_optimizer.optimize_indicator_params(df)
        self.optimal_params = result['best_params']
        return result

    def rank_symbols(
        self,
        symbols_data: Dict[str, pd.DataFrame]
    ) -> List[Dict]:
        """排名交易品种"""
        ranked = self.symbol_filter.rank_symbols(symbols_data)
        self.symbol_rankings = [
            {
                'symbol': a.symbol,
                'score': a.score,
                'grade': a.grade.value,
                'reasons': a.reasons,
            }
            for a in ranked
        ]
        return self.symbol_rankings

    def get_trade_suggestions(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        existing_positions: List[str] = None
    ) -> Dict[str, List[str]]:
        """获取交易建议"""
        return self.symbol_filter.get_trade_suggestions(
            symbols_data,
            existing_positions,
            max_positions=self.risk_metrics.max_positions
        )

    # 辅助计算函数
    def _calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        """计算 RSI"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / (loss + 1e-6)
        return 100 - (100 / (1 + rs))

    def _calculate_macd(
        self,
        data: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算 MACD"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    def _calculate_bollinger_bands(
        self,
        data: pd.Series,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """计算布林带"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower

    def _calculate_atr(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> float:
        """计算 ATR"""
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.rolling(window=period).mean().iloc[-1]


class AdvancedSignalFilter:
    """高级信号过滤器"""

    def __init__(self, engine: EnhancedStrategyEngine):
        self.engine = engine
        self.min_confidence = 0.6
        self.min_strength = 0.5

    def filter_signals(
        self,
        signals: List[EnhancedSignal],
        check_risk: bool = True,
        account_info: Dict = None,
        positions: List[Dict] = None
    ) -> List[EnhancedSignal]:
        """
        过滤信号

        Args:
            signals: 信号列表
            check_risk: 是否检查风险
            account_info: 账户信息
            positions: 当前持仓

        Returns:
            过滤后的信号
        """
        filtered = []

        for signal in signals:
            # 检查置信度
            if signal.confidence < self.min_confidence:
                continue

            # 检查强度
            if signal.strength < self.min_strength:
                continue

            # 风险检查
            if check_risk and account_info and positions:
                risk_ok, risk_reason = self._check_risk(
                    signal, account_info, positions
                )
                if not risk_ok:
                    continue

            filtered.append(signal)

        # 按强度排序
        filtered.sort(key=lambda x: x.strength * x.confidence, reverse=True)

        return filtered

    def _check_risk(
        self,
        signal: EnhancedSignal,
        account_info: Dict,
        positions: List[Dict]
    ) -> Tuple[bool, str]:
        """检查风险"""
        rm = self.engine.risk_metrics

        # 检查持仓数
        if len(positions) >= rm.max_positions:
            return False, f"已达最大持仓数 {rm.max_positions}"

        # 检查日亏损
        daily_pnl = account_info.get('daily_pnl', 0)
        if daily_pnl < -rm.max_daily_loss * account_info['balance']:
            return False, f"已达日亏损限制 {rm.max_daily_loss * 100}%"

        # 检查回撤
        peak_equity = account_info.get('peak_equity', account_info['balance'])
        if peak_equity > 0:
            drawdown = (peak_equity - account_info['equity']) / peak_equity
            if drawdown > rm.max_drawdown:
                return False, f"已达最大回撤 {rm.max_drawdown * 100}%"

        return True, "OK"


# 便捷函数
def create_enhanced_engine(
    use_ml: bool = True,
    use_factor: bool = True,
    use_multi_tf: bool = True,
    risk_metrics: RiskMetrics = None
) -> EnhancedStrategyEngine:
    """创建增强版引擎"""
    return EnhancedStrategyEngine(
        risk_metrics=risk_metrics,
        use_ml=use_ml,
        use_factor_analysis=use_factor,
        use_multi_tf=use_multi_tf,
    )