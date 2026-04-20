"""
MemGPT 集成示例 - 基础使用
演示核心功能：记忆存储、检索、上下文管理
"""

import sys
sys.path.insert(0, "..")

from memgpt import MemGPTIntegration


def example_basic_memory():
    """基础记忆管理示例"""
    print("\n=== 基础记忆管理 ===\n")
    
    # 创建集成实例
    memgpt = MemGPTIntegration(
        agent_id="example_agent",
        db_path="memory/example.db"
    )
    
    # 存储核心记忆（身份信息）
    memgpt.remember(
        content="我是 Erbing，OpenClaw 的工作代理",
        category="identity",
        importance=1.0,
        to_core=True
    )
    
    # 存储用户偏好
    memgpt.remember(
        content="用户喜欢使用 Python 进行数据分析",
        category="preference",
        importance=0.8
    )
    
    # 存储重要事实
    memgpt.remember(
        content="用户的时区是 Asia/Shanghai",
        category="fact",
        importance=0.7
    )
    
    print("已存储记忆")
    
    # 检索记忆
    results = memgpt.recall(
        query="用户的偏好",
        top_k=5
    )
    
    print("\n检索结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. [{result['layer']}] {result['content'][:50]}...")
    
    # 获取统计信息
    stats = memgpt.get_stats()
    print(f"\n统计信息:")
    print(f"- 核心记忆: {stats['memory']['core_memory']['total_entries']} 条")
    print(f"- 工作记忆: {stats['memory']['working_memory']['total_messages']} 条")


def example_context_management():
    """上下文管理示例"""
    print("\n\n=== 上下文管理 ===\n")
    
    memgpt = MemGPTIntegration(
        agent_id="context_example",
        db_path="memory/context_example.db"
    )
    
    # 添加系统消息
    memgpt.add_message(
        role="system",
        content="你是一个有用的 AI 助手。",
        priority=3
    )
    
    # 添加对话
    memgpt.add_message(
        role="user",
        content="你好，请介绍一下你自己",
        priority=2
    )
    
    memgpt.add_message(
        role="assistant",
        content="你好！我是 Erbing，一个 AI 助手。我可以帮助你完成各种任务。",
        priority=1
    )
    
    memgpt.add_message(
        role="user",
        content="你能做什么？",
        priority=2
    )
    
    memgpt.add_message(
        role="assistant",
        content="我可以帮助你：管理记忆、检索信息、管理上下文窗口等。",
        priority=1
    )
    
    # 获取当前上下文
    context = memgpt.get_current_context()
    print("当前上下文:")
    for msg in context:
        role = msg["role"]
        content = msg["content"][:50]
        print(f"  [{role}]: {content}...")
    
    # 获取上下文摘要
    print(f"\n{memgpt.context.get_summary()}")


def example_memory_layers():
    """三层记忆示例"""
    print("\n\n=== 三层记忆架构 ===\n")
    
    from memgpt.memory import MemoryManager
    
    manager = MemoryManager(
        agent_id="layer_example",
        db_path="memory/layers_example.db"
    )
    
    # 1. 核心记忆 - 始终在线
    print("1. 核心记忆（始终在上下文中）:")
    manager.core_memory.add(
        id="identity",
        content="代理名称: Erbing",
        category="identity",
        importance=1.0
    )
    manager.core_memory.add(
        id="owner",
        content="用户: xl",
        category="identity",
        importance=1.0
    )
    
    core_stats = manager.core_memory.stats()
    print(f"   - 条目数: {core_stats['total_entries']}")
    print(f"   - 令牌使用: {core_stats['total_tokens']}/{core_stats['max_tokens']}")
    
    # 2. 工作记忆 - 会话级别
    print("\n2. 工作记忆（当前会话）:")
    manager.working_memory.add(
        content="用户问：今天天气怎么样？",
        message_type="user",
        importance=0.6
    )
    manager.working_memory.add(
        content="根据查询，今天天气晴朗",
        message_type="assistant",
        importance=0.5
    )
    
    working_stats = manager.working_memory.get_summary()
    print(f"   - 会话ID: {working_stats['session_id']}")
    print(f"   - 消息数: {working_stats['total_messages']}")
    
    # 3. 归档记忆 - 长期存储
    print("\n3. 归档记忆（长期存储）:")
    
    # 添加一些归档记忆
    manager.archival_memory.add(
        content="用户在2026年4月15日询问了关于 Python 数据分析的问题",
        summary="Python 数据分析咨询",
        category="interaction",
        importance=0.6,
        tags=["python", "data-analysis"]
    )
    
    manager.archival_memory.add(
        content="用户偏好使用 Jupyter Notebook 作为开发环境",
        category="preference",
        importance=0.7,
        tags=["preference", "development"]
    )
    
    archival_stats = manager.archival_memory.stats()
    print(f"   - 总条目: {archival_stats['total_entries']}")
    print(f"   - 按类别: {archival_stats['by_category']}")


