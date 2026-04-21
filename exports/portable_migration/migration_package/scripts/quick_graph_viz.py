#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速知识图谱可视化 - 独立版本"""

import sqlite3
import networkx as nx
import plotly.graph_objects as go
from collections import defaultdict

def create_interactive_graph():
    """创建交互式知识图谱"""
    
    # 连接数据库
    db_path = "C:/Users/Administrator/.openclaw/workspace/memory/database/xiaozhi_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取记忆节点
    cursor.execute("""
        SELECT id, type, title, category, importance, created_at
        FROM memories
        ORDER BY importance DESC
        LIMIT 100
    """)
    nodes = cursor.fetchall()
    
    # 获取关系
    cursor.execute("""
        SELECT source_memory_id, target_memory_id, relation_type, relation_strength
        FROM knowledge_relations
        WHERE source_memory_id IN (SELECT id FROM memories ORDER BY importance DESC LIMIT 100)
        AND target_memory_id IN (SELECT id FROM memories ORDER BY importance DESC LIMIT 100)
    """)
    edges = cursor.fetchall()
    
    conn.close()
    
    print(f"加载了 {len(nodes)} 个节点, {len(edges)} 条边")
    
    # 创建图谱
    G = nx.DiGraph()
    
    # 节点字典
    node_dict = {}
    for node in nodes:
        node_id, node_type, title, category, importance, created_at = node
        node_dict[node_id] = {
            'label': title[:30] if title else f"Node {node_id}",
            'type': node_type,
            'category': category or 'unknown',
            'importance': importance or 5
        }
        G.add_node(node_id)
    
    # 添加边
    for edge in edges:
        source_id, target_id, relation_type, strength = edge
        if source_id in node_dict and target_id in node_dict:
            G.add_edge(source_id, target_id, relation=relation_type, strength=strength or 0.5)
    
    # 计算布局
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 创建节点轨迹
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    color_map = {
        'knowledge': '#1f77b4',
        'learning': '#ff7f0e',
        'event': '#2ca02c',
        'preference': '#d62728',
        'decision': '#9467bd',
        'test': '#8c564b',
        'unknown': '#7f7f7f'
    }
    
    for node_id in G.nodes():
        if node_id not in pos:
            continue
        x, y = pos[node_id]
        node_x.append(x)
        node_y.append(y)
        
        node = node_dict.get(node_id, {})
        label = node.get('label', f"Node {node_id}")
        category = node.get('category', 'unknown')
        importance = node.get('importance', 5)
        
        node_text.append(f"{label}<br>Category: {category}<br>Importance: {importance}")
        node_size.append(10 + importance * 3)
        node_color.append(color_map.get(category, '#7f7f7f'))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color='white'),
            showscale=False
        ),
        text=[node_dict.get(nid, {}).get('label', f"Node {nid}") for nid in G.nodes() if nid in pos],
        textposition="top center",
        hovertext=node_text,
        hoverinfo='text',
        name='Nodes'
    )
    
    # 创建边轨迹
    edge_x = []
    edge_y = []
    edge_colors = []
    
    relation_colors = {
        'related_to': '#2ca02c',
        'is_a': '#1f77b4',
        'part_of': '#ff7f0e',
        'similar_to': '#d62728',
        'opposite_of': '#9467bd',
        'depends_on': '#8c564b'
    }
    
    for edge in G.edges(data=True):
        source, target, data = edge
        if source in pos and target in pos:
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_colors.append(relation_colors.get(data.get('relation', 'related_to'), '#aaaaaa'))
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1.5, color='#888888'),
        hoverinfo='none',
        name='Edges'
    )
    
    # 创建图形
    fig = go.Figure(data=[edge_trace, node_trace],
        layout=go.Layout(
            title=dict(text='知识点关系图谱 (交互式可视化)', font=dict(size=16)),
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            paper_bgcolor='white',
            plot_bgcolor='white'
        ))
    
    # 添加图例
    fig.update_layout(
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # 保存并打开
    save_path = "C:/Users/Administrator/.openclaw/workspace/knowledge_graph_interactive.html"
    fig.write_html(save_path)
    print(f"可视化已保存到: {save_path}")
    
    # 自动打开
    import os
    os.startfile(save_path)
    print("已打开可视化界面！")
    
    return save_path

if __name__ == "__main__":
    create_interactive_graph()
