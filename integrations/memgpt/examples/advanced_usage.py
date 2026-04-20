"""
MemGPT 集成示例 - 高级用法
演示与 OpenClaw 现有系统的集成
"""

import sys
sys.path.insert(0, "..")

from memgpt import MemGPTIntegration
from pathlib import Path


def example_memory_md_sync():
    """MEMORY.md 同步示例"""
    print("\n=== MEMORY.md 同步 ===\n")
    
    memgpt = MemGPTIntegration(
        agent_id="sync_example",
        db_path="memory/sync_example.db"
    )
    
    # 从 MEMORY.md 加载核心记忆
    memory_md_path = Path("../../MEMORY.md")
    
    if memory_md_path.exists():
        loaded = memgpt.memory.load_from_memory_md(str(memory_md_path))
        print(f"从 MEMORY.md 加载了 {loaded} 条核心记忆")
    else:
        print("MEMORY.md 不存在，创建示例数据")
        
        # 手动添加一些核心记忆
        memgpt.remember(
            content="我是 Erbing，OpenClaw 的工作代理",
            category="identity",
            importance=1.0,
            to_core=True
        )
        
        memgpt.remember(
            content="用户是 xl，希望我能够自主学习技能",
            category="user",
            importance=0.9,
            to_core=True
        )
    
    # 导出回 MEMORY.md
    export_path = "memory/example_memory_export.md"
    if memgpt.memory.export_to_memory_md(export_path):
        print(f"已导出核心记忆到 {export_path}")
    
    # 显示当前核心记忆
    print("\n当前核心记忆:")
    for entry in memgpt.memory.core_memory.get_all():
        print(f"  [{entry.category}] {entry.content[:50]}...")


def example_session_lifecycle():
    """会话生命周期示例"""
    print("\n\n=== 会话生命周期 ===\n")
    
    memgpt = MemGPTIntegration(
        agent_id="lifecycle_example",
        db_path="memory/lifecycle.db"
    )
    
    # 开始新会话
    print("1. 开始会话")
    session_id = memgpt.memory.working_memory.session_id
    print(f"   会话ID: {session_id}")
    
    # 会话交互
    print("\n2. 会话交互")
    
    interactions = [
        ("user", "你好，请帮我分析一下项目结构"),
        ("assistant", "好的，让我先了解一下项目的目录结构..."),
        ("user", "主要关注 integrations 目录"),
        ("assistant", "integrations 目录包含 MemGPT、LangChain、CrewAI 等集成..."),
        ("user", "好的，那 MemGPT 的主要组件是什么？"),
        ("assistant", "MemGPT 主要包含三层记忆、检索系统和上下文管理器..."),
    ]
    
    for role, content in interactions:
        memgpt.add_message(role=role, content=content)
        print(f"   [{role}]: {content[:40]}...")
    
    # 检查工作记忆状态
    print("\n3. 工作记忆状态")
    stats = memgpt.memory.working_memory.get_summary()
    print(f"   消息数: {stats['total_messages']}")
    print(f"   令牌使用: {stats['utilization']:.1%}")
    
    # 结束会话，归档
    print("\n4. 归档会话")
    archived_ids = memgpt.archive_session()
    print(f"   归档了 {len(archived_ids)} 条记忆")
    
    # 从归档检索
    print("\n5. 从归档检索")
    results = memgpt.recall(
        query="MemGPT 组件",
        top_k=3
    )
    
    print("   检索结果:")
    for result in results:
        print(f"   - [{result['layer']}] {result['content'][:50]}...")


def example_knowledge_graph_link():
    """知识图谱链接示例"""
    print("\n\n=== 知识图谱链接 ===\n")
    
    from memgpt.memory import MemoryManager
    
    manager = MemoryManager(
        agent_id="kg_example",
        db_path="memory/kg_example.db"
    )
    
    # 存储带标签的记忆
    print("1. 存储带标签的记忆")
    
    memory_id_1 = manager.archival_memory.add(
        content="Python 是用户最常用的编程语言",
        summary="用户偏好 Python",
        category="preference",
        importance=0.8,
        tags=["python", "programming", "preference"]
    )
    print(f"   存储: {memory_id_1}")
    
    memory_id_2 = manager.archival_memory.add(
        content="用户正在学习机器学习相关的知识",
        summary="机器学习学习",
        category="activity",
        importance=0.7,
        tags=["machine-learning", "learning", "ai"]
    )
    print(f"   存储: {memory_id_2}")
    
    # 按标签检索
    print("\n2. 按标签关联")
    
    # 使用检索管理器
    from memgpt.retrieval import RetrievalManager
    
    # 模拟从归档获取所有记忆
    all_memories = manager.archival_memory.get_recent(days=30)
    
    documents = [
        {
            "content": m.content,
            "category": m.category,
            "tags": m.tags,
            "importance": m.importance
        }
        for m in all_memories
    ]
    
    retrieval = RetrievalManager()
    
    results = retrieval.search(
        query="Python 学习",
        documents=documents,
        top_k=5
    )
    
    print("   关联结果:")
    for doc, score in results:
        print(f"   - [{score:.2f}] {doc['content'][:50]}...")
        print(f"     标签: {doc.get('tags', [])}")


