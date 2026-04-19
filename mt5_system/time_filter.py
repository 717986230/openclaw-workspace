"""
MT5 顶配盯盘系统 - 时间过滤和波动率过滤模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


# 重大财经事件日历 (简化版)
HIGH_IMPACT_EVENTS = [
    'NFP', 'FOMC', 'ECB', 'BOE', 'BOJ',  # 央行决议
    'CPI', 'GDP', 'PMI',  # 经济数据
    'Election', 'Trade War',  # 地缘政治
]

# 交易时段
TRADE_SESSIONS = {
    'Sydney': {'start': time(22, 0), 'end': time(7, 0), 'timezone': 'UTC+10'},
    'Tokyo': {'start': time(0, 0), 'end': time(9, 0), 'timezone': 'UTC+9'},
    'London': {'start': time(7, 0), 'end': time(16, 0), 'timezone': 'UTC+1'},
    'NewYork': {'start': time(12, 0), 'end': time(21, 0), 'timezone': 'UTC-5'},
}


class TimeFilter:
    """时间过滤器 - 避开重大新闻和低流动性时段"""

    def __init__(self):
        self.enabled = True
        self.news_window_minutes = 30  # 新闻前后窗口期（分钟）

    def is_trade_allowed(
        self,
        symbol: str,
        current_time: datetime = None
    ) -> Tuple[bool, str]:
        """
        检查是否允许交易

        Returns:
            (允许交易, 原因)
        """
        if current_time is None:
            current_time = datetime.utcnow()

        now = current_time.time()

        # 检查交易时段
        in_session, session_name = self._is_in_trade_session(symbol, now)
        if not in_session:
            return False, f"不在交易时段 ({session_name})"

        # 检查是否是低流动性时段
        if self._is_low_liquidity_period(now):
            return False, "低流动性时段 (午休/隔夜)"

        # 检查是否有重大新闻
        has_news, news_info = self._check_news_events(current_time)
        if has_news:
            return False, f"临近重大新闻: {news_info}"

        return True, "允许交易"

    def _is_in_trade_session(self, symbol: str, now: time) -> Tuple[bool, str]:
        """检查是否在交易时段"""
        # 主要货币对
        if 'EUR' in symbol or 'GBP' in symbol or 'CHF' in symbol:
            # 伦敦时段 7:00-16:00 UTC
            if time(7, 0) <= now <= time(16, 0):
                return True, 'London'
            return False, 'London'

        elif 'JPY' in symbol:
            # 东京时段 0:00-9:00 UTC
            if time(0, 0) <= now <= time(9, 0):
                return True, 'Tokyo'
            return False, 'Tokyo'

        elif 'USD' in symbol or 'CAD' in symbol or 'AUD' in symbol or 'NZD' in symbol:
            # 纽约时段 12:00-21:00 UTC
            if time(12, 0) <= now <= time(21, 0):
                return True, 'NewYork'
            return False, 'NewYork'

        elif 'XAU' in symbol or 'XAG' in symbol:
            # 黄金白银 24 小时可交易，但伦敦和纽约时段最佳
            if time(7, 0) <= now <= time(21, 0):
                return True, 'London/NY'
            return False, 'London/NY'

        return True, 'Unknown'

    def _is_low_liquidity_period(self, now: time) -> bool:
        """检查低流动性时段"""
        # 午休时段 (12:00-13:00 UTC) - 亚洲午休
        if time(12, 0) <= now <= time(13, 0):
            return True

        # 隔夜时段 (21:00-22:00 UTC) - 纽约尾盘/亚太开盘
        if time(21, 0) <= now <= time(22, 0):
            return True

        # 周末前 30 分钟
        # (假设周五 21:30 后为周末)

        return False

    def _check_news_events(
        self,
        current_time: datetime
    ) -> Tuple[bool, str]:
        """检查重大财经事件"""
        # 这是一个简化版本，实际应该接入财经日历 API
        # 例如: Investing.com, Forex Factory, etc.

        # 假设每周五 13:30 UTC 发布非农数据 (美国)
        if current_time.weekday() == 4:  # 周五
            if time(13, 0) <= current_time.time() <= time(15, 0):
                return True, "非农数据"

        # 每月第二周周三 19:00 UTC FOMC 会议
        if current_time.day >= 8 and current_time.day <= 14:
            if current_time.weekday() == 2:  # 周三
                if time(18, 30) <= current_time.time() <= time(20, 0):
                    return True, "FOMC 会议"

        return False, ""

    def get_next_event_time(
        self,
        current_time: datetime = None
    ) -> Optional[datetime]:
        """获取下次重大事件时间"""
        if current_time is None:
            current_time = datetime.utcnow()

        # 简化: 返回下次非农时间 (每月第一个周五 13:30 UTC)
        # 实际应该计算正确的日期
        days_until_friday = (4 - current_time.weekday()) % 7
        if days_until_friday == 0 and current_time.time() > time(13, 30):
            days_until_friday = 7

        next_friday = current_time.replace(
            hour=13, minute=30, second=0, microsecond=0
        ) + pd.Timedelta(days=days_until_friday)

        return next_friday

    def calculate_trade_score(
        self,
        symbol: str,
        current_time: datetime = None
    ) -> float:
        """
        计算交易时段评分 (0-100)

        基于:
        - 流动性
        - 波动性
        - 趋势稳定性
        """
        if current_time is None:
            current_time = datetime.utcnow()

        now = current_time.time()
        score = 50.0

        # 时段评分
        if 'EUR' in symbol or 'GBP' in symbol:
            if time(7, 0) <= now <= time(10, 0):
                score = 95.0  # 伦敦开盘
            elif time(10, 0) <= now <= time(16, 0):
                score = 85.0  # 伦敦时段
            elif time(12, 0) <= now <= time(14, 0):
                score = 60.0  # 欧美重叠

        elif 'JPY' in symbol:
            if time(0, 0) <= now <= time(3, 0):
                score = 90.0  # 东京开盘
            elif time(3, 0) <= now <= time(9, 0):
                score = 80.0  # 东京时段

        elif 'USD' in symbol:
            if time(12, 0) <= now <= time(15, 0):
                score = 95.0  # 纽约开盘
            elif time(15, 0) <= now <= time(17, 0):
                score = 85.0  # 纽约时段
            elif time(17, 0) <= now <= time(21, 0):
                score = 70.0  # 纽约尾盘

        elif 'XAU' in symbol or 'XAG' in symbol:
            if time(7, 0) <= now <= time(16, 0):
                score = 90.0  # 伦敦时段最佳
            elif time(12, 0) <= now <= time(21, 0):
                score = 85.0  # 纽约时段
            elif time(21, 0) <= now <= time(22, 0):
                score = 50.0  # 隔夜

        return score


class VolatilityFilter:
    """波动率过滤器"""

    def __init__(self):
        self.min_volatility = 0.0005  # 最小波动率 (ATR/价格)
        self.max_volatility = 0.03    # 最大波动率

    def analyze_volatility(
        self,
        df: pd.DataFrame,
        lookback: int = 20
    ) -> Dict[str, any]:
        """
        分析波动率状态

        Returns:
            {
                'current': float,  # 当前波动率
                'average': float,  # 平均波动率
                'ratio': float,    # 当前/平均
                'state': str,      # 'low', 'normal', 'high', 'extreme'
                'recommendation': str,
            }
        """
        atr = self._calculate_atr(df)
        current_price = df['close'].iloc[-1]

        current_vol = atr.iloc[-1] / current_price
        avg_vol = atr.tail(lookback).mean() / current_price

        ratio = current_vol / (avg_vol + 1e-6)

        # 判断状态
        if ratio < 0.5:
            state = 'low'
            recommendation = '波动率过低，建议等待或缩小仓位'
        elif ratio < 0.8:
            state = 'normal_low'
            recommendation = '波动率偏低，可以考虑突破策略'
        elif ratio < 1.2:
            state = 'normal'
            recommendation = '波动率正常，适合所有策略'
        elif ratio < 2.0:
            state = 'high'
            recommendation = '波动率偏高，谨慎加仓'
        else:
            state = 'extreme'
            recommendation = '波动率极端，考虑减仓或观望'

        return {
            'current': current_vol,
            'average': avg_vol,
            'ratio': ratio,
            'state': state,
            'recommendation': recommendation,
        }

    def should_trade(
        self,
        df: pd.DataFrame,
        strategy_type: str = 'trend'
    ) -> Tuple[bool, str]:
        """
        判断是否应该交易

        Args:
            df: 价格数据
            strategy_type: 'trend', 'range', 'breakout'
        """
        vol_analysis = self.analyze_volatility(df)

        current_vol = vol_analysis['current']
        state = vol_analysis['state']

        # 基于策略类型判断
        if strategy_type == 'trend':
            if state in ['low', 'extreme']:
                return False, f"趋势策略不适合: {vol_analysis['recommendation']}"
            return True, "波动率适合趋势策略"

        elif strategy_type == 'range':
            if state in ['high', 'extreme']:
                return False, f"区间策略不适合: {vol_analysis['recommendation']}"
            return True, "波动率适合区间策略"

        elif strategy_type == 'breakout':
            if state in ['low', 'normal_low']:
                return False, f"突破策略需要更高波动率: {vol_analysis['recommendation']}"
            return True, "波动率适合突破策略"

        return True, "允许交易"

    def calculate_position_size_adjustment(
        self,
        df: pd.DataFrame,
        base_size: float
    ) -> float:
        """
        根据波动率调整仓位大小

        波动率高时减少仓位，波动率低时增加仓位
        """
        vol_analysis = self.analyze_volatility(df)
        ratio = vol_analysis['ratio']

        # 波动率高时减少仓位
        if ratio > 1.5:
            adjustment = 0.5
        elif ratio > 1.2:
            adjustment = 0.75
        elif ratio < 0.5:
            adjustment = 1.5  # 低波动时可以增大仓位
        elif ratio < 0.8:
            adjustment = 1.25
        else:
            adjustment = 1.0

        return base_size * adjustment

    def _calculate_atr(
        self,
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """计算 ATR"""
        high = df['high']
        low = df['low']
        close = df['close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        return tr.rolling(window=period).mean()

    def detect_volatility_regime(
        self,
        df: pd.DataFrame,
        window: int = 100
    ) -> Dict[str, any]:
        """
        检测波动率制度

        使用 HMM (隐马尔可夫模型) 的简化版本
        实际应该使用真正的 HMM 或 GARCH 模型
        """
        returns = df['close'].pct_change().dropna()

        if len(returns) < window:
            return {'regime': 'unknown', 'probability': 0.0}

        recent_returns = returns.tail(window)

        # 计算统计量
        mean = recent_returns.mean()
        std = recent_returns.std()
        skewness = recent_returns.skew()
        kurtosis = recent_returns.kurtosis()

        # 简单分类
        if std > 0.02:  # 高波动
            regime = 'high_volatility'
            probability = min(std / 0.05, 1.0)
        elif std < 0.005:  # 低波动
            regime = 'low_volatility'
            probability = min(0.01 / std, 1.0) if std > 0 else 0.5
        else:
            regime = 'normal_volatility'
            probability = 0.7

        return {
            'regime': regime,
            'probability': probability,
            'mean': mean,
            'std': std,
            'skewness': skewness,
            'kurtosis': kurtosis,
        }