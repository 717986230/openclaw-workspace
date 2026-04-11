#!/usr/bin/env python3
"""
Erbing 知识蒸馏 - 训练数据生成器
从数据库记忆生成 QLoRA 微调数据
"""
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Database path (use absolute path)
DB_PATH = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database\xiaozhi_memory.db")

class TrainingDataGenerator:
    """训练数据生成器"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def generate_all_data(self) -> Dict[str, List[Dict]]:
        """生成所有类型的训练数据"""
        return {
            "architecture": self.generate_architecture_data(),
            "code": self.generate_code_data(),
            "retrieval": self.generate_retrieval_data(),
            "knowledge": self.generate_knowledge_data(),
            "conversation": self.generate_conversation_data(),
        }
    
    def generate_architecture_data(self) -> List[Dict]:
        """生成架构设计数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memories 
            WHERE type IN ('architecture', 'milestone', 'learning')
            AND (title LIKE '%架构%' OR title LIKE '%Erbing-1B%' OR title LIKE '%设计%')
            ORDER BY importance DESC
        """)
        
        data = []
        for row in cursor.fetchall():
            mem = dict(row)
            
            # 任务 1: 架构问答
            data.append({
                "instruction": f"请详细介绍 {mem['title']} 的架构设计。",
                "input": "",
                "output": mem['content'][:1500],
                "category": "architecture_qa"
            })
            
            # 任务 2: 架构改进建议
            data.append({
                "instruction": "分析以下架构设计，并提出改进建议：",
                "input": mem['content'][:800],
                "output": f"基于 {mem['title']} 的设计，建议：\n1. 优化数据流路径，减少冗余计算\n2. 增加缓存机制，提升响应速度\n3. 完善错误处理，提高系统稳定性",
                "category": "architecture_improvement"
            })
        
        return data
    
    def generate_code_data(self) -> List[Dict]:
        """生成代码相关数据"""
        # 从文件读取代码
        code_files = [
            ("retrieval_strategies.py", "四策略检索系统"),
            ("migration_plan_v2.py", "数据库迁移方案"),
            ("hybrid_memory.py", "混合记忆系统"),
        ]
        
        data = []
        base_dir = Path(r"C:\Users\Administrator\.openclaw\workspace\memory\database")
        
        for filename, desc in code_files:
            code_path = base_dir / filename
            if code_path.exists():
                code = code_path.read_text(encoding='utf-8')
                
                # 任务 1: 代码解释
                data.append({
                    "instruction": f"请解释以下 {desc} 代码的核心逻辑：",
                    "input": code[:1000],
                    "output": f"这是 {desc} 的核心实现。主要特点包括：\n1. 模块化设计，职责清晰\n2. 高效的数据处理流程\n3. 完善的错误处理机制",
                    "category": "code_explanation"
                })
                
                # 任务 2: 代码补全
                data.append({
                    "instruction": f"根据以下代码片段，补全 {desc} 的实现：",
                    "input": f"# {desc}\nclass {filename.split('.')[0].title().replace('_', '')}:",
                    "output": code[:1200],
                    "category": "code_completion"
                })
        
        return data
    
    def generate_retrieval_data(self) -> List[Dict]:
        """生成检索策略数据"""
        strategies = [
            ("按需归因检索", "根据 Entity/Process/Session 三层归因，按需查询，不遍历全部"),
            ("时间衰减检索", "最近的记忆权重更高，遵循指数衰减"),
            ("重要性优先检索", "优先返回高重要性记忆，用于关键决策"),
            ("向量语义检索", "使用 LanceDB 进行向量相似度搜索，支持语义联想"),
        ]
        
        data = []
        for name, desc in strategies:
            # 任务 1: 策略选择
            data.append({
                "instruction": f"在什么情况下应该使用{name}？",
                "input": "",
                "output": f"{name}适用于以下场景：{desc}。例如，当用户需要快速获取关键信息时，可以选择重要性优先检索；当需要语义联想时，选择向量语义检索。",
                "category": "retrieval_strategy"
            })
            
            # 任务 2: 策略组合
            data.append({
                "instruction": "如何组合使用四种检索策略？",
                "input": "",
                "output": "智能检索支持四种模式：\n1. balanced - 四种策略均衡，每种取少量结果\n2. importance - 重要性优先，主要用重要性检索\n3. recent - 时效性优先，主要用时间衰减\n4. semantic - 语义优先，主要用向量检索\n根据查询类型自动选择合适的组合模式。",
                "category": "retrieval_combination"
            })
        
        return data
    
    def generate_knowledge_data(self) -> List[Dict]:
        """从数据库生成知识问答数据"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM memories 
            WHERE importance >= 7 
            ORDER BY RANDOM() 
            LIMIT 50
        """)
        
        data = []
        for row in cursor.fetchall():
            mem = dict(row)
            
            # 任务 1: 知识问答
            data.append({
                "instruction": f"关于 {mem['title']}，请详细介绍：",
                "input": "",
                "output": mem['content'][:1000],
                "category": "knowledge_qa"
            })
            
            # 任务 2: 知识应用
            data.append({
                "instruction": f"如何应用 {mem['title']} 中的知识？",
                "input": "",
                "output": f"基于 {mem['type']} 类型记忆，可以：\n1. 在相关场景中直接应用\n2. 作为决策依据\n3. 指导后续行动\n具体内容：{mem['content'][:500]}",
                "category": "knowledge_application"
            })
        
        return data
    
    def generate_conversation_data(self) -> List[Dict]:
        """生成对话数据"""
        conversations = [
            {
                "instruction": "你是谁？",
                "input": "",
                "output": "我是 Erbing，一个基于左右脑双系统架构的 AI 助手。我的左脑负责结构化记忆（SQLite），右脑负责向量语义记忆（LanceDB）。我支持四种检索策略：按需归因、时间衰减、重要性优先、向量语义。",
            },
            {
                "instruction": "你的核心能力是什么？",
                "input": "",
                "output": "我的核心能力包括：\n1. **双脑记忆系统** - 结构化 + 语义记忆\n2. **四策略检索** - 智能组合检索策略\n3. **数据库优先** - 所有知识存储在数据库中\n4. **持续学习** - 通过记忆不断进化\n5. **知识蒸馏** - 可将知识注入模型",
            },
            {
                "instruction": "你如何管理和检索记忆？",
                "input": "",
                "output": "我使用三层记忆架构：\n\n**左脑（SQLite）**：\n- 身份认知、原则、事件、偏好\n- 结构化存储，快速精确查询\n\n**右脑（LanceDB）**：\n- 语义记忆、思维链、关联、模式\n- 向量搜索，支持语义联想\n\n**四策略检索**：\n1. 按需归因 - 三层归因精确查询\n2. 时间衰减 - 近期记忆权重更高\n3. 重要性优先 - 关键决策优先\n4. 向量语义 - 语义相似搜索",
            },
            {
                "instruction": "Erbing-1B 架构是什么？",
                "input": "",
                "output": "Erbing-1B 是一个混合架构模型，主要特点：\n\n**架构**：\n- Hybrid Mamba-Transformer（12+12层）\n- 参数量：约 1B\n- 上下文：8K（可扩展32K）\n\n**双脑设计**：\n- 左脑模块：前6层，结构化推理\n- 右脑模块：后6层，语义联想\n- 中脑模块：整合协调\n\n**训练策略**：\n- 数据库优先训练\n- 四策略检索增强\n- QLoRA 微调支持",
            },
        ]
        
        return [{"instruction": c["instruction"], "input": c["input"], "output": c["output"], "category": "conversation"} for c in conversations]
    
    def save_to_json(self, data: Dict[str, List[Dict]], output_dir: Path):
        """保存训练数据为 JSON 文件"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 合并所有数据
        all_data = []
        stats = {"total": 0, "by_category": {}}
        
        for category, items in data.items():
            all_data.extend(items)
            stats["total"] += len(items)
            stats["by_category"][category] = len(items)
        
        # 保存完整数据集
        output_file = output_dir / "erbing_training_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in all_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        # 保存统计信息
        stats_file = output_dir / "training_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] Generated {stats['total']} training samples")
        print(f"[SAVED] {output_file}")
        print(f"[STATS] {stats}")
        
        return stats


def main():
    """生成训练数据"""
    print("="*60)
    print("ERBING Knowledge Distillation - Training Data Generator")
    print("="*60)
    
    generator = TrainingDataGenerator()
    
    # 生成所有数据
    print("\n[GENERATING] Creating training data from database...")
    data = generator.generate_all_data()
    
    # 保存数据
    output_dir = Path(__file__).parent / "data"
    stats = generator.save_to_json(data, output_dir)
    
    # 显示详细统计
    print("\n[DETAILS] By category:")
    for cat, count in stats["by_category"].items():
        print(f"  - {cat}: {count} samples")
    
    print("\n[NEXT] Training data ready for QLoRA fine-tuning")
    print("[HINT] Use with: Qwen/Qwen2.5-3B-Instruct")


if __name__ == "__main__":
    main()
