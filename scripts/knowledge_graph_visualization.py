#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识点关系图谱可视化
Knowledge Graph Visualization

使用NetworkX和Plotly实现交互式知识点关系图谱可视化
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

class KnowledgeGraphLayout(Enum):
    """图谱布局"""
    SPRING = "spring"
    CIRCULAR = "circular"
    RANDOM = "random"
    SHELL = "shell"
    KAMADA_KAWAI = "kamada_kawai"
    FRUCHTERMAN_REINGOLD = "fruchterman_reingold"
    BIPARTITE = "bipartite"

class RelationType(Enum):
    """关系类型"""
    IS_A = "is_a"
    PART_OF = "part_of"
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"
    OPPOSITE_OF = "opposite_of"
    DEPENDS_ON = "depends_on"
    PRECEDES = "precedes"
    FOLLOWS = "follows"
    CAUSES = "causes"
    CAUSED_BY = "caused_by"
    CONTAINS = "contains"
    CONTAINED_IN = "contained_in"
    EXEMPLIFIES = "exemplifies"
    EXEMPLIFIED_BY = "exemplified_by"
    CONTEXT_FOR = "context_for"
    CONTEXT_OF = "context_of"

@dataclass
class KnowledgeNode:
    """知识节点"""
    id: int
    label: str
    type: str
    category: str
    importance: float
    created_at: str

@dataclass
class KnowledgeEdge:
    """知识边"""
    source: int
    target: int
    relation_type: str
    relation_strength: float
    relation_direction: str
    attributes: str

