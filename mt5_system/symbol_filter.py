"""
MT5 顶配盯盘系统 - 品种筛选模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SymbolScore(Enum):
    """品种评分"""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 70-90
    FAIR = "fair"  # 50-70
    POOR = "poor"  # 30-50
    AVOID = "avoid"  # 0-30


@dataclass
class SymbolAnalysis:
    """品种分析结果"""
    symbol: str
    score: float
    grade: SymbolScore
    liquidity_score: float
    volatility_score: float
    trend_score: float
    correlation_score: float
    session_score: float
    reasons: List[str]
    recommendations: List[str]


class SymbolFilter:
    """品种筛选器"""

    # 主要交易品种
    MAJOR_SYMBOLS = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
        'AUDUSD', 'USDCAD', 'NZDUSD',
        'EURGBP', 'EURJPY', 'GBPJPY'
    ]

    # 商品
    COMMODITIES = [
        'XAUUSD', 'XAGUSD', 'USOIL', 'UKOIL',
        'NATGAS', 'COPPER'
    ]

    # 指数
    INDICES = [
        'US30', 'US100', 'US500', 'GER40',
        'UK100', 'JPN225', 'AUS200'
    ]

    # 最佳交易时段 (UTC)
    BEST_SESSIONS = {
        'London': ('07:00', '16:00'),
        'NewYork': ('12:00', '21:00'),
        'Tokyo': ('00:00', '09:00'),
        'Sydney': ('22:00', '07:00'),
    }

    def __init__(self):
        """初始化"""
        self.min_liquidity = 1000  # 最小流动性评分
        self.min_volatility = 0.3  # 最小波动率 (ATR/价格 %)
        self.max_volatility = 5.0  # 最大波动率
        self.max_correlation = 0.7  # 最大相关性

    def analyze_symbol(
        self,
        symbol: str,
        data: pd.DataFrame,
        correlation_data: Dict[str, pd.DataFrame] = None
    ) -> SymbolAnalysis:
        """
        分析单个品种

        Args:
            symbol: 品种代码
            data: 历史数据 (需要 OHLCV)
            correlation_data: 相关品种数据字典

        Returns:
            SymbolAnalysis: 品种分析结果
        """
        if len(data) < 100:
            return SymbolAnalysis(
                symbol=symbol,
                score=0.0,
                grade=SymbolScore.AVOID,
                liquidity_score=0.0,
                volatility_score=0.0,
                trend_score=0.0,
                correlation_score=0.0,
                session_score=0.0,
                reasons=['数据不足'],
                recommendations=['跳过该品种']
            )

        reasons = []
        recommendations = []

        # 1. 流动性评分
        liquidity_score = self._calculate_liquidity_score(data, symbol)
        if liquidity_score < self.min_liquidity:
            reasons.append(f'流动性不足 ({liquidity_score:.0f})')
        else:
            reasons.append(f'流动性良好 ({liquidity_score:.0f})')

        # 2. 波动率评分
        volatility_score = self._calculate_volatility_score(data)
        if volatility_score < self.min_volatility:
            reasons.append(f'波动率过低 ({volatility_score:.2%})')
            recommendations.append('波动率不足，可能难以获利')
        elif volatility_score > self.max_volatility:
            reasons.append(f'波动率过高 ({volatility_score:.2%})')
            recommendations.append('波动率过高，风险较大')
        else:
            reasons.append(f'波动率适中 ({volatility_score:.2%})')

        # 3. 趋势评分
        trend_score = self._calculate_trend_score(data)
        if trend_score > 0.3:
            reasons.append(f'趋势向上 ({trend_score:.2%})')
        elif trend_score < -0.3:
            reasons.append(f'趋势向下 ({trend_score:.2%})')
        else:
            reasons.append(f'趋势不明 ({trend_score:.2%})')

        # 4. 相关性评分
        correlation_score = 1.0
        if correlation_data and symbol in correlation_data:
            correlation_score = self._calculate_correlation_score(
                data, correlation_data, symbol
            )
            if correlation_score > self.max_correlation:
                reasons.append(f'与其他持仓高度相关 ({correlation_score:.2f})')
                recommendations.append('考虑只交易相关性较低的品种')

        # 5. 交易时段评分
        session_score = self._calculate_session_score(symbol)

        # 综合评分
        weights = {
            'liquidity': 0.25,
            'volatility': 0.20,
            'trend': 0.20,
            'correlation': 0.15,
            'session': 0.20,
        }

        total_score = (
            liquidity_score * weights['liquidity'] +
            volatility_score * 100 * weights['volatility'] +  # 波动率转 0-100
            (trend_score + 1) * 50 * weights['trend'] +  # 趋势转 0-100
            (1 - correlation_score) * 100 * weights['correlation'] +  # 相关性转 0-100
            session_score * weights['session']
        )

        # 确定等级
        if total_score >= 90:
            grade = SymbolScore.EXCELLENT
            recommendations.append('强烈推荐交易')
        elif total_score >= 70:
            grade = SymbolScore.GOOD
            recommendations.append('推荐交易')
        elif total_score >= 50:
            grade = SymbolScore.FAIR
            recommendations.append('可以交易但需谨慎')
        elif total_score >= 30:
            grade = SymbolScore.POOR
            recommendations.append('建议避开')
        else:
            grade = SymbolScore.AVOID
            recommendations.append('不建议交易')

        return SymbolAnalysis(
            symbol=symbol,
            score=total_score,
            grade=grade,
            liquidity_score=liquidity_score,
            volatility_score=volatility_score,
            trend_score=trend_score,
            correlation_score=correlation_score,
            session_score=session_score,
            reasons=reasons,
            recommendations=recommendations
        )

    def rank_symbols(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        top_n: int = 10
    ) -> List[SymbolAnalysis]:
        """
        排名多个品种

        Args:
            symbols_data: 品种数据字典
            top_n: 返回前 N 个

        Returns:
            排序后的品种分析列表
        """
        analyses = []

        for symbol, data in symbols_data.items():
            analysis = self.analyze_symbol(symbol, data)
            analyses.append(analysis)

        # 按评分排序
        analyses.sort(key=lambda x: x.score, reverse=True)

        return analyses[:top_n]

    def filter_symbols(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        min_score: float = 50.0,
        exclude_correlated: bool = True
    ) -> List[str]:
        """
        筛选品种

        Args:
            symbols_data: 品种数据字典
            min_score: 最小评分
            exclude_correlated: 是否排除高相关品种

        Returns:
            符合条件的品种列表
        """
        # 排名所有品种
        ranked = self.rank_symbols(symbols_data)

        # 筛选
        selected = []
        selected_symbols_set = set()

        for analysis in ranked:
            # 检查评分
            if analysis.score < min_score:
                continue

            # 检查相关性
            if exclude_correlated:
                # 这里简化处理，实际应该计算真实相关性
                is_correlated = False
                for selected_sym in selected_symbols_set:
                    # 主要货币对相关性检查
                    if self._are_correlated(analysis.symbol, selected_sym):
                        is_correlated = True
                        break

                if is_correlated:
                    continue

            selected.append(analysis.symbol)
            selected_symbols_set.add(analysis.symbol)

        return selected

    def _calculate_liquidity_score(
        self,
        data: pd.DataFrame,
        symbol: str
    ) -> float:
        """
        计算流动性评分 (0-100)

        基于:
        - 成交量
        - 点差
        - 持仓量
        """
        if 'volume' not in data.columns:
            return 75.0  # 默认中等流动性

        # 最近 20 根 K 线的平均成交量
        avg_volume = data['volume'].tail(20).mean()
        current_volume = data['volume'].iloc[-1]

        # 成交量稳定性
        volume_std = data['volume'].tail(20).std()
        volume_cv = volume_std / (avg_volume + 1e-6)

        # 评分
        volume_score = min(current_volume / avg_volume * 50, 50)
        stability_score = max(50 - volume_cv * 25, 0)

        return volume_score + stability_score

    def _calculate_volatility_score(
        self,
        data: pd.DataFrame
    ) -> float:
        """
        计算波动率评分

        返回 ATR/价格 的百分比
        """
        high = data['high']
        low = data['low']
        close = data['close']

        # 计算 ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()

        # 波动率
        current_price = close.iloc[-1]
        volatility = atr.iloc[-1] / current_price

        return volatility if not pd.isna(volatility) else 0.0

    def _calculate_trend_score(
        self,
        data: pd.DataFrame
    ) -> float:
        """
        计算趋势评分

        返回 -1 到 1 的值
        - 正数表示向上趋势
        - 负数表示向下趋势
        """
        close = data['close']

        # 多条均线
        ma_20 = close.rolling(20).mean()
        ma_50 = close.rolling(50).mean()
        ma_200 = close.rolling(200).mean()

        current_price = close.iloc[-1]

        # 计算趋势
        trend = 0.0
        count = 0

        if len(ma_20) > 0 and not pd.isna(ma_20.iloc[-1]):
            if current_price > ma_20.iloc[-1]:
                trend += 0.3
            else:
                trend -= 0.3
            count += 1

        if len(ma_50) > 0 and not pd.isna(ma_50.iloc[-1]):
            if current_price > ma_50.iloc[-1]:
                trend += 0.3
            else:
                trend -= 0.3
            count += 1

        if len(ma_200) > 0 and not pd.isna(ma_200.iloc[-1]):
            if current_price > ma_200.iloc[-1]:
                trend += 0.4
            else:
                trend -= 0.4
            count += 1

        return trend / count if count > 0 else 0.0

    def _calculate_correlation_score(
        self,
        data: pd.DataFrame,
        correlation_data: Dict[str, pd.DataFrame],
        symbol: str
    ) -> float:
        """计算与其他持仓的平均相关性"""
        if symbol not in correlation_data:
            return 0.0

        correlations = []
        symbol_returns = data['close'].pct_change().tail(50)

        for other_symbol, other_data in correlation_data.items():
            if other_symbol == symbol:
                continue

            other_returns = other_data['close'].pct_change().tail(50)

            if len(symbol_returns) == len(other_returns):
                corr = symbol_returns.corr(other_returns)
                if not pd.isna(corr):
                    correlations.append(abs(corr))

        return np.mean(correlations) if correlations else 0.0

    def _calculate_session_score(self, symbol: str) -> float:
        """
        计算交易时段评分

        基于当前时间是否在最佳交易时段
        """
        from datetime import datetime, time

        # 获取当前 UTC 时间
        now = datetime.utcnow().time()

        # 确定品种的交易时段
        if any(s in symbol for s in ['EUR', 'GBP', 'CHF']):
            # 欧洲货币对 - 伦敦时段最佳
            london_start = time(7, 0)
            london_end = time(16, 0)
            if london_start <= now <= london_end:
                return 100.0
            elif now >= time(5, 0) and now <= time(20, 0):
                return 70.0
            else:
                return 30.0

        elif 'JPY' in symbol:
            # 日元对 - 东京时段最佳
            tokyo_start = time(0, 0)
            tokyo_end = time(9, 0)
            if tokyo_start <= now <= tokyo_end:
                return 100.0
            elif now >= time(22, 0) or now <= time(12, 0):
                return 70.0
            else:
                return 30.0

        elif 'USD' in symbol:
            # 美元对 - 纽约时段最佳
            ny_start = time(12, 0)
            ny_end = time(21, 0)
            if ny_start <= now <= ny_end:
                return 100.0
            elif now >= time(10, 0) and now <= time(23, 0):
                return 70.0
            else:
                return 30.0

        elif symbol in ['XAUUSD', 'XAGUSD']:
            # 黄金白银 - 24 小时可交易
            return 80.0

        else:
            return 50.0  # 默认中等

    def _are_correlated(self, symbol1: str, symbol2: str) -> bool:
        """快速检查两个品种是否高度相关"""
        # 主要货币对
        major_currencies = ['EUR', 'GBP', 'USD', 'JPY', 'AUD', 'CAD', 'NZD', 'CHF']

        # 提取货币
        curr1 = []
        curr2 = []
        for curr in major_currencies:
            if curr in symbol1:
                curr1.append(curr)
            if curr in symbol2:
                curr2.append(curr)

        # 检查共同货币
        common = set(curr1) & set(curr2)
        if common:
            return True

        # 黄金白银
        if ('XAU' in symbol1 or 'XAG' in symbol1) and \
           ('XAU' in symbol2 or 'XAG' in symbol2):
            return True

        # 原油
        if ('OIL' in symbol1 or 'NATGAS' in symbol1) and \
           ('OIL' in symbol2 or 'NATGAS' in symbol2):
            return True

        return False

    def get_trade_suggestions(
        self,
        symbols_data: Dict[str, pd.DataFrame],
        existing_positions: List[str] = None,
        max_positions: int = 5
    ) -> Dict[str, List[str]]:
        """
        获取交易建议

        Args:
            symbols_data: 品种数据
            existing_positions: 已有持仓
            max_positions: 最大持仓数

        Returns:
            {
                'buy': ['EURUSD', ...],
                'sell': ['GBPJPY', ...],
                'avoid': ['NATGAS', ...]
            }
        """
        if existing_positions is None:
            existing_positions = []

        # 排名品种
        ranked = self.rank_symbols(symbols_data)

        suggestions = {
            'buy': [],
            'sell': [],
            'avoid': []
        }

        for analysis in ranked:
            if analysis.score < 30:
                suggestions['avoid'].append(analysis.symbol)
                continue

            # 检查是否已持仓
            if analysis.symbol in existing_positions:
                continue

            # 检查持仓数量
            if len(suggestions['buy']) + len(existing_positions) >= max_positions:
                break

            if analysis.trend_score > 0.2:
                suggestions['buy'].append(analysis.symbol)
            elif analysis.trend_score < -0.2:
                suggestions['sell'].append(analysis.symbol)

        # 添加应避开的品种
        for analysis in ranked:
            if analysis.score < 30:
                suggestions['avoid'].append(analysis.symbol)

        return suggestions