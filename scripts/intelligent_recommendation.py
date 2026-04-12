#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能推荐系统
Intelligent Recommendation System
"""

import sqlite3
import numpy as np
import networkx as nx
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import random

class RecommendationMethod(Enum):
    CONTENT_BASED = "content_based"
    COLLABORATIVE = "collaborative"
    GRAPH_BASED = "graph_based"
    HYBRID = "hybrid"

@dataclass
class RecommendationResult:
    memory_id: int
    title: str
    content: str
    type: str
    category: str
    importance: float
    recommendation_score: float
    recommendation_method: str
    explanation: str
    related_memories: List[int]

class IntelligentRecommendation:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()
        self.memories = {}
        self.user_history = defaultdict(list)

    def load_graph(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content, type, category, importance FROM memories LIMIT ?", (limit,))
        for row in cursor.fetchall():
            self.memories[row[0]] = {'id': row[0], 'title': row[1], 'content': row[2], 'type': row[3], 'category': row[4], 'importance': row[5]}
            self.graph.add_node(row[0])

        cursor.execute("SELECT source_memory_id, target_memory_id, relation_type, relation_strength FROM knowledge_relations WHERE source_memory_id IN (SELECT id FROM memories LIMIT ?) AND target_memory_id IN (SELECT id FROM memories LIMIT ?)", (limit, limit))
        for row in cursor.fetchall():
            self.graph.add_edge(row[0], row[1], relation_type=row[2], strength=row[3])

        conn.close()
        return {'memories': len(self.memories), 'edges': self.graph.number_of_edges()}

    def content_based_recommendation(self, memory_id: int, max_results: int = 10) -> List[RecommendationResult]:
        if memory_id not in self.memories:
            return []
        target_memory = self.memories[memory_id]
        results = []
        for other_id, other_memory in self.memories.items():
            if other_id == memory_id:
                continue
            similarity = self._compute_content_similarity(target_memory, other_memory)
            if similarity > 0.3:
                result = RecommendationResult(memory_id=other_id, title=other_memory['title'], content=other_memory['content'], type=other_memory['type'], category=other_memory['category'], importance=other_memory['importance'], recommendation_score=similarity, recommendation_method='content_based', explanation=f"Content-based similarity: {similarity:.2f}", related_memories=[memory_id])
                results.append(result)
        results.sort(key=lambda x: x.recommendation_score, reverse=True)
        return results[:max_results]

    def collaborative_recommendation(self, user_id: str, max_results: int = 10) -> List[RecommendationResult]:
        if user_id not in self.user_history:
            return []
        user_memories = self.user_history[user_id]
        if not user_memories:
            return []
        results = []
        for other_id, other_memory in self.memories.items():
            if other_id in user_memories:
                continue
            score = self._compute_collaborative_score(user_memories, other_id)
            if score > 0.3:
                result = RecommendationResult(memory_id=other_id, title=other_memory['title'], content=other_memory['content'], type=other_memory['type'], category=other_memory['category'], importance=other_memory['importance'], recommendation_score=score, recommendation_method='collaborative', explanation=f"Collaborative filtering score: {score:.2f}", related_memories=user_memories)
                results.append(result)
        results.sort(key=lambda x: x.recommendation_score, reverse=True)
        return results[:max_results]

    def graph_based_recommendation(self, memory_id: int, max_results: int = 10) -> List[RecommendationResult]:
        if memory_id not in self.memories:
            return []
        results = []
        if self.graph.has_node(memory_id):
            neighbors = list(self.graph.neighbors(memory_id))
            for neighbor_id in neighbors:
                if neighbor_id in self.memories:
                    edge_data = self.graph.get_edge_data(memory_id, neighbor_id)
                    strength = edge_data.get('strength', 0.0) if edge_data else 0.0
                    memory = self.memories[neighbor_id]
                    result = RecommendationResult(memory_id=neighbor_id, title=memory['title'], content=memory['content'], type=memory['type'], category=memory['category'], importance=memory['importance'], recommendation_score=strength, recommendation_method='graph_based', explanation=f"Graph-based strength: {strength:.2f}", related_memories=[memory_id])
                    results.append(result)
        results.sort(key=lambda x: x.recommendation_score, reverse=True)
        return results[:max_results]

    def hybrid_recommendation(self, memory_id: int, user_id: Optional[str] = None, max_results: int = 10) -> List[RecommendationResult]:
        content_results = self.content_based_recommendation(memory_id, max_results)
        graph_results = self.graph_based_recommendation(memory_id, max_results)
        collaborative_results = []
        if user_id:
            collaborative_results = self.collaborative_recommendation(user_id, max_results)
        all_results = defaultdict(lambda: {'memory_id': None, 'title': '', 'content': '', 'type': '', 'category': '', 'importance': 0.0, 'scores': [], 'methods': [], 'explanations': [], 'related_memories': []})
        for result in content_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['scores'].append(result.recommendation_score)
            all_results[result.memory_id]['methods'].append(result.recommendation_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
            all_results[result.memory_id]['related_memories'].extend(result.related_memories)
        for result in graph_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['scores'].append(result.recommendation_score)
            all_results[result.memory_id]['methods'].append(result.recommendation_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
            all_results[result.memory_id]['related_memories'].extend(result.related_memories)
        for result in collaborative_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['scores'].append(result.recommendation_score)
            all_results[result.memory_id]['methods'].append(result.recommendation_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
            all_results[result.memory_id]['related_memories'].extend(result.related_memories)
        final_results = []
        for memory_id, data in all_results.items():
            avg_score = np.mean(data['scores'])
            combined_explanation = '; '.join(data['explanations'])
            result = RecommendationResult(memory_id=data['memory_id'], title=data['title'], content=data['content'], type=data['type'], category=data['category'], importance=data['importance'], recommendation_score=avg_score, recommendation_method='hybrid', explanation=f"Hybrid: {combined_explanation}", related_memories=data['related_memories'])
            final_results.append(result)
        final_results.sort(key=lambda x: x.recommendation_score, reverse=True)
        return final_results[:max_results]

    def update_user_history(self, user_id: str, memory_id: int):
        self.user_history[user_id].append(memory_id)

    def _compute_content_similarity(self, memory1: Dict, memory2: Dict) -> float:
        text1 = memory1['title'] + ' ' + memory1['content']
        text2 = memory2['title'] + ' ' + memory2['content']
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union

    def _compute_collaborative_score(self, user_memories: List[int], target_id: int) -> float:
        if target_id not in self.memories:
            return 0.0
        target_memory = self.memories[target_id]
        total_similarity = 0.0
        count = 0
        for user_memory_id in user_memories:
            if user_memory_id in self.memories:
                user_memory = self.memories[user_memory_id]
                similarity = self._compute_content_similarity(target_memory, user_memory)
                total_similarity += similarity
                count += 1
        return total_similarity / count if count > 0 else 0.0

if __name__ == "__main__":
    print("Testing Intelligent Recommendation...")
    recommendation = IntelligentRecommendation("memory/database/xiaozhi_memory.db")
    load_result = recommendation.load_graph(limit=100)
    print(f"Loaded {load_result['memories']} memories, {load_result['edges']} edges")
    if recommendation.memories:
        first_id = list(recommendation.memories.keys())[0]
        results = recommendation.content_based_recommendation(first_id, max_results=5)
        print(f"Content-based recommendation: {len(results)} results")
        results = recommendation.graph_based_recommendation(first_id, max_results=5)
        print(f"Graph-based recommendation: {len(results)} results")
        results = recommendation.hybrid_recommendation(first_id, max_results=5)
        print(f"Hybrid recommendation: {len(results)} results")
    print("Intelligent Recommendation test complete!")
