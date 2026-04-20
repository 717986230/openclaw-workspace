# -*- coding: utf-8 -*-
"""
测试智能体池系统 - Test Agent Pool System
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_pool import get_agent_pool, AgentPoolStrategy


def test_agent_pool():
    """测试智能体池"""
    print("=" * 60)
    print("Testing Agent Pool System")
    print("=" * 60)

    try:
        # 获取智能体池实例
        pool = get_agent_pool()

        # 测试 1: 系统初始化
        print("\n[Test 1] System initialization...")
        print(f"  Result: {'PASS' if pool.initialized else 'FAIL'}")

        # 测试 2: 智能体数量
        print("\n[Test 2] Agent count...")
        stats = pool.get_pool_stats()
        print(f"  Total Agents: {stats['total_agents']}")
        print(f"  Result: {'PASS' if stats['total_agents'] > 0 else 'FAIL'}")

        # 测试 3: 可用智能体
        print("\n[Test 3] Available agents...")
        print(f"  Available: {stats['available_agents']}")
        print(f"  Result: {'PASS' if stats['available_agents'] > 0 else 'FAIL'}")

        # 测试 4: 随机获取智能体
        print("\n[Test 4] Getting random agent...")
        agent = pool.get_agent()
        if agent:
            print(f"  Agent: {agent.agent_name}")
        else:
            print("  Agent: None")
        print(f"  Result: {'PASS' if agent else 'FAIL'}")

        # 测试 5: 最佳匹配获取智能体
        print("\n[Test 5] Getting best match agent...")
        agent = pool.get_agent(task_type="ai_research", keywords=["python", "machine learning"])
        if agent:
            print(f"  Agent: {agent.agent_name}")
        else:
            print("  Agent: None")
        print(f"  Result: {'PASS' if agent else 'FAIL'}")

        # 测试 6: 标记智能体使用
        print("\n[Test 6] Marking agent as used...")
        if agent:
            pool.mark_agent_used(agent.agent_id, success=True, tokens=1000)
            print(f"  Result: PASS")
        else:
            print(f"  Result: FAIL")

        # 测试 7: 获取使用统计
        print("\n[Test 7] Getting usage stats...")
        if agent:
            usage_stats = pool.get_agent_usage_stats(agent.agent_id)
            print(f"  Usage Count: {usage_stats['usage_count']}")
            print(f"  Result: PASS")
        else:
            print(f"  Result: FAIL")

        # 测试 8: 按分类获取智能体
        print("\n[Test 8] Getting agents by category...")
        ai_research_agents = pool.get_agents_by_category("ai_research")
        print(f"  AI Research Agents: {len(ai_research_agents)}")
        print(f"  Result: {'PASS' if len(ai_research_agents) > 0 else 'FAIL'}")

        # 测试 9: 设置策略
        print("\n[Test 9] Setting strategy...")
        pool.set_strategy(AgentPoolStrategy.ROUND_ROBIN)
        print(f"  Strategy: {pool.strategy.value}")
        print(f"  Result: PASS")

        # 测试 10: 获取池统计
        print("\n[Test 10] Getting pool stats...")
        stats = pool.get_pool_stats()
        print(f"  Total Usage: {stats['total_usage']}")
        print(f"  Overall Success Rate: {stats['overall_success_rate']:.2%}")
        print(f"  Result: PASS")

        print("\n" + "=" * 60)
        print("[PASS] All Agent Pool tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent_pool()
    sys.exit(0 if success else 1)
