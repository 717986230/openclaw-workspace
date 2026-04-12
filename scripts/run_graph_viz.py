#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""运行组合图谱可视化"""

import sys
sys.path.insert(0, '.')

from scripts.knowledge_graph_visualization import KnowledgeGraphVisualizer, KnowledgeGraphLayout

def main():
    print("正在启动知识图谱可视化...")
    
    # 创建可视化器
    visualizer = KnowledgeGraphVisualizer("memory/database/xiaozhi_memory.db")
    
    # 加载数据
    load_result = visualizer.load_from_database(limit=100)
    print(f"加载了 {load_result['nodes']} 个节点, {load_result['edges']} 条边")
    
    # 获取统计信息
    stats = visualizer.get_graph_statistics()
    print(f"图谱统计: {stats}")
    
    # 可视化
    save_path = "knowledge_graph.html"
    fig = visualizer.visualize(
        layout=KnowledgeGraphLayout.SPRING,
        save_path=save_path
    )
    print(f"可视化已保存到: {save_path}")
    
    # 自动打开HTML文件
    import os
    os.startfile(save_path)
    print("已打开可视化界面")
    
    return save_path

if __name__ == "__main__":
    main()