def example_context_optimization():
    """上下文优化示例"""
    print("\n\n=== 上下文优化 ===\n")
    
    memgpt = MemGPTIntegration(
        agent_id="optimize_example",
        db_path="memory/optimize_example.db",
        max_context_tokens=2000  # 设置较小的限制以演示优化
    )
    
    # 添加大量消息
    print("1. 添加消息...")
    
    for i in range(20):
        memgpt.add_message(
            role="user" if i % 2 == 0 else "assistant",
            content=f"这是第 {i+1} 条消息，用于测试上下文优化功能。消息内容包含一些详细信息和讨论。",
            priority=2 if i >= 18 else 1  # 最后两条优先级更高
        )
    
    stats_before = memgpt.context.get_stats()
    print(f"   消息数: {stats_before['context_window']['total_blocks']}")
    print(f"   令牌使用: {stats_before['context_window']['token_usage']['utilization']:.1%}")
    
    # 执行优化
    print("\n2. 执行优化...")
    result = memgpt.optimize()
    
    print(f"   时间衰减: {'是' if result['context'].get('decay_applied') else '否'}")
    if 'compression' in result['context']:
        comp = result['context']['compression']
        print(f"   压缩: {'是' if comp['performed'] else '否'}")
        if comp['performed']:
            print(f"   压缩比: {comp['ratio']:.2f}")
    
    stats_after = memgpt.context.get_stats()
    print(f"\n   优化后消息数: {stats_after['context_window']['total_blocks']}")
    print(f"   优化后令牌使用: {stats_after['context_window']['token_usage']['utilization']:.1%}")


def example_state_persistence():
    """状态持久化示例"""
    print("\n\n=== 状态持久化 ===\n")
    
    # 创建并保存状态
    print("1. 创建并保存状态")
    
    memgpt_1 = MemGPTIntegration(
        agent_id="persist_example",
        db_path="memory/persist_example.db"
    )
    
    memgpt_1.remember(
        content="这是一个测试记忆，用于验证持久化功能",
        category="test",
        importance=0.5
    )
    
    memgpt_1.add_message(
        role="user",
        content="这是测试消息"
    )
    
    state_path = "memory/example_state.json"
    memgpt_1.save_state(state_path)
    print(f"   状态已保存到 {state_path}")
    
    # 加载状态
    print("\n2. 加载状态")
    
    memgpt_2 = MemGPTIntegration(
        agent_id="persist_example",
        db_path="memory/persist_example.db"
    )
    
    if memgpt_2.load_state(state_path):
        print("   状态加载成功")
        
        # 验证数据
        context = memgpt_2.get_current_context()
        print(f"   上下文消息数: {len(context)}")
        
        if context:
            print(f"   最后一条消息: {context[-1]['content'][:30]}...")


def example_performance_monitoring():
    """性能监控示例"""
    print("\n\n=== 性能监控 ===\n")
    
    import time
    
    memgpt = MemGPTIntegration(
        agent_id="perf_example",
        db_path="memory/perf_example.db"
    )
    
    # 测试存储性能
    print("1. 存储性能测试")
    
    start = time.time()
    for i in range(100):
        memgpt.remember(
            content=f"测试记忆 {i}: 这是一些测试内容，用于性能评估",
            category="test",
            importance=0.5
        )
    elapsed = time.time() - start
    
    print(f"   存储 100 条记忆: {elapsed:.3f} 秒")
    print(f"   平均: {elapsed/100*1000:.1f} 毫秒/条")
    
    # 测试检索性能
    print("\n2. 检索性能测试")
    
    queries = ["测试", "性能", "记忆", "内容", "评估"]
    
    start = time.time()
    for query in queries:
        results = memgpt.recall(query=query, top_k=10)
    elapsed = time.time() - start
    
    print(f"   5 次检索: {elapsed:.3f} 秒")
    print(f"   平均: {elapsed/5*1000:.1f} 毫秒/次")
    
    # 获取完整统计
    print("\n3. 完整统计信息")
    
    stats = memgpt.get_stats()
    print(f"   记忆统计:")
    print(f"     - 核心: {stats['memory']['core_memory']['total_entries']} 条")
    print(f"     - 工作: {stats['memory']['working_memory']['total_messages']} 条")
    print(f"     - 归档: {stats['memory']['archival_memory']['total_entries']} 条")
    
    print(f"\n   上下文统计:")
    print(f"     - 块数: {stats['context']['context_window']['total_blocks']}")
    print(f"     - 令牌: {stats['context']['context_window']['token_usage']['current']}")


def main():
    """运行所有高级示例"""
    print("=" * 60)
    print("MemGPT 集成 - 高级示例")
    print("=" * 60)
    
    example_memory_md_sync()
    example_session_lifecycle()
    example_knowledge_graph_link()
    example_context_optimization()
    example_state_persistence()
    example_performance_monitoring()
    
    print("\n" + "=" * 60)
    print("高级示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
