#!/usr/bin/env python3
"""
自我反思循环 - AutoGPT风格的持续改进机制
"""
import json
from pathlib import Path
from datetime import datetime

class SelfReflectionLoop:
    """自我反思和持续改进系统"""
    
    def __init__(self):
        self.log_dir = Path("memory/reflection_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def reflect(self, execution_result):
        """对执行结果进行反思"""
        
        # 1. 评估结果质量
        quality_score = self._evaluate_quality(execution_result)
        
        # 2. 识别问题
        issues = self._identify_issues(execution_result)
        
        # 3. 生成改进建议（限制数量）
        improvements = self._generate_improvements(issues)[:3]  # 最多3条
        
        # 4. 创建修正计划
        correction_plan = self._create_correction_plan(improvements)
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "issues_count": len(issues),
            "improvements_count": len(improvements),
            "correction_plan": correction_plan
        }
        
        # 保存反思记录（覆盖旧记录）
        self._save_reflection(reflection)
        
        return reflection
    
    def _evaluate_quality(self, result):
        """评估执行质量（简化）"""
        return min(100, 50 + (20 if result.get("output") else 0) + (20 if not result.get("errors") else 0) + (10 if result.get("duration", 0) < 60 else 0))
    
    def _identify_issues(self, result):
        """识别问题（简化）"""
        issues = []
        if result.get("errors"): issues.append("error")
        if not result.get("completed", True): issues.append("incomplete")
        if result.get("duration", 0) > 120: issues.append("slow")
        return issues
    
    def _generate_improvements(self, issues):
        """生成改进建议（精简）"""
        mapping = {"error": "添加错误处理", "incomplete": "检查前置条件", "slow": "优化执行流程"}
        return [mapping.get(i, "优化") for i in issues]
    
    def _create_correction_plan(self, improvements):
        """创建修正计划"""
        return [{"step": i+1, "action": imp, "status": "pending"} for i, imp in enumerate(improvements)]
    
    def _save_reflection(self, reflection):
        """保存反思记录（单文件）"""
        reflection_file = self.log_dir / "latest_reflection.json"
        with open(reflection_file, "w", encoding="utf-8") as f:
            json.dump(reflection, f, ensure_ascii=False, indent=2)

def main():
    loop = SelfReflectionLoop()
    test_result = {"output": "完成", "errors": [], "completed": True, "duration": 50}
    reflection = loop.reflect(test_result)
    print(f"\n[反思] 质量: {reflection['quality_score']}/100")
    print(f"  问题: {reflection['issues_count']}个")
    print(f"  改进: {reflection['improvements_count']}项")

if __name__ == "__main__":
    main()
