"""
基因神经元记忆系统 - 测试文件

测试所有核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from genetic_neural_system import (
    GeneticMemoryAPI,
    setup_genetic_tables,
)
from genetic_neural_system.core import (
    MemoryGene,
    Synapse,
    MemoryNeuron,
    HebbianEngine,
    ConsolidationEngine,
    SpreadingActivationEngine,
    SynapticWeightCalculator,
    GeneticEvolutionEngine,
    ConsolidationLevel,
)


def test_memory_gene():
    """测试记忆基因"""
    print("\n=== 测试记忆基因 ===")

    gene = MemoryGene()
    print(f"初始基因: {gene}")

    # 测试适应度计算
    gene.access_count = 10
    gene.success_rate = 0.8
    gene.consolidation_level = 2
    fitness = gene.calculate_fitness()
    print(f"适应度: {fitness:.3f}")

    # 测试突变
    gene.mutate(mutation_rate=1.0)  # 强制突变
    print(f"突变后基因: {gene}")

    print("✓ 记忆基因测试通过")


def test_synapse():
    """测试突触"""
    print("\n=== 测试突触 ===")

    synapse = Synapse(source_id=1, target_id=2)
    print(f"初始突触: {synapse}")

    # 测试强化
    synapse.strengthen(0.1)
    print(f"强化后: weight={synapse.weight}, count={synapse.co_activation_count}")

    # 测试弱化
    synapse.weaken(0.05)
    print(f"弱化后: weight={synapse.weight}, count={synapse.co_activation_count}")

    # 测试衰减
    decay = synapse.calculate_decay(0.05)
    print(f"衰减: {decay:.3f}")

    print("✓ 突触测试通过")


def test_memory_neuron():
    """测试记忆神经元"""
    print("\n=== 测试记忆神经元 ===")

    neuron = MemoryNeuron(
        id=1,
        content="测试记忆内容",
        importance=0.8,
        tags=["test", "memory"]
    )
    print(f"初始神经元: {neuron}")

    # 测试添加突触
    synapse = neuron.add_synapse(target_id=2, weight=0.5)
    print(f"添加突触: {synapse}")

    # 测试记录访问
    neuron.record_access(success=True)
    print(f"访问后: count={neuron.gene.access_count}, success_rate={neuron.gene.success_rate:.3f}")

    # 测试计算年龄
    age_days = neuron.calculate_age_days()
    print(f"年龄: {age_days} 天")

    # 测试计算近期性
    recency = neuron.calculate_recency()
    print(f"近期性: {recency:.3f}")

    # 测试计算活力
    vitality = neuron.calculate_vitality()
    print(f"活力: {vitality:.3f}")

    print("✓ 记忆神经元测试通过")


def test_hebbian_engine():
    """测试赫布学习引擎"""
    print("\n=== 测试赫布学习引擎 ===")

    neuron_a = MemoryNeuron(id=1, content="记忆A")
    neuron_b = MemoryNeuron(id=2, content="记忆B")

    engine = HebbianEngine()

    # 测试成功学习
    engine.learn(neuron_a, neuron_b, success=True)
    synapse = neuron_a.get_synapse(2)
    print(f"成功学习: weight={synapse.weight:.3f}")

    # 测试失败学习
    engine.learn(neuron_a, neuron_b, success=False)
    print(f"失败学习: weight={synapse.weight:.3f}")

    print("✓ 赫布学习引擎测试通过")


def test_consolidation_engine():
    """测试记忆巩固引擎"""
    print("\n=== 测试记忆巩固引擎 ===")

    neuron = MemoryNeuron(id=1, content="测试记忆")
    engine = ConsolidationEngine()

    # 测试L0→L1
    neuron.gene.access_count = 3
    level = engine.consolidate(neuron)
    print(f"L0→L1: {level}")
    assert level == ConsolidationLevel.L1_SPRINT

    # 测试L1→L2
    neuron.gene.access_count = 10
    level = engine.consolidate(neuron)
    print(f"L1→L2: {level}")
    assert level == ConsolidationLevel.L2_MONTHLY

    # 测试L2→L3
    neuron.gene.success_rate = 0.8
    level = engine.consolidate(neuron)
    print(f"L2→L3: {level}")
    assert level == ConsolidationLevel.L3_PERMANENT

    # 测试L3→L2（降级）
    neuron.gene.success_rate = 0.5
    level = engine.consolidate(neuron)
    print(f"L3→L2: {level}")
    assert level == ConsolidationLevel.L2_MONTHLY

    # 测试修剪
    neuron.gene.consolidation_level = 0
    neuron.gene.access_count = 0
    should_prune = engine.should_prune(neuron)
    print(f"应该修剪: {should_prune}")

    print("✓ 记忆巩固引擎测试通过")


def test_spreading_activation_engine():
    """测试传播激活引擎"""
    print("\n=== 测试传播激活引擎 ===")

    # 创建神经元网络
    neuron1 = MemoryNeuron(id=1, content="记忆1")
    neuron2 = MemoryNeuron(id=2, content="记忆2")
    neuron3 = MemoryNeuron(id=3, content="记忆3")

    # 建立连接
    neuron1.add_synapse(2, weight=0.8)
    neuron2.add_synapse(3, weight=0.6)

    neurons = {1: neuron1, 2: neuron2, 3: neuron3}
    engine = SpreadingActivationEngine()

    # 测试传播激活
    activated = engine.activate(neuron1, neurons, max_depth=2)
    print(f"激活结果: {activated}")

    print("✓ 传播激活引擎测试通过")


def test_synaptic_weight_calculator():
    """测试突触权重计算器"""
    print("\n=== 测试突触权重计算器 ===")

    neuron = MemoryNeuron(
        id=1,
        content="测试记忆",
        importance=0.8,
        tags=["test", "important"]
    )
    neuron.embedding = [0.1, 0.2, 0.3, 0.4]

    query_embedding = [0.1, 0.2, 0.3, 0.4]
    context_tags = {"test", "important"}

    calculator = SynapticWeightCalculator()

    # 测试权重计算
    weight = calculator.calculate(neuron, query_embedding, context_tags)
    print(f"突触权重: {weight:.3f}")

    # 测试余弦相似度
    similarity = calculator._cosine_similarity(
        neuron.embedding, query_embedding
    )
    print(f"余弦相似度: {similarity:.3f}")

    # 测试上下文相似度
    context_sim = calculator._calculate_context_similarity(
        set(neuron.tags), context_tags
    )
    print(f"上下文相似度: {context_sim:.3f}")

    print("✓ 突触权重计算器测试通过")


def test_genetic_evolution_engine():
    """测试基因进化引擎"""
    print("\n=== 测试基因进化引擎 ===")

    # 创建神经元
    neurons = []
    for i in range(10):
        neuron = MemoryNeuron(id=i, content=f"记忆{i}")
        neuron.gene.access_count = i * 10
        neuron.gene.success_rate = 0.5 + (i * 0.05)
        neurons.append(neuron)

    engine = GeneticEvolutionEngine()

    # 测试进化
    pruned, new = engine.evolve(
        neurons,
        mutation_rate=0.0,  # 不突变
        selection_threshold=0.3,
        reproduction_threshold=0.8
    )

    print(f"淘汰数量: {len(pruned)}")
    print(f"繁殖数量: {len(new)}")

    print("✓ 基因进化引擎测试通过")


def test_database_integration():
    """测试数据库集成"""
    print("\n=== 测试数据库集成 ===")

    # 创建测试数据库
    test_db_path = "C:/Users/Administrator/.openclaw/workspace/memory/database/test_genetic_memory.db"

    # 设置表
    setup_genetic_tables(test_db_path)
    print("✓ 数据库表创建成功")

    # 创建API
    api = GeneticMemoryAPI(test_db_path)
    print("✓ API创建成功")

    # 测试初始化记忆
    success = api.initialize_memory(
        memory_id=1,
        content="测试记忆内容",
        importance=0.8,
        tags=["test", "important"]
    )
    print(f"初始化记忆: {success}")

    # 测试记录交互
    success = api.record_interaction(1, 2, success=True)
    print(f"记录交互: {success}")

    # 测试巩固记忆
    success, level = api.consolidate_memory(1)
    print(f"巩固记忆: {success}, level={level}")

    # 测试获取统计信息
    stats = api.get_memory_statistics()
    print(f"统计信息: {stats}")

    print("✓ 数据库集成测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("基因神经元记忆系统 - 测试套件")
    print("=" * 60)

    try:
        test_memory_gene()
        test_synapse()
        test_memory_neuron()
        test_hebbian_engine()
        test_consolidation_engine()
        test_spreading_activation_engine()
        test_synaptic_weight_calculator()
        test_genetic_evolution_engine()
        test_database_integration()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
