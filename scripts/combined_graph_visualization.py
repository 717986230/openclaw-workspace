#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组合图谱可视化
Combined Graph Visualization

同时展示因果关系和知识点关系的组合图谱可视化
"""

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import sqlite3
import json
from scripts.causal_graph_visualization import CausalGraphVisualizer, CausalGraphLayout
from scripts.knowledge_graph_visualization import KnowledgeGraphVisualizer, KnowledgeGraphLayout

class CombinedGraphLayout(Enum):
    """组合图谱布局"""
    SPRING = "spring"
    CIRCULAR = "circular"
    RANDOM = "random"
    SHELL = "shell"
    KAMADA_KAWAI = "kamada_kawai"
    FRUCHTERMAN_REINGOLD = "fruchterman_reingold"

@dataclass
class CombinedNode:
    """组合节点"""
    id: int
    label: str
    type: str
    category: str
    importance: float
    created_at: str

@dataclass
class CombinedEdge:
    """组合边"""
    source: int
    target: int
    edge_type: str  # 'causal' or 'knowledge'
    relation_type: str
    strength: float
    confidence: float
    direction: str

class CombinedGraphVisualizer:
    """组合图谱可视化器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()
        self.nodes = {}
        self.edges = {}

        # 初始化子可视化器
        self.causal_visualizer = CausalGraphVisualizer(db_path)
        self.knowledge_visualizer = KnowledgeGraphVisualizer(db_path)

    def load_from_database(self, limit: int = 100) -> Dict:
        """从数据库加载图谱数据"""
        # 加载因果关系
        causal_result = self.causal_visualizer.load_from_database(limit)

        # 加载知识点关系
        knowledge_result = self.knowledge_visualizer.load_from_database(limit)

        # 合并节点
        for node_id, node in self.causal_visualizer.nodes.items():
            if node_id not in self.nodes:
                self.nodes[node_id] = node
                self.graph.add_node(node_id, **node.__dict__)

        for node_id, node in self.knowledge_visualizer.nodes.items():
            if node_id not in self.nodes:
                self.nodes[node_id] = node
                self.graph.add_node(node_id, **node.__dict__)

        # 合并边（因果关系）
        for edge_key, edge in self.causal_visualizer.edges.items():
            combined_edge = CombinedEdge(
                source=edge.source,
                target=edge.target,
                edge_type='causal',
                relation_type=edge.causal_type,
                strength=edge.strength,
                confidence=edge.confidence,
                direction='forward'
            )
            self.edges[(edge.source, edge.target, 'causal')] = combined_edge
            self.graph.add_edge(edge.source, edge.target, **combined_edge.__dict__)

        # 合并边（知识点关系）
        for edge_key, edge in self.knowledge_visualizer.edges.items():
            combined_edge = CombinedEdge(
                source=edge.source,
                target=edge.target,
                edge_type='knowledge',
                relation_type=edge.relation_type,
                strength=edge.relation_strength,
                confidence=0.0,
                direction=edge.relation_direction
            )
            self.edges[(edge.source, edge.target, 'knowledge')] = combined_edge
            self.graph.add_edge(edge.source, edge.target, **combined_edge.__dict__)

        return {
            'nodes': len(self.nodes),
            'causal_edges': len([e for e in self.edges.values() if e.edge_type == 'causal']),
            'knowledge_edges': len([e for e in self.edges.values() if e.edge_type == 'knowledge']),
            'total_edges': len(self.edges)
        }

    def compute_layout(self, layout: CombinedGraphLayout = CombinedGraphLayout.SPRING) -> Dict:
        """计算图谱布局"""
        if layout == CombinedGraphLayout.SPRING:
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == CombinedGraphLayout.CIRCULAR:
            pos = nx.circular_layout(self.graph)
        elif layout == CombinedGraphLayout.RANDOM:
            pos = nx.random_layout(self.graph)
        elif layout == CombinedGraphLayout.SHELL:
            pos = nx.shell_layout(self.graph)
        elif layout == CombinedGraphLayout.KAMADA_KAWAI:
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == CombinedGraphLayout.FRUCHTERMAN_REINGOLD:
            pos = nx.fruchterman_reingold_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph)

        return pos

    def create_node_trace(self, pos: Dict) -> go.Scatter:
        """创建节点轨迹"""
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        for node_id in self.graph.nodes():
            x, y = pos[node_id]
            node_x.append(x)
            node_y.append(y)

            node = self.nodes[node_id]
            node_text.append(
                f"{node.label}<br>"
                f"Type: {node.type}<br>"
                f"Category: {node.category}<br>"
                f"Importance: {node.importance}"
            )

            # 根据重要性设置节点大小
            node_size.append(10 + node.importance * 5)

            # 根据类别设置节点颜色
            color_map = {
                'knowledge': '#1f77b4',
                'learning': '#ff7f0e',
                'event': '#2ca02c',
                'preference': '#d62728',
                'decision': '#9467bd',
                'test': '#8c564b'
            }
            node_color.append(color_map.get(node.category, '#7f7f7f'))

        return go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            text=[self.nodes[nid].label for nid in self.graph.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            name='Nodes'
        )

    def create_causal_edge_trace(self, pos: Dict) -> go.Scatter:
        """创建因果关系边轨迹"""
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in self.edges.values():
            if edge.edge_type != 'causal':
                continue

            x0, y0 = pos[edge.source]
            x1, y1 = pos[edge.target]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_text.append(
                f"Type: Causal<br>"
                f"Relation: {edge.relation_type}<br>"
                f"Strength: {edge.strength:.2f}<br>"
                f"Confidence: {edge.confidence:.2f}"
            )

        return go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=3, color='red'),
            hovertext=edge_text,
            hoverinfo='text',
            name='Causal Edges'
        )

    def create_knowledge_edge_trace(self, pos: Dict) -> go.Scatter:
        """创建知识点关系边轨迹"""
        edge_x = []
        edge_y = []
        edge_text = []
        edge_colors = []

        # 关系类型颜色映射
        relation_colors = {
            'is_a': '#1f77b4',
            'part_of': '#ff7f0e',
            'related_to': '#2ca02c',
            'similar_to': '#d62728',
            'opposite_of': '#9467bd',
            'depends_on': '#8c564b',
            'precedes': '#e377c2',
            'follows': '#7f7f7f',
            'causes': '#bcbd22',
            'caused_by': '#17becf',
            'contains': '#aec7e8',
            'contained_in': '#ffbb78',
            'exemplifies': '#98df8a',
            'exemplified_by': '#ff9896',
            'context_for': '#c5b0d5',
            'context_of': '#c49c94'
        }

        for edge in self.edges.values():
            if edge.edge_type != 'knowledge':
                continue

            x0, y0 = pos[edge.source]
            x1, y1 = pos[edge.target]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_text.append(
                f"Type: Knowledge<br>"
                f"Relation: {edge.relation_type}<br>"
                f"Strength: {edge.strength:.2f}<br>"
                f"Direction: {edge.direction}"
            )

            edge_colors.append(relation_colors.get(edge.relation_type, '#7f7f7f'))

        return go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=2, color=edge_colors),
            hovertext=edge_text,
            hoverinfo='text',
            name='Knowledge Edges'
        )

    def visualize(self, layout: CombinedGraphLayout = CombinedGraphLayout.SPRING,
                  show_causal: bool = True,
                  show_knowledge: bool = True,
                  save_path: Optional[str] = None) -> go.Figure:
        """可视化组合图谱"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建轨迹
        node_trace = self.create_node_trace(pos)

        traces = [node_trace]

        if show_causal:
            causal_edge_trace = self.create_causal_edge_trace(pos)
            traces.append(causal_edge_trace)

        if show_knowledge:
            knowledge_edge_trace = self.create_knowledge_edge_trace(pos)
            traces.append(knowledge_edge_trace)

        # 创建图形
        fig = go.Figure(data=traces,
                       layout=go.Layout(
                           title='Combined Graph Visualization (Causal + Knowledge)',
                           titlefont_size=16,
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[
                               dict(
                                   text="Red: Causal Relations | Colored: Knowledge Relations",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(size=12)
                               )
                           ],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        # 保存图形
        if save_path:
            fig.write_html(save_path)
            print(f"Graph saved to {save_path}")

        return fig

    def visualize_separated(self, layout: CombinedGraphLayout = CombinedGraphLayout.SPRING,
                            save_path: Optional[str] = None) -> go.Figure:
        """分离可视化（两个子图）"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Causal Graph', 'Knowledge Graph'),
            specs=[[{'type': 'scatter'}, {'type': 'scatter'}]]
        )

        # 因果图谱
        causal_node_trace = self.create_node_trace(pos)
        causal_edge_trace = self.create_causal_edge_trace(pos)

        fig.add_trace(causal_edge_trace, row=1, col=1)
        fig.add_trace(causal_node_trace, row=1, col=1)

        # 知识图谱
        knowledge_node_trace = self.create_node_trace(pos)
        knowledge_edge_trace = self.create_knowledge_edge_trace(pos)

        fig.add_trace(knowledge_edge_trace, row=1, col=2)
        fig.add_trace(knowledge_node_trace, row=1, col=2)

        # 更新布局
        fig.update_layout(
            title='Separated Graph Visualization',
            titlefont_size=16,
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40)
        )

        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
        fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

        # 保存图形
        if save_path:
            fig.write_html(save_path)
            print(f"Graph saved to {save_path}")

        return fig

    def filter_by_edge_type(self, edge_type: str, layout: CombinedGraphLayout = CombinedGraphLayout.SPRING,
                          save_path: Optional[str] = None) -> go.Figure:
        """按边类型过滤可视化"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建节点轨迹
        node_trace = self.create_node_trace(pos)

        # 创建边轨迹
        if edge_type == 'causal':
            edge_trace = self.create_causal_edge_trace(pos)
            title = 'Causal Graph Only'
        elif edge_type == 'knowledge':
            edge_trace = self.create_knowledge_edge_trace(pos)
            title = 'Knowledge Graph Only'
        else:
            edge_trace = go.Scatter()
            title = 'No Edges'

        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=title,
                           titlefont_size=16,
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        # 保存图形
        if save_path:
            fig.write_html(save_path)
            print(f"Graph saved to {save_path}")

        return fig

    def export_graph(self, format: str = 'json', save_path: str = 'combined_graph.json') -> bool:
        """导出图谱"""
        if format == 'json':
            data = {
                'nodes': [node.__dict__ for node in self.nodes.values()],
                'edges': [edge.__dict__ for edge in self.edges.values()]
            }

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Graph exported to {save_path}")
            return True

        elif format == 'gexf':
            nx.write_gexf(self.graph, save_path)
            print(f"Graph exported to {save_path}")
            return True

        elif format == 'graphml':
            nx.write_graphml(self.graph, save_path)
            print(f"Graph exported to {save_path}")
            return True

        else:
            print(f"Unsupported format: {format}")
            return False

    def get_graph_statistics(self) -> Dict:
        """获取图谱统计信息"""
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'num_causal_edges': len([e for e in self.edges.values() if e.edge_type == 'causal']),
            'num_knowledge_edges': len([e for e in self.edges.values() if e.edge_type == 'knowledge']),
            'density': nx.density(self.graph),
            'is_directed': self.graph.is_directed(),
            'is_connected': nx.is_weakly_connected(self.graph),
            'num_components': nx.number_weakly_connected_components(self.graph)
        }

        if self.graph.number_of_nodes() > 0:
            stats['avg_degree'] = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
            stats['max_degree'] = max(dict(self.graph.degree()).values())
            stats['min_degree'] = min(dict(self.graph.degree()).values())

        # 关系类型统计
        causal_relation_counts = {}
        knowledge_relation_counts = {}

        for edge in self.edges.values():
            if edge.edge_type == 'causal':
                causal_relation_counts[edge.relation_type] = causal_relation_counts.get(edge.relation_type, 0) + 1
            elif edge.edge_type == 'knowledge':
                knowledge_relation_counts[edge.relation_type] = knowledge_relation_counts.get(edge.relation_type, 0) + 1

        stats['causal_relation_counts'] = causal_relation_counts
        stats['knowledge_relation_counts'] = knowledge_relation_counts

        return stats


if __name__ == "__main__":
    # 测试代码
    print("Testing Combined Graph Visualization...")

    # 创建可视化器
    visualizer = CombinedGraphVisualizer("memory/database/xiaozhi_memory.db")

    # 加载数据
    load_result = visualizer.load_from_database(limit=50)
    print(f"Loaded {load_result['nodes']} nodes, {load_result['causal_edges']} causal edges, {load_result['knowledge_edges']} knowledge edges")

    # 获取统计信息
    stats = visualizer.get_graph_statistics()
    print(f"Graph statistics: {stats}")

    # 可视化组合图谱
    fig = visualizer.visualize(
        layout=CombinedGraphLayout.SPRING,
        show_causal=True,
        show_knowledge=True,
        save_path="combined_graph.html"
    )
    print("Combined graph visualization created")

    # 分离可视化
    fig_separated = visualizer.visualize_separated(
        layout=CombinedGraphLayout.SPRING,
        save_path="combined_graph_separated.html"
    )
    print("Separated graph visualization created")

    # 只显示因果关系
    fig_causal = visualizer.filter_by_edge_type(
        edge_type='causal',
        layout=CombinedGraphLayout.SPRING,
        save_path="combined_graph_causal.html"
    )
    print("Causal graph visualization created")

    # 只显示知识点关系
    fig_knowledge = visualizer.filter_by_edge_type(
        edge_type='knowledge',
        layout=CombinedGraphLayout.SPRING,
        save_path="combined_graph_knowledge.html"
    )
    print("Knowledge graph visualization created")

    # 导出图谱
    visualizer.export_graph(format='json', save_path='combined_graph.json')
    print("Graph exported")

    print("Combined Graph Visualization test complete!")
