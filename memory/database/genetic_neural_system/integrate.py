"""
基因神经元记忆系统 - 集成脚本

将基因神经元系统集成到现有的记忆系统中
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genetic_neural_system import (
    GeneticMemoryAPI,
    setup_genetic_tables,
)
from genetic_neural_system.database import GeneticMemoryDatabase


def integrate_with_existing_memory():
    """集成到现有记忆系统"""
    print("=" * 60)
    print("基因神经元记忆系统 - 集成脚本")
    print("=" * 60)

    # 数据库路径
    db_path = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"

    # 1. 设置基因神经元表
    print("\n[1/5] 设置基因神经元表...")
    setup_genetic_tables(db_path)
    print("✓ 基因神经元表创建成功")

    # 2. 创建API实例
    print("\n[2/5] 创建API实例...")
    api = GeneticMemoryAPI(db_path)
    print("✓ API实例创建成功")

    # 3. 迁移现有记忆
    print("\n[3/5] 迁移现有记忆...")
    migrate_existing_memories(api, db_path)
    print("✓ 现有记忆迁移完成")

    # 4. 创建示例突触连接
    print("\n[4/5] 创建示例突触连接...")
    create_sample_synapses(api)
    print("✓ 示例突触连接创建完成")

    # 5. 验证集成
    print("\n[5/5] 验证集成...")
    verify_integration(api)
    print("✓ 集成验证完成")

    print("\n" + "=" * 60)
    print("✓ 基因神经元记忆系统集成完成！")
    print("=" * 60)


def migrate_existing_memories(api: GeneticMemoryAPI, db_path: str):
    """迁移现有记忆"""
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取所有现有记忆
    cursor.execute("SELECT id, title, content, importance, tags FROM memories")
    memories = cursor.fetchall()

    migrated_count = 0
    for memory in memories:
        memory_id = memory['id']
        title = memory['title']
        content = memory['content'] or title
        importance = memory['importance'] or 0.5
        tags_str = memory['tags']

        # 解析标签
        tags = []
        if tags_str:
            try:
                import json
                tags = json.loads(tags_str)
            except:
                tags = []

        # 初始化基因神经元
        success = api.initialize_memory(
            memory_id=memory_id,
            content=content,
            importance=importance,
            tags=tags
        )

        if success:
            migrated_count += 1

    conn.close()
    print(f"  迁移了 {migrated_count} 个记忆")


def create_sample_synapses(api: GeneticMemoryAPI):
    """创建示例突触连接"""
    import sqlite3

    db_path = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取现有知识关系
    cursor.execute("""
        SELECT source_memory_id, target_memory_id, relation_strength
        FROM knowledge_relations
        LIMIT 100
    """)
    relations = cursor.fetchall()

    created_count = 0
    for relation in relations:
        source_id = relation['source_memory_id']
        target_id = relation['target_memory_id']
        strength = relation['relation_strength'] or 0.5

        # 创建突触连接
        success = api.db.insert_synapse(source_id, target_id, strength)
        if success:
            created_count += 1

    conn.close()
    print(f"  创建了 {created_count} 个突触连接")


def verify_integration(api: GeneticMemoryAPI):
    """验证集成"""
    # 获取统计信息
    stats = api.get_memory_statistics()

    print(f"  总记忆数: {stats['total_memories']}")
    print(f"  总突触数: {stats['total_synapses']}")
    print(f"  平均成功率: {stats['avg_success_rate']:.3f}")
    print(f"  平均访问次数: {stats['avg_access_count']:.1f}")

    print(f"  巩固级别分布:")
    for level, count in stats['consolidation_distribution'].items():
        print(f"    L{level}: {count}")


def run_demo():
    """运行演示"""
    print("\n" + "=" * 60)
    print("基因神经元记忆系统 - 演示")
    print("=" * 60)

    db_path = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
    api = GeneticMemoryAPI(db_path)

    # 1. 创建测试记忆
    print("\n[演示1] 创建测试记忆...")
    api.initialize_memory(
        memory_id=9999,
        content="用户喜欢喝咖啡",
        importance=0.8,
        tags=["preference", "coffee"]
    )
    api.initialize_memory(
        memory_id=9998,
        content="咖啡含有咖啡因",
        importance=0.6,
        tags=["fact", "caffeine"]
    )
    print("✓ 测试记忆创建成功")

    # 2. 记录交互
    print("\n[演示2] 记录交互（赫布学习）...")
    api.record_interaction(9999, 9998, success=True)
    print("✓ 交互记录成功")

    # 3. 巩固记忆
    print("\n[演示3] 巩固记忆...")
    success, level = api.consolidate_memory(9999)
    print(f"✓ 记忆9999巩固到级别: {level}")

    # 4. 搜索记忆
    print("\n[演示4] 搜索记忆...")
    results = api.search_memories(
        query_embedding=[0.1, 0.2, 0.3],
        context_tags={"preference"},
        top_k=5
    )
    print(f"✓ 找到 {len(results)} 个相关记忆")
    for result in results[:3]:
        print(f"  - ID: {result['memory_id']}, 权重: {result['weight']:.3f}")

    # 5. 获取记忆详情
    print("\n[演示5] 获取记忆详情...")
    details = api.get_memory_details(9999)
    if details:
        print(f"✓ 记忆详情:")
        print(f"  - 内容: {details['content']}")
        print(f"  - 重要性: {details['importance']}")
        print(f"  - 巩固级别: {details['gene']['consolidation_level']}")
        print(f"  - 适应度: {details['gene']['fitness']:.3f}")

    # 6. 进化记忆
    print("\n[演示6] 进化记忆...")
    evolution_result = api.evolve_memories(
        mutation_rate=0.01,
        selection_threshold=0.3,
        reproduction_threshold=0.8
    )
    print(f"✓ 进化完成:")
    print(f"  - 淘汰数量: {evolution_result['pruned_count']}")
    print(f"  - 繁殖数量: {evolution_result['reproduction_count']}")

    print("\n" + "=" * 60)
    print("✓ 演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="基因神经元记忆系统集成脚本")
    parser.add_argument("--integrate", action="store_true", help="集成到现有记忆系统")
    parser.add_argument("--demo", action="store_true", help="运行演示")
    parser.add_argument("--all", action="store_true", help="集成并运行演示")

    args = parser.parse_args()

    if args.all:
        integrate_with_existing_memory()
        run_demo()
    elif args.integrate:
        integrate_with_existing_memory()
    elif args.demo:
        run_demo()
    else:
        parser.print_help()
