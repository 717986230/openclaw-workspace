"""
基因神经元记忆系统 - API接口

提供完整的API接口
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import json

from .core import (
    GeneticMemorySystem,
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
from .database import GeneticMemoryDatabase


class GeneticMemoryAPI:
    """基因神经元记忆API"""

    def __init__(self, db_path: str):
        self.db = GeneticMemoryDatabase(db_path)
        self.system = GeneticMemorySystem()
        self._load_from_database()

    def _load_from_database(self):
        """从数据库加载所有数据"""
        # 加载基因数据
        genes = self.db.get_all_genes()
        for gene_data in genes:
            memory_id = gene_data['memory_id']
            gene = MemoryGene(
                activation_threshold=gene_data['activation_threshold'],
                decay_rate=gene_data['decay_rate'],
                plasticity=gene_data['plasticity'],
                strengthening_rate=gene_data['strengthening_rate'],
                weakening_rate=gene_data['weakening_rate'],
                consolidation_level=gene_data['consolidation_level'],
                last_accessed=self._parse_datetime(gene_data['last_accessed']),
                access_count=gene_data['access_count'],
                success_rate=gene_data['success_rate'],
                failure_count=gene_data['failure_count'],
                total_attempts=gene_data['total_attempts'],
            )
            # 创建神经元（需要从memories表获取内容）
            # 这里简化处理，实际需要从memories表查询
            neuron = MemoryNeuron(
                id=memory_id,
                content="",  # 需要从memories表获取
                gene=gene
            )
            self.system.add_neuron(neuron)

        # 加载突触连接
        synapses = self.db.get_all_synapses()
        for synapse_data in synapses:
            source_id = synapse_data['source_id']
            target_id = synapse_data['target_id']
            weight = synapse_data['weight']

            source_neuron = self.system.get_neuron(source_id)
            if source_neuron:
                synapse = source_neuron.add_synapse(target_id, weight)
                synapse.co_activation_count = synapse_data['co_activation_count']
                synapse.last_co_activation = self._parse_datetime(
                    synapse_data['last_co_activation']
                )

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """解析日期时间字符串"""
        if dt_str:
            try:
                return datetime.fromisoformat(dt_str)
            except:
                return None
        return None

    def initialize_memory(self, memory_id: int, content: str,
                         importance: float = 0.5, tags: List[str] = None) -> bool:
        """
        初始化记忆

        Args:
            memory_id: 记忆ID
            content: 记忆内容
            importance: 重要性
            tags: 标签

        Returns:
            是否成功
        """
        try:
            # 创建基因
            gene = MemoryGene()
            gene_data = {
                'activation_threshold': gene.activation_threshold,
                'decay_rate': gene.decay_rate,
                'plasticity': gene.plasticity,
                'strengthening_rate': gene.strengthening_rate,
                'weakening_rate': gene.weakening_rate,
                'consolidation_level': gene.consolidation_level,
                'access_count': gene.access_count,
                'success_rate': gene.success_rate,
                'failure_count': gene.failure_count,
                'total_attempts': gene.total_attempts,
            }
            self.db.insert_gene(memory_id, gene_data)

            # 创建神经元
            neuron = MemoryNeuron(
                id=memory_id,
                content=content,
                gene=gene,
                importance=importance,
                tags=tags or []
            )
            self.system.add_neuron(neuron)

            return True
        except Exception as e:
            print(f"Error initializing memory: {e}")
            return False

    def record_interaction(self, memory_a_id: int, memory_b_id: int,
                         success: bool) -> bool:
        """
        记录交互（赫布学习）

        Args:
            memory_a_id: 第一个记忆ID
            memory_b_id: 第二个记忆ID
            success: 是否成功

        Returns:
            是否成功
        """
        try:
            # 记录到系统
            self.system.record_interaction(memory_a_id, memory_b_id, success)

            # 更新数据库
            neuron_a = self.system.get_neuron(memory_a_id)
            neuron_b = self.system.get_neuron(memory_b_id)

            if neuron_a and neuron_b:
                # 更新基因
                self.db.update_gene(memory_a_id, {
                    'access_count': neuron_a.gene.access_count,
                    'success_rate': neuron_a.gene.success_rate,
                    'failure_count': neuron_a.gene.failure_count,
                    'total_attempts': neuron_a.gene.total_attempts,
                    'last_accessed': neuron_a.gene.last_accessed,
                })
                self.db.update_gene(memory_b_id, {
                    'access_count': neuron_b.gene.access_count,
                    'success_rate': neuron_b.gene.success_rate,
                    'failure_count': neuron_b.gene.failure_count,
                    'total_attempts': neuron_b.gene.total_attempts,
                    'last_accessed': neuron_b.gene.last_accessed,
                })

                # 更新突触权重
                synapse = neuron_a.get_synapse(memory_b_id)
                if synapse:
                    self.db.update_synapse_weight(memory_a_id, memory_b_id, synapse.weight)

            return True
        except Exception as e:
            print(f"Error recording interaction: {e}")
            return False

    def consolidate_memory(self, memory_id: int) -> Tuple[bool, ConsolidationLevel]:
        """
        巩固记忆

        Args:
            memory_id: 记忆ID

        Returns:
            (是否成功, 巩固级别)
        """
        try:
            neuron = self.system.get_neuron(memory_id)
            if not neuron:
                return False, ConsolidationLevel.L0_RAW

            old_level = neuron.gene.consolidation_level
            new_level = self.system.consolidation_engine.consolidate(neuron)

            if old_level != new_level:
                # 记录巩固历史
                reason = f"Access count: {neuron.gene.access_count}, Success rate: {neuron.gene.success_rate}"
                self.db.record_consolidation(memory_id, old_level, new_level, reason)

                # 更新数据库
                self.db.update_gene(memory_id, {
                    'consolidation_level': new_level,
                })

            return True, ConsolidationLevel(new_level)
        except Exception as e:
            print(f"Error consolidating memory: {e}")
            return False, ConsolidationLevel.L0_RAW

    def consolidate_all(self) -> Dict[str, int]:
        """
        巩固所有记忆

        Returns:
            统计信息
        """
        results = self.system.consolidate_all()
        stats = {
            'total': len(results),
            'L0': 0,
            'L1': 0,
            'L2': 0,
            'L3': 0,
        }

        for memory_id, level in results:
            stats[f'L{level.value}'] += 1

        return stats

    def search_memories(
        self,
        query_embedding: List[float],
        context_tags: Optional[Set[str]] = None,
        top_k: int = 10,
        use_spreading_activation: bool = True
    ) -> List[Dict]:
        """
        搜索记忆

        Args:
            query_embedding: 查询嵌入
            context_tags: 上下文标签
            top_k: 返回前K个结果
            use_spreading_activation: 是否使用传播激活

        Returns:
            搜索结果列表
        """
        results = []

        for neuron_id, neuron in self.system.neurons.items():
            if neuron.embedding is None:
                continue

            # 计算突触权重
            weight = self.system.weight_calculator.calculate(
                neuron, query_embedding, context_tags
            )

            if weight > 0.1:  # 阈值
                results.append({
                    'memory_id': neuron_id,
                    'weight': weight,
                    'content': neuron.content,
                    'importance': neuron.importance,
                    'consolidation_level': neuron.gene.consolidation_level,
                    'access_count': neuron.gene.access_count,
                    'success_rate': neuron.gene.success_rate,
                })

        # 排序
        results.sort(key=lambda x: x['weight'], reverse=True)

        # 传播激活
        if use_spreading_activation and results:
            top_neuron = self.system.get_neuron(results[0]['memory_id'])
            if top_neuron:
                activated = self.system.spreading_activation_engine.activate(
                    top_neuron, self.system.neurons, max_depth=2
                )

                # 添加传播激活的结果
                for activated_id, activation_value in activated.items():
                    if activated_id not in [r['memory_id'] for r in results]:
                        activated_neuron = self.system.get_neuron(activated_id)
                        if activated_neuron:
                            results.append({
                                'memory_id': activated_id,
                                'weight': activation_value * 0.5,  # 传播激活权重降低
                                'content': activated_neuron.content,
                                'importance': activated_neuron.importance,
                                'consolidation_level': activated_neuron.gene.consolidation_level,
                                'access_count': activated_neuron.gene.access_count,
                                'success_rate': activated_neuron.gene.success_rate,
                            })

                # 重新排序
                results.sort(key=lambda x: x['weight'], reverse=True)

        # 记录激活历史
        for result in results[:top_k]:
            self.db.record_activation(
                result['memory_id'],
                result['weight'],
                query_embedding,
                list(context_tags) if context_tags else None
            )

        return results[:top_k]

    def evolve_memories(
        self,
        mutation_rate: float = 0.01,
        selection_threshold: float = 0.3,
        reproduction_threshold: float = 0.8
    ) -> Dict[str, any]:
        """
        进化记忆

        Args:
            mutation_rate: 突变率
            selection_threshold: 选择阈值
            reproduction_threshold: 繁殖阈值

        Returns:
            进化结果
        """
        neurons = list(self.system.neurons.values())
        pruned_ids, new_ids = self.system.evolution_engine.evolve(
            neurons, mutation_rate, selection_threshold, reproduction_threshold
        )

        # 更新数据库
        for neuron in neurons:
            self.db.update_gene(neuron.id, {
                'activation_threshold': neuron.gene.activation_threshold,
                'decay_rate': neuron.gene.decay_rate,
                'plasticity': neuron.gene.plasticity,
            })

        # 记录进化历史
        for neuron_id in pruned_ids:
            neuron = self.system.get_neuron(neuron_id)
            if neuron:
                self.db.record_evolution(
                    neuron_id,
                    'pruned',
                    {'consolidation_level': neuron.gene.consolidation_level},
                    {},
                    neuron.gene.calculate_fitness()
                )

        for neuron_id in new_ids:
            neuron = self.system.get_neuron(neuron_id)
            if neuron:
                self.db.record_evolution(
                    neuron_id,
                    'reproduction',
                    {},
                    {'consolidation_level': neuron.gene.consolidation_level},
                    neuron.gene.calculate_fitness()
                )

        return {
            'pruned_count': len(pruned_ids),
            'reproduction_count': len(new_ids),
            'pruned_ids': pruned_ids,
            'new_ids': new_ids,
        }

    def get_memory_statistics(self) -> Dict:
        """
        获取记忆统计信息

        Returns:
            统计信息
        """
        db_stats = self.db.get_statistics()

        # 计算系统统计
        total_fitness = 0
        fitness_count = 0
        for neuron in self.system.neurons.values():
            fitness = neuron.gene.calculate_fitness()
            total_fitness += fitness
            fitness_count += 1

        avg_fitness = total_fitness / fitness_count if fitness_count > 0 else 0.0

        return {
            **db_stats,
            'avg_fitness': avg_fitness,
            'total_neurons': len(self.system.neurons),
        }

    def get_memory_details(self, memory_id: int) -> Optional[Dict]:
        """
        获取记忆详情

        Args:
            memory_id: 记忆ID

        Returns:
            记忆详情
        """
        neuron = self.system.get_neuron(memory_id)
        if not neuron:
            return None

        gene_data = self.db.get_gene(memory_id)
        synapses = self.db.get_synapses(memory_id)

        return {
            'id': neuron.id,
            'content': neuron.content,
            'importance': neuron.importance,
            'tags': neuron.tags,
            'category': neuron.category,
            'created_at': neuron.created_at.isoformat(),
            'updated_at': neuron.updated_at.isoformat(),
            'gene': {
                'activation_threshold': neuron.gene.activation_threshold,
                'decay_rate': neuron.gene.decay_rate,
                'plasticity': neuron.gene.plasticity,
                'strengthening_rate': neuron.gene.strengthening_rate,
                'weakening_rate': neuron.gene.weakening_rate,
                'consolidation_level': neuron.gene.consolidation_level,
                'last_accessed': neuron.gene.last_accessed.isoformat() if neuron.gene.last_accessed else None,
                'access_count': neuron.gene.access_count,
                'success_rate': neuron.gene.success_rate,
                'failure_count': neuron.gene.failure_count,
                'total_attempts': neuron.gene.total_attempts,
                'fitness': neuron.gene.calculate_fitness(),
            },
            'synapses': synapses,
        }

    def get_activation_history(self, memory_id: int, limit: int = 10) -> List[Dict]:
        """
        获取激活历史

        Args:
            memory_id: 记忆ID
            limit: 返回数量

        Returns:
            激活历史列表
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM activation_history
                WHERE memory_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (memory_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_consolidation_history(self, memory_id: int, limit: int = 10) -> List[Dict]:
        """
        获取巩固历史

        Args:
            memory_id: 记忆ID
            limit: 返回数量

        Returns:
            巩固历史列表
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM consolidation_history
                WHERE memory_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (memory_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_evolution_history(self, memory_id: int, limit: int = 10) -> List[Dict]:
        """
        获取进化历史

        Args:
            memory_id: 记忆ID
            limit: 返回数量

        Returns:
            进化历史列表
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM evolution_history
                WHERE memory_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (memory_id, limit))
            return [dict(row) for row in cursor.fetchall()]
