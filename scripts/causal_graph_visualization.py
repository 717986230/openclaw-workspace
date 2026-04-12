#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
因果关系图谱可视化
Causal Graph Visualization

使用NetworkX和Plotly实现交互式因果关系图谱可视化
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

class CausalGraphLayout(Enum):
    """图谱布局"""
    SPRING = "spring"
    CIRCULAR = "circular"
    RANDOM = "random"
    SHELL = "shell"
    KAMADA_KAWAI = "kamada_kawai"
    FRUCHTERMAN_REINGOLD = "fruchterman_reingold"

@dataclass
class CausalNode:
    """因果节点"""
    id: int
    label: str
    type: str
    importance: float
    created_at: str

@dataclass
class CausalEdge:
    """因果边"""
    source: int
    target: int
    causal_type: str
    strength: float
    confidence: float
    evidence: str

class CausalGraphVisualizer:
    """因果关系图谱可视化器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.edges = {}

    def load_from_database(self, limit: int = 100) -> Dict:
        """从数据库加载图谱数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 加载记忆节点
        cursor.execute("""
            SELECT id, title, type, importance, created_at
            FROM memories
            LIMIT ?
        """, (limit,))

        for row in cursor.fetchall():
            node = CausalNode(
                id=row[0],
                label=row[1],
                type=row[2],
                importance=row[3],
                created_at=row[4]
            )
            self.nodes[node.id] = node
            self.graph.add_node(node.id, **node.__dict__)

        # 加载因果关系边
        cursor.execute("""
            SELECT cause_memory_id, effect_memory_id, causal_type, strength, confidence, evidence
            FROM causal_relations
            WHERE cause_memory_id IN (SELECT id FROM memories LIMIT ?)
            AND effect_memory_id IN (SELECT id FROM memories LIMIT ?)
        """, (limit, limit))

        for row in cursor.fetchall():
            edge = CausalEdge(
                source=row[0],
                target=row[1],
                causal_type=row[2],
                strength=row[3],
                confidence=row[4],
                evidence=row[5]
            )
            self.edges[(edge.source, edge.target)] = edge
            self.graph.add_edge(edge.source, edge.target, **edge.__dict__)

        conn.close()

        return {
            'nodes': len(self.nodes),
            'edges': len(self.edges)
        }

    def compute_layout(self, layout: CausalGraphLayout = CausalGraphLayout.SPRING) -> Dict:
        """计算图谱布局"""
        if layout == CausalGraphLayout.SPRING:
            pos = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout == CausalGraphLayout.CIRCULAR:
            pos = nx.circular_layout(self.graph)
        elif layout == CausalGraphLayout.RANDOM:
            pos = nx.random_layout(self.graph)
        elif layout == CausalGraphLayout.SHELL:
            pos = nx.shell_layout(self.graph)
        elif layout == CausalGraphLayout.KAMADA_KAWAI:
            pos = nx.kamada_kawai_layout(self.graph)
        elif layout == CausalGraphLayout.FRUCHTERMAN_REINGOLD:
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
            node_text.append(f"{node.label}<br>Type: {node.type}<br>Importance: {node.importance}")

            # 根据重要性设置节点大小
            node_size.append(10 + node.importance * 5)

            # 根据类型设置节点颜色
            color_map = {
                'learning': '#1f77b4',
                'event': '#ff7f0e',
                'preference': '#2ca02c',
                'decision': '#d62728',
                'test': '#9467bd'
            }
            node_color.append(color_map.get(node.type, '#7f7f7f'))

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

    def create_edge_trace(self, pos: Dict) -> go.Scatter:
        """创建边轨迹"""
        edge_x = []
        edge_y = []
        edge_text = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_data = self.edges[edge]
            edge_text.append(
                f"Type: {edge_data.causal_type}<br>"
                f"Strength: {edge_data.strength:.2f}<br>"
                f"Confidence: {edge_data.confidence:.2f}"
            )

        return go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=2, color='gray'),
            hovertext=edge_text,
            hoverinfo='text',
            name='Edges'
        )

    def create_arrow_trace(self, pos: Dict) -> go.Scatter:
        """创建箭头轨迹"""
        arrow_x = []
        arrow_y = []

        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # 计算箭头位置（在边的中间）
            arrow_x.append((x0 + x1) / 2)
            arrow_y.append((y0 + y1) / 2)

        return go.Scatter(
            x=arrow_x,
            y=arrow_y,
            mode='markers',
            marker=dict(
                symbol='triangle-up',
                size=10,
                color='red',
                angle=0
            ),
            name='Arrows'
        )

    def visualize(self, layout: CausalGraphLayout = CausalGraphLayout.SPRING,
                  save_path: Optional[str] = None) -> go.Figure:
        """可视化图谱"""
        # 计算布局
        pos = self.compute_layout(layout)

        # 创建轨迹
        node_trace = self.create_node_trace(pos)
        edge_trace = self.create_edge_trace(pos)
        arrow_trace = self.create_arrow_trace(pos)

        # 创建图形
        fig = go.Figure(data=[edge_trace, arrow_trace, node_trace],
                       layout=go.Layout(
                           title=dict(text='Causal Graph Visualization', font=dict(size=16)),
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           annotations=[
                               dict(
                                   text="Causal Relationships",
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

    def visualize_subgraph(self, center_node: int, radius: int = 2,
                          layout: CausalGraphLayout = CausalGraphLayout.SPRING,
                          save_path: Optional[str] = None) -> go.Figure:
        """可视化子图"""
        # 获取子图
        subgraph_nodes = set([center_node])

        for _ in range(radius):
            new_nodes = set()
            for node in subgraph_nodes:
                neighbors = list(self.graph.neighbors(node)) + list(self.graph.predecessors(node))
                new_nodes.update(neighbors)
            subgraph_nodes.update(new_nodes)

        # 创建子图
        subgraph = self.graph.subgraph(subgraph_nodes)

        # 计算布局
        if layout == CausalGraphLayout.SPRING:
            pos = nx.spring_layout(subgraph, k=1, iterations=50)
        elif layout == CausalGraphLayout.CIRCULAR:
            pos = nx.circular_layout(subgraph)
        elif layout == CausalGraphLayout.RANDOM:
            pos = nx.random_layout(subgraph)
        elif layout == CausalGraphLayout.SHELL:
            pos = nx.shell_layout(subgraph)
        elif layout == CausalGraphLayout.KAMADA_KAWAI:
            pos = nx.kamada_kawai_layout(subgraph)
        elif layout == CausalGraphLayout.FRUCHTERMAN_REINGOLD:
            pos = nx.fruchterman_reingold_layout(subgraph)
        else:
            pos = nx.spring_layout(subgraph)

        # 创建轨迹
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        for node_id in subgraph.nodes():
            x, y = pos[node_id]
            node_x.append(x)
            node_y.append(y)

            node = self.nodes[node_id]
            node_text.append(f"{node.label}<br>Type: {node.type}<br>Importance: {node.importance}")

            node_size.append(10 + node.importance * 5)

            color_map = {
                'learning': '#1f77b4',
                'event': '#ff7f0e',
                'preference': '#2ca02c',
                'decision': '#d62728',
                'test': '#9467bd'
            }
            node_color.append(color_map.get(node.type, '#7f7f7f'))

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            text=[self.nodes[nid].label for nid in subgraph.nodes()],
            textposition="top center",
            hovertext=node_text,
            hoverinfo='text',
            name='Nodes'
        )

        edge_x = []
        edge_y = []
        edge_text = []

        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

            edge_data = self.edges[edge]
            edge_text.append(
                f"Type: {edge_data.causal_type}<br>"
                f"Strength: {edge_data.strength:.2f}<br>"
                f"Confidence: {edge_data.confidence:.2f}"
            )

        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            mode='lines',
            line=dict(width=2, color='gray'),
            hovertext=edge_text,
            hoverinfo='text',
            name='Edges'
        )

        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=dict(text=f'Causal Graph Subgraph (Center: {self.nodes[center_node].label}, Radius: {radius})', font=dict(size=16)),
                           showlegend=True,
                           hovermode='closest',
                           margin=dict(b=20, l=5, r=5, t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))

        # 保存图形
        if save_path:
            fig.write_html(save_path)
            print(f"Subgraph saved to {save_path}")

        return fig

    def export_graph(self, format: str = 'json', save_path: str = 'causal_graph.json') -> bool:
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

        return stats


if __name__ == "__main__":
    # 测试代码
    print("Testing Causal Graph Visualization...")

    # 创建可视化器
    visualizer = CausalGraphVisualizer("memory/database/xiaozhi_memory.db")

    # 加载数据
    load_result = visualizer.load_from_database(limit=50)
    print(f"Loaded {load_result['nodes']} nodes and {load_result['edges']} edges")

    # 获取统计信息
    stats = visualizer.get_graph_statistics()
    print(f"Graph statistics: {stats}")

    # 可视化图谱
    fig = visualizer.visualize(layout=CausalGraphLayout.SPRING, save_path="causal_graph.html")
    print("Graph visualization created")

    # 可视化子图
    if visualizer.nodes:
        first_node = list(visualizer.nodes.keys())[0]
        subgraph_fig = visualizer.visualize_subgraph(
            center_node=first_node,
            radius=2,
            layout=CausalGraphLayout.SPRING,
            save_path="causal_subgraph.html"
        )
        print("Subgraph visualization created")

    # 导出图谱
    visualizer.export_graph(format='json', save_path='causal_graph.json')
    print("Graph exported")

    print("Causal Graph Visualization test complete!")
