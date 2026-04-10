#!/usr/bin/env python3
"""
AutoGPT风格任务分解器 - 自动拆解复杂任务
"""
import json
from pathlib import Path
from datetime import datetime

class AutoGPTTaskDecomposer:
    """自主任务分解系统"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.log_dir = Path("memory/task_decomposition")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def decompose(self, task_description):
        """分解任务为子任务"""
        
        # 1. 分析任务复杂度
        complexity = self._analyze_complexity(task_description)
        
        # 2. 识别主要步骤
        steps = self._identify_steps(task_description, complexity)
        
        # 3. 生成子任务列表
        subtasks = self._generate_subtasks(steps)
        
        # 4. 排序优先级
        prioritized = self._prioritize_subtasks(subtasks)
        
        # 5. 生成执行计划
        plan = {
            "original_task": task_description,
            "complexity": complexity,
            "subtasks": prioritized,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存计划
        self._save_plan(plan)
        
        return plan
    
    def _analyze_complexity(self, task):
        """分析任务复杂度"""
        # 简单启发式
        keywords = {
            "simple": ["查看", "读取", "显示", "列出"],
            "medium": ["修改", "创建", "更新", "删除"],
            "complex": ["设计", "构建", "实现", "优化", "重构"]
        }
        
        for level, words in keywords.items():
            for word in words:
                if word in task:
                    return level
        
        return "medium"
    
    def _identify_steps(self, task, complexity):
        """识别执行步骤"""
        
        templates = {
            "simple": [
                "收集信息",
                "执行操作",
                "验证结果"
            ],
            "medium": [
                "需求分析",
                "信息收集",
                "执行操作",
                "验证结果",
                "记录总结"
            ],
            "complex": [
                "需求分析",
                "方案设计",
                "信息收集",
                "分步实现",
                "测试验证",
                "优化改进",
                "文档总结"
            ]
        }
        
        return templates.get(complexity, templates["medium"])
    
    def _generate_subtasks(self, steps):
        """生成子任务"""
        subtasks = []
        
        for i, step in enumerate(steps, 1):
            subtasks.append({
                "id": f"subtask_{i:03d}",
                "name": step,
                "status": "pending",
                "dependencies": [] if i == 1 else [f"subtask_{i-1:03d}"]
            })
        
        return subtasks
    
    def _prioritize_subtasks(self, subtasks):
        """排序优先级"""
        # 按依赖关系排序（拓扑排序）
        # 简化版本：已经按顺序生成，直接返回
        return subtasks
    
    def _save_plan(self, plan):
        """保存执行计划"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        plan_file = self.log_dir / f"plan_{timestamp}.json"
        
        with open(plan_file, "w", encoding="utf-8") as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"[计划已保存] {plan_file}")

def main():
    import sys
    
    decomposer = AutoGPTTaskDecomposer()
    
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:])
    else:
        task = "构建一个完整的自动化工作流系统"
    
    print(f"\n[任务分解器]")
    print(f"原始任务: {task}\n")
    
    plan = decomposer.decompose(task)
    
    print(f"复杂度: {plan['complexity']}")
    print(f"子任务数: {len(plan['subtasks'])}\n")
    
    print("执行计划:")
    for subtask in plan['subtasks']:
        deps = ", ".join(subtask['dependencies']) if subtask['dependencies'] else "无"
        print(f"  [{subtask['id']}] {subtask['name']} (依赖: {deps})")

if __name__ == "__main__":
    main()
