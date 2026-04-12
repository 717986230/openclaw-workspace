#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新图谱关系强度
Auto-Update Graph Relation Strength
"""

import sqlite3
import numpy as np
import networkx as nx
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class UpdateStrategy(Enum):
    FREQUENCY_BASED = "frequency_based"
    TIME_DECAY = "time_decay"
    REINFORCEMENT = "reinforcement"
    HYBRID = "hybrid"

@dataclass
class UpdateResult:
    relation_id: int
    old_strength: float
    new_strength: float
    update_strategy: str
    explanation: str

class AutoUpdateRelationStrength:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()
        self.relation_access_count = {}
        self.relation_last_access = {}

    def load_graph(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM memories LIMIT ?", (limit,))
        memory_ids = [row[0] for row in cursor.fetchall()]
        for memory_id in memory_ids:
            self.graph.add_node(memory_id)

        cursor.execute("SELECT id, source_memory_id, target_memory_id, relation_type, relation_strength, created_at FROM knowledge_relations WHERE source_memory_id IN (SELECT id FROM memories LIMIT ?) AND target_memory_id IN (SELECT id FROM memories LIMIT ?)", (limit, limit))
        for row in cursor.fetchall():
            relation_id = row[0]
            source = row[1]
            target = row[2]
            relation_type = row[3]
            strength = row[4]
            created_at = row[5]
            self.graph.add_edge(source, target, relation_id=relation_id, relation_type=relation_type, strength=strength, created_at=created_at)
            self.relation_access_count[relation_id] = 0
            self.relation_last_access[relation_id] = created_at

        conn.close()
        return {'nodes': self.graph.number_of_nodes(), 'edges': self.graph.number_of_edges()}

    def record_access(self, relation_id: int):
        if relation_id in self.relation_access_count:
            self.relation_access_count[relation_id] += 1
            self.relation_last_access[relation_id] = datetime.now().isoformat()

    def frequency_based_update(self, relation_id: int, decay_factor: float = 0.1) -> UpdateResult:
        if relation_id not in self.relation_access_count:
            return UpdateResult(relation_id=relation_id, old_strength=0.0, new_strength=0.0, update_strategy='frequency_based', explanation='Relation not found')
        access_count = self.relation_access_count[relation_id]
        old_strength = self._get_relation_strength(relation_id)
        new_strength = min(1.0, old_strength + (access_count * decay_factor))
        self._update_relation_strength(relation_id, new_strength)
        return UpdateResult(relation_id=relation_id, old_strength=old_strength, new_strength=new_strength, update_strategy='frequency_based', explanation=f'Updated based on {access_count} accesses')

    def time_decay_update(self, relation_id: int, decay_rate: float = 0.01) -> UpdateResult:
        if relation_id not in self.relation_last_access:
            return UpdateResult(relation_id=relation_id, old_strength=0.0, new_strength=0.0, update_strategy='time_decay', explanation='Relation not found')
        last_access_str = self.relation_last_access[relation_id]
        try:
            last_access = datetime.fromisoformat(last_access_str)
        except:
            last_access = datetime.now()
        time_since_access = (datetime.now() - last_access).total_seconds()
        days_since_access = time_since_access / 86400.0
        old_strength = self._get_relation_strength(relation_id)
        new_strength = max(0.0, old_strength * (1.0 - decay_rate * days_since_access))
        self._update_relation_strength(relation_id, new_strength)
        return UpdateResult(relation_id=relation_id, old_strength=old_strength, new_strength=new_strength, update_strategy='time_decay', explanation=f'Updated based on {days_since_access:.2f} days since last access')

    def reinforcement_update(self, relation_id: int, reward: float, learning_rate: float = 0.1) -> UpdateResult:
        old_strength = self._get_relation_strength(relation_id)
        new_strength = np.clip(old_strength + learning_rate * reward, 0.0, 1.0)
        self._update_relation_strength(relation_id, new_strength)
        return UpdateResult(relation_id=relation_id, old_strength=old_strength, new_strength=new_strength, update_strategy='reinforcement', explanation=f'Updated with reward {reward:.2f}')

    def hybrid_update(self, relation_id: int, decay_factor: float = 0.1, decay_rate: float = 0.01, reward: float = 0.0, learning_rate: float = 0.1) -> UpdateResult:
        frequency_result = self.frequency_based_update(relation_id, decay_factor)
        time_result = self.time_decay_update(relation_id, decay_rate)
        if reward != 0.0:
            reinforcement_result = self.reinforcement_update(relation_id, reward, learning_rate)
            final_strength = reinforcement_result.new_strength
        else:
            final_strength = (frequency_result.new_strength + time_result.new_strength) / 2.0
        self._update_relation_strength(relation_id, final_strength)
        return UpdateResult(relation_id=relation_id, old_strength=frequency_result.old_strength, new_strength=final_strength, update_strategy='hybrid', explanation='Hybrid update combining frequency, time decay, and reinforcement')

    def batch_update(self, update_strategy: UpdateStrategy = UpdateStrategy.HYBRID) -> List[UpdateResult]:
        results = []
        for relation_id in self.relation_access_count.keys():
            if update_strategy == UpdateStrategy.FREQUENCY_BASED:
                result = self.frequency_based_update(relation_id)
            elif update_strategy == UpdateStrategy.TIME_DECAY:
                result = self.time_decay_update(relation_id)
            elif update_strategy == UpdateStrategy.REINFORCEMENT:
                result = self.reinforcement_update(relation_id, reward=0.0)
            else:
                result = self.hybrid_update(relation_id)
            results.append(result)
        return results

    def _get_relation_strength(self, relation_id: int) -> float:
        for u, v, data in self.graph.edges(data=True):
            if data.get('relation_id') == relation_id:
                return data.get('strength', 0.0)
        return 0.0

    def _update_relation_strength(self, relation_id: int, new_strength: float):
        for u, v, data in self.graph.edges(data=True):
            if data.get('relation_id') == relation_id:
                data['strength'] = new_strength
                break

    def get_statistics(self) -> Dict:
        stats = {
            'total_relations': len(self.relation_access_count),
            'total_accesses': sum(self.relation_access_count.values()),
            'avg_accesses': np.mean(list(self.relation_access_count.values())) if self.relation_access_count else 0.0,
            'max_accesses': max(self.relation_access_count.values()) if self.relation_access_count else 0,
            'min_accesses': min(self.relation_access_count.values()) if self.relation_access_count else 0
        }
        return stats

if __name__ == "__main__":
    print("Testing Auto-Update Relation Strength...")
    updater = AutoUpdateRelationStrength("memory/database/xiaozhi_memory.db")
    load_result = updater.load_graph(limit=100)
    print(f"Loaded {load_result['nodes']} nodes, {load_result['edges']} edges")
    if updater.relation_access_count:
        first_relation = list(updater.relation_access_count.keys())[0]
        updater.record_access(first_relation)
        result = updater.frequency_based_update(first_relation)
        print(f"Frequency-based update: {result.explanation}")
        result = updater.time_decay_update(first_relation)
        print(f"Time decay update: {result.explanation}")
        result = updater.reinforcement_update(first_relation, reward=0.5)
        print(f"Reinforcement update: {result.explanation}")
        result = updater.hybrid_update(first_relation)
        print(f"Hybrid update: {result.explanation}")
    stats = updater.get_statistics()
    print(f"Statistics: {stats}")
    print("Auto-Update Relation Strength test complete!")
