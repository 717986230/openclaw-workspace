#!/usr/bin/env python3
"""
蚁群蜂群协同进化引擎 - 统一策略协调和进化
"""
import json
from datetime import datetime
from pathlib import Path
import subprocess

class SwarmCoEvolver:
    """蚁群蜂群协同进化器"""
    
    def __init__(self):
        self.config_dir = Path("skills/swarm-orchestration/config")
        self.log_dir = Path("memory/swarm_co_evolution")
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def co_evolve(self):
        """协同进化"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        print(f"\n{'='*70}")
        print(f"[蚁群蜂群协同进化] {datetime.now().isoformat()}")
        print(f"{'='*70}\n")
        
        # 1. 蚁群策略进化
        print("[1/4] 蚁群策略进化...")
        ant_result = self._run_ant_evolution()
        
        # 2. 蜂群策略进化
        print("\n[2/4] 蜂群策略进化...")
        bee_result = self._run_bee_evolution()
        
        # 3. 协同优化
        print("\n[3/4] 协同优化...")
        synergy_result = self._optimize_synergy(ant_result, bee_result)
        
        # 4. 生成报告
        print("\n[4/4] 生成进化报告...")
        report = self._generate_report(ant_result, bee_result, synergy_result)
        
        # 保存结果
        self._save_evolution_log(report)
        
        return report
    
    def _run_ant_evolution(self):
        """运行蚁群进化"""
        try:
            result = subprocess.run(
                ["python", "scripts/ant_strategy_evolver.py"],
                capture_output=True, text=True, timeout=30
            )
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _run_bee_evolution(self):
        """运行蜂群进化"""
        try:
            result = subprocess.run(
                ["python", "scripts/bee_strategy_evolver.py"],
                capture_output=True, text=True, timeout=30
            )
            return {"status": "success", "output": result.stdout}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _optimize_synergy(self, ant_result, bee_result):
        """优化协同机制"""
        synergy = {
            "communication_protocol": {
                "ant_to_bee": "pheromone_handoff",
                "bee_to_ant": "quality_feedback",
                "frequency": "per_task"
            },
            "resource_allocation": {
                "ant_focus": "exploration",
                "bee_focus": "analysis",
                "overlap_handling": "priority_queue"
            },
            "conflict_resolution": {
                "strategy": "weighted_voting",
                "ant_weight": 0.4,
                "bee_weight": 0.6,
                "tie_breaker": "quality_score"
            }
        }
        
        return synergy
    
    def _generate_report(self, ant_result, bee_result, synergy_result):
        """生成进化报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "ant_evolution": ant_result,
            "bee_evolution": bee_result,
            "synergy_optimization": synergy_result,
            "next_evolution": "1小时后"
        }
        
        return report
    
    def _save_evolution_log(self, report):
        """保存进化日志"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        log_file = self.log_dir / f"co_evolution_{timestamp}.json"
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[保存] {log_file}")

def main():
    import sys
    
    evolver = SwarmCoEvolver()
    
    if "--once" in sys.argv:
        evolver.co_evolve()
    else:
        # 持续进化
        import schedule
        import time
        
        print("\n[蚁群蜂群协同进化系统启动]")
        print("进化周期: 每小时一次\n")
        
        evolver.co_evolve()
        
        schedule.every().hour.do(evolver.co_evolve)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    main()
