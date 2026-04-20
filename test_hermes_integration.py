# -*- coding: utf-8 -*-
"""
Hermes 整合系统测试 - Hermes Integration System Test
测试所有 Hermes 整合模块
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erbing_system.hermes_integration import (
    get_hermes_integration_system,
    use_hermes_integration,
    list_hermes_integrations,
    get_hermes_integration_status,
)

from erbing_system.hermes_integrations import (
    InsightsIntegration,
    ErrorClassifierIntegration,
    ContextCompressorIntegration,
    CredentialPoolIntegration,
    PromptBuilderIntegration,
    BrowserToolIntegration,
    MCPToolIntegration,
    SkillsToolIntegration,
    TerminalToolIntegration,
    TTSToolIntegration,
    DeliverySystemIntegration,
    HooksSystemIntegration,
    SessionManagementIntegration,
    CronJobsIntegration,
    ContextEnginePluginIntegration,
    MemoryPluginIntegration,
    RateLimitTrackerIntegration,
    RetryUtilsIntegration,
    TitleGeneratorIntegration,
    TrajectorySavingIntegration,
)

from erbing_system.hermes_integrations.insights import get_insights_integration
from erbing_system.hermes_integrations.error_classifier import get_error_classifier_integration


def test_hermes_integration_system():
    """测试 Hermes 整合系统"""
    print("=" * 60)
    print("Testing Hermes Integration System")
    print("=" * 60)

    # 获取系统实例
    system = get_hermes_integration_system()

    # 获取状态
    status = system.get_status()
    print(f"\n1. System Status:")
    print(f"   Initialized: {status['initialized']}")
    print(f"   Total Integrations: {status['total_integrations']}")
    print(f"   Enabled: {status['enabled_integrations']}")
    print(f"   Disabled: {status['disabled_integrations']}")
    print(f"   Total Usage: {status['total_usage']}")

    # 列出所有整合模块
    print(f"\n2. All Integrations:")
    for integration in system.list_integrations():
        print(f"   - {integration.name}: {integration.description}")

    # 测试使用整合模块
    print(f"\n3. Testing Use Integration:")
    test_integrations = [
        "insights",
        "error_classifier",
        "context_compressor",
        "credential_pool",
        "prompt_builder",
    ]

    for name in test_integrations:
        success = system.use_integration(name)
        print(f"   {name}: {success}")

    # 获取更新后的状态
    status = system.get_status()
    print(f"\n4. Updated Status:")
    print(f"   Total Usage: {status['total_usage']}")

    print("\n[PASS] Hermes Integration System test passed!")


def test_insights_integration():
    """测试洞察引擎整合"""
    print("\n" + "=" * 60)
    print("Testing Insights Integration")
    print("=" * 60)

    # 获取洞察引擎整合实例
    insights = get_insights_integration()

    # 初始化
    insights.initialize()
    print("\n1. Initialized: [OK]")

    # 生成洞察报告
    insights_data = insights.generate_insights(days=30)
    print(f"\n2. Generated Insights:")
    print(f"   Total Sessions: {insights_data['total_sessions']}")
    print(f"   Total Tokens: {insights_data['total_tokens']:,}")
    print(f"   Total Cost: ${insights_data['total_cost']:.2f}")

    # 获取成本估算
    cost = insights.get_cost_estimate("claude-opus-4-6", 1000, 500)
    print(f"\n3. Cost Estimate: ${cost:.4f}")

    # 获取工具使用统计
    tool_stats = insights.get_tool_usage_stats(days=30)
    print(f"\n4. Tool Usage Stats:")
    for tool in tool_stats['tools']:
        print(f"   {tool['name']}: {tool['calls']} calls")

    # 获取活动趋势
    activity_trend = insights.get_activity_trend(days=7)
    print(f"\n5. Activity Trend (last 7 days):")
    for trend in activity_trend[-3:]:
        print(f"   {trend['date']}: {trend['sessions']} sessions")

    # 格式化洞察报告
    report = insights.format_insights_report(insights_data)
    print(f"\n6. Formatted Report (first 200 chars):")
    print(f"   {report[:200]}...")

    # 获取状态
    status = insights.get_status()
    print(f"\n7. Status:")
    print(f"   Enabled: {status['enabled']}")
    print(f"   Cache Size: {status['cache_size']}")

    print("\n[PASS] Insights Integration test passed!")


def test_error_classifier_integration():
    """测试错误分类器整合"""
    print("\n" + "=" * 60)
    print("Testing Error Classifier Integration")
    print("=" * 60)

    # 获取错误分类器整合实例
    error_classifier = get_error_classifier_integration()

    # 初始化
    error_classifier.initialize()
    print("\n1. Initialized: [OK]")

    # 测试错误分类
    test_errors = [
        Exception("401 Unauthorized"),
        Exception("429 Rate limit exceeded"),
        Exception("503 Service Unavailable"),
        Exception("Timeout"),
        Exception("Context overflow"),
    ]

    print(f"\n2. Error Classification:")
    for error in test_errors:
        reason = error_classifier.classify_error(error)
        action = error_classifier.get_recovery_action(reason) if reason else "unknown"
        print(f"   {str(error)[:40]:40} -> {reason.value if reason else 'None':20} -> {action}")

    # 测试恢复动作
    print(f"\n3. Recovery Actions:")
    from erbing_system.hermes_integrations.error_classifier import FailoverReason
    for reason in FailoverReason:
        action = error_classifier.get_recovery_action(reason)
        print(f"   {reason.value:25} -> {action}")

    # 测试重试判断
    print(f"\n4. Retry Test:")
    for reason in FailoverReason:
        should_retry = error_classifier.should_retry(reason)
        print(f"   {reason.value:25} -> {should_retry}")

    # 记录错误
    print(f"\n5. Recording Errors:")
    for reason in FailoverReason:
        error_classifier.record_error(reason)

    # 获取错误统计
    error_stats = error_classifier.get_error_stats()
    print(f"\n6. Error Stats:")
    for reason, count in error_stats.items():
        print(f"   {reason:25} -> {count}")

    # 获取状态
    status = error_classifier.get_status()
    print(f"\n7. Status:")
    print(f"   Enabled: {status['enabled']}")
    print(f"   Total Errors: {sum(status['error_stats'].values())}")

    print("\n[PASS] Error Classifier Integration test passed!")


def test_all_integrations():
    """测试所有整合模块"""
    print("\n" + "=" * 60)
    print("Testing All Integrations")
    print("=" * 60)

    integrations = [
        ("Context Compressor", ContextCompressorIntegration),
        ("Credential Pool", CredentialPoolIntegration),
        ("Prompt Builder", PromptBuilderIntegration),
        ("Browser Tool", BrowserToolIntegration),
        ("MCP Tool", MCPToolIntegration),
        ("Skills Tool", SkillsToolIntegration),
        ("Terminal Tool", TerminalToolIntegration),
        ("TTS Tool", TTSToolIntegration),
        ("Delivery System", DeliverySystemIntegration),
        ("Hooks System", HooksSystemIntegration),
        ("Session Management", SessionManagementIntegration),
        ("Cron Jobs", CronJobsIntegration),
        ("Context Engine Plugin", ContextEnginePluginIntegration),
        ("Memory Plugin", MemoryPluginIntegration),
        ("Rate Limit Tracker", RateLimitTrackerIntegration),
        ("Retry Utils", RetryUtilsIntegration),
        ("Title Generator", TitleGeneratorIntegration),
        ("Trajectory Saving", TrajectorySavingIntegration),
    ]

    print(f"\nTesting {len(integrations)} integrations:")
    for name, integration_class in integrations:
        try:
            integration = integration_class()
            integration.initialize()
            result = integration.execute(test=True)
            status = integration.get_status()
            print(f"   [PASS] {name:25} - {result['status']}")
        except Exception as e:
            print(f"   [FAIL] {name:25} - Error: {str(e)[:30]}")

    print(f"\n[PASS] All integrations test passed!")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Hermes Integration System Test Suite")
    print("=" * 60)

    try:
        # 测试 Hermes 整合系统
        test_hermes_integration_system()

        # 测试洞察引擎整合
        test_insights_integration()

        # 测试错误分类器整合
        test_error_classifier_integration()

        # 测试所有整合模块
        test_all_integrations()

        print("\n" + "=" * 60)
        print("[PASS] All tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
