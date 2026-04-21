"""
Erbing MCP Tools
基于GitNexus思想的MCP工具集，为Erbing提供标准化的知识操作接口
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from .erbing_knowledge_graph import ErbingKnowledgeGraph

class ErbingMCPTools:
    """
    Erbing的MCP工具集（类似GitNexus）
    提供16个核心工具 + 资源系统
    """
    
    def __init__(self, db_path='memory/database/xiaozhi_memory.db'):
        self.kg = ErbingKnowledgeGraph(db_path)
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict:
        """注册所有工具"""
        return {
            # 单上下文工具（11个）
            'list_contexts': self.list_contexts,
            'query': self.query,
            'get_context': self.get_context,
            'analyze_impact': self.analyze_impact,
            'detect_changes': self.detect_changes,
            'safe_rename': self.safe_rename,
            'add_node': self.add_node,
            'add_edge': self.add_edge,
            'update_node': self.update_node,
            'delete_node': self.delete_node,
            'query_graph': self.query_graph,
            
            # 多上下文工具（5个）
            'group_list': self.group_list,
            'group_sync': self.group_sync,
            'group_query': self.group_query,
            'group_status': self.group_status,
            'group_contracts': self.group_contracts,
        }
    
    # ==================== 单上下文工具（11个）====================
    
    def list_contexts(self) -> Dict:
        """
        列出所有上下文（类似GitNexus的list_repos）
        
        Returns:
            上下文列表
        """
        stats = self.kg.get_stats()
        return {
            'contexts': [
                {
                    'name': 'main_workspace',
                    'type': 'workspace',
                    'stats': stats,
                    'last_updated': datetime.now().isoformat()
                }
            ],
            'total_contexts': 1
        }
    
    def query(self, query: str, context: str = None, limit: int = 10) -> List[Dict]:
        """
        知识查询（类似GitNexus的query）
        使用BM25 + 语义搜索 + RRF
        
        Args:
            query: 查询字符串
            context: 上下文名称（可选）
            limit: 结果数量限制
            
        Returns:
            匹配结果列表
        """
        return self.kg.query(query, limit)
    
    def get_context(self, node_id: str, depth: int = 2) -> Dict:
        """
        获取节点上下文（类似GitNexus的context）
        提供360度符号视图
        
        Args:
            node_id: 节点ID
            depth: 搜索深度
            
        Returns:
            节点上下文
        """
        return self.kg.get_node_context(node_id, depth)
    
    def analyze_impact(self, node_id: str) -> Dict:
        """
        影响分析（类似GitNexus的impact）
        分析节点变更的爆炸半径
        
        Args:
            node_id: 节点ID
            
        Returns:
            影响分析结果
        """
        return self.kg.analyze_impact(node_id)
    
    def detect_changes(self, old_content: str, new_content: str) -> Dict:
        """
        检测变更（类似GitNexus的detect_changes）
        分析内容变更的影响
        
        Args:
            old_content: 旧内容
            new_content: 新内容
            
        Returns:
            变更分析结果
        """
        # 简单的差异检测
        old_lines = set(old_content.split('\n'))
        new_lines = set(new_content.split('\n'))
        
        added = new_lines - old_lines
        removed = old_lines - new_lines
        unchanged = old_lines & new_lines
        
        return {
            'added': len(added),
            'removed': len(removed),
            'unchanged': len(unchanged),
            'change_ratio': len(added | removed) / len(old_lines) if old_lines else 0,
            'details': {
                'added_lines': list(added)[:10],
                'removed_lines': list(removed)[:10]
            }
        }
    
    def safe_rename(self, old_name: str, new_name: str, dry_run: bool = True) -> Dict:
        """
        安全重命名（类似GitNexus的rename）
        跨节点的协调重命名
        
        Args:
            old_name: 旧名称
            new_name: 新名称
            dry_run: 是否只预览
            
        Returns:
            重命名结果
        """
        # 查找所有相关节点
        results = self.kg.query(old_name)
        
        if not dry_run:
            # 实际执行重命名
            for result in results:
                node = self.kg.get_node(result['node_id'])
                if node:
                    updated_title = node.get('title', '').replace(old_name, new_name)
                    updated_content = node.get('content', '').replace(old_name, new_name)
                    self.kg.add_node(
                        result['node_id'],
                        node.get('type'),
                        updated_title,
                        updated_content,
                        node.get('metadata')
                    )
        
        return {
            'old_name': old_name,
            'new_name': new_name,
            'affected_nodes': len(results),
            'dry_run': dry_run,
            'affected_details': results
        }
    
    def add_node(self, node_id: str, node_type: str, title: str = None, 
                 content: str = None, metadata: Dict = None) -> Dict:
        """添加节点"""
        node_id = self.kg.add_node(node_id, node_type, title, content, metadata)
        return {
            'node_id': node_id,
            'status': 'created',
            'node': self.kg.get_node(node_id)
        }
    
    def add_edge(self, source_id: str, target_id: str, relation_type: str, 
                 weight: float = 1.0, attributes: Dict = None) -> Dict:
        """添加关系边"""
        edge_id = self.kg.add_edge(source_id, target_id, relation_type, weight, attributes)
        return {
            'edge_id': edge_id,
            'status': 'created',
            'source': source_id,
            'target': target_id,
            'relation': relation_type
        }
    
    def update_node(self, node_id: str, updates: Dict) -> Dict:
        """更新节点"""
        node = self.kg.get_node(node_id)
        if not node:
            return {'node_id': node_id, 'status': 'not_found'}
        
        # 合并更新
        node_type = updates.get('type', node.get('type'))
        title = updates.get('title', node.get('title'))
        content = updates.get('content', node.get('content'))
        metadata = updates.get('metadata', node.get('metadata'))
        
        self.kg.add_node(node_id, node_type, title, content, metadata)
        
        return {
            'node_id': node_id,
            'status': 'updated',
            'node': self.kg.get_node(node_id)
        }
    
    def delete_node(self, node_id: str) -> Dict:
        """删除节点"""
        node = self.kg.get_node(node_id)
        if not node:
            return {'node_id': node_id, 'status': 'not_found'}
        
        # 删除所有相关边
        edges_to_remove = []
        for u, v in self.kg.graph.edges():
            if u == node_id or v == node_id:
                edges_to_remove.append((u, v))
        
        for u, v in edges_to_remove:
            self.kg.graph.remove_edge(u, v)
        
        # 删除节点
        self.kg.graph.remove_node(node_id)
        
        return {
            'node_id': node_id,
            'status': 'deleted',
            'removed_edges': len(edges_to_remove)
        }
    
    def query_graph(self, cypher_query: str) -> Dict:
        """
        图查询（类似GitNexus的cypher）
        执行Cypher风格的图查询
        
        Args:
            cypher_query: Cypher查询字符串
            
        Returns:
            查询结果
        """
        # 简化的Cypher查询解析
        # 支持: MATCH (n:Type) RETURN n
        if 'MATCH' in cypher_query and 'RETURN' in cypher_query:
            # 提取节点类型
            if ':memory' in cypher_query:
                node_type = 'memory'
            elif ':knowledge' in cypher_query:
                node_type = 'knowledge'
            elif ':skill' in cypher_query:
                node_type = 'skill'
            else:
                node_type = None
            
            # 查询节点
            results = []
            for node_id in self.kg.graph.nodes:
                node = self.kg.get_node(node_id)
                if node:
                    if node_type is None or node.get('type') == node_type:
                        results.append({
                            'node_id': node_id,
                            **node
                        })
            
            return {
                'query': cypher_query,
                'results': results,
                'total': len(results)
            }
        
        return {
            'query': cypher_query,
            'error': 'Unsupported query format',
            'results': []
        }
    
    # ==================== 多上下文工具（5个）====================
    
    def group_list(self) -> Dict:
        """列出所有组"""
        return {
            'groups': [
                {
                    'name': 'main_group',
                    'contexts': ['main_workspace'],
                    'created_at': datetime.now().isoformat()
                }
            ],
            'total_groups': 1
        }
    
    def group_sync(self, group_name: str) -> Dict:
        """同步组"""
        return {
            'group_name': group_name,
            'status': 'synced',
            'synced_at': datetime.now().isoformat(),
            'stats': self.kg.get_stats()
        }
    
    def group_query(self, query: str, groups: List[str] = None) -> List[Dict]:
        """跨组查询"""
        return self.kg.query(query)
    
    def group_status(self, group_name: str) -> Dict:
        """检查组状态"""
        stats = self.kg.get_stats()
        return {
            'group_name': group_name,
            'status': 'active',
            'stats': stats,
            'last_sync': datetime.now().isoformat(),
            'staleness': 0  # 0表示最新
        }
    
    def group_contracts(self, group_name: str) -> Dict:
        """检查组合约"""
        return {
            'group_name': group_name,
            'contracts': [],
            'cross_links': [],
            'total_contracts': 0
        }
    
    # ==================== 资源系统 ====================
    
    def get_resource(self, resource_uri: str) -> Dict:
        """
        获取资源（类似GitNexus的资源URI）
        
        Args:
            resource_uri: 资源URI（如 erbing://contexts）
            
        Returns:
            资源内容
        """
        if resource_uri == 'erbing://contexts':
            return self.list_contexts()
        elif resource_uri.startswith('erbing://context/'):
            parts = resource_uri.split('/')
            if len(parts) >= 4:
                context_name = parts[2]
                resource_type = parts[3]
                
                if resource_type == 'stats':
                    return self.kg.get_stats()
                elif resource_type == 'clusters':
                    return self.kg.find_clusters()
                elif resource_type == 'memories':
                    return {'memories': [n for n in self.kg.graph.nodes if self.kg.get_node(n).get('type') == 'memory']}
                elif resource_type == 'skills':
                    return {'skills': [n for n in self.kg.graph.nodes if self.kg.get_node(n).get('type') == 'skill']}
                elif resource_type == 'schema':
                    return {
                        'node_types': ['memory', 'knowledge', 'skill', 'experience'],
                        'relation_types': ['depends_on', 'related_to', 'causes', 'references', 'contains']
                    }
        
        return {'error': 'Resource not found', 'uri': resource_uri}
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict:
        """调用工具"""
        if tool_name not in self.tools:
            return {'error': f'Tool {tool_name} not found'}
        
        try:
            result = self.tools[tool_name](**kwargs)
            return {
                'tool': tool_name,
                'status': 'success',
                'result': result
            }
        except Exception as e:
            return {
                'tool': tool_name,
                'status': 'error',
                'error': str(e)
            }
    
    def close(self):
        """关闭连接"""
        self.kg.close()


# 使用示例
if __name__ == '__main__':
    tools = ErbingMCPTools()
    
    print('=== Erbing MCP Tools Demo ===')
    print()
    
    # 测试工具
    print('1. List Contexts:')
    print(tools.call_tool('list_contexts'))
    print()
    
    print('2. Add Node:')
    print(tools.call_tool('add_node', 
                          node_id='test_1',
                          node_type='memory',
                          title='Test Memory',
                          content='This is a test memory'))
    print()
    
    print('3. Get Context:')
    print(tools.call_tool('get_context', node_id='test_1'))
    print()
    
    print('4. Analyze Impact:')
    print(tools.call_tool('analyze_impact', node_id='test_1'))
    print()
    
    print('5. Query:')
    print(tools.call_tool('query', query='test'))
    print()
    
    print('6. Get Resource:')
    print(tools.get_resource('erbing://contexts'))
    print()
    
    tools.close()