class KnowledgeGraphVisualizer:
    """知识点关系图谱可视化器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.MultiDiGraph()
        self.nodes = {}
        self.edges = {}

        # 关系类型颜色映射
        self.relation_colors = {
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

    def load_from_database(self, limit: int = 100) -> Dict:
        """从数据库加载图谱数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 加载记忆节点
        cursor.execute("""
            SELECT id, title, type, category, importance, created_at
            FROM memories
            LIMIT ?
        """, (limit,))

        for row in cursor.fetchall():
            node = KnowledgeNode(
                id=row[0],
                label=row[1],
                type=row[2],
                category=row[3] if row[3] else 'general',
                importance=row[4],
                created_at=row[5]
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)

        # 加载知识点关系边
        cursor.execute("""
            SELECT source_memory_id, target_memory_id, relation_type,
                   relation_strength, relation_direction, attributes
            FROM knowledge_relations
            WHERE source_memory_id IN (SELECT id FROM memories LIMIT ?)
            AND target_memory_id IN (SELECT id FROM memories LIMIT ?)
        """, (limit, limit))

        for row in cursor.fetchall():
            edge = KnowledgeEdge(
                source=row[0],
                target=row[1],
                relation_type=row[2],
                relation_strength=row[3],
                relation_direction=row[4],
                attributes=row[5]
            )
            self.edges[(edge.source, edge.target)] = edge
            self.graph.add_edge(edge.source, edge.target, **edge.__dict__)

        conn.close()

        return {
            'nodes': len(self.nodes),
            'edges': len(self.edges)
        }

    def compute_layout(self, layout: KnowledgeGraphLayout = KnowledgeGraphLayout.SPRING) -> Dict:
        """计算图谱布局"""
        if layout == KnowledgeGraphLayout.SPRING:
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == KnowledgeGraphLayout.CIRCULAR:
            pos = nx.circular_layout(self.graph)
        elif layout == KnowledgeGraphLayout.RANDOM:
            pos = nx.random_layout(self.graph)
        elif layout == KnowledgeGraphLayout.SHELL:
            pos = nx.shell_layout(self.graph)
        elif layout == KnowledgeGraphLayout.KAMADA_KAWAI:
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == KnowledgeGraphLayout.FRUCHTERMAN_REINGOLD:
            pos = nx.fruchterman_reingold_layout(self.graph)
        elif layout == KnowledgeGraphLayout.BIPARTITE:
            pos = nx.bipartite_layout(self.graph, list(self.nodes.keys())[:len(self.nodes)//2])
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

    def create_edge_trace(self, pos: Dict, relation_type: Optional[str] = None) -> go.Scatter:
        """创建边轨迹"""
        edge_x = []
        edge_y = []
        edge_text = []
        edge_colors = []

        for edge in self.graph.edges(keys=True):
            edge_data = self.edges[(edge[0], edge[1])]

            # 过滤关系类型
            if relation_type and edge_data.relation_type != relation_type:
                continue

            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_text.append(
                f"Type: {edge_data.relation_type}<br>"
                f"Strength: {edge_data.relation_strength:.2f}<br>"
                f"Direction: {edge_data.relation_direction}"
            )

            # 根据关系类型设置边颜色
            edge_colors.append(self.relation_colors.get(edge_data.relation_type, '#7f7f7f'))

        return go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=2, color=edge_colors),
            hovertext=edge_text,
            hoverinfo='text',
            name=f'Edges ({relation_type})' if relation_type else 'Edges'
        )

    def visualize(self, layout: KnowledgeGraphLayout = KnowledgeGraphLayout.SPRING,
                  filter_relation: Optional[str] = None,
                  save_path: Optional[str] = None) -> go.Figure:
        """可视化图谱"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建轨迹
        node_trace = self.create_node_trace(pos)
        edge_trace = self.create_edge_trace(pos, filter_relation)

        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='Knowledge Graph Visualization',
                           titlefont_size=16,
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[
                               dict(
                                   text="Knowledge Relationships",
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

    def visualize_by_relation_type(self, layout: KnowledgeGraphLayout = KnowledgeGraphLayout.SPRING,
                                    save_path: Optional[str] = None) -> go.Figure:
        """按关系类型可视化"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建节点轨迹
        node_trace = self.create_node_trace(pos)

        # 为每种关系类型创建边轨迹
        edge_traces = []
        for relation_type in self.relation_colors.keys():
            edge_trace = self.create_edge_trace(pos, relation_type)
            if len(edge_trace.x) > 0:
                edge_traces.append(edge_trace)

        # 创建图形
        fig = go.Figure(data=edge_traces + [node_trace],
                       layout=go.Layout(
                           title='Knowledge Graph by Relation Type',
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

    def visualize_communities(self, layout: KnowledgeGraphLayout = KnowledgeGraphLayout.SPRING,
                              save_path: Optional[str] = None) -> go.Figure:
        """可视化社区"""
        # 检测社区
        communities = nx.community.greedy_modularity_communities(self.graph.to_undirected())

        # 计算布局
        pos = self.compute_layout(layout)

        # 为每个社区创建节点轨迹
        node_traces = []
        for i, community in enumerate(communities):
            node_x = []
            node_y = []
            node_text = []
            node_size = []

            for node_id in community:
                if node_id in pos:
                    x, y = pos[node_id]
                    node_x.append(x)
                    node_y.append(y)

                    node = self.nodes[node_id]
                    node_text.append(f"{node.label}")

                    node_size.append(10 + node.importance * 5)

            # 为每个社区使用不同的颜色
            colors = px.colors.qualitative.Plotly
            color = colors[i % len(colors)]

            node_trace = go.Scatter(
                x=node_x,
                y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_size,
                    color=color,
                    line=dict(width=2, color='white')
                ),
                text=node_text,
                textposition="top center",
                hovertext=node_text,
                hoverinfo='text',
                name=f'Community {i+1}'
            )
            node_traces.append(node_trace)

        # 创建边轨迹
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_data = self.edges[(edge[0], edge[1])]
            edge_text.append(
                f"Type: {edge_data.relation_type}<br>"
                f"Strength: {edge_data.relation_strength:.2f}"
            )

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=1, color='gray'),
            hovertext=edge_text,
            hoverinfo='text',
            name='Edges'
        )

        # 创建图形
        fig = go.Figure(data=[edge_trace] + node_traces,
                       layout=go.Layout(
                           title=f'Knowledge Graph Communities ({len(communities)} communities)',
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

    def export_graph(self, format: str = 'json', save_path: str = 'knowledge_graph.json') -> bool:
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
        relation_counts = {}
        for edge in self.edges.values():
            relation_counts[edge.relation_type] = relation_counts.get(edge.relation_type, 0) + 1
        stats['relation_counts'] = relation_counts

        return stats


if __name__ == "__main__":
    # 测试代码
    print("Testing Knowledge Graph Visualization...")

    # 创建可视化器
    visualizer = KnowledgeGraphVisualizer("memory/database/xiaozhi_memory.db")

    # 加载数据
    load_result = visualizer.load_from_database(limit=50)
    print(f"Loaded {load_result['nodes']} nodes and {load_result['edges']} edges")

    # 获取统计信息
    stats = visualizer.get_graph_statistics()
    print(f"Graph statistics: {stats}")

    # 可视化图谱
    fig = visualizer.visualize(layout=KnowledgeGraphLayout.SPRING, save_path="knowledge_graph.html")
    print("Graph visualization created")

    # 按关系类型可视化
    fig_by_type = visualizer.visualize_by_relation_type(
        layout=KnowledgeGraphLayout.SPRING,
        save_path="knowledge_graph_by_type.html"
    )
    print("Graph by relation type visualization created")

    # 可视化社区
    fig_communities = visualizer.visualize_communities(
        layout=KnowledgeGraphLayout.SPRING,
        save_path="knowledge_graph_communities.html"
    )
    print("Graph communities visualization created")

    # 导出图谱
    visualizer.export_graph(format='json', save_path='knowledge_graph.json')
    print("Graph exported")

    print("Knowledge Graph Visualization test complete!")
