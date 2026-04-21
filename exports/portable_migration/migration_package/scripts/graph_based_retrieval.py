#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于图谱的智能检索
Graph-Based Intelligent Retrieval
"""

import sqlite3
import numpy as np
import networkx as nx
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import re

class RetrievalMethod(Enum):
    GRAPH_EXPANSION = "graph_expansion"
    PATH_RETRIEVAL = "path_retrieval"
    COMMUNITY_RETRIEVAL = "community_retrieval"
    CENTRALITY_RETRIEVAL = "centrality_retrieval"
    HYBRID = "hybrid"

@dataclass
class RetrievalResult:
    memory_id: int
    title: str
    content: str
    type: str
    category: str
    importance: float
    relevance_score: float
    retrieval_path: List[int]
    retrieval_method: str
    explanation: str

class GraphBasedRetrieval:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.causal_graph = nx.DiGraph()
        self.knowledge_graph = nx.MultiDiGraph()
        self.combined_graph = nx.MultiDiGraph()
        self.memories = {}

    def load_graphs(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title, content, type, category, importance FROM memories LIMIT ?", (limit,))
        for row in cursor.fetchall():
            self.memories[row[0]] = {'id': row[0], 'title': row[1], 'content': row[2], 'type': row[3], 'category': row[4], 'importance': row[5]}
            self.causal_graph.add_node(row[0])
            self.knowledge_graph.add_node(row[0])
            self.combined_graph.add_node(row[0])

        cursor.execute("SELECT cause_memory_id, effect_memory_id, causal_type, strength FROM causal_relations WHERE cause_memory_id IN (SELECT id FROM memories LIMIT ?) AND effect_memory_id IN (SELECT id FROM memories LIMIT ?)", (limit, limit))
        for row in cursor.fetchall():
            self.causal_graph.add_edge(row[0], row[1], causal_type=row[2], strength=row[3])
            self.combined_graph.add_edge(row[0], row[1], edge_type='causal', relation_type=row[2], strength=row[3])

        cursor.execute("SELECT source_memory_id, target_memory_id, relation_type, relation_strength FROM knowledge_relations WHERE source_memory_id IN (SELECT id FROM memories LIMIT ?) AND target_memory_id IN (SELECT id FROM memories LIMIT ?)", (limit, limit))
        for row in cursor.fetchall():
            self.knowledge_graph.add_edge(row[0], row[1], relation_type=row[2], strength=row[3])
            self.combined_graph.add_edge(row[0], row[1], edge_type='knowledge', relation_type=row[2], strength=row[3])

        conn.close()
        return {'memories': len(self.memories), 'causal_edges': self.causal_graph.number_of_edges(), 'knowledge_edges': self.knowledge_graph.number_of_edges(), 'combined_edges': self.combined_graph.number_of_edges()}

    def graph_expansion_retrieval(self, query: str, max_depth: int = 3, max_results: int = 20) -> List[RetrievalResult]:
        initial_nodes = self._find_initial_nodes(query)
        if not initial_nodes:
            return []
        results = []
        visited = set()
        for initial_node in initial_nodes:
            if initial_node in visited:
                continue
            visited.add(initial_node)
            queue = [(initial_node, 0, [initial_node])]
            while queue and len(results) < max_results:
                current_node, depth, path = queue.pop(0)
                if depth > max_depth:
                    continue
                if current_node in self.memories:
                    memory = self.memories[current_node]
                    relevance_score = self._compute_relevance(query, memory, depth, path)
                    result = RetrievalResult(memory_id=current_node, title=memory['title'], content=memory['content'], type=memory['type'], category=memory['category'], importance=memory['importance'], relevance_score=relevance_score, retrieval_path=path, retrieval_method='graph_expansion', explanation=f"Found via graph expansion from node {initial_node} at depth {depth}")
                    results.append(result)
                neighbors = list(self.combined_graph.neighbors(current_node))
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        new_path = path + [neighbor]
                        queue.append((neighbor, depth + 1, new_path))
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    def path_retrieval(self, query: str, max_path_length: int = 5, max_results: int = 20) -> List[RetrievalResult]:
        initial_nodes = self._find_initial_nodes(query)
        if not initial_nodes:
            return []
        results = []
        visited = set()
        for start_node in initial_nodes:
            if start_node in visited:
                continue
            visited.add(start_node)
            for end_node in self.memories.keys():
                if end_node == start_node or end_node in visited:
                    continue
                try:
                    path = nx.shortest_path(self.combined_graph, start_node, end_node)
                    if len(path) <= max_path_length:
                        memory = self.memories[end_node]
                        relevance_score = self._compute_path_relevance(query, memory, path)
                        result = RetrievalResult(memory_id=end_node, title=memory['title'], content=memory['content'], type=memory['type'], category=memory['category'], importance=memory['importance'], relevance_score=relevance_score, retrieval_path=path, retrieval_method='path_retrieval', explanation=f"Found via path from node {start_node} to node {end_node} (length: {len(path)})")
                        results.append(result)
                        visited.add(end_node)
                except nx.NetworkXNoPath:
                    continue
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    def community_retrieval(self, query: str, max_results: int = 20) -> List[RetrievalResult]:
        communities = nx.community.greedy_modularity_communities(self.combined_graph.to_undirected())
        relevant_communities = []
        for community in communities:
            for node_id in community:
                if node_id in self.memories:
                    memory = self.memories[node_id]
                    if self._keyword_match(query, memory['title'] + ' ' + memory['content']):
                        relevant_communities.append(community)
                        break
        if not relevant_communities:
            return []
        results = []
        for community in relevant_communities:
            for node_id in community:
                if node_id in self.memories and len(results) < max_results:
                    memory = self.memories[node_id]
                    relevance_score = self._compute_relevance(query, memory, 0, [node_id])
                    result = RetrievalResult(memory_id=node_id, title=memory['title'], content=memory['content'], type=memory['type'], category=memory['category'], importance=memory['importance'], relevance_score=relevance_score, retrieval_path=[node_id], retrieval_method='community_retrieval', explanation=f"Found in relevant community (size: {len(community)})")
                    results.append(result)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    def centrality_retrieval(self, query: str, max_results: int = 20) -> List[RetrievalResult]:
        degree_centrality = nx.degree_centrality(self.combined_graph)
        betweenness_centrality = nx.betweenness_centrality(self.combined_graph)
        closeness_centrality = nx.closeness_centrality(self.combined_graph)
        results = []
        for node_id in self.memories.keys():
            memory = self.memories[node_id]
            centrality_score = degree_centrality.get(node_id, 0) * 0.4 + betweenness_centrality.get(node_id, 0) * 0.3 + closeness_centrality.get(node_id, 0) * 0.3
            relevance_score = self._compute_relevance(query, memory, 0, [node_id])
            combined_score = relevance_score * 0.7 + centrality_score * 0.3
            result = RetrievalResult(memory_id=node_id, title=memory['title'], content=memory['content'], type=memory['type'], category=memory['category'], importance=memory['importance'], relevance_score=combined_score, retrieval_path=[node_id], retrieval_method='centrality_retrieval', explanation=f"Found via centrality-based retrieval (centrality: {centrality_score:.2f})")
            results.append(result)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]

    def hybrid_retrieval(self, query: str, max_results: int = 20) -> List[RetrievalResult]:
        graph_expansion_results = self.graph_expansion_retrieval(query, max_depth=2, max_results=max_results)
        path_results = self.path_retrieval(query, max_path_length=3, max_results=max_results)
        community_results = self.community_retrieval(query, max_results=max_results)
        centrality_results = self.centrality_retrieval(query, max_results=max_results)
        all_results = defaultdict(lambda: {'memory_id': None, 'title': '', 'content': '', 'type': '', 'category': '', 'importance': 0.0, 'relevance_scores': [], 'retrieval_paths': [], 'retrieval_methods': [], 'explanations': []})
        for result in graph_expansion_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['relevance_scores'].append(result.relevance_score)
            all_results[result.memory_id]['retrieval_paths'].append(result.retrieval_path)
            all_results[result.memory_id]['retrieval_methods'].append(result.retrieval_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
        for result in path_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['relevance_scores'].append(result.relevance_score)
            all_results[result.memory_id]['retrieval_paths'].append(result.retrieval_path)
            all_results[result.memory_id]['retrieval_methods'].append(result.retrieval_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
        for result in community_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['relevance_scores'].append(result.relevance_score)
            all_results[result.memory_id]['retrieval_paths'].append(result.retrieval_path)
            all_results[result.memory_id]['retrieval_methods'].append(result.retrieval_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
        for result in centrality_results:
            all_results[result.memory_id]['memory_id'] = result.memory_id
            all_results[result.memory_id]['title'] = result.title
            all_results[result.memory_id]['content'] = result.content
            all_results[result.memory_id]['type'] = result.type
            all_results[result.memory_id]['category'] = result.category
            all_results[result.memory_id]['importance'] = result.importance
            all_results[result.memory_id]['relevance_scores'].append(result.relevance_score)
            all_results[result.memory_id]['retrieval_paths'].append(result.retrieval_path)
            all_results[result.memory_id]['retrieval_methods'].append(result.retrieval_method)
            all_results[result.memory_id]['explanations'].append(result.explanation)
        final_results = []
        for memory_id, data in all_results.items():
            avg_relevance_score = np.mean(data['relevance_scores'])
            combined_explanation = '; '.join(data['explanations'])
            result = RetrievalResult(memory_id=data['memory_id'], title=data['title'], content=data['content'], type=data['type'], category=data['category'], importance=data['importance'], relevance_score=avg_relevance_score, retrieval_path=data['retrieval_paths'][0] if data['retrieval_paths'] else [], retrieval_method='hybrid', explanation=f"Hybrid retrieval: {combined_explanation}")
            final_results.append(result)
        final_results.sort(key=lambda x: x.relevance_score, reverse=True)
        return final_results[:max_results]

    def _find_initial_nodes(self, query: str) -> List[int]:
        initial_nodes = []
        query_lower = query.lower()
        for memory_id, memory in self.memories.items():
            if self._keyword_match(query_lower, memory['title'] + ' ' + memory['content']):
                initial_nodes.append(memory_id)
        return initial_nodes

    def _keyword_match(self, query: str, text: str) -> bool:
        query_lower = query.lower()
        text_lower = text.lower()
        keywords = query_lower.split()
        for keyword in keywords:
            if keyword in text_lower:
                return True
        return False

    def _compute_relevance(self, query: str, memory: Dict, depth: int, path: List[int]) -> float:
        keyword_score = self._compute_keyword_score(query, memory)
        depth_penalty = 1.0 / (1.0 + depth)
        path_penalty = 1.0 / (1.0 + len(path))
        importance_weight = memory['importance'] / 10.0
        relevance_score = keyword_score * 0.5 + depth_penalty * 0.2 + path_penalty * 0.2 + importance_weight * 0.1
        return relevance_score

    def _compute_path_relevance(self, query: str, memory: Dict, path: List[int]) -> float:
        keyword_score = self._compute_keyword_score(query, memory)
        path_quality = self._compute_path_quality(path)
        importance_weight = memory['importance'] / 10.0
        relevance_score = keyword_score * 0.5 + path_quality * 0.3 + importance_weight * 0.2
        return relevance_score

    def _compute_keyword_score(self, query: str, memory: Dict) -> float:
        query_lower = query.lower()
        text = memory['title'] + ' ' + memory['content']
        text_lower = text.lower()
        keywords = query_lower.split()
        match_count = sum(1 for keyword in keywords if keyword in text_lower)
        return match_count / len(keywords) if keywords else 0.0

    def _compute_path_quality(self, path: List[int]) -> float:
        if len(path) <= 1:
            return 1.0
        path_strength = 0.0
        for i in range(len(path) - 1):
            if self.combined_graph.has_edge(path[i], path[i+1]):
                edge_data = self.combined_graph.get_edge_data(path[i], path[i+1])
                if edge_data:
                    strength = edge_data.get('strength', 0.0)
                    path_strength += strength
        return path_strength / (len(path) - 1) if len(path) > 1 else 0.0

if __name__ == "__main__":
    print("Testing Graph-Based Retrieval...")
    retrieval = GraphBasedRetrieval("memory/database/xiaozhi_memory.db")
    load_result = retrieval.load_graphs(limit=100)
    print(f"Loaded {load_result['memories']} memories, {load_result['causal_edges']} causal edges, {load_result['knowledge_edges']} knowledge edges")
    results = retrieval.graph_expansion_retrieval("python", max_depth=2, max_results=10)
    print(f"Graph expansion retrieval: {len(results)} results")
    results = retrieval.path_retrieval("python", max_path_length=3, max_results=10)
    print(f"Path retrieval: {len(results)} results")
    results = retrieval.community_retrieval("python", max_results=10)
    print(f"Community retrieval: {len(results)} results")
    results = retrieval.centrality_retrieval("python", max_results=10)
    print(f"Centrality retrieval: {len(results)} results")
    results = retrieval.hybrid_retrieval("python", max_results=10)
    print(f"Hybrid retrieval: {len(results)} results")
    print("Graph-Based Retrieval test complete!")
