# -*- coding: utf-8 -*-
"""
WorldMonitor 整合适配器 - WorldMonitor Integration Adapter
将 WorldMonitor 的核心功能整合到二饼系统中
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class NewsCategory(Enum):
    """新闻类别"""
    GENERAL = "general"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    POLITICS = "politics"
    MILITARY = "military"
    ECONOMY = "economy"
    DISASTER = "disaster"
    SCIENCE = "science"
    SPORTS = "sports"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    ENVIRONMENT = "environment"
    ENERGY = "energy"
    TRANSPORTATION = "transportation"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class NewsItem:
    """新闻项"""
    id: str
    title: str
    summary: str
    content: str
    category: NewsCategory
    source: str
    url: str
    published_at: datetime
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GeopoliticalEvent:
    """地缘政治事件"""
    id: str
    title: str
    description: str
    location: str
    severity: int  # 1-10
    category: str
    related_countries: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class InfrastructureStatus:
    """基础设施状态"""
    id: str
    name: str
    type: str
    location: str
    status: str
    last_updated: datetime
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MarketData:
    """市场数据"""
    id: str
    symbol: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: float
    timestamp: datetime
    created_at: datetime = field(default_factory=datetime.now)


class WorldMonitorAdapter:
    """WorldMonitor 适配器"""

    def __init__(self):
        self.news_items: Dict[str, NewsItem] = {}
        self.geopolitical_events: Dict[str, GeopoliticalEvent] = {}
        self.infrastructure_statuses: Dict[str, InfrastructureStatus] = {}
        self.market_data: Dict[str, MarketData] = {}
        self.initialized = False

    def initialize(self):
        """初始化适配器"""
        logger.info("Initializing WorldMonitor Adapter...")

        # 添加示例数据
        self._add_sample_data()

        self.initialized = True
        logger.info("WorldMonitor Adapter initialized successfully")

    def _add_sample_data(self):
        """添加示例数据"""
        # 添加示例新闻
        self.add_news_item(
            NewsItem(
                id="news_1",
                title="AI Technology Breakthrough",
                summary="New AI technology achieves significant breakthrough",
                content="Detailed content about the AI breakthrough...",
                category=NewsCategory.TECHNOLOGY,
                source="Tech News",
                url="https://example.com/news/1",
                published_at=datetime.now(),
            )
        )

        # 添加示例地缘政治事件
        self.add_geopolitical_event(
            GeopoliticalEvent(
                id="event_1",
                title="International Summit",
                description="Major international summit held",
                location="Geneva",
                severity=5,
                category="diplomatic",
                related_countries=["USA", "China", "EU"],
            )
        )

        # 添加示例基础设施状态
        self.add_infrastructure_status(
            InfrastructureStatus(
                id="infra_1",
                name="Power Grid",
                type="energy",
                location="New York",
                status="operational",
                last_updated=datetime.now(),
            )
        )

        # 添加示例市场数据
        self.add_market_data(
            MarketData(
                id="market_1",
                symbol="AAPL",
                name="Apple Inc.",
                price=150.0,
                change=2.5,
                change_percent=1.7,
                volume=1000000,
                timestamp=datetime.now(),
            )
        )

    def add_news_item(self, news_item: NewsItem) -> bool:
        """添加新闻项"""
        if news_item.id in self.news_items:
            logger.warning(f"News item '{news_item.id}' already exists")
            return False

        self.news_items[news_item.id] = news_item
        logger.info(f"News item '{news_item.id}' added successfully")
        return True

    def get_news_item(self, news_id: str) -> Optional[NewsItem]:
        """获取新闻项"""
        return self.news_items.get(news_id)

    def list_news_items(self, category: Optional[NewsCategory] = None) -> List[NewsItem]:
        """列出新闻项"""
        if category:
            return [item for item in self.news_items.values() if item.category == category]
        return list(self.news_items.values())

    def remove_news_item(self, news_id: str) -> bool:
        """移除新闻项"""
        if news_id not in self.news_items:
            logger.warning(f"News item '{news_id}' not found")
            return False

        del self.news_items[news_id]
        logger.info(f"News item '{news_id}' removed successfully")
        return True

    def add_geopolitical_event(self, event: GeopoliticalEvent) -> bool:
        """添加地缘政治事件"""
        if event.id in self.geopolitical_events:
            logger.warning(f"Geopolitical event '{event.id}' already exists")
            return False

        self.geopolitical_events[event.id] = event
        logger.info(f"Geopolitical event '{event.id}' added successfully")
        return True

    def get_geopolitical_event(self, event_id: str) -> Optional[GeopoliticalEvent]:
        """获取地缘政治事件"""
        return self.geopolitical_events.get(event_id)

    def list_geopolitical_events(self, severity: Optional[int] = None) -> List[GeopoliticalEvent]:
        """列出地缘政治事件"""
        if severity:
            return [event for event in self.geopolitical_events.values() if event.severity >= severity]
        return list(self.geopolitical_events.values())

    def remove_geopolitical_event(self, event_id: str) -> bool:
        """移除地缘政治事件"""
        if event_id not in self.geopolitical_events:
            logger.warning(f"Geopolitical event '{event_id}' not found")
            return False

        del self.geopolitical_events[event_id]
        logger.info(f"Geopolitical event '{event_id}' removed successfully")
        return True

    def add_infrastructure_status(self, status: InfrastructureStatus) -> bool:
        """添加基础设施状态"""
        if status.id in self.infrastructure_statuses:
            logger.warning(f"Infrastructure status '{status.id}' already exists")
            return False

        self.infrastructure_statuses[status.id] = status
        logger.info(f"Infrastructure status '{status.id}' added successfully")
        return True

    def get_infrastructure_status(self, status_id: str) -> Optional[InfrastructureStatus]:
        """获取基础设施状态"""
        return self.infrastructure_statuses.get(status_id)

    def list_infrastructure_statuses(self, status_type: Optional[str] = None) -> List[InfrastructureStatus]:
        """列出基础设施状态"""
        if status_type:
            return [s for s in self.infrastructure_statuses.values() if s.type == status_type]
        return list(self.infrastructure_statuses.values())

    def remove_infrastructure_status(self, status_id: str) -> bool:
        """移除基础设施状态"""
        if status_id not in self.infrastructure_statuses:
            logger.warning(f"Infrastructure status '{status_id}' not found")
            return False

        del self.infrastructure_statuses[status_id]
        logger.info(f"Infrastructure status '{status_id}' removed successfully")
        return True

    def add_market_data(self, data: MarketData) -> bool:
        """添加市场数据"""
        if data.id in self.market_data:
            logger.warning(f"Market data '{data.id}' already exists")
            return False

        self.market_data[data.id] = data
        logger.info(f"Market data '{data.id}' added successfully")
        return True

    def get_market_data(self, data_id: str) -> Optional[MarketData]:
        """获取市场数据"""
        return self.market_data.get(data_id)

    def list_market_data(self, symbol: Optional[str] = None) -> List[MarketData]:
        """列出市场数据"""
        if symbol:
            return [data for data in self.market_data.values() if data.symbol == symbol]
        return list(self.market_data.values())

    def remove_market_data(self, data_id: str) -> bool:
        """移除市场数据"""
        if data_id not in self.market_data:
            logger.warning(f"Market data '{data_id}' not found")
            return False

        del self.market_data[data_id]
        logger.info(f"Market data '{data_id}' removed successfully")
        return True

    def get_status(self) -> Dict[str, Any]:
        """获取适配器状态"""
        return {
            "initialized": self.initialized,
            "total_news_items": len(self.news_items),
            "total_geopolitical_events": len(self.geopolitical_events),
            "total_infrastructure_statuses": len(self.infrastructure_statuses),
            "total_market_data": len(self.market_data),
            "news_items": {
                item_id: {
                    "title": item.title,
                    "summary": item.summary,
                    "category": item.category.value,
                    "source": item.source,
                    "published_at": item.published_at.isoformat(),
                }
                for item_id, item in self.news_items.items()
            },
            "geopolitical_events": {
                event_id: {
                    "title": event.title,
                    "description": event.description,
                    "location": event.location,
                    "severity": event.severity,
                    "category": event.category,
                    "related_countries": event.related_countries,
                }
                for event_id, event in self.geopolitical_events.items()
            },
            "infrastructure_statuses": {
                status_id: {
                    "name": status.name,
                    "type": status.type,
                    "location": status.location,
                    "status": status.status,
                    "last_updated": status.last_updated.isoformat(),
                }
                for status_id, status in self.infrastructure_statuses.items()
            },
            "market_data": {
                data_id: {
                    "symbol": data.symbol,
                    "name": data.name,
                    "price": data.price,
                    "change": data.change,
                    "change_percent": data.change_percent,
                    "volume": data.volume,
                    "timestamp": data.timestamp.isoformat(),
                }
                for data_id, data in self.market_data.items()
            },
        }


# 全局实例
_world_monitor_adapter = None


def get_world_monitor_adapter() -> WorldMonitorAdapter:
    """获取 WorldMonitor 适配器实例"""
    global _world_monitor_adapter
    if _world_monitor_adapter is None:
        _world_monitor_adapter = WorldMonitorAdapter()
        _world_monitor_adapter.initialize()
    return _world_monitor_adapter


if __name__ == "__main__":
    # 测试 WorldMonitor 适配器
    print("Testing WorldMonitor Adapter...")

    # 获取适配器实例
    adapter = get_world_monitor_adapter()

    # 获取状态
    status = adapter.get_status()
    print(f"\nWorldMonitor Adapter Status:")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total News Items: {status['total_news_items']}")
    print(f"  Total Geopolitical Events: {status['total_geopolitical_events']}")
    print(f"  Total Infrastructure Statuses: {status['total_infrastructure_statuses']}")
    print(f"  Total Market Data: {status['total_market_data']}")

    print("\nWorldMonitor Adapter tested successfully!")
