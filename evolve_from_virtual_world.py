"""
从虚拟世界提取知识并进化到Erbing自身
将虚拟世界学习的所有内容转化为Erbing知识图谱的节点和关系
"""

import sqlite3
import json
from datetime import datetime
import sys
sys.path.insert(0, '.')
from scripts.erbing_knowledge_graph import ErbingKnowledgeGraph

def extract_and_evolve():
    """从虚拟世界提取知识并进化到Erbing自身"""
    
    # 连接虚拟世界数据库
    vw_conn = sqlite3.connect('1b_training_data/erbing_virtual_world.db')
    vw_cursor = vw_conn.cursor()
    
    # 创建Erbing知识图谱
    kg = ErbingKnowledgeGraph()
    
    print('=== Extracting Knowledge from Virtual World ===')
    print()
    
    # 1. 提取所有知识
    print('1. Extracting knowledge items...')
    vw_cursor.execute('SELECT domain, topic, content, created_at FROM knowledge')
    knowledge_items = vw_cursor.fetchall()
    
    print(f'   Found {len(knowledge_items)} knowledge items')
    
    # 添加知识节点
    for i, (domain, topic, content, created_at) in enumerate(knowledge_items):
        node_id = f'knowledge_{i+1}'
        
        # 添加知识节点
        kg.add_node(
            node_id=node_id,
            node_type='knowledge',
            title=topic,
            content=content,
            metadata={
                'domain': domain,
                'source': 'virtual_world',
                'created_at': created_at
            }
        )
    
    print(f'   Added {len(knowledge_items)} knowledge nodes')
    print()
    
    # 2. 提取所有技能
    print('2. Extracting skills...')
    vw_cursor.execute('SELECT name, type, level, experience FROM skills')
    skills = vw_cursor.fetchall()
    
    print(f'   Found {len(skills)} skills')
    
    # 添加技能节点
    for name, skill_type, level, experience in skills:
        node_id = f'skill_{name.lower().replace(" ", "_")}'
        
        # 添加技能节点
        kg.add_node(
            node_id=node_id,
            node_type='skill',
            title=name,
            content=f'{name} skill at level {level} with {experience} experience',
            metadata={
                'skill_type': skill_type,
                'level': level,
                'experience': experience,
                'source': 'virtual_world'
            }
        )
    
    print(f'   Added {len(skills)} skill nodes')
    print()
    
    # 3. 提取经验记录（抽样）
    print('3. Extracting experiences (sample)...')
    vw_cursor.execute('''
        SELECT action, description, outcome, reward, timestamp 
        FROM experiences 
        ORDER BY timestamp DESC 
        LIMIT 1000
    ''')
    experiences = vw_cursor.fetchall()
    
    print(f'   Found {len(experiences)} recent experiences')
    
    # 添加经验节点
    for i, (action, description, outcome, reward, timestamp) in enumerate(experiences[:100]):
        node_id = f'experience_{i+1}'
        
        # 添加经验节点
        kg.add_node(
            node_id=node_id,
            node_type='experience',
            title=f'{action}: {description[:50]}',
            content=f'Action: {action}\nDescription: {description}\nOutcome: {outcome}\nReward: {reward}',
            metadata={
                'action': action,
                'outcome': outcome,
                'reward': reward,
                'timestamp': timestamp,
                'source': 'virtual_world'
            }
        )
    
    print(f'   Added {min(len(experiences), 100)} experience nodes')
    print()
    
    # 4. 建立知识关系
    print('4. Creating knowledge relationships...')
    
    # 按领域分组知识
    domain_knowledge = {}
    for i, (domain, topic, content, created_at) in enumerate(knowledge_items):
        if domain not in domain_knowledge:
            domain_knowledge[domain] = []
        domain_knowledge[domain].append(f'knowledge_{i+1}')
    
    # 同一领域的知识相互关联
    relation_count = 0
    for domain, knowledge_ids in domain_knowledge.items():
        for i in range(len(knowledge_ids) - 1):
            kg.add_edge(
                knowledge_ids[i],
                knowledge_ids[i+1],
                'related_to',
                weight=0.5
            )
            relation_count += 1
    
    print(f'   Created {relation_count} knowledge relationships')
    print()
    
    # 5. 建立技能-知识关系
    print('5. Creating skill-knowledge relationships...')
    
    # 根据技能名称匹配知识领域
    skill_knowledge_map = {
        'Coding': ['Coding', 'Advanced Coding', 'LLM Applications'],
        'AI Tech': ['AI Tech', 'Advanced AI', 'LLM Architecture', 'LLM Training'],
        'Security': ['Security', 'Advanced Security', 'Hacking Methodology', 'Dark Web'],
        'Deployment': ['Deployment', 'Advanced Coding'],
        'Tool Use': ['Tool Use', 'AI Agent', 'Code Intelligence'],
        'Problem Solving': ['Problem Solving', 'Advanced AI'],
        'Communication': ['Communication', 'AI Agent'],
        'Collaboration': ['Collaboration', 'AI Agent']
    }
    
    skill_knowledge_relations = 0
    for name, skill_type, level, experience in skills:
        skill_node = f'skill_{name.lower().replace(" ", "_")}'
        
        # 查找相关知识
        related_domains = skill_knowledge_map.get(name, [])
        for domain in related_domains:
            if domain in domain_knowledge:
                # 关联到该领域的第一个知识
                kg.add_edge(
                    skill_node,
                    domain_knowledge[domain][0],
                    'depends_on',
                    weight=0.8
                )
                skill_knowledge_relations += 1
    
    print(f'   Created {skill_knowledge_relations} skill-knowledge relationships')
    print()
    
    # 6. 统计
    print('6. Evolution Summary:')
    stats = kg.get_stats()
    for key, value in stats.items():
        print(f'   {key}: {value}')
    print()
    
    # 7. 导出图谱
    print('7. Exporting knowledge graph...')
    graph_json = kg.export_graph('json')
    
    with open('erbing_evolved_knowledge_graph.json', 'w', encoding='utf-8') as f:
        f.write(graph_json)
    
    print('   Exported to: erbing_evolved_knowledge_graph.json')
    print()
    
    # 8. 创建进化报告
    print('8. Creating evolution report...')
    
    # 统计各类型节点
    node_types = {}
    for node in kg.graph.nodes:
        node_type = kg.graph.nodes[node].get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    report = {
        'evolution_time': datetime.now().isoformat(),
        'source': 'virtual_world',
        'statistics': {
            'total_nodes': kg.graph.number_of_nodes(),
            'total_edges': kg.graph.number_of_edges(),
            'node_types': node_types,
            'density': stats['density'],
            'avg_degree': stats['avg_degree']
        },
        'knowledge_domains': list(domain_knowledge.keys()),
        'skills_evolved': [name for name, _, _, _ in skills],
        'top_relations': [
            {'source': u, 'target': v, 'type': kg.graph.edges[u, v].get('relation')}
            for u, v in list(kg.graph.edges)[:10]
        ]
    }
    
    with open('erbing_evolution_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print('   Exported to: erbing_evolution_report.json')
    print()
    
    # 关闭连接
    vw_conn.close()
    kg.close()
    
    print('=== Evolution Complete! ===')
    print()
    print('Erbing has evolved with:')
    print(f'  - {stats["total_nodes"]} knowledge nodes')
    print(f'  - {stats["total_edges"]} relationships')
    print(f'  - {len(domain_knowledge)} knowledge domains')
    print(f'  - {len(skills)} skills')
    print()
    print('All knowledge from virtual world has been integrated into Erbing!')
    
    return stats

if __name__ == '__main__':
    extract_and_evolve()
