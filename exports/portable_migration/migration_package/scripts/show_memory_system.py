#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory System Status Display
"""

import sqlite3
import json
from datetime import datetime

def show_memory_system_status():
    print("=" * 70)
    print("MEMORY SYSTEM STATUS - COMPLETE OVERVIEW")
    print("=" * 70)
    
    # Database connection
    conn = sqlite3.connect('memory/database/xiaozhi_memory.db')
    cursor = conn.cursor()
    
    # 1. Basic Statistics
    print("\n[1] BASIC STATISTICS")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM memories")
    total_memories = cursor.fetchone()[0]
    print(f"Total memories: {total_memories}")
    
    cursor.execute("SELECT COUNT(*) FROM knowledge_relations")
    knowledge_relations = cursor.fetchone()[0]
    print(f"Knowledge relations: {knowledge_relations}")
    
    cursor.execute("SELECT COUNT(*) FROM causal_relations")
    causal_relations = cursor.fetchone()[0]
    print(f"Causal relations: {causal_relations}")
    
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
    total_tables = cursor.fetchone()[0]
    print(f"Total tables: {total_tables}")
    
    # 2. Memory Types Distribution
    print("\n[2] MEMORY TYPES DISTRIBUTION")
    print("-" * 70)
    
    cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:5d}")
    
    # 3. Memory Categories
    print("\n[3] MEMORY CATEGORIES")
    print("-" * 70)
    
    cursor.execute("SELECT category, COUNT(*) FROM memories GROUP BY category")
    for row in cursor.fetchall():
        category = row[0] if row[0] else 'None'
        print(f"  {category:30s}: {row[1]:5d}")
    
    # 4. Recent Memories
    print("\n[4] RECENT MEMORIES (Last 5)")
    print("-" * 70)
    
    cursor.execute("SELECT id, type, title, created_at FROM memories ORDER BY created_at DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]:10s} - {row[2][:40]:40s}")
        print(f"       Created: {row[3]}")
    
    # 5. Knowledge Relation Types
    print("\n[5] KNOWLEDGE RELATION TYPES")
    print("-" * 70)
    
    cursor.execute("SELECT relation_type, COUNT(*) FROM knowledge_relations GROUP BY relation_type")
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:5d}")
    
    # 6. Causal Relation Types
    print("\n[6] CAUSAL RELATION TYPES")
    print("-" * 70)
    
    cursor.execute("SELECT causal_type, COUNT(*) FROM causal_relations GROUP BY causal_type")
    for row in cursor.fetchall():
        print(f"  {row[0]:20s}: {row[1]:5d}")
    
    # 7. High Importance Memories
    print("\n[7] HIGH IMPORTANCE MEMORIES (Importance >= 8)")
    print("-" * 70)
    
    cursor.execute("SELECT id, title, importance FROM memories WHERE importance >= 8 ORDER BY importance DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1][:40]:40s} - Importance: {row[2]}")
    
    # 8. Database Tables
    print("\n[8] DATABASE TABLES")
    print("-" * 70)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i:2d}. {table_name}")
    
    conn.close()
    
    # 9. Genetic Neuron System
    print("\n[9] GENETIC NEURON SYSTEM")
    print("-" * 70)
    
    try:
        with open('genetic_neuron_system.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"  Genome ID: {data['genome_id']}")
        print(f"  Generation: {data['generation']}")
        print(f"  Best Fitness: {data['best_fitness']:.4f}")
        print(f"  Node Genes: {len(data['node_genes'])}")
        print(f"  Connection Genes: {len(data['connection_genes'])}")
        print(f"  Fitness History: {len(data['fitness_history'])} entries")
    except FileNotFoundError:
        print("  [INFO] Genetic neuron system not initialized yet")
    
    # 10. System Capabilities
    print("\n[10] SYSTEM CAPABILITIES")
    print("-" * 70)
    
    capabilities = [
        "Genetic Encoding (NEAT-based)",
        "Genetic Mutation (Weight, Node, Connection)",
        "Synaptic Plasticity (Hebbian, STDP)",
        "Neurogenesis (Neuron Growth & Pruning)",
        "Memory Consolidation (LTP, Replay)",
        "Attention Mechanism (Spatial, Temporal)",
        "Neuromodulation (Dopamine, Serotonin, NE)",
        "Spiking Neural Networks (SNN)",
        "Structural Plasticity (Dynamic Rewiring)",
        "Heterogeneous Neurons (10 Types)",
        "Modularity (Functional Modules)",
        "Evolution Strategies (CMA-ES, OpenAI-ES, QD)",
        "Graph-Based Retrieval",
        "Intelligent Recommendation",
        "LLM Integration (Detection, Generation, Q&A)",
        "Auto-Update Relation Strength",
        "Auto Cleanup & Optimization",
        "Advanced Graph Analysis",
        "System Optimization",
        "Security & Privacy",
        "Real-time Monitoring & Alerting",
        "Backup & Recovery",
        "Multi-user Support"
    ]
    
    for i, capability in enumerate(capabilities, 1):
        print(f"  {i:2d}. {capability}")
    
    print("\n" + "=" * 70)
    print(f"[STATUS] Memory System Overview Complete - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    show_memory_system_status()
