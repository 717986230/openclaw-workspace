#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级图谱分析
Advanced Graph Analysis
"""

import sqlite3
import numpy as np
import networkx as nx
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

class AnalysisType(Enum):
    PATH_ANALYSIS = "path_analysis"
    CENTRALITY_ANALYSIS = "centrality_analysis"
    CLUSTERING_ANALYSIS = "clustering_analysis"
    COMMUNITY_DETECTION = "community_detection"

@dataclass
class AnalysisResult:
    analysis_type: str
    results: Dict
    explanation: str

class AdvancedGraphAnalysis:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()
        self.memories = {}

    def load_graph(self, limit: int = 1000) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM memories LIMIT ?", (limit,))
        for row in cursor.fetchall():
            self.memories[row[0]] = {'id': row[0], 'title': row[1]}
            self.graph.add_node(row[0])

        cursor.execute("SELECT source_memory_id, target_memory_id, relation_strength FROM knowledge_relations WHERE source_memory_id IN (SELECT id FROM memories LIMIT ?) AND target_memory_id IN (SELECT id FROM memories LIMIT ?)", (limit, limit))
        for row in cursor.fetchall():
            self.graph.add_edge(row[0], row[1], strength=row[2])

        conn.close()
        return {'nodes': self.graph.number_of_nodes(), 'edges': self.graph.number_of_edges()}

    def path_analysis(self, source_id: int, target_id: int) -> AnalysisResult:
        if source_id not in self.graph or target_id not in self.graph:
            return AnalysisResult(analysis_type='path_analysis', results={}, explanation='Source or target node not found')
        try:
            shortest_path = nx.shortest_path(self.graph, source_id, target_id)
            all_paths = list(nx.all_simple_paths(self.graph, source_id, target_id, cutoff=5))
            path_length = len(shortest_path)
            path_weight = self._compute_path_weight(shortest_path)
            results = {
                'shortest_path': shortest_path,
                'path_length': path_length,
                'path_weight': path_weight,
                'all_paths_count': len(all_paths),
                'all_paths': all_paths[:10]
            }
            explanation = f'Found shortest path of length {path_length} with weight {path_weight:.2f}'
        except nx.NetworkXNoPath:
            results = {'shortest_path': [], 'path_length': 0, 'path_weight': 0.0, 'all_paths_count': 0, 'all_paths': []}
            explanation = 'No path found between nodes'
        return AnalysisResult(analysis_type='path_analysis', results=results, explanation=explanation)

    def centrality_analysis(self) -> AnalysisResult:
        if self.graph.number_of_nodes() == 0:
            return AnalysisResult(analysis_type='centrality_analysis', results={}, explanation='Graph is empty')
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)
        closeness_centrality = nx.closeness_centrality(self.graph)
        eigenvector_centrality = nx.eigenvector_centrality(self.graph, max_iter=1000)
        pagerank = nx.pagerank(self.graph)
        results = {
            'degree_centrality': degree_centrality,
            'betweenness_centrality': betweenness_centrality,
            'closeness_centrality': closeness_centrality,
            'eigenvector_centrality': eigenvector_centrality,
            'pagerank': pagerank,
            'top_degree': sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_betweenness': sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10],
            'top_pagerank': sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        explanation = f'Computed centrality measures for {self.graph.number_of_nodes()} nodes'
        return AnalysisResult(analysis_type='centrality_analysis', results=results, explanation=explanation)

    def clustering_analysis(self) -> AnalysisResult:
        if self.graph.number_of_nodes() == 0:
            return AnalysisResult(analysis_type='clustering_analysis', results={}, explanation='Graph is empty')
        undirected_graph = self.graph.to_undirected()
        clustering_coefficient = nx.clustering(undirected_graph)
        avg_clustering = nx.average_clustering(undirected_graph)
        results = {
            'clustering_coefficient': clustering_coefficient,
            'average_clustering': avg_clustering,
            'top_clusters': sorted(clustering_coefficient.items(), key=lambda x: x[1], reverse=True)[:10]
        }
        explanation = f'Computed clustering coefficients, average clustering: {avg_clustering:.3f}'
        return AnalysisResult(analysis_type='clustering_analysis', results=results, explanation=explanation)

    def community_detection(self) -> AnalysisResult:
        if self.graph.number_of_nodes() == 0:
            return AnalysisResult(analysis_type='community_detection', results={}, explanation='Graph is empty')
        undirected_graph = self.graph.to_undirected()
        communities = nx.community.greedy_modularity_communities(undirected_graph)
        community_dict = {}
        for i, community in enumerate(communities):
            for node in community:
                community_dict[node] = i
        modularity = nx.community.modularity(undirected_graph, communities)
        results = {
            'num_communities': len(communities),
            'communities': [list(c) for c in communities],
            'community_dict': community_dict,
            'modularity': modularity,
            'community_sizes': [len(c) for c in communities]
        }
        explanation = f'Detected {len(communities)} communities with modularity {modularity:.3f}'
        return AnalysisResult(analysis_type='community_detection', results=results, explanation=explanation)

    def comprehensive_analysis(self) -> Dict:
        results = {}
        results['centrality'] = self.centrality_analysis()
        results['clustering'] = self.clustering_analysis()
        results['community'] = self.community_detection()
        return results

    def _compute_path_weight(self, path: List[int]) -> float:
        if len(path) < 2:
            return 0.0
        total_weight = 0.0
        for i in range(len(path) - 1):
            if self.graph.has_edge(path[i], path[i+1]):
                edge_data = self.graph.get_edge_data(path[i], path[i+1])
                if edge_data:
                    strength = edge_data.get('strength', 0.0)
                    total_weight += strength
        return total_weight

    def get_analysis_statistics(self) -> Dict:
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph.to_undirected()),
            'num_components': nx.number_connected_components(self.graph.to_undirected())
        }
        return stats

if __name__ == "__main__":
    print("Testing Advanced Graph Analysis...")
    analysis = AdvancedGraphAnalysis("memory/database/xiaozhi_memory.db")
    load_result = analysis.load_graph(limit=100)
    print(f"Loaded {load_result['nodes']} nodes, {load_result['edges']} edges")
    result = analysis.centrality_analysis()
    print(f"Centrality analysis: {result.explanation}")
    result = analysis.clustering_analysis()
    print(f"Clustering analysis: {result.explanation}")
    result = analysis.community_detection()
    print(f"Community detection: {result.explanation}")
    if analysis.memories:
        first_id = list(analysis.memories.keys())[0]
        second_id = list(analysis.memories.keys())[1] if len(analysis.memories) > 1 else first_id
        result = analysis.path_analysis(first_id, second_id)
        print(f"Path analysis: {result.explanation}")
    results = analysis.comprehensive_analysis()
    print(f"Comprehensive analysis: {results}")
    stats = analysis.get_analysis_statistics()
    print(f"Statistics: {stats}")
    print("Advanced Graph Analysis test complete!")
