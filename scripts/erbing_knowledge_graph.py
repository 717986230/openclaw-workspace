"""
Erbing Knowledge Graph System
基于GitNexus思想的知识图谱系统，让Erbing能够理解知识之间的关系
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import networkx as nx
from collections import defaultdict

class ErbingKnowledgeGraph:
    """
    Erbing的知识图谱系统（类似GitNexus）
    追踪所有记忆、技能、知识之间的关系
    """
    
    def __init__(self, db_path='memory/database/xiaozhi_memory.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 使用NetworkX进行图分析
        self.graph = nx.DiGraph()
        
        # 节点缓存
        self.nodes_cache = {}
        self.edges_cache = []
        
        # 初始化图谱表
        self._init_graph_tables()
        
        # 加载现有数据
        self._load_existing_data()
    
    def _init_graph_tables(self):
        """初始化知识图谱表"""
        # 知识节点表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 知识关系表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_edges (
                edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                attributes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES knowledge_nodes(node_id),
                FOREIGN KEY (target_id) REFERENCES knowledge_nodes(node_id)
            )
        ''')
        
        # 创建索引
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_type ON knowledge_nodes(node_type)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON knowledge_edges(source_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON knowledge_edges(target_id)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_type ON knowledge_edges(relation_type)')
        
        self.conn.commit()
    
    def _load_existing_data(self):
        """加载现有数据到内存图谱"""
        # 加载节点
        self.cursor.execute('SELECT node_id, node_type, title, content, metadata FROM knowledge_nodes')
        for node_id, node_type, title, content, metadata in self.cursor.fetchall():
            self.graph.add_node(node_id, 
                               type=node_type, 
                               title=title, 
                               content=content,
                               metadata=json.loads(metadata) if metadata else {})
        
        # 加载边
        self.cursor.execute('SELECT source_id, target_id, relation_type, weight FROM knowledge_edges')
        for source_id, target_id, relation_type, weight in self.cursor.fetchall():
            self.graph.add_edge(source_id, target_id, 
                               relation=relation_type, 
                               weight=weight)
    
    def add_node(self, node_id: str, node_type: str, title: str = None, 
                 content: str = None, metadata: Dict = None):
        """
        添加知识节点
        
        Args:
            node_id: 节点唯一ID
            node_type: 节点类型（memory, knowledge, skill, experience等）
            title: 节点标题
            content: 节点内容
            metadata: 元数据字典
        """
        metadata_json = json.dumps(metadata) if metadata else None
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO knowledge_nodes 
            (node_id, node_type, title, content, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (node_id, node_type, title, content, metadata_json, datetime.now()))
        
        self.conn.commit()
        
        # 更新内存图谱
        self.graph.add_node(node_id,
                           type=node_type,
                           title=title,
                           content=content,
                           metadata=metadata or {})
        
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, relation_type: str, 
                 weight: float = 1.0, attributes: Dict = None):
        """
        添加知识关系边
        
        Args:
            source_id: 源节点ID
            target_id: 目标节点ID
            relation_type: 关系类型（depends_on, related_to, causes, references等）
            weight: 关系权重
            attributes: 关系属性
        """
        attributes_json = json.dumps(attributes) if attributes else None
        
        self.cursor.execute('''
            INSERT INTO knowledge_edges 
            (source_id, target_id, relation_type, weight, attributes)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_id, target_id, relation_type, weight, attributes_json))
        
        self.conn.commit()
        
        # 更新内存图谱
        self.graph.add_edge(source_id, target_id,
                           relation=relation_type,
                           weight=weight,
                           attributes=attributes or {})
        
        return self.cursor.lastrowid
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """获取节点信息"""
        if node_id in self.graph.nodes:
            return dict(self.graph.nodes[node_id])
        return None
    
    def get_node_context(self, node_id: str, depth: int = 2) -> Dict:
        """
        获取节点的360度上下文（类似GitNexus的context工具）
        
        Args:
            node_id: 节点ID
            depth: 搜索深度
            
        Returns:
            包含所有相关节点的上下文字典
        """
        if node_id not in self.graph.nodes:
            return {}
        
        # 获取所有相关节点
        predecessors = list(self.graph.predecessors(node_id))
        successors = list(self.graph.successors(node_id))
        
        # 扩展到指定深度
        all_related = set([node_id])
        current_nodes = set(predecessors + successors)
        
        for _ in range(depth - 1):
            next_nodes = set()
            for node in current_nodes:
                if node in self.graph.nodes:
                    next_nodes.update(self.graph.predecessors(node))
                    next_nodes.update(self.graph.successors(node))
            all_related.update(current_nodes)
            current_nodes = next_nodes
        
        all_related.update(current_nodes)
        
        # 构建上下文
        context = {
            'node': self.get_node(node_id),
            'predecessors': {n: self.get_node(n) for n in predecessors if n in all_related},
            'successors': {n: self.get_node(n) for n in successors if n in all_related},
            'all_related': {n: self.get_node(n) for n in all_related if n != node_id},
            'depth': depth,
            'total_nodes': len(all_related)
        }
        
        return context
    
    def query(self, query: str, limit: int = 10) -> List[Dict]:
        """
        知识查询（类似GitNexus的query工具）
        使用BM25 + 语义搜索
        
        Args:
            query: 查询字符串
            limit: 返回结果数量限制
            
        Returns:
            匹配的节点列表
        """
        # 简单的关键词搜索（可以后续集成向量搜索）
        self.cursor.execute('''
            SELECT node_id, node_type, title, content 
            FROM knowledge_nodes 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for node_id, node_type, title, content in self.cursor.fetchall():
            results.append({
                'node_id': node_id,
                'node_type': node_type,
                'title': title,
                'content': content[:200] + '...' if len(content or '') > 200 else content,
                'score': 1.0  # 简单评分
            })
        
        return results
    
    def analyze_impact(self, node_id: str) -> Dict:
        """
        影响分析（类似GitNexus的impact工具）
        分析节点变更对其他节点的影响
        
        Args:
            node_id: 节点ID
            
        Returns:
            影响分析结果
        """
        if node_id not in self.graph.nodes:
            return {}
        
        # 获取所有受影响的节点
        descendants = nx.descendants(self.graph, node_id)
        ancestors = nx.ancestors(self.graph, node_id)
        
        # 按距离分组
        impact_by_distance = defaultdict(list)
        for descendant in descendants:
            distance = nx.shortest_path_length(self.graph, node_id, descendant)
            impact_by_distance[distance].append(descendant)
        
        return {
            'node': self.get_node(node_id),
            'direct_impact': list(self.graph.successors(node_id)),
            'indirect_impact': list(descendants - set(self.graph.successors(node_id))),
            'reverse_dependencies': list(ancestors),
            'impact_by_distance': dict(impact_by_distance),
            'total_impact': len(descendants),
            'blast_radius': len(descendants) + len(ancestors)
        }
    
    def find_clusters(self) -> Dict:
        """
        发现知识集群（类似GitNexus的Leiden社区检测）
        
        Returns:
            知识集群字典
        """
        # 使用NetworkX的社区检测
        if len(self.graph.nodes) < 2:
            return {}
        
        # 转换为无向图进行社区检测
        undirected_graph = self.graph.to_undirected()
        
        # 使用贪婪模块度社区检测
        communities = nx.algorithms.community.greedy_modularity_communities(undirected_graph)
        
        clusters = {}
        for i, community in enumerate(communities):
            cluster_nodes = list(community)
            cluster_info = {
                'cluster_id': i,
                'nodes': cluster_nodes,
                'size': len(cluster_nodes),
                'node_details': [self.get_node(n) for n in cluster_nodes[:10]],
                'cohesion': self._calculate_cohesion(cluster_nodes)
            }
            clusters[i] = cluster_info
        
        return clusters
    
    def _calculate_cohesion(self, nodes: List[str]) -> float:
        """计算集群内聚度"""
        if len(nodes) < 2:
            return 1.0
        
        subgraph = self.graph.subgraph(nodes)
        possible_edges = len(nodes) * (len(nodes) - 1)
        actual_edges = subgraph.number_of_edges()
        
        return actual_edges / possible_edges if possible_edges > 0 else 0.0
    
    def get_shortest_path(self, source: str, target: str) -> List[str]:
        """获取两个节点之间的最短路径"""
        try:
            return nx.shortest_path(self.graph, source, target)
        except nx.NetworkXNoPath:
            return []
    
    def get_stats(self) -> Dict:
        """获取图谱统计信息"""
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': dict(nx.get_node_attributes(self.graph, 'type').values()),
            'relation_types': list(set(nx.get_edge_attributes(self.graph, 'relation').values())),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0
        }
    
    def export_graph(self, format: str = 'json') -> str:
        """导出图谱"""
        if format == 'json':
            data = {
                'nodes': [
                    {
                        'id': node,
                        **self.graph.nodes[node]
                    } for node in self.graph.nodes
                ],
                'edges': [
                    {
                        'source': u,
                        'target': v,
                        **self.graph.edges[u, v]
                    } for u, v in self.graph.edges
                ]
            }
            return json.dumps(data, indent=2)
        elif format == 'gexf':
            return '\n'.join(nx.generate_gexf(self.graph))
        else:
            return ''
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()


# 使用示例
if __name__ == '__main__':
    # 创建知识图谱
    kg = ErbingKnowledgeGraph()
    
    print('=== Erbing Knowledge Graph System ===')
    print(f'Stats: {kg.get_stats()}')
    print()
    
    # 添加示例节点
    kg.add_node('memory_1', 'memory', 'First Memory', 'This is my first memory')
    kg.add_node('knowledge_1', 'knowledge', 'Python Knowledge', 'Python is a programming language')
    kg.add_node('skill_1', 'skill', 'Coding Skill', 'My coding skill')
    
    # 添加关系
    kg.add_edge('memory_1', 'knowledge_1', 'references')
    kg.add_edge('skill_1', 'knowledge_1', 'depends_on')
    
    print('=== Nodes Added ===')
    print(f'Node 1: {kg.get_node("memory_1")}')
    print(f'Node 2: {kg.get_node("knowledge_1")}')
    print(f'Node 3: {kg.get_node("skill_1")}')
    print()
    
    print('=== Context Analysis ===')
    context = kg.get_node_context('knowledge_1')
    print(f'Context: {context}')
    print()
    
    print('=== Impact Analysis ===')
    impact = kg.analyze_impact('knowledge_1')
    print(f'Impact: {impact}')
    print()
    
    print('=== Query Test ===')
    results = kg.query('Python')
    print(f'Query results: {results}')
    print()
    
    print('=== Graph Stats ===')
    print(f'Stats: {kg.get_stats()}')
    
    kg.close()
