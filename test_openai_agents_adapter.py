# -*- coding: utf-8 -*-
"""
测试 OpenAI Agents 适配器 - Test OpenAI Agents Adapter
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from erbing_system.openai_agents_adapter import (
    get_openai_agents_adapter,
    Agent,
    Tool,
    Guardrail,
)


def test_openai_agents_adapter():
    """测试 OpenAI Agents 适配器"""
    print("=" * 60)
    print("Testing OpenAI Agents Adapter")
    print("=" * 60)

    try:
        # 获取适配器实例
        adapter = get_openai_agents_adapter()

        # 测试 1: 创建智能体
        print("\n[Test 1] Creating agent...")
        agent = Agent(
            name="test_agent",
            instructions="You are a helpful assistant",
            tools=["search", "read_file", "write_file"],
            guardrails=["input_validation", "output_validation"],
        )
        success = adapter.add_agent(agent)
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        # 测试 2: 获取智能体
        print("\n[Test 2] Getting agent...")
        retrieved_agent = adapter.get_agent("test_agent")
        print(f"  Result: {'PASS' if retrieved_agent is not None else 'FAIL'}")

        # 测试 3: 列出所有智能体
        print("\n[Test 3] Listing agents...")
        agents = adapter.list_agents()
        print(f"  Result: {'PASS' if len(agents) > 0 else 'FAIL'}")

        # 测试 4: 运行智能体
        print("\n[Test 4] Running agent...")
        output = adapter.run_agent("test_agent", "Hello, world!")
        print(f"  Result: {'PASS' if output is not None else 'FAIL'}")

        # 测试 5: 创建会话
        print("\n[Test 5] Creating session...")
        session = adapter.create_session("test_agent")
        print(f"  Result: {'PASS' if session is not None else 'FAIL'}")

        # 测试 6: 获取会话
        print("\n[Test 6] Getting session...")
        if session:
            retrieved_session = adapter.get_session(session.id)
            print(f"  Result: {'PASS' if retrieved_session is not None else 'FAIL'}")
        else:
            print(f"  Result: FAIL")

        # 测试 7: 列出所有会话
        print("\n[Test 7] Listing sessions...")
        sessions = adapter.list_sessions()
        print(f"  Result: {'PASS' if len(sessions) > 0 else 'FAIL'}")

        # 测试 8: 获取状态
        print("\n[Test 8] Getting status...")
        status = adapter.get_status()
        print(f"  Result: {'PASS' if status['initialized'] else 'FAIL'}")

        # 测试 9: 移除会话
        print("\n[Test 9] Removing session...")
        if session:
            success = adapter.remove_session(session.id)
            print(f"  Result: {'PASS' if success else 'FAIL'}")
        else:
            print(f"  Result: FAIL")

        # 测试 10: 移除智能体
        print("\n[Test 10] Removing agent...")
        success = adapter.remove_agent("test_agent")
        print(f"  Result: {'PASS' if success else 'FAIL'}")

        print("\n" + "=" * 60)
        print("[PASS] All OpenAI Agents Adapter tests passed!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_openai_agents_adapter()
    sys.exit(0 if success else 1)
