# -*- coding: utf-8 -*-
"""
洞察引擎整合 - Insights Integration
将 Hermes Agent 的洞察引擎整合到二饼系统中
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class InsightsIntegration:
    """洞察引擎整合"""

    def __init__(self):
        self.enabled = True
        self.db_path = None
        self.cache = {}
        self.cache_ttl = 3600  # 1小时缓存

    def initialize(self, db_path: str = None):
        """初始化洞察引擎"""
        self.db_path = db_path
        logger.info("Insights Integration initialized")

    def generate_insights(self, days: int = 30) -> Dict[str, Any]:
        """生成洞察报告"""
        logger.info(f"Generating insights for last {days} days")

        # 模拟洞察数据
        insights = {
            "period_days": days,
            "total_sessions": 150,
            "total_tokens": 500000,
            "total_cost": 25.50,
            "avg_tokens_per_session": 3333,
            "top_models": [
                {"model": "claude-opus-4-6", "usage": 60},
                {"model": "gemini-2-5-flash", "usage": 30},
                {"model": "gpt-4-turbo", "usage": 10},
            ],
            "top_tools": [
                {"tool": "terminal", "usage": 80},
                {"tool": "browser", "usage": 50},
                {"tool": "file_operations", "usage": 40},
            ],
            "activity_trend": [
                {"date": "2026-04-01", "sessions": 10},
                {"date": "2026-04-02", "sessions": 15},
                {"date": "2026-04-03", "sessions": 12},
            ],
        }

        return insights

    def get_cost_estimate(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """获取成本估算"""
        # 简化的成本估算
        pricing = {
            "claude-opus-4-6": {"input": 0.000015, "output": 0.000075},
            "gemini-2-5-flash": {"input": 0.000001, "output": 0.000004},
            "gpt-4-turbo": {"input": 0.00001, "output": 0.00003},
        }

        if model not in pricing:
            return 0.0

        model_pricing = pricing[model]
        cost = (input_tokens * model_pricing["input"] + output_tokens * model_pricing["output"])
        return cost

    def get_tool_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """获取工具使用统计"""
        logger.info(f"Getting tool usage stats for last {days} days")

        stats = {
            "period_days": days,
            "total_tool_calls": 500,
            "tools": [
                {"name": "terminal", "calls": 200, "success_rate": 0.95},
                {"name": "browser", "calls": 150, "success_rate": 0.90},
                {"name": "file_operations", "calls": 100, "success_rate": 0.98},
                {"name": "mcp", "calls": 50, "success_rate": 0.85},
            ],
        }

        return stats

    def get_activity_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取活动趋势"""
        logger.info(f"Getting activity trend for last {days} days")

        trend = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
            trend.append({
                "date": date,
                "sessions": 10 + (i % 5),
                "tokens": 3000 + (i % 10) * 100,
            })

        return trend

    def format_insights_report(self, insights: Dict[str, Any]) -> str:
        """格式化洞察报告"""
        report = f"""
# 洞察报告

## 概览
- 统计周期: {insights['period_days']} 天
- 总会话数: {insights['total_sessions']}
- 总 Token 数: {insights['total_tokens']:,}
- 总成本: ${insights['total_cost']:.2f}
- 平均每会话 Token: {insights['avg_tokens_per_session']:,}

## 热门模型
"""
        for model in insights['top_models']:
            report += f"- {model['model']}: {model['usage']}%\n"

        report += "\n## 热门工具\n"
        for tool in insights['top_tools']:
            report += f"- {tool['tool']}: {tool['usage']} 次使用\n"

        report += "\n## 活动趋势\n"
        for trend in insights['activity_trend']:
            report += f"- {trend['date']}: {trend['sessions']} 会话\n"

        return report

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        return {
            "enabled": self.enabled,
            "db_path": self.db_path,
            "cache_size": len(self.cache),
        }


# 全局实例
_insights_integration = None


def get_insights_integration() -> InsightsIntegration:
    """获取洞察引擎整合实例"""
    global _insights_integration
    if _insights_integration is None:
        _insights_integration = InsightsIntegration()
    return _insights_integration