def example_retrieval():
    """检索系统示例"""
    print("\n\n=== 检索系统 ===\n")
    
    from memgpt.retrieval import RetrievalManager, RetrievalMethod
    
    retrieval = RetrievalManager(
        default_method=RetrievalMethod.HYBRID
    )
    
    # 示例文档
    documents = [
        {
            "content": "Python 是一种流行的编程语言，广泛用于数据科学和机器学习",
            "category": "programming",
            "importance": 0.8
        },
        {
            "content": "用户偏好使用 VS Code 作为代码编辑器",
            "category": "preference",
            "importance": 0.7
        },
        {
            "content": "上次讨论了关于 API 设计的最佳实践",
            "category": "discussion",
            "importance": 0.6
        },
        {
            "content": "Python 的 pandas 库非常适合数据处理",
            "category": "programming",
            "importance": 0.75
        }
    ]
    
    # 语义检索
    print("1. 语义检索:")
    results = retrieval.search(
        query="编程语言",
        documents=documents,
        method=RetrievalMethod.SEMANTIC,
        top_k=2
    )
    
    for doc, score in results:
        print(f"   - [{score:.2f}] {doc['content'][:40]}...")
    
    # 关键词检索
    print("\n2. 关键词检索:")
    results = retrieval.search(
        query="Python",
        documents=documents,
        method=RetrievalMethod.KEYWORD,
        top_k=2
    )
    
    for doc, score in results:
        print(f"   - [{score:.2f}] {doc['content'][:40]}...")
    
    # 混合检索
    print("\n3. 混合检索:")
    results = retrieval.search(
        query="用户偏好 Python",
        documents=documents,
        method=RetrievalMethod.HYBRID,
        top_k=3
    )
    
    for doc, score in results:
        print(f"   - [{score:.2f}] {doc['content'][:40]}...")


def example_context_compression():
    """上下文压缩示例"""
    print("\n\n=== 上下文压缩 ===\n")
    
    from memgpt.context import ContextCompressor
    
    compressor = ContextCompressor(
        compression_threshold=0.8,
        preserve_recent=2
    )
    
    # 模拟长对话
    messages = [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的吗？"},
        {"role": "user", "content": "我想了解一下 Python"},
        {"role": "assistant", "content": "Python 是一种高级编程语言，以简洁易读著称。"},
        {"role": "user", "content": "Python 适合做什么？"},
        {"role": "assistant", "content": "Python 广泛用于：Web开发、数据科学、人工智能、自动化脚本等。"},
        {"role": "user", "content": "推荐的 Python 学习资源？"},
        {"role": "assistant", "content": "推荐资源：官方文档、Real Python、Coursera 课程等。"},
    ]
    
    print(f"原始消息数: {len(messages)}")
    
    # 压缩
    compressed, result = compressor.compress_messages(
        messages,
        keep_full=2
    )
    
    print(f"压缩后消息数: {len(compressed)}")
    print(f"压缩比: {result.compression_ratio:.2f}")
    print(f"摘要: {result.summary[:100]}...")
    
    print("\n压缩后的上下文:")
    for msg in compressed:
        role = msg["role"]
        content = msg["content"][:60]
        print(f"  [{role}]: {content}...")


def main():
    """运行所有示例"""
    print("=" * 60)
    print("MemGPT 集成示例")
    print("=" * 60)
    
    example_basic_memory()
    example_context_management()
    example_memory_layers()
    example_retrieval()
    example_context_compression()
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
