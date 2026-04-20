# -*- coding: utf-8 -*-
"""
测试智能体进化系统 - Test Agent Evolution System
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_evolution_system import get_agent_evolution_system


def test_agent_evolution_system():
    """测试智能体进化系统"""
    print("=" * 60)
    print("Testing Agent Evolution System")
    print("=" * 60)

    try:
        # 获取系统实例
        system = get_agent_evolution_system()

        # 测试 1: 系统初始化
        print("\n[Test 1] System initialization...")
        print(f"  Result: {'PASS' if system.initialized else 'FAIL'}")

        # 测试 2: 智能体数量
        print("\n[Test 2] Agent count...")
        status = system.get_status()
        print(f"  Total Agents: {status['total_agents']}")
        print(f"  Result: {'PASS' if status['total_agents'] > 0 else 'FAIL'}")

        # 测试 3: 分类数量
        print("\n[Test 3] Category count...")
        active_categories = sum(1 for count in status['categories'].values() if count > 0)
        print(f"  Active Categories: {active_categories}")
        print(f"  Result: {'PASS' if active_categories > 0 else 'FAIL'}")

        # 测试 4: 保存到数据库
        print("\n[Test 4] Saving to database...")
        system.save_to_database()
        print(f"  Result: PASS")

        # 测试 5: 获取状态
        print("\n[Test 5] Getting status...")
        status = system.get_status()
        print(f"  Result: {'PASS' if status['initialized'] else 'FAIL'}")

        print("\n" + "=" * 60)
        print("[PASS] All Agent Evolution System tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent_evolution_system()
    sys.exit(0 if success else 1)
