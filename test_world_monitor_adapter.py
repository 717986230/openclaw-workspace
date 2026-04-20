# -*- coding: utf-8 -*-
"""
测试 WorldMonitor 适配器 - Test WorldMonitor Adapter
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erbing_system.world_monitor_adapter import (
    get_world_monitor_adapter,
    NewsItem,
    GeopoliticalEvent,
    InfrastructureStatus,
    MarketData,
    NewsCategory,
)


def test_world_monitor_adapter():
    """测试 WorldMonitor 适配器"""
    print("=" * 60)
    print("Testing WorldMonitor Adapter")
    print("=" * 60)

    try:
        # 获取适配器实例
        adapter = get_world_monitor_adapter()

        # 测试 1: 添加新闻项
        print("\n[Test 1] Adding news item...")
        news_item = NewsItem(
            id="test_news",
            title="Test News",
            summary="Test summary",
            content="Test content",
            category=NewsCategory.GENERAL,
            source="Test Source",
            url="https://example.com/test",
            published_at=datetime.now(),
        )
        success = adapter.add_news_item(news_item)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 2: 获取新闻项
        print("\n[Test 2] Getting news item...")
        retrieved_news = adapter.get_news_item("test_news")
        print(f"  Result: {'PASS' if retrieved_news is not None else 'FAIL'}")

        # 测试 3: 列出新闻项
        print("\n[Test 3] Listing news items...")
        news_items = adapter.list_news_items()
        print(f"  Result: {'PASS' if len(news_items) > 0 else 'FAIL'}")

        # 测试 4: 添加地缘政治事件
        print("\n[Test 4] Adding geopolitical event...")
        event = GeopoliticalEvent(
            id="test_event",
            title="Test Event",
            description="Test description",
            location="Test Location",
            severity=5,
            category="test",
        )
        success = adapter.add_geopolitical_event(event)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 5: 获取地缘政治事件
        print("\n[Test 5] Getting geopolitical event...")
        retrieved_event = adapter.get_geopolitical_event("test_event")
        print(f"  Result: {'PASS' if retrieved_event is not None else 'FAIL'}")

        # 测试 6: 列出地缘政治事件
        print("\n[Test 6] Listing geopolitical events...")
        events = adapter.list_geopolitical_events()
        print(f"  Result: {'PASS' if len(events) > 0 else 'FAIL'}")

        # 测试 7: 添加基础设施状态
        print("\n[Test 7] Adding infrastructure status...")
        status = InfrastructureStatus(
            id="test_status",
            name="Test Infrastructure",
            type="test",
            location="Test Location",
            status="operational",
            last_updated=datetime.now(),
        )
        success = adapter.add_infrastructure_status(status)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 8: 获取基础设施状态
        print("\n[Test 8] Getting infrastructure status...")
        retrieved_status = adapter.get_infrastructure_status("test_status")
        print(f"  Result: {'PASS' if retrieved_status is not None else 'FAIL'}")

        # 测试 9: 列出基础设施状态
        print("\n[Test 9] Listing infrastructure statuses...")
        statuses = adapter.list_infrastructure_statuses()
        print(f"  Result: {'PASS' if len(statuses) > 0 else 'FAIL'}")

        # 测试 10: 添加市场数据
        print("\n[Test 10] Adding market data...")
        market_data = MarketData(
            id="test_market",
            symbol="TEST",
            name="Test Stock",
            price=100.0,
            change=1.0,
            change_percent=1.0,
            volume=1000000,
            timestamp=datetime.now(),
        )
        success = adapter.add_market_data(market_data)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 11: 获取市场数据
        print("\n[Test 11] Getting market data...")
        retrieved_market = adapter.get_market_data("test_market")
        print(f"  Result: {'PASS' if retrieved_market is not None else 'FAIL'}")

        # 测试 12: 列出市场数据
        print("\n[Test 12] Listing market data...")
        market_data_list = adapter.list_market_data()
        print(f"  Result: {'PASS' if len(market_data_list) > 0 else 'FAIL'}")

        # 测试 13: 获取状态
        print("\n[Test 13] Getting status...")
        status_info = adapter.get_status()
        print(f"  Result: {'PASS' if status_info['initialized'] else 'FAIL'}")

        # 测试 14: 移除新闻项
        print("\n[Test 14] Removing news item...")
        success = adapter.remove_news_item("test_news")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 15: 移除地缘政治事件
        print("\n[Test 15] Removing geopolitical event...")
        success = adapter.remove_geopolitical_event("test_event")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 16: 移除基础设施状态
        print("\n[Test 16] Removing infrastructure status...")
        success = adapter.remove_infrastructure_status("test_status")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 17: 移除市场数据
        print("\n[Test 17] Removing market data...")
        success = adapter.remove_market_data("test_market")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        print("\n" + "=" * 60)
        print("[PASS] All WorldMonitor Adapter tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    from datetime import datetime
    success = test_world_monitor_adapter()
    sys.exit(0 if success else 1)
