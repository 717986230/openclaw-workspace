#!/usr/bin/env python3
"""
持续反省机制 - 每次行动前后的自我检查
"""
import json
from pathlib import Path
from datetime import datetime

class ContinuousReflector:
    """持续反省系统"""
    
    def __init__(self):
        self.log_dir = Path("memory/reflection")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def before_action(self, action_type, action_detail):
        """行动前反思"""
        checks = {
            "necessary": self._check_necessity(action_detail),
            "duplicate": self._check_duplicate(action_detail),
            "reuse": self._check_reuse(action_detail),
            "maintenance": self._check_maintenance(action_detail)
        }
        
        should_proceed = all([
            checks["necessary"]["result"],
            not checks["duplicate"]["result"],
            checks["reuse"]["suggestion"] or True
        ])
        
        return {
            "should_proceed": should_proceed,
            "checks": checks,
            "timestamp": datetime.now().isoformat()
        }
    
    def after_action(self, action_type, result):
        """行动后评估"""
        evaluation = {
            "goal_achieved": self._evaluate_goal(result),
            "redundancy": self._evaluate_redundancy(result),
            "improvements": self._suggest_improvements(result)
        }
        
        # 保存评估
        self._save_evaluation(evaluation)
        
        return evaluation
    
    def _check_necessity(self, detail):
        """检查必要性"""
        # 如果是核心功能，必要
        core_keywords = ["采集", "学习", "进化", "优化"]
        is_necessary = any(kw in detail for kw in core_keywords)
        
        return {
            "result": is_necessary,
            "reason": "核心功能" if is_necessary else "评估是否真的需要"
        }
    
    def _check_duplicate(self, detail):
        """检查重复"""
        # 检查是否与现有功能重复
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            existing = [f.stem for f in scripts_dir.glob("*.py")]
            is_duplicate = any(script in detail.lower() for script in existing)
        else:
            is_duplicate = False
        
        return {
            "result": is_duplicate,
            "reason": "功能已存在" if is_duplicate else "无重复"
        }
    
    def _check_reuse(self, detail):
        """检查可复用"""
        can_reuse = "使用现有" in detail or "run.py" in detail
        
        return {
            "suggestion": "使用 run.py 调用现有脚本" if not can_reuse else "已考虑复用",
            "result": can_reuse
        }
    
    def _check_maintenance(self, detail):
        """检查维护负担"""
        will_add_burden = "新增" in detail and "脚本" in detail
        
        return {
            "result": not will_add_burden,
            "reason": "会增加维护负担" if will_add_burden else "无额外负担"
        }
    
    def _evaluate_goal(self, result):
        """评估目标达成"""
        return result.get("success", False)
    
    def _evaluate_redundancy(self, result):
        """评估冗余"""
        return result.get("created_files", 0) > 3
    
    def _suggest_improvements(self, result):
        """建议改进"""
        improvements = []
        
        if self._evaluate_redundancy(result):
            improvements.append("减少输出文件数量")
        
        if result.get("duration", 0) > 60:
            improvements.append("优化执行效率")
        
        return improvements
    
    def _save_evaluation(self, evaluation):
        """保存评估"""
        log_file = self.log_dir / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)

# 使用示例
def main():
    reflector = ContinuousReflector()
    
    # 行动前检查
    print("\n[行动前反思]")
    action = "创建新的采集脚本"
    check = reflector.before_action("create", action)
    
    print(f"  是否必要: {check['checks']['necessary']['reason']}")
    print(f"  是否重复: {check['checks']['duplicate']['reason']}")
    print(f"  复用建议: {check['checks']['reuse']['suggestion']}")
    print(f"  维护负担: {check['checks']['maintenance']['reason']}")
    print(f"\n  建议执行: {'是' if check['should_proceed'] else '否 - 重新考虑'}")

if __name__ == "__main__":
    main()
